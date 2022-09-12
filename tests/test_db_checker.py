import pytest
from work_with_db.db_checker import DbChecker


class TestDbChecker:

    @pytest.mark.asyncio
    async def test_check_schema(self):
        path_to_db = '/Users/ilya/PycharmProjects/python_basic_diploma' \
                    '/work_with_db/test_db.sqlite3'
        await DbChecker(path_to_db).check_schema(path_to_db)

    @pytest.mark.asyncio
    async def test_check_db(self):
        db_name = 'travel_bot_db_test.sqlite3'
        path_to_db = f'/Users/ilya/PycharmProjects/python_basic_diploma' \
                     f'/database/{db_name}'
        await DbChecker(path_to_db).check_db()
