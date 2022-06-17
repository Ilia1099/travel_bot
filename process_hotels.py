import asyncio
from typing import Callable, List
from telebot.async_telebot import AsyncTeleBot
from dataclasses_for_parsing import PhotoKeeper, ResultsStorage
from parse_data import ParseData
from requester import AioRequester, ReqParams


class Processor:
    def __init__(self, form: dict, bot: AsyncTeleBot, mes: int):
        self._c_session: AioRequester = AioRequester()
        self._params = ReqParams(form)
        self._bot = bot
        self._mes = mes
        self._req_param: ReqParams
        self._need_photo: bool = False
        self._limit = int(form.get('pageSize'))
        self._set_request_params(form)
        self._semaphore = asyncio.BoundedSemaphore(4)
        self._photos = PhotoKeeper()
        self._hotels = []

    async def __get_data(self) -> ResultsStorage:
        async with self._c_session as ses:
            distids = await ses.make_req(
                self._semaphore, self._c_session.LOCATIONS,
                self._params.get_locals())
            distids = ParseData().get_dids(distids)
            self._hotels = self._req_batch(
                self._semaphore, ses, distids, self._c_session.PROPERTIES,
                self._req_param)
            print('started gathering')
            self._hotels = await asyncio.gather(*self._hotels)
            print('finished gathering')
            self._hotels = ParseData().get_hotels(self._hotels)
            self._hotels = ParseData().hotel_data(self._hotels)
            if self._need_photo:
                await self._get_photos(self._hotels, self._semaphore,
                                       ses, self._c_session.GET_PHOTOS)
            return self._hotels

    async def send_data_to_user(self, prep_data: ResultsStorage):
        for hotel in sorted(prep_data.list_of_results)[:self._limit]:
            await self._bot.send_message(chat_id=self._mes, text=hotel)
            if self._need_photo:
                for photo in self._photos.collected_photos.get(hotel.id):
                    await self._bot.send_photo(chat_id=self._mes, photo=photo)

    def _set_request_params(self, form: dict):
        if form.get('get_photos') == 'Yes':
            self._need_photo = True
        if form.get('params') in ['/lowest_price', '/highest_price']:
            self._req_param = self._params.get_properties
        else:
            self._req_param = self._params.get_best_deal

    @classmethod
    def _req_batch(cls, sem, session, ids, endpoint, re_params):
        """Method for creating batch of requests for following execution in
        asyncio.gather
        :param session: ClientSession context manager
        :param ids: list which contains necessary ids
        :param endpoint: an endpoint for request stored inside AioRequester
        :param re_params: returned dict of request parameters from
        ReqParams method"""
        sem: asyncio.BoundedSemaphore
        session: AioRequester
        endpoint: AioRequester
        re_params: Callable
        ids: List
        tasks = []
        for c_id in ids:
            tasks.append(asyncio.create_task(session.make_req(
                sem, endpoint, re_params(c_id))))
        return tasks

    async def _get_photos(self, hotels, sem, session, re_params):
        """
        Method for requesting photos for each of given hotel
        :param hotels: ResultsStorage object which contains list of
        FoundHotel objects
        :param sem: asyncio.BoundedSemaphore for strict limiting number of
        simultaneous requests
        :param session: ClientSession context manager
        :param re_params: GetPhotoReq dataclass for parametrizing request
        :return:
        """
        hotels: ResultsStorage
        sem: asyncio.BoundedSemaphore
        session: AioRequester
        re_params: Callable

        hotel_ids = [hotel.id for hotel in hotels.list_of_results]
        photos = self._req_batch(sem, session, hotel_ids,
                                 self._c_session.GET_PHOTOS, re_params)
        photos = await asyncio.gather(*photos)
        return ParseData().get_photo_urls(self._photos, photos)

    async def operate(self):
        list_of_hotels = await self.__get_data()
        await self.send_data_to_user(list_of_hotels)