from typing import Iterable, Sequence
from dataclasses_for_parsing import FoundHotel, ResultsStorage, PhotoKeeper
from requester import NoData
from telebot.types import InputMediaPhoto


class ParseHotelData:
    """Class which contains methods for parsing data received from raidapi
    hotels"""
    @classmethod
    def get_hotels(cls, list_of_responses: Iterable) -> ResultsStorage:
        """
        Method which iterates over container with responses and extracts
        hotels data from them
        :param list_of_responses: container with gathered responses
        :return: ResultsStorage instance
        """
        print('gathering hotels')
        current_results = ResultsStorage()
        for resp in list_of_responses:
            if resp.get('result') == 'OK':
                resp = resp.get('data').get('body').get('searchResults').get(
                    'results')
                current_results.list_of_results.extend(resp)
        print('finished gathering hotels')
        return current_results

    def hotel_data(self, results: ResultsStorage, limit: int, query: str):
        """
        Method which take ResultsStorage with extracted hotels data and
        continues processing by creating FoundHotel dataclass instance
        :param results:
        :param limit: maximum length of list with results, depends on users
        choice
        :param query: type of query which represents a command selected by user
        :return: same but updated ResultsStorage object
        """
        print('preparing responses')
        for ind, hotel in enumerate(results.list_of_results):
            c_hotel = FoundHotel(
                id=hotel.get('id'),
                name=hotel.get('name'),
                address=self._get_address(hotel.get('address')),
                label=hotel.get('landmarks')[0].get('label'),
                distance=hotel.get('landmarks')[0].get('distance'),
                price=hotel.get('ratePlan').get('price').get('current'),
                exact_price=hotel.get('ratePlan').get('price').get(
                    'exactCurrent'),
                query_type=query
            )
            results.list_of_results[ind] = c_hotel
        results.list_of_results = sorted(results.list_of_results)[:limit]
        print('finished preparation responses')
        return results

    @classmethod
    def get_dids(cls, response: dict) -> tuple | None:
        """Method which retrieves destinationid of city from CITY group and
        returns it as a list, if no results were received raises NoData
        exception
        """
        entities = response.get('suggestions')[0].get('entities')
        if entities:
            return tuple([entities[0].get('destinationId')])
        raise NoData

    @classmethod
    def get_photo_urls(cls, photos: PhotoKeeper,list_of_resps: Sequence[dict])\
            -> PhotoKeeper:
        """A method which receives list of responses containing photos of
        requested hotels, retrieves template url and adds size parameter to
        each, then creates a record inside PhotoKeeper.collected_photos
        dictionary with hotelId as key and list of InputMediaPhoto objects
        as value
        :param photos: PhotoKeeper object
        :param list_of_resps: list of gathered responses
        """
        for resp in list_of_resps:
            photos.collected_photos[resp.get('hotelId')] = resp.get(
                'hotelImages')
        for key, val in photos.collected_photos.items():
            limit = len(val) // 5
            for ind, url in enumerate(val[::limit]):
                c_url = url.get('baseUrl')
                c_url = ''.join([c_url[:len(c_url)-10], 'd.jpg'])
                val[ind] = InputMediaPhoto(c_url)
            else:
                photos.collected_photos[key] = val[:5]
        return photos

    @classmethod
    def _get_address(cls, ad_dict: dict) -> str:
        """
        Method for extracting all address related data and combing it into
        single string
        :param ad_dict: nested dictionary which contains address related data
        :return: full address string
        """
        ad_line = ' '.join([ad_dict[key] for key in ad_dict
                            if isinstance(ad_dict[key], str) and ad_dict[key]])
        return ad_line
