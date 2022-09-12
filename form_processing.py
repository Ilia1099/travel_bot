from telebot.async_telebot import types, AsyncTeleBot
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from markups import Switcher, ComBtns
from typing import Optional
from form_parametres import CreateParams
import re
from logging_class import my_log


@my_log
class Tools:
    """Class to collect different support methods for working with form"""

    @staticmethod
    async def check_completion(*args, **kwargs):
        bot: AsyncTeleBot = kwargs.get('bot')
        mes: types.Message = kwargs.get('mes')
        if await bot.get_state(mes.from_user.id, mes.chat.id):
            await bot.delete_state(mes.from_user.id, mes.chat.id)

    @staticmethod
    async def begin(*args, **kwargs) -> None:
        bot: AsyncTeleBot = kwargs.get('bot')
        mes: types.Message = kwargs.get('mes')
        intro: str = kwargs.get('intro')
        init_state: str = kwargs.get('init_state')
        """Class method to initialize data collection
        :param bot: current bot instance
        :param mes: message object
        :param order_type: variant of ordering responses, corresponds to api
        requirements
        """
        await bot.set_state(
            mes.from_user.id, init_state, mes.chat.id
        )
        await bot.send_message(
            mes.from_user.id,
            text=intro, protect_content=True,
            reply_markup=kwargs.get('markup')
        )
        async with bot.retrieve_data(
                mes.from_user.id, mes.chat.id) as data:
            data["sortOrder"] = kwargs.get('order_type')
            data['params'] = mes.text[1:]

    @staticmethod
    def format_form(*args, **kwargs):
        """
        Method which converts some values to suit api requirements
        """
        form = kwargs.get('form')
        if form.get('get_photos') == 'Yes':
            form['get_photos'] = True
        else:
            form['get_photos'] = False
        return form

    @staticmethod
    async def prep_date_next_step(*args, **kwargs):
        """
        Supporting method for getting date range values; Saves received data to cash
        :return: tuple of data necessary for next step
        """
        from form_parametres import CreateParams
        bot = kwargs.get('bot')
        callback = kwargs.get('callback')
        result = kwargs.get('result')

        async with bot.retrieve_data(callback.from_user.id,
                                     callback.message.chat.id) as data:
            param = data.get('params')
            c_state = 'checkOut'
            if 'checkIn' not in data:
                c_state = 'checkIn'
            data[c_state] = result
            params = await CreateParams().get_params(param)
            params = params.get(c_state)
            text = params.get('text')
            next_step = params.get('next_step')
            markup = await Switcher().c_markup(params.get('markup'))
            await bot.set_state(callback.from_user.id, next_step,
                                callback.message.chat.id)
        return next_step, text, markup

    @staticmethod
    def str_to_date(*args, **kwargs):
        from dataclasses_for_requests import to_iso
        import datetime
        min_date = to_iso(kwargs.get('min_date'))
        min_date = datetime.datetime.strptime(min_date, '%Y-%m-%d') + \
                   datetime.timedelta(days=1)
        return min_date


@my_log
class Form:
    """Class to get form data"""
    def __init__(self, bot, mes):
        self._bot: AsyncTeleBot = bot
        self._mes: types.Message = mes

    async def operate(self) -> Optional:
        """Method which runs process of questioning"""
        print(self._mes.from_user.id,
                                           self._mes.chat.id)
        async with self._bot.retrieve_data(self._mes.from_user.id,
                                           self._mes.chat.id) as data:
            param = data.get('params')
        c_state = await self._bot.get_state(self._mes.from_user.id,
                                            self._mes.chat.id)
        params = await CreateParams().get_params(param)
        params = params.get(c_state)
        text = params.get('text')
        next_step = params.get('next_step')
        validation = params.get('validation_mask')
        not_valid = params.get('not_valid')

        if c_state == 'end_step':
            markup = ComBtns().c_markup()
            async with self._bot.retrieve_data(
                    self._mes.from_user.id, self._mes.chat.id) as data:
                await self._bot.send_message(
                    self._mes.from_user.id,
                    text='request created',
                    protect_content=True,
                    reply_markup=await markup)
                return data
        elif c_state in ['pageSize']:
            calendar, step = DetailedTelegramCalendar().build()
            await self._bot.send_message(
                self._mes.chat.id, f"Select {LSTEP[step]}",
                reply_markup=calendar)
            await self._bot.set_state(
                self._mes.from_user.id, next_step, self._mes.chat.id)
        else:
            if re.match(validation, self._mes.text):
                await self._get_data(text, next_step, params)
            else:
                await self._bot.send_message(
                    self._mes.from_user.id, text=not_valid,
                    protect_content=True)

    async def _get_data(self, step_mes: str, next_state, params: dict) -> None:
        """
        Method which saves states to make sure that next step will be
        exactly as expected
        :param step_mes: Response message for next step
        :param next_state: Next_state == next data to be received
        """
        markup = Switcher().c_markup(params.get('markup'))
        await self._bot.set_state(self._mes.from_user.id, next_state,
                                  self._mes.chat.id)
        await self._bot.send_message(
            self._mes.from_user.id, protect_content=True,
            text=step_mes,  reply_markup=await markup)

