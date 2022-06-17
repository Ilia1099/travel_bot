from typing import Iterable, List
from dataclasses_for_parsing import FoundHotel, ResultsStorage, PhotoKeeper


class ParseData:
    """Class for parsing data"""
    def __init__(self):
        self.__c_hotels = []

    def get_hotels(self, list_of_responses: Iterable):
        print('gathering hotels')
        current_results = ResultsStorage()
        for resp in list_of_responses:
            # print(resp)
            if 'OK' == resp.get('result'):
                resp = resp.get('data').get('body').get('searchResults').get(
                    'results')
                current_results.list_of_results.extend(resp)
                # print(resp)
        print('finished gathering hotels')
        return current_results

    def hotel_data(self, results: ResultsStorage):
        # get rid of dublicates
        print('preparing responses')
        for ind, hotel in enumerate(results.list_of_results):
            c_hotel = FoundHotel(
                id=hotel.get('id'),
                name=hotel.get('name'),
                address=self.__from_nested_dict(hotel.get('address')),
                label=hotel.get('landmarks')[0].get('label'),
                distance=hotel.get('landmarks')[0].get('distance'),
                price=hotel.get('ratePlan').get('price').get('current'),
                exact_price=hotel.get('ratePlan').get('price').get(
                    'exactCurrent')
            )
            results.list_of_results[ind] = c_hotel
        print('finished preparation responses')
        return results

    @classmethod
    def get_dids(cls, response: dict) -> List:
        """
        Method which retrieves destinationid of city from CITY group and
        returns it as a list
        """
        entities = response.get('suggestions')[0].get('entities')
        return [entities[0].get('destinationId')]

    @classmethod
    def get_photo_urls(cls, photos: PhotoKeeper,
                       list_of_resps: Iterable[dict]):
        for resp in list_of_resps:
            photos.collected_photos[resp.get('hotelId')] = resp.get(
                'hotelImages')
        for val in photos.collected_photos.values():
            for ind, url in enumerate(val):
                c_url = url.get('baseUrl')
                c_url = ''.join([c_url[:len(c_url)-10], 'd.jpg'])
                val[ind] = c_url
        return photos

    @classmethod
    def __from_nested_dict(cls, ad_dict: dict):
        ad_line = ' '.join([ad_dict[key] for key in ad_dict
                            if isinstance(ad_dict[key], str) and ad_dict[key]])
        return ad_line
