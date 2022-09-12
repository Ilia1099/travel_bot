import asyncio
from typing import Callable, Iterable
from telebot import formatting
from telebot.async_telebot import AsyncTeleBot
from dataclasses_for_parsing import PhotoKeeper, ResultsStorage
from parse_data import ParseHotelData
from requester import AioRequester, ReqParams
from custom_exceptions import NoData
from work_with_db.push_data import UpdateDb
from markups import FormTextResp
from logging_class import my_log


@my_log
class Processor:
    """Class which contains methods and attributes required for requesting,
    processing responses and following output of prepared data
    """
    def __init__(self, **kwargs):
        self._form: dict = kwargs.get('form')
        self._c_session: AioRequester = AioRequester()
        self._params: ReqParams = ReqParams(self._form)
        self._bot: AsyncTeleBot = kwargs.get('bot')
        self._user_id: int = kwargs.get('user_id')
        self._need_photo: bool = self._form.get('get_photos')
        self._pagesize = int(self._form.get('pageSize'))
        self._photo_limit = int(self._form.get('end_step', 10))
        self._semaphore: asyncio.BoundedSemaphore = asyncio.BoundedSemaphore(4)
        self._format: FormTextResp = FormTextResp()
        self._photos = PhotoKeeper()
        self._hotels = None

    async def _get_data(self) -> ResultsStorage:
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
                distids = ParseHotelData().get_dids(response=distids)
                print(f'destination ids parsed')
                hotels = self._req_batch(
                    semaphore=self._semaphore, session=session, ids=distids,
                    endpoint=self._c_session.PROPERTIES,
                    req_params=self._request_params())
                print('started gathering')
                hotels = await asyncio.gather(*hotels)
                print('finished gathering')
                hotels = ParseHotelData().get_hotels(list_of_responses=hotels)
                hotels = ParseHotelData().hotel_data(
                    hotels, self._pagesize, self._form)
                if self._need_photo:
                    await self._get_photos(hotels, self._semaphore, session,
                                           self._params.get_photos)
                    print('finished gathering photo')
                return hotels
            except NoData:
                await self._bot.send_message(chat_id=self._user_id,
                                             text='no data found')

    async def _send_data_to_user(self, prep_data: ResultsStorage) -> None:
        """Method which is responsible for sending collected information
        back to user
        """
        self._hotels = prep_data
        for hotel in sorted(prep_data.list_of_results):
            text = formatting.format_text(
                    self._format.main_text(['Name: ', hotel.name]),
                    self._format.main_text(['Address: ', hotel.address]),
                    self._format.main_text([f"Distance from {hotel.label}: ",
                                            hotel.distance]),
                    self._format.main_text(['Current average price per '
                                            'night: ', hotel.exact_price]),
                    self._format.main_text(['URL: ', hotel.hotel_url])
                    )
            print(f'sending hotel {hotel.id} data')
            if hotel.id in self._photos.collected_photos:
                batch = self._photos.collected_photos.get(hotel.id)
                from telebot.types import InputMediaPhoto
                batch[0] = InputMediaPhoto(
                    batch[0].media, caption=text, parse_mode='MarkdownV2')
                await self._bot.send_media_group(
                    chat_id=self._user_id, media=batch)
            else:
                await self._bot.send_message(
                    self._user_id, text, parse_mode='MarkdownV2')

    def _request_params(self) -> Callable:
        """Method which returns suitable method of ReqParams class depending on
        type of command user selected
        """
        if self._form.get('params') in ['lowest_price', 'highest_price']:
            return self._params.get_properties
        return self._params.get_best_deal

    @staticmethod
    def _req_batch(*args, **kwargs):
        """Method for creating batch of requests for following execution in
        asyncio.gather
        :param session: ClientSession context manager
        :param ids: list which contains necessary ids
        :param endpoint: an endpoint for request stored inside AioRequester
        :param req_params: returned dict of request parameters from
        ReqParams method"""
        semaphore: asyncio.BoundedSemaphore = kwargs.get('semaphore')
        session: AioRequester = kwargs.get('session')
        endpoint: AioRequester = kwargs.get('endpoint')
        req_params: Callable = kwargs.get('req_params')
        ids: Iterable = kwargs.get('ids')

        tasks = []
        print('started req_batch')
        for c_id in ids:
            tasks.append(asyncio.create_task(session.make_req(
                semaphore, endpoint, req_params(id=c_id),
            session.req_timeout)))
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
        photos = self._req_batch(
            semaphore=semaphore, session=session, ids=hotel_ids,
            endpoint=self._c_session.GET_PHOTOS, req_params=req_params)
        photos = await asyncio.gather(*photos)
        print('finished gathering photos')
        return ParseHotelData().get_photo_urls(
            photos=self._photos, list_of_resps=photos,
            photo_limit=self._photo_limit)

    async def operate(self) -> None:
        """
        Method which starts gathering and outputting information
        """
        list_of_hotels = await self._get_data()
        await self._send_data_to_user(list_of_hotels)
        print('db started')
        await (UpdateDb(
            io_hotels=self._hotels.list_of_results, form=self._form,
            user_id=self._user_id, photos=self._photos
        ).main())
        