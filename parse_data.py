from typing import Iterable, Sequence
from custom_exceptions import NoData
from dataclasses_for_parsing import FoundHotel, ResultsStorage, PhotoKeeper
from telebot.types import InputMediaPhoto
from datetime import datetime
from logging_class import my_log


@my_log
class ParseHotelData:
    """Class which contains methods for parsing data received from raidapi
    hotels"""
    @staticmethod
    def get_hotels(*args, **kwargs) -> ResultsStorage:
        """
        Method which iterates over container with responses and extracts
        hotels data from them
        :param list_of_responses: container with gathered responses
        :return: ResultsStorage instance
        """
        list_of_responses: Iterable = kwargs.get('list_of_responses')
        print('gathering hotels')
        current_results = ResultsStorage()
        for resp in list_of_responses:
            if resp.get('result') == 'OK':
                resp = resp.get('data').get('body').get('searchResults').get(
                    'results')
                current_results.list_of_results.extend(resp)
        print('finished gathering hotels')
        return current_results

    def hotel_data(self, results: ResultsStorage, limit: int, form: dict):
        """
        Method which take ResultsStorage with extracted hotels data and
        continues processing by creating FoundHotel dataclass instance
        :param results:
        :param limit: maximum length of list with results, depends on users
        choice
        :param form: request parameters
        :return: same but updated ResultsStorage object
        """
        print('preparing responses')
        query = form.get('params')
        start_date = datetime.strptime(form.get('checkOut'), '%Y-%m-%d')
        end_date = datetime.strptime(form.get('checkIn'), '%Y-%m-%d')
        delta_days = end_date-start_date
        for ind, hotel in enumerate(results.list_of_results):
            c_hotel = FoundHotel(
                id=hotel.get('id'),
                name=hotel.get('name'),
                address=self._get_address(ad_dict=hotel.get('address')),
                label=hotel.get('landmarks')[0].get('label'),
                distance=hotel.get('landmarks')[0].get('distance'),
                price=hotel.get('ratePlan').get('price').get('current'),
                exact_price=hotel.get('ratePlan').get('price').get(
                    'exactCurrent'),
                query_type=query,
                total_days=int(delta_days.days)
            )
            results.list_of_results[ind] = c_hotel
        results.list_of_results = sorted(results.list_of_results)[:limit]
        print('finished preparation responses')
        return results

    @staticmethod
    def get_dids(*args, **kwargs) -> tuple | None:
        """Method which retrieves destinationid of city from CITY group and
        returns it as a list, if no results were received raises NoData
        exception
        """
        response: dict = kwargs.get('response')
        entities = response.get('suggestions')[0].get('entities')
        if entities:
            return tuple([entities[0].get('destinationId')])
        raise NoData

    @staticmethod
    def get_photo_urls(*args, **kwargs) -> PhotoKeeper:
        """A method which receives list of responses containing photos of
        requested hotels, retrieves template url and adds size parameter to
        each, then creates a record inside PhotoKeeper.collected_photos
        dictionary with hotelId as key and list of InputMediaPhoto objects
        as value
        :param photo_limit: amount of photos to be viewed max 8
        :param photos: PhotoKeeper object
        :param list_of_resps: list of gathered responses
        """
        photos: PhotoKeeper = kwargs.get('photos')
        list_of_resps: Sequence[dict] = kwargs.get('list_of_resps')
        photo_limit: int = kwargs.get('photo_limit')
        # TODO
        # remove second loop into separate function, this method still
        # returns PhotoKeeper
        # while sending hotels to user transform list of photos into list of
        # inputmediaphoto and override it in the same PhotoKeeper

        size = 'z'
        for resp in list_of_resps:
            photos.collected_photos[resp.get('hotelId')] = resp.get(
                'hotelImages')[:photo_limit]
        for key, val in photos.collected_photos.items():
            for ind, url in enumerate(val[:photo_limit]):
                c_url = url.get('baseUrl')
                c_url = ''.join([c_url[:len(c_url)-10], f'{size}.jpg'])
                val[ind] = InputMediaPhoto(c_url, parse_mode='MarkdownV2')
        return photos

    @staticmethod
    def _get_address(*args, **kwargs) -> str:
        """
        Method for extracting all address related data and combing it into
        single string
        :param ad_dict: nested dictionary which contains address related data
        :return: full address string
        """
        ad_dict: dict = kwargs.get('ad_dict')
        ad_line = ' '.join([ad_dict[key] for key in ad_dict
                            if isinstance(ad_dict[key], str) and ad_dict[key]])
        return ad_line

