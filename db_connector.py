from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from bot_models import Users, Hotels, HotelPhotos, Queries, Base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine
from sqlalchemy import event
from logging_class import my_log

MODELS = {
    'Users': Users,
    'Hotels': Hotels,
    'HotelPhotos': HotelPhotos,
    'Queries': Queries
}


@my_log
class DbSesManager:
    """
    Context manager which initializes connection to database
    """
    async def __aenter__(self):
        """
        function _enable_pk_sqlite is required for enabling foreign keys in
        sqlite, according to documentation
        :return:  instance of session class
        """
        @event.listens_for(Engine, 'connect')
        def _enable_pk_sqlite(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

        from pathlib import Path
        path_to_db = Path(
            'database/travel_bot_db.sqlite3').absolute().resolve()
        self._engine = create_async_engine(
            f"sqlite+aiosqlite:///{path_to_db}",
            echo=True,
            future=True
        )
        self._session = sessionmaker(
            self._engine, expire_on_commit=False, class_=AsyncSession)
        return self._session()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self._session = None
