from telebot.async_telebot import types, AsyncTeleBot
from os import linesep
from abc import ABC, abstractmethod
from typing import List
import asyncio

COMMANDS_REF = {
    '/start': 'start command',
    '/help': 'shows commands description',
    '/lowest_price': 'command for making query of lowest cost hotels',
    '/highest_price': 'command for making query of highest cost hotels',
    '/history': 'shows history of users requests',
    '/best_deal': 'shows best hotel for given parameters'

}


class MyButtons(ABC):
    """Class for containing all custom button objects"""
    _help_b = types.KeyboardButton('/help')
    _best_deal = types.KeyboardButton('/best_deal')
    _lowest_price = types.KeyboardButton('/lowest_price')
    _highest_price = types.KeyboardButton('/highest_price')
    _back = types.KeyboardButton('/back')
    _stop_chat = types.KeyboardButton('/stop_chat')
    _history = types.KeyboardButton('/history')
    _yes = types.KeyboardButton('Yes')
    _no = types.KeyboardButton('No')

    @abstractmethod
    async def _btns(self):
        pass

    @abstractmethod
    async def c_markup(self, state=None):
        pass


class ComBtns(MyButtons):
    """Class which contains buttons available for all users"""
    help_b = MyButtons._help_b
    best_deal = MyButtons._best_deal
    lowest_price = MyButtons._lowest_price
    highest_price = MyButtons._highest_price
    back = MyButtons._back
    stop_chat = MyButtons._stop_chat
    history = MyButtons._history

    async def _btns(self):
        base_markup = types.ReplyKeyboardMarkup(row_width=3,
                                                resize_keyboard=True)
        return base_markup.add(*[getattr(ComBtns, btn) for btn in dir(ComBtns)
                                 if not btn.startswith('_')
                                 and not callable(getattr(ComBtns, btn))])

    async def c_markup(self, state=None):
        return await self._btns()


class Switcher(MyButtons):
    yes = MyButtons._yes
    no = MyButtons._no

    async def _btns(self):
        base_markup = types.ReplyKeyboardMarkup(row_width=3,
                                                resize_keyboard=True)
        return base_markup.add(*[self.yes, self.no])

    async def c_markup(self, state=None):
        if state == 'get_photos':
            return await self._btns()
        else:
            return types.ReplyKeyboardRemove()


class MyCommands:
    """Class for containing custom command objects"""
    _com_help = types.BotCommand('/help', 'shows reference')
    _com_bdeal = types.BotCommand('/best_deal', 'create request which returns'
                                               'shows best deal')
    _com_lprice = types.BotCommand('/lowest_price',
                                  'create request which returns '
                                  'list of cheapest hotels')
    _com_hprice = types.BotCommand('/highest_price',
                                  'create request which returns'
                                  'list of cheapest hotels')
    _com_hist = types.BotCommand('/history', 'shows history of your requests')
    _com_back = types.BotCommand('/back', 'returns to previous command')
    _com_stop_chat = types.BotCommand('/stop_chat', 'stops certain chat')


class MyCommSet(types.BotCommandScopeDefault):
    """
    Class container for common custom functions
    """
    def __init__(self):
        super().__init__()

    @classmethod
    def show_coms(cls) -> List[types.BotCommand]:
        """
        Method which returns a list of commands
        """
        return [getattr(MyCommands, com) for com in dir(MyCommands) if
                com.startswith('_com')]


async def show_commands(message: types.Message, bot: AsyncTeleBot) -> None:
    """
    Function which applies send_message method to a given AsyncTeleBot
    object in a certain chat, sends to user a pairs of custom command name and
    it's reference
    """
    for key in COMMANDS_REF:
        await bot.send_message(message.from_user.id,
                               f'{key}: {COMMANDS_REF[key]}{linesep}')
