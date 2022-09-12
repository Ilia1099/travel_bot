from unittest.mock import Mock, patch, MagicMock
from unittest import TestCase

import pytest
from telebot.types import InputMediaPhoto

from bot_models import Users, Queries, Hotels
from mock_alchemy.mocking import AlchemyMagicMock
from process_history import ShowQueryHistory
from work_with_db import push_data
from dataclasses_for_parsing import FoundHotel, PhotoKeeper
from work_with_db.push_data import UpdateDb


class TestSaveQr:
    test_hotel = FoundHotel(
        id=222222,
        name='Testing2',
        address='abrakadabra street',
        distance='23km',
        price='10',
        exact_price=11,
        query_type='lower',
        total_days=2,
        label='kkk'
    )
    list_of_hotels = [test_hotel]
    user_id = 222222
    p_keeper = PhotoKeeper()
    c_url = [(f'https://exp.cdn-hotels.com/hotels/1000000/10000/1200/1111' \
            f'/a9608a12333333e_d.jpg') for num in range(10)]
    c_url = [InputMediaPhoto(url) for url in c_url]
    photos = {222222: c_url}
    p_keeper.collected_photos.update(photos)
    c_form = {
        'params': 'lowest',
        'checkIn': '2022.10.10',
        'checkOut': '2022.10.15',
        'priceMin': '10',
        'priceMax': '11',
        'not_farther': '111',
        'not_closer': '11'
    }

    @pytest.mark.asyncio
    async def test_save_query(self):
        await UpdateDb(
            io_hotels=self.list_of_hotels,
            form=self.c_form,
            photos=self.p_keeper,
            user_id=self.user_id
        ).main()
        pass


