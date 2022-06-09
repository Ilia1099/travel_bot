# from abc import ABC, abstractmethod
# from sqlalchemy.orm import sessionmaker
# from bot_models import Users, Queries, Hotels
# from typing import Any
# from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
# from sqlalchemy.future import select
# import asyncio
# import aiosqlite
#
# engine = create_async_engine('sqlite+aiosqlite:////Users/ilya/PycharmProjects/'
#                              'python_basic_diploma/database/easyBot.sqlite3')
#
# Session = sessionmaker(bind=engine, expire_on_commit=False,
#                        class_=AsyncSession, future=True)
# session = Session()
# # async with session as ses:
# #     async with ses.begin():
# #         ses.add_all()
# #         await ses.commit()
# user_id = 332323
# res = select(Users)
#
#
# class PushData(ABC):
#     @classmethod
#     async def get_or_create(cls, c_session: Session,
#                             model: Any[Users | Queries | Hotels], **kwargs):
#         async with c_session as ses:
#             async with ses.begin():
#                 instance = await ses.execute(res)
#                 if instance:
#                     return await instance
#                 else:
#                     instance = await ses.add(model)
#                     await ses.commit()
#                     return await instance
#
#     @abstractmethod
#     async def push(self):
#         pass
#
#
# class InstanceCreator(ABC):
#     @abstractmethod
#     async def parse_data(self):
#         pass
