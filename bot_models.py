from sqlalchemy import Column, String, VARCHAR, Integer, \
    DateTime, ForeignKey, Table
from sqlalchemy.orm import declarative_base, relationship

REGISTERED_MODELS_FOR_BOT = [
    'Users', 'association_hotels', 'Queries', 'Hotels', 'Hotelphotos'
]

Base = declarative_base()


class Users(Base):
    __tablename__ = 'Users'
    id = Column(Integer, primary_key=True, autoincrement='auto')
    user_id = Column(Integer, unique=True, index=True)

    def __repr__(self):
        return f"User_id: {self.user_id}"


associate_hotel_query = Table(
    "association_hotels",
    Base.metadata,
    Column("Hotel_id", ForeignKey("Hotels.id"), primary_key=True),
    Column("Query_id", ForeignKey("Queries.id"), primary_key=True)
)


class Queries(Base):
    __tablename__ = 'Queries'
    id = Column(Integer, primary_key=True, autoincrement='auto')
    users_id = Column(Integer, ForeignKey('Users.id', ondelete='CASCADE'))
    date_added = Column(DateTime)
    query_type = Column(String(20))
    city = Column(String(25))
    date_in = Column(String(20))
    date_out = Column(String(20))
    price_low = Column(String(20))
    price_high = Column(String(20))
    distance_low = Column(String, default=None)
    distance_high = Column(String, default=None)

    user = relationship('Users', innerjoin=True, backref='Queries')
    hotel = relationship(
        'Hotels', innerjoin=True, secondary=associate_hotel_query,
        back_populates='query'
    )

    __mapper_args__ = {"eager_defaults": True}

    def __repr__(self):
        return f"id: {self.id}, query_type: {self.query_type}, query_date: " \
               f"{self.date_added}, user_id: {self.users_id}"


class Hotels(Base):
    __tablename__ = 'Hotels'
    id = Column(Integer, primary_key=True, autoincrement='auto')
    name = Column(String, unique=True, index=True)
    address = Column(String(150))
    hotel_id = Column(Integer, unique=True)
    url = Column(String(150), default=None)
    query = relationship(
        'Queries', innerjoin=True,
        secondary=associate_hotel_query, back_populates='hotel'
    )

    __mapper_args__ = {"eager_defaults": True}

    def __repr__(self):
        return f"Hotel: {self.name}"


class HotelPhotos(Base):
    __tablename__ = 'Hotelphotos'
    id = Column(Integer, primary_key=True, autoincrement='auto')
    hotel_name = Column(String, ForeignKey('Hotels.name', ondelete='CASCADE'))
    photos_url = Column(VARCHAR, unique=True)

    hotel = relationship('Hotels', innerjoin=True, backref='Hotelphotos')

    def __repr__(self):
        return f"{self.photos_url}"
