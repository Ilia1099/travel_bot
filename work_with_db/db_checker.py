from pathlib import Path
from logging_class import my_log, log
from sqlalchemy import event, inspect, create_engine
from sqlalchemy.engine import Engine
from bot_models import Base, REGISTERED_MODELS_FOR_BOT


@my_log
class DbChecker:
    """Class which contains methods for checking database existence
    and it's schema"""
    def __init__(self, path: Path, name: str):
        self._path = path.joinpath(name).resolve()
        self._folder = path
        self._db_name = name

    def check_db(self) -> None:
        """
        Methods which checks existence of db file at specified path if
        exists, runs method to check it's schema, else runs method to create it
        """
        if self._path.is_file():
            log.debug('Database exists')
            return self.check_schema(str(self._path))
        log.debug('Database does not exist')
        self.create_db(str(self._path))

    def check_schema(self, path) -> None:
        """
        Method which checks schema of the db by calling inspect function
        from sqlalchemy. For checking REGISTERED_MODELS_FOR_BOT list was
        created, if difference of sets between inspect results and this list
        != 0, then db schema is updated
        :param path: absolute path to database file
        """
        engine = create_engine(
            f"sqlite:///{path}", echo=True
        )
        with engine.begin() as conn:
            tables = inspect(conn).get_table_names()
        if len(set(REGISTERED_MODELS_FOR_BOT).difference(set(tables))) != 0:
            self.create_db(path, drop_tables=False)
            log.debug('Database updated')

    def create_db(self, path, drop_tables=True) -> None:
        """
        Method which creates database file, by default if called drops all
        tables as precaution, but flag could be set to False, in case of
        just updating schema.
        :param path: absolute path to database file
        :param drop_tables: Bool flag to drop tables or not
        """
        @event.listens_for(Engine, 'connect')
        def _enable_pk_sqlite(dbapi_connection, connection_record):
            """
            It's told in official documentation to add this code as sqlite3
            has some issues with enabling foreign keys by sqlalchemy
            """
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

        if not self._folder.exists():
            self._folder.mkdir()
        engine = create_engine(
            f"sqlite:///{path}", echo=True, future=True
        )
        if drop_tables:
            with engine.begin() as conn:
                Base.metadata.drop_all(conn)
        with engine.begin() as conn:
            Base.metadata.create_all(conn)
