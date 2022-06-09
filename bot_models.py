import sqlalchemy
from sqlalchemy import Column, String, VARCHAR, BOOLEAN, Integer, \
    create_engine, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, \
    sessionmaker, selectinload, Session
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
import asyncio
import aiosqlite
#
# engine = create_engine('sqlite+aiosqlite:////Users/ilya/PycharmProjects'
#                        '/python_basic_diploma/database/easy_bot_db.sqlite3',
#                        echo=True, future=True)

Base = declarative_base()


class Users(Base):
    __tablename__ = 'Users'
    id = Column(Integer, primary_key=True, autoincrement='auto')
    user_id = Column(Integer, unique=True, index=True)
    query = relationship('Queries', innerjoin=True)

    def __repr__(self):
        return f"User_id: {self.user_id}"


class Queries(Base):
    __tablename__ = 'Queries'
    id = Column(Integer, primary_key=True, autoincrement='auto')
    users_id = Column(Integer, ForeignKey('Users.id', ondelete='CASCADE'))
    date_added = Column(DateTime)
    query_name = Column(String(20))
    hotel_name = Column(String, ForeignKey('Hotels.name'))
    date_in = Column(DateTime)
    date_out = Column(DateTime)
    low_price = Column(String, nullable=True)
    hi_price = Column(String, nullable=True)
    centre_cl = Column(String, nullable=True)
    centre_fr = Column(String, nullable=True)
    hotel = relationship('Hotels', innerjoin=True)

    def __repr__(self):
        return f"Date_added: {self.date_added}; query_name: {self.query_name}"


class Hotels(Base):
    __tablename__ = 'Hotels'
    id = Column(Integer, primary_key=True, autoincrement='auto')
    name = Column(String, unique=True, index=True)
    e_mail = Column(String)
    city = Column(String)

    def __repr__(self):
        return f"Name of the hotel: {self.name}; city: {self.city}, email: " \
               f"{self.name}"
