import asyncio
from typing import Callable, Iterable
from telebot.async_telebot import AsyncTeleBot
from dataclasses_for_parsing import PhotoKeeper, ResultsStorage
from parse_data import ParseHotelData
from requester import AioRequester, ReqParams, NoData


class Processor:
    """Class which contains methods and attributes required for requesting,
    processing responses and following output of prepared data
    """
    def __init__(self, form, ses_context, bot, req_params, mes_id,
                 semaphore):
        self._form: dict = form
        self._c_session: AioRequester = ses_context()
        self._params: ReqParams = req_params(form)
        self._bot: AsyncTeleBot = bot
        self._mes: int = mes_id
        self._need_photo: bool = self._form.get('get_photos')
        self._limit = int(form.get('pageSize'))
        self._semaphore: asyncio.BoundedSemaphore = semaphore(4)
        self._photos = PhotoKeeper()

    async def __get_data(self) -> ResultsStorage:
        """
        Method which runs a series of requests for necessary data
        :return: an instance of ResultsStorage which contains collected hotels
        """
        async with self._c_session as session:
            try:
                distids = await session.make_req(
                    self._semaphore, self._c_session.LOCATIONS,
                    self._params.get_locals(), session.req_timeout)
                print(f'destination ids received')
                distids = ParseHotelData().get_dids(distids)
                print(f'destination ids parsed')
                hotels = self._req_batch(
                    self._semaphore, session, distids,
                    self._c_session.PROPERTIES, self._request_params())
                print('started gathering')
                hotels = await asyncio.gather(*hotels)
                print('finished gathering')
                hotels = ParseHotelData().get_hotels(hotels)
                hotels = ParseHotelData().hotel_data(
                    hotels, self._limit, self._form.get('params'))
                if self._need_photo:
                    await self._get_photos(hotels, self._semaphore, session,
                                           self._params.get_photos)
                    print('finished gathering photo')
                return hotels
            except NoData:
                await self._bot.send_message(chat_id=self._mes,
                                             text='no data found')

    async def send_data_to_user(self, prep_data: ResultsStorage) -> None:
        """Method which is responsible for sending collected information
        back to user
        """
        for hotel in sorted(prep_data.list_of_results):
            print(f'sending hotel {hotel.id} data')
            await self._bot.send_message(chat_id=self._mes, text=hotel)
            if hotel.id in self._photos.collected_photos:
                batch = self._photos.collected_photos.get(hotel.id)
                await self._bot.send_media_group(chat_id=self._mes,media=batch)

    def _request_params(self) -> Callable:
        """Method which returns suitable method of ReqParams class depending on
        type of command user selected
        """
        if self._form.get('params') in ['/lowest_price', '/highest_price']:
            return self._params.get_properties
        return self._params.get_best_deal

    @classmethod
    def _req_batch(cls, semaphore, session, ids, endpoint, req_params):
        """Method for creating batch of requests for following execution in
        asyncio.gather
        :param session: ClientSession context manager
        :param ids: list which contains necessary ids
        :param endpoint: an endpoint for request stored inside AioRequester
        :param req_params: returned dict of request parameters from
        ReqParams method"""
        semaphore: asyncio.BoundedSemaphore
        session: AioRequester
        endpoint: AioRequester
        req_params: Callable
        ids: Iterable

        tasks = []
        print('started req_batch')
        for c_id in ids:
            tasks.append(asyncio.create_task(session.make_req(
                semaphore, endpoint, req_params(c_id), session.req_timeout)))
        print('finished req_batch')
        return tasks

    async def _get_photos(self, hotels, semaphore, session, req_params) -> \
            PhotoKeeper:
        """Method for requesting photos for each of given hotel
        :param hotels: ResultsStorage object which contains list of
        FoundHotel objects
        :param semaphore: asyncio.BoundedSemaphore for strict limiting
        number of simultaneous requests
        :param session: ClientSession context manager
        :param req_params: GetPhotoReq dataclass for request parametrizing
        """
        hotels: ResultsStorage
        semaphore: asyncio.BoundedSemaphore
        session: AioRequester
        req_params: Callable

        hotel_ids = [hotel.id for hotel in hotels.list_of_results]
        photos = self._req_batch(semaphore, session, hotel_ids,
                                 self._c_session.GET_PHOTOS, req_params)
        print('gathering photos')
        photos = await asyncio.gather(*photos)
        print('finished gathering photos')
        return ParseHotelData().get_photo_urls(self._photos, photos)

    async def operate(self) -> None:
        """
        Method which starts gathering and outputting information
        """
        list_of_hotels = await self.__get_data()
        await self.send_data_to_user(list_of_hotels)
        