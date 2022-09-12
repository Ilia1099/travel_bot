from datetime import timedelta
from sqlalchemy.exc import NoResultFound
from bot_models import Users, Queries, Hotels, HotelPhotos
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from datetime import datetime


def check_empty(func):
    """
    Decorator which takes query function, runs it, if result is empty,
    raises NoResultFound error, otherwise returns result in list
    """
    async def inner(*args, **kwargs):
        result = await func(*args, **kwargs)
        result = result.fetchall()
        print(result)
        if len(result) == 0:
            print('NoResultFound')
            raise NoResultFound
        return result
    return inner


class SelectsHotelsHistory:

    @check_empty
    async def select_hotels(self, ses: AsyncSession, q_id: int):
        stmt = await ses.execute(
            select(Queries.date_added, Hotels.name, Hotels.url).
            join(Queries.hotel).
            where(Queries.id == q_id))
        return stmt

    @classmethod
    async def select_photos(cls, ses: AsyncSession, hotel_name: str):
        stmt = await ses.execute(
            select(HotelPhotos.photos_url).
            where(HotelPhotos.hotel_name == hotel_name))
        return stmt

    @check_empty
    async def select_query(self, ses: AsyncSession, uid, delta: int = 0):
        stmt = await ses.execute(
            select(Queries.id, Queries.date_added).
            join(Users, Users.id == Queries.users_id).
            where(Queries.date_added >=
                  (datetime.today() - timedelta(days=delta + 1))).
            where((Queries.date_added <= (datetime.today()))).
            where(Users.user_id == uid).
            order_by(desc(Queries.date_added)))
        return stmt
