from telebot.asyncio_handler_backends import BaseMiddleware
from telebot.async_telebot import types
from telebot.async_telebot import AsyncTeleBot
import re
from form_processing import Tools


class FormMiddleware(BaseMiddleware):
    """Class for controlling form"""
    def __init__(self, bot: AsyncTeleBot):
        print('start middleware')
        self.__bot = bot
        self.update_types = ['message']
        super().__init__()

    async def pre_process(self, message: types.Message, data) -> None:
        """
        Method which checks for existence of state if exists changes content
        type to make sure that message will be processed by specified
        handler and saves response of the current state
        """
        state = await self.__bot.get_state(message.from_user.id, message.chat.id)
        if state:
            if not re.match(r'/st[ao]+|/hi+|/he+|/be+|/lo+|/bac+',
                            message.text):
                async with self.__bot.retrieve_data(message.from_user.id,
                                                    message.chat.id) as data:
                    data[state] = message.text
                message.content_type = 'form_text'
            else:
                reply = f'Form cleared, new command: {message.text}'
                await Tools.check_completion(self.__bot, message)
                await self.__bot.send_message(message.from_user.id,
                                              text=reply)

    async def post_process(self, message, data, exception):
        pass
