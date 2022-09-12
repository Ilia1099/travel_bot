from dataclasses import asdict

from telebot import formatting

from dataclasses_for_parsing import FoundHotel
from markups import FormTextResp

f = FormTextResp()



class TestFoundHotel:
    test_hotel = FoundHotel(
        id=1111,
        name='aaaa',
        address='bbbb',
        label='lllll',
        distance='00000',
        price='12',
        exact_price=13,
        query_type='low',
        total_days=10
    )

    def test_output(self):
        print(self.test_hotel)
        # print(asdict(self.test_hotel))
        # print(type(asdict(self.test_hotel).get('print_info')))
