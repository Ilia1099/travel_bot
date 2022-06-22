from dataclasses_for_requests import BASE_REQUEST_PARAMS, PropParams, \
    BestDeal, CommonParams, GetPhotoReq, asdict
import time
import asyncio
import aiohttp


class NoData(BaseException):
    """Exception for case when response doesn't contain data in body"""


class ReqParams:
    """Class for preparing request parameters"""
    def __init__(self, form: dict):
        self._form = form

    def get_locals(self) -> dict:
        """Method which creates instance of CommonParams class and returns it
        as dict"""
        return asdict(CommonParams(query=self._form.get('query')))

    def get_properties(self, destid: str) -> dict:
        """Method which creates instance of PropParams class and returns it as
        dict"""
        if destid.isdigit():
            query, checkout, checkin, pagesize, sortorder = self._fill_params()
            return asdict(PropParams(query=query, checkIn=checkin,
                                     checkOut=checkout, pageSize=pagesize,
                                     destinationId=destid, sortOrder=sortorder))
        raise TypeError('variable destid is not a digit string')

    def get_best_deal(self, destid: str) -> dict:
        """Method which creates instance of BestDeal class and returns it
        as dict"""
        if destid.isdigit():
            query, checkout, checkin, pagesize, sortorder = self._fill_params()
            maxprice = self._form.get('priceMax')
            minprice = self._form.get('priceMin')
            return asdict(BestDeal(query=query, checkIn=checkin,
                                   checkOut=checkout, pageSize=pagesize,
                                   destinationId=destid, sortOrder=sortorder,
                                   priceMin=minprice, priceMax=maxprice))
        raise TypeError('variable destid is not a digit string')

    @classmethod
    def get_photos(cls, hotel_id: int) -> dict:
        """Method which creates instance of GetPhotoReq class and returns it as
        dict"""
        if isinstance(hotel_id, int):
            return asdict(GetPhotoReq(id=str(hotel_id)))
        raise TypeError("hotel_id variable is not an integer")

    def _fill_params(self) -> tuple:
        query = self._form.get('query')
        checkin = self._form.get('checkIn')
        checkout = self._form.get('checkOut')
        pagesize = self._form.get('pageSize')
        sortorder = self._form.get('sortOrder')
        return query, checkout, checkin, pagesize, sortorder


class AioRequester:
    """Class context manager for creating session"""
    LOCATIONS = '/locations/v2/search'
    PROPERTIES = '/properties/list'
    GET_PHOTOS = '/properties/get-hotel-photos'

    async def __aenter__(self):
        self.req_timeout = aiohttp.ClientTimeout(total=10)
        self.__c_session = aiohttp.ClientSession(
            base_url=BASE_REQUEST_PARAMS.base_url,
            headers=BASE_REQUEST_PARAMS.headers)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.__c_session.close()
        self.__c_session = None

    async def make_req(self, mysem: asyncio.BoundedSemaphore, sub_url,
                       parameters, timeout) -> dict | None:
        """Method for making get requests inside given Session
        :param mysem: asyncio.BoundedSemaphore for strict limiting number of
        simultaneous requests
        :param sub_url: an endpoint for current data
        :param parameters: parameters for current batch of requests
        :param timeout: aiohttp.ClientTimeout object with set total timeout
        limit
        """
        async with mysem:
            print(f"Successfully acquired the semaphore")
            started = time.time()
            async with self.__c_session.get(
                    sub_url, timeout=timeout, params=parameters) as resp:
                result = await resp.json()
                print(f"Successfully released the semaphore")
                delta = time.time() - started
                if delta < 1:
                    await asyncio.sleep(1 - delta)
                return result
