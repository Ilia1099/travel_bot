from sqlalchemy.exc import NoResultFound
from db_connector import DbSesManager
from work_with_db.pull_data import SelectsHotelsHistory
import pytest


class TestPullData:
    session = DbSesManager
    selects = SelectsHotelsHistory()
    user_id = 266918760

    @pytest.mark.asyncio
    async def test_prepare_result_query(self):
        async with self.session() as ses:
            async with ses.begin():
                test_q = await self.selects.select_query(ses, '332348446')
                for _ in test_q:
                    print(type(_.id))
                assert len(test_q) > 0

    @pytest.mark.asyncio
    async def test_prepare_result(self):
        async with self.session() as ses:
            async with ses.begin():
                test_q = await self.selects.select_query(ses, '332348446')
                for q in test_q:
                    test_h = await self.selects.select_hotels(ses, q.id)
                    assert len(test_h) > 0

                    for h in test_h:
                        print(h.name)
                        photos = await self.selects.select_photos(ses, h.name)

                        for p in photos:
                            print(p)

    @pytest.mark.asyncio
    async def test_prepare_result_fail(self):
        with pytest.raises(NoResultFound):
            async with self.session() as ses:
                async with ses.begin():
                    test_q = await self.selects.select_query(ses, '266918760')

    @pytest.mark.asyncio
    async def test_load_hotels(self):
        async with self.session() as ses:
            async with ses.begin():
                test_q = await self.selects.select_query(ses, '266918760')
                for q in test_q:
                    test_h = await self.selects.select_hotels(ses, q.id)
                    for h in test_h:
                        print(h)
                    assert len(test_h) > 0

    @pytest.mark.asyncio
    async def test_load_hotels_fail(self):
        with pytest.raises(NoResultFound):
            async with self.session() as ses:
                async with ses.begin():
                    test_q = await self.selects.select_query(ses,
                                                             '266918760', 0)
                    for q in test_q:
                        test_h = await self.selects.select_hotels(
                            ses, q.date_added)

    @pytest.mark.asyncio
    async def test_load_photos_fail(self):
        async with self.session() as ses:
            async with ses.begin():
                test_p = await self.selects.select_photos(ses, 'Bposhtels Hollywood Florida')
                for p in test_p:
                    print(p)
                print(f'query: {test_p.fetchall()}')