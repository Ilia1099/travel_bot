import asyncio
from telebot.async_telebot import types, AsyncTeleBot
from markups import Switcher, ComBtns
from typing import Optional
from form_parametres import CreateParams
from requester import AioRequester, ReqParams
import process_hotels
import re


class Tools:
    """Class to collect different support methods for working with form"""
    @classmethod
    async def check_completion(cls, bot: AsyncTeleBot, mes: types.Message):
        if await bot.get_state(mes.from_user.id, mes.chat.id):
            await bot.delete_state(mes.from_user.id, mes.chat.id)


class Form:
    """Class to get form data"""
    def __init__(self, bot, mes):
        self._bot: AsyncTeleBot = bot
        self._mes: types.Message = mes

    async def operate(self) -> Optional:
        """Method which runs process of questioning"""
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

        if c_state == 'get_photos':
            markup = ComBtns().c_markup()
            async with self._bot.retrieve_data(self._mes.from_user.id,
                                               self._mes.chat.id) as data:
                self._format_form(data)
                await self._bot.send_message(self._mes.from_user.id,
                                             text='request created',
                                             reply_markup=await markup)
                await process_hotels.Processor(
                    form=data, ses_context=AioRequester, bot=self._bot,
                    req_params=ReqParams, mes_id=self._mes.from_user.id,
                    semaphore=asyncio.BoundedSemaphore).operate()
                await self._bot.delete_state(self._mes.from_user.id,
                                             self._mes.chat.id)
        else:
            if re.match(validation, self._mes.text):
                await self._get_data(text, next_step)
            else:
                await self._bot.send_message(self._mes.from_user.id,
                                             text=not_valid)

    async def _get_data(self, step_mes: str, next_state: str) -> None:
        """
        Method which saves states to make sure that next step will be
        exactly as expected
        :param step_mes: Response message for next step
        :param next_state: Next_state == next data to be received
        :return:
        """
        markup = Switcher().c_markup(next_state)
        await self._bot.set_state(self._mes.from_user.id, next_state,
                                  self._mes.chat.id)
        await self._bot.send_message(
            self._mes.from_user.id, text=step_mes,  reply_markup=await markup)

    @classmethod
    async def begin(cls, bot: AsyncTeleBot, mes: types.Message,
                    order_type: str) -> None:
        """Class method to initialize data collection
        :param bot: current bot instance
        :param mes: message object
        :param order_type: variant of ordering responses, corresponds to api
        requirements
        """
        await bot.set_state(mes.from_user.id, 'query', mes.chat.id)
        await bot.send_message(mes.from_user.id,
                               text='First, enter country and required city',
                               reply_markup=types.ReplyKeyboardRemove())
        async with bot.retrieve_data(mes.from_user.id, mes.chat.id) as data:
            data["sortOrder"] = order_type
            data['params'] = mes.text

    @classmethod
    def _format_form(cls, form: dict):
        if form.get('get_photos') == 'Yes':
            form['get_photos'] = True
        else:
            form['get_photos'] = False
