import time
from telebot.asyncio_handler_backends import BaseMiddleware\
    , CancelUpdate
from telebot.async_telebot import types
from telebot.async_telebot import AsyncTeleBot
import re
from typing import Dict
from form_processing import Tools


class FormMiddleware(BaseMiddleware):
    """Class for controlling form"""
    def __init__(self, bot: AsyncTeleBot):
        print('start middleware')
        self._bot = bot
        self.update_types = ['message']
        super().__init__()

    async def pre_process(self, message: types.Message, data) -> None:
        """Method which checks for existence of state
        If exists changes content type to make sure that message will be
        processed by specified handler and saves response of the current state
        """
        state = await self._bot.get_state(message.from_user.id, message.chat.id)
        if state:
            if not re.match(r'/st[ao]+|/hi+|/he+|/be+|/lo+|/bac+',
                            message.text):
                async with self._bot.retrieve_data(message.from_user.id,
                                                   message.chat.id) as data:
                    print(data)
                    data[state] = message.text
                message.content_type = 'form_text'
            else:
                reply = f'Form cleared, new command: {message.text}'
                await Tools.check_completion(bot=self._bot, mes=message)
                await self._bot.send_message(
                    message.from_user.id, text=reply, protect_content=True)

    async def post_process(self, message, data, exception):
        pass


class AntiFloodMiddleware(BaseMiddleware):
    """
    Moddleware for limiting max amount of messages from user per minute (
    telegram standard is 20 messages per  min, according to docs)
    Thus default time delta between messages is 3 seconds
    This is the first implementation of such mechanism will be refactored
    in future
    """
    def __init__(self, bot: AsyncTeleBot, limit: int = 3):
        self._bot = bot
        self.update_types = ['message', 'commands']
        self._limit = limit
        self._register: Dict[int: list] = {}
        super().__init__()

    async def pre_process(self, message: types.Message, data):
        """
        Method which checks if user is new or not;
        If not checks time delta between current and previous message
        If time delta is less than limit, returns CancelUpdate object and
        sends warning, otherwise passes execution further and updates time
        value in register
        """
        rpm = self._register.get(message.from_user.id)
        if not rpm:
            self._register[message.from_user.id] = [time.time()]
            return
        else:
            c_time = time.time()
            rpm.append(c_time)
            await self.check_time(message, rpm, c_time)
            if len(rpm) > 20:
                await self._bot.send_message(
                    message.from_user.id, protect_content=True,
                    text='Flood detected, wait a while!')
                return CancelUpdate()

    async def post_process(self, message, data, exception):
        pass

    async def check_time(self, message, rpm: list, c_time):
        """
        Method which checks difference between each time stamp and the
        latest, if difference is more than 60 time stamp is filtered out,
        thus lowering flooding threshold
        :param message: types.Message
        :param rpm: list of time stamps
        :param c_time: time of the latest operation
        """
        self._register[message.from_user.id] = \
            [tm for tm in rpm if c_time - tm < 60]

