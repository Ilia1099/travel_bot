from typing import Any, IO, List, Iterator, Iterable
from decouple import config
from os import linesep
import re
import asyncio
import aiohttp
import datetime
from telebot.async_telebot import AsyncTeleBot, types

example = {'sortOrder': 'PRICE_HIGHEST_FIRST', 'params': '/highest_price',
           'query': 'usa new york', 'pageSize': '7',
           'checkIn': '2022.12.12', 'checkOut': '2022.12.12',
           'get_photos': 'Yes'}

tes_form = {'sortOrder': 'PRICE', 'params': '/lowest_price', 'query': 'h h',
            'pageSize': '4', 'checkIn': '2022-12-12', 'checkOut': '2022-12-12',
            'get_photos': 'Yes'}


class ReqParams:
    """Class for preparing request parameters"""
    __loc_params = {"query": None, "locale": "en_US", "currency": "USD"}
    __prop_params = {"pageNumber": "1",
                     "pageSize": None, "checkIn": '', "checkOut": '',
                     "adults1": "1", "sortOrder": None, "locale": "en_US",
                     "currency": "USD"}
    __photo_params = {"id": None}

    def __init__(self, form: dict):
        self.__form = form
        self.__query = self.__form.pop('query', None)
        self.__need_photo = self.__form.pop('get_photos', None)
        self.__query_type = self.__form.pop('params', None)
        self._closer = self.__form.pop('not_closer', None)
        self.__farther = self.__form.pop('not_farther', None)

    async def get_locals(self) -> dict:
        """
        Method which updates template parameter and returns it
        """
        self.__loc_params['query'] = self.__query
        return self.__loc_params

    async def get_properties(self, destid: str) -> dict:
        """
        Method which updates template parameter and returns it
        """
        await self.__date_to_int()
        self.__prop_params.update(self.__form)
        self.__prop_params['destinationId'] = destid
        return self.__prop_params

    async def get_photos(self, hotel_id: str):
        """
        Method which updates template parameter and returns it
        """
        self.__photo_params = hotel_id
        return self.__photo_params

    async def __date_to_int(self):
        """
        Method which converts string data inside form into iso standard
        """
        for date in ('checkIn', 'checkOut'):
            n_date = list(map(int, re.split(r"[!#$%&'()*+,-./:;<=>?@[\]^_`{"
                                            r"|}~]", self.__form.get(date))))
            self.__form[date] = datetime.date(*n_date).isoformat()


class AioRequester:
    """Class context manager for creating session"""
    __HEADERS = headers = {"X-RapidAPI-Host": "hotels4.p.rapidapi.com",
                           "X-RapidAPI-Key": config('hotels_api_token')}
    __ROOT_URL = 'https://hotels4.p.rapidapi.com'
    LOCATIONS = '/locations/v2/search'
    PROPERTIES = '/properties/list'
    GET_PHOTOS = '/properties/get-hotel-photos'

    async def __aenter__(self):
        self.__c_session = aiohttp.ClientSession(base_url=self.__ROOT_URL,
                                                 headers=self.__HEADERS)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.__c_session.close()
        self.__c_session = None

    async def make_req(self, sub_url, parameters) -> dict:
        """
        Method for making get requests inside given Session
        :param sub_url: current endpoint
        :param parameters: parameters necessary for current endpoint
        """
        async with self.__c_session.get(sub_url, params=parameters) as resp:
            print(resp.status)
            return await resp.json()


class ParseData:
    """Class for parsing data"""
    def __init__(self):
        self.__c_hotels = []

    async def get_values(self, response: dict, c_key: str) -> List:
        """
        A method which recursively parses given dictionary to find required
        value
        :param response: Response.json() object
        :param c_key: necessary key
        :return: list of objects found in value
        """
        if c_key in response.keys():
            self.__c_hotels.insert(0, response.get(c_key))
        else:
            for key in response:
                if isinstance(response[key], dict):
                    await self.get_values(response.get(key), c_key)
                elif isinstance(response[key], list):
                    for dct in response.get(key):
                        await self.get_values(dct, c_key)
        return self.__c_hotels

    async def prep_user_response(self, list_of_hotels: List[dict]):
        for ind, hotel in enumerate(list_of_hotels):
            ind = dict()
            ind['name'] = hotel['name']
            ind['address'] = await self.__from_nested_dict(
                hotel['address'])
            ind['price'] = await self.__from_nested_dict(
                hotel['ratePlan']['price'])
            ind['distance'] = await self.__from_nested_dict(
                hotel['landmarks'][0])
            yield ind

    @classmethod
    async def __from_nested_dict(cls, ad_dict: dict):
        ad_line = ' '.join([ad_dict[key] for key in ad_dict
                            if isinstance(ad_dict[key], str) and ad_dict[key]])
        return ad_line


class Processor:
    def __init__(self, form: dict, bot: AsyncTeleBot, mes: int):
        self.__c_session: AioRequester = AioRequester()
        self.__params = ReqParams(form)
        self.__bot = bot
        self.__mes = mes
        self.__counter = 1

    async def __get_data(self) -> List:
        async with self.__c_session as ses:
            hotels = []
            distids = await ses.make_req(self.__c_session.LOCATIONS,
                                         await self.__params.get_locals())
            distids = await ParseData().get_values(distids, 'destinationId')
            for d_id in distids:
                if self.__counter % 5 == 0:
                    await asyncio.sleep(2)
                print(f'request {d_id}')
                hotels.append(asyncio.create_task(ses.make_req(
                    self.__c_session.PROPERTIES,
                    await self.__params.get_properties(d_id))))
                self.__counter += 1
            print('started gathering')
            hotels = await asyncio.gather(*hotels)
            print('finished gathering')
            # здесь код виснет
            hotels = sum([sum(await ParseData().get_values(hotel, 'results'), [])
                      for hotel in hotels], [])
            print(hotels)
            return hotels

    async def send_data_to_user(self, list_of_hotels: List):
        def get_prise(hotel: dict): return hotel.get('price')
        print('started messaging')
        responses = [hotel async for hotel
                     in ParseData().prep_user_response(list_of_hotels)]
        for hotel in sorted(responses, key=get_prise):
            message = f'{linesep}' \
                      f'Hotel name: {hotel.get("name")}{linesep}' \
                      f'Address: {hotel.get("address")}{linesep}' \
                      f'Lowest price: {hotel.get("price")}{linesep}' \
                      f'Distance from {hotel.get("distance").lower()}{linesep}'
            await self.__bot.send_message(chat_id=self.__mes, text=message)

    async def operate(self):
        list_of_hotels = await self.__get_data()
        await self.send_data_to_user(list_of_hotels)

# if __name__ == '__main__':
#     asyncio.run(Processor().__get_data())
