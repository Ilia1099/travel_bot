import re
from telebot.async_telebot import AsyncTeleBot, types, StatePickleStorage
from decouple import config
from markups import ComBtns, show_commands
from form_processing import Form, Tools
from middleware import FormMiddleware, AntiFloodMiddleware
from work_with_db.db_checker import DbChecker
from command_operating import CommandManager
from pathlib import Path
from os import linesep
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
import asyncio

state_storage = StatePickleStorage()
bot = AsyncTeleBot(token=config('bot_token'), state_storage=state_storage)
bot.setup_middleware(FormMiddleware(bot))
bot.setup_middleware(AntiFloodMiddleware(bot))

CHATS = {}


@bot.message_handler(
    func=lambda message: not re.match(r'/st[ao]+|/hi+|/he+|/be+|/lo+|/bac+',
                                      message.text))
async def echo(message: types.Message):
    reply = f'Hi, {message.from_user.username}, i am travelbot{linesep}' \
            f'I can only perform commands below{linesep}' \
            f'Please, select one'
    await bot.send_message(
        message.from_user.id, text=reply,
        reply_markup=await ComBtns().c_markup())


@bot.message_handler(commands=['start', 'back'])
async def greeter(message: types.Message) -> None:
    """
    Message handler which awaits 'start' or 'back' command. Checks if user is
    new or not. If 'start' initializes custom set of commands, sends keyboard
    with commands. If 'back' resends initial keyboard markup no matter from
    where
    :param message: types.Message object
    """
    reply = ''
    if message.chat.id not in CHATS:
        CHATS[message.chat.id] = message.chat.id
        reply = 'Hi, here are available commands'
    else:
        reply = 'Select a command: '
    await bot.send_message(
        message.from_user.id, text=reply, protect_content=True,
        reply_markup=await ComBtns().c_markup())


@bot.message_handler(commands=['help'])
async def helper(message: types.Message) -> None:
    """
    Message handler which awaits 'help' command. Up on match calls
    show_commands() function
    :param message: types.Message
    """
    markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    markup.add(ComBtns.back)
    await bot.send_message(
        message.from_user.id, text='Here is description of each command',
        reply_markup=markup)
    await show_commands(message, bot)


@bot.message_handler(commands=['best_deal'])
async def best_deal(message: types.Message):
    """
    Message handler which launches questioning to make a corresponding request
    """
    intro = 'First, enter country and required city'
    await Tools().begin(
        bot=bot, mes=message, intro=intro, init_state='query',
        order_type='PRICE')


@bot.message_handler(commands=['highest_price'])
async def highest_price(message: types.Message):
    """
    Message handler which launches questioning to make a corresponding request
    """
    intro = 'First, enter country and required city'
    await Tools().begin(
        bot=bot, mes=message, intro=intro, init_state='query',
        order_type='PRICE_HIGHEST_FIRST')


@bot.message_handler(commands=['history'])
async def history(message: types.Message):
    """
    Message handler which returns results of previous search query
    """
    intro = 'How many days do you want to check?'
    await Tools().begin(
        bot=bot, mes=message, intro=intro, init_state='am_days')


@bot.message_handler(commands='lowest_price')
async def lowest_price(message):
    """
    Message handler which launches questioning to make a corresponding request
    """
    intro = 'First, enter country and required city'
    await Tools().begin(
        bot=bot, mes=message, intro=intro, init_state='query',
        order_type='PRICE')


@bot.message_handler(content_types=['form_text'])
async def form_processing(message):
    """
    Method which responsible for following  questioning
    """
    form = await Form(bot, message).operate()
    if form:
        form = Tools().format_form(form=form)
        manager = CommandManager(form.get('params'))
        await manager.resp_to_user(
            bot=bot, user_id=message.from_user.id, form=form)
        await bot.delete_state(message.from_user.id, message.chat.id)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func())
async def cal(callback):
    from dataclasses_for_requests import to_iso

    result, key, step = DetailedTelegramCalendar().process(callback.data)
    if not result and key:
        await bot.edit_message_text(
            f"Select {LSTEP[step]}", callback.message.chat.id,
            callback.message.message_id, reply_markup=key)
    elif result:
        result = to_iso(str(result))
        next_step = await Tools.prep_date_next_step(
            bot=bot, callback=callback, result=result)
        calendar, step = DetailedTelegramCalendar().build()
        text = f"Select {LSTEP[step]}"
        if next_step[0] != 'checkOut':
            text = next_step[1]
            calendar = next_step[2]
        await bot.send_message(
            callback.message.chat.id, text, reply_markup=calendar)


if __name__ == '__main__':
    db_name = 'travel_bot_db.sqlite3'
    path_to_db = Path('database').absolute().resolve()
    DbChecker(path_to_db, db_name).check_db()
    asyncio.run(bot.infinity_polling(timeout=300, request_timeout=300))
