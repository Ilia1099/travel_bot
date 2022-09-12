from sqlalchemy.ext.asyncio import AsyncSession
from telebot.types import InputMediaPhoto
from sqlalchemy.exc import NoResultFound
from telebot.async_telebot import AsyncTeleBot
from bot_models import Base
from db_connector import DbSesManager
from logging_class import my_log
from work_with_db.pull_data import SelectsHotelsHistory
from telebot import formatting
from markups import FormTextResp


@my_log
class ShowQueryHistory:
    """Class for maintaining process of requesting data from data base and
    it's output"""
    def __init__(self, **kwargs):
        self._format = FormTextResp()
        self._form: dict = kwargs.get('form')
        self._bot: AsyncTeleBot = kwargs.get('bot')
        self._user_id: int = kwargs.get('user_id')
        self._Session = DbSesManager
        self._selects: SelectsHotelsHistory = SelectsHotelsHistory()
        self._delta: int = int(self._form.get('am_days', 0))
        self._photo: int = int(self._form.get('end_step', 0))

    async def operate(self):
        """
        Method which starts session to database and makes a cascade of
        selects, outputting data up on its retrieval
        """
        async with self._Session() as ses:
            async with ses.begin():
                try:
                    queries = await self._selects.select_query(
                        ses, self._user_id, self._delta)
                    for query in queries:
                        q_text = f'Query of {query.date_added.date()}'
                        await self._sender(self._format.header, q_text)
                        hotels = await self._selects.select_hotels(
                            ses, query.id)
                        for hotel in hotels:
                            text = formatting.format_text(
                                self._format.main_text(
                                    ['Hotel: ', hotel.name]),
                                self._format.main_text(
                                    ['URL: ', hotel.url])
                            )
                            if self._photo:
                                batch = await self._input_media_grouping(
                                    ses, hotel.name, text)
                                if len(batch) == 0:
                                    await self._bot.send_message(
                                        self._user_id, text,
                                        parse_mode='MarkdownV2')
                                else:
                                    await self._bot.send_media_group(
                                        self._user_id, media=batch
                                    )
                            await self._bot.send_message(
                                self._user_id, text=f'{"_"*len(q_text)}')
                except NoResultFound:
                    print('exception occurred')
                    await self._bot.send_message(
                        self._user_id, text='No data found')

    async def _input_media_grouping(self, ses: AsyncSession, hotel: Base,
                                    text):
        """
        Method which makes a select query after photos and transforms result
        into InputMediaPhoto object, returns it for following output,
        trimed to the length of photo limit
        """
        batch = await self._selects.select_photos(ses, hotel)
        batch = [InputMediaPhoto(q.photos_url, caption=text,
                                 parse_mode='MarkdownV2')
                 if i == 0 else InputMediaPhoto(q.photos_url)
                 for i, q in enumerate(batch.fetchall())]
        return batch[:self._photo]

    async def _sender(self, style, formated_text):
        """Method which outputs textual information"""
        await self._bot.send_message(
            self._user_id,
            formatting.format_text(style(formated_text)),
            parse_mode='MarkdownV2')
