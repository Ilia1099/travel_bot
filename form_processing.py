from telebot.async_telebot import types, AsyncTeleBot
from markups import Switcher, ComBtns
from typing import Optional
from form_parametres import CreateParams
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
        self.__bot: AsyncTeleBot = bot
        self.__mes: types.Message = mes
        self.__temp_storage = {}

    async def operate(self) -> Optional:
        """
        Method which runs process of questioning
        :return:
        """
        async with self.__bot.retrieve_data(self.__mes.from_user.id,
                                            self.__mes.chat.id) as data:
            param = data.get('params')
        c_state = await self.__bot.get_state(self.__mes.from_user.id,
                                             self.__mes.chat.id)
        params = await CreateParams().get_params(param)
        params = params.get(c_state)
        text = params.get('text')
        next_step = params.get('next_step')
        validation = params.get('validation_mask')
        not_valid = params.get('not_valid')

        if c_state == 'get_photos':
            markup = ComBtns().c_markup()
            async with self.__bot.retrieve_data(self.__mes.from_user.id,
                                                self.__mes.chat.id) as data:
                self.__temp_storage.update(data)
            await self.__bot.delete_state(self.__mes.from_user.id,
                                          self.__mes.chat.id)
            await self.__bot.send_message(self.__mes.from_user.id,
                                          text='request created',
                                          reply_markup=await markup)
            await process_hotels.Processor(self.__temp_storage, self.__bot,
                                           self.__mes.from_user.id).operate()
        else:
            if re.match(validation, self.__mes.text):
                await self._get_data(text, next_step)
            else:
                await self.__bot.send_message(self.__mes.from_user.id,
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
        await self.__bot.set_state(self.__mes.from_user.id, next_state,
                                   self.__mes.chat.id)
        await self.__bot.send_message(self.__mes.from_user.id,
                                      text=step_mes,
                                      reply_markup=await markup)

    @classmethod
    async def begin(cls, bot: AsyncTeleBot, mes: types.Message,
                    flag: str | bool):
        """Class method to initialize data collection"""
        await bot.set_state(mes.from_user.id, 'query', mes.chat.id)
        await bot.send_message(mes.from_user.id,
                               text='First, enter country and required city',
                               reply_markup=types.ReplyKeyboardRemove())
        async with bot.retrieve_data(mes.from_user.id, mes.chat.id) as data:
            data["sortOrder"] = flag
            data['params'] = mes.text
