from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from db_connector import DbSesManager, MODELS
from bot_models import Users, Hotels, HotelPhotos, Queries, Base
from dataclasses_for_parsing import PhotoKeeper, FoundHotel
from datetime import datetime


Session = DbSesManager


class UpdateDb:
    """
    Class for maintaining entire process of writing collected information
    into database
    """
    def __init__(self, io_hotels, form, user_id, photos):
        self._Session = DbSesManager
        self._received_hotels: list[FoundHotel] = io_hotels
        self._form: dict = form
        self._user_id: int = user_id
        self._photos: PhotoKeeper = photos

    async def check_exists(self, key_id, current_model, parameter, ses) -> \
            Base:
        key_id: int | str
        current_model: Base
        parameter: Base
        ses: AsyncSession
        """
        Method which takes parameters and check whether current_model 
        record already exists or not
        """
        model = MODELS.get(current_model.__class__.__name__)
        try:
            query = await ses.execute(select(model).where(
                parameter == key_id))
            query = query.scalar_one()
            return query
        except NoResultFound:
            return current_model

    async def main(self) -> None:
        """
        Method which opens session and runs writing of data
        """
        async with self._Session() as ses:
            async with ses.begin():
                print('started db writing')
                await self.save_query(ses)

    async def save_query(self, session: AsyncSession) -> None:
        """
        Method which step by step check for existence each model,
        adds each model to session and commits them in the end
        """
        user = ModelPrep.prepare_user(self._user_id)
        user = await self.check_exists(
            self._user_id, user, Users.user_id, session)
        print('saved user')
        query = ModelPrep.prepare_query(self._form, user)
        print('saved query')
        hotels = await self.process_hotels(query, session)
        print('saved hotels')
        if self._photos.collected_photos:
            photos = await self.process_photos(hotels, session)
            session.add_all(photos)
        session.add_all(hotels)
        session.add_all([query, user])
        print('finished')

    async def process_hotels(self, query: Queries, session: AsyncSession) ->\
            list[Hotels]:
        """
        Method which iterates over collection of FoundHotel objects,
        creates a model for each and creates relationship with query
        """
        hotels = []
        for hotel in self._received_hotels:
            c_hotel = ModelPrep.prepare_hotel(hotel)
            c_hotel = await self.check_exists(
                c_hotel.name, c_hotel, Hotels.name, session)
            query.hotel.append(c_hotel)
            hotels.append(c_hotel)
        return hotels

    async def process_photos(self, hotels: list[Hotels],
                             session: AsyncSession):
        """
        Method which iterates over collection of collected photos ,
        creates a model for each and creates relationship with hotel
        """
        photos_models = []
        for hotel in hotels:
            urls = [u.media for u in self._photos.collected_photos.get(hotel.hotel_id)]
            # for url in self._photos.collected_photos.get(hotel.hotel_id):
            for url in set(urls):
                # url = str(url.media)
                c_url = ModelPrep.prepare_photo(hotel, url)
                photos_models.append(
                    await self.check_exists(
                        url, c_url, HotelPhotos.photos_url, session))
        return photos_models


class ModelPrep:
    """
    Class which contains methods for creating model objects
    """
    @classmethod
    def prepare_user(cls, user_id: int):
        c_user = Users(user_id=user_id)
        return c_user

    @classmethod
    def prepare_query(cls, query_form: dict, user: Base):
        c_query = Queries(
            user=user,
            date_added=datetime.now(),
            query_type=query_form.get('params'),
            date_in=query_form.get('checkIn'),
            date_out=query_form.get('checkOut'),
            price_low=query_form.get('priceMin'),
            price_high=query_form.get('priceMax'),
            distance_low=query_form.get('not_closer'),
            distance_high=query_form.get('not_farther'),
            city=query_form.get('query')
        )
        return c_query

    @classmethod
    def prepare_hotel(cls, hotel: FoundHotel):
        c_hotel = Hotels(
            name=hotel.name,
            address=hotel.address,
            hotel_id=hotel.id,
            url=hotel.hotel_url
        )
        return c_hotel

    @classmethod
    def prepare_photo(cls, c_hotel: Base, photo: str):
        c_photo = HotelPhotos(
            photos_url=photo,
            hotel_name=c_hotel.name,
            hotel=c_hotel
        )
        return c_photo
