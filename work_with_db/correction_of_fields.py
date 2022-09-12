import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, update, values
from bot_models import Users, Queries, Hotels, HotelPhotos
from telebot.types import InputMediaPhoto
from sqlalchemy.exc import NoResultFound
from telebot.async_telebot import AsyncTeleBot
from bot_models import Base
from db_connector import DbSesManager

"""
A set of functions to update Hotels.url field
"""

Session = DbSesManager


async def select_hotels(ses: AsyncSession):
    stmt = await ses.execute(
        select(Hotels.name, Hotels.hotel_id).
        where(Hotels.url == None))
    return stmt


async def upd_hotel(ses: AsyncSession, name, url):
    await ses.execute(update(Hotels).
                      where(Hotels.name == name).
                      values(url=url)
                      )


def gen_url(data: tuple):
    url = f'www.hotels.com/ho{data[1]}'
    return url


async def operate():
    async with Session() as ses:
        async with ses.begin():
            tasks = []
            res = await select_hotels(ses)
            res = ((r.name, r.hotel_id) for r in res)
            for tup in res:
                url = gen_url(tup)
                tasks.append(asyncio.create_task(upd_hotel(ses, tup[0], url)))
            res = await asyncio.gather(*tasks)

if __name__ == '__main__':
    asyncio.run(operate())
