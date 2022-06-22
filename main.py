from telebot.async_telebot import AsyncTeleBot, types, StatePickleStorage
from decouple import config
from markups import ComBtns, MyCommSet, show_commands
from form_processing import Form
from middleware import FormMiddleware
import asyncio

state_storage = StatePickleStorage()
bot = AsyncTeleBot(token=config('bot_token'), state_storage=state_storage)
bot.setup_middleware(FormMiddleware(bot))

CHATS = {}


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
    await bot.set_my_commands(commands=MyCommSet.show_coms())
    await bot.send_message(message.from_user.id, text=reply,
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
    await bot.send_message(message.from_user.id,
                           text='Here is description of each command',
                           reply_markup=markup)
    await show_commands(message, bot)


@bot.message_handler(commands=['best_deal'])
async def best_deal(message: types.Message):
    """
    Message handler which launches questioning to make a corresponding request
    """
    await Form.begin(bot, message, 'PRICE')


@bot.message_handler(commands=['highest_price'])
async def highest_price(message: types.Message):
    """
    Message handler which launches questioning to make a corresponding request
    """
    await Form.begin(bot, message, 'PRICE_HIGHEST_FIRST')


@bot.message_handler(commands=['history'])
async def history(message: types.Message):
    """
    Message handler which returns results of previous search query
    """
    await bot.send_message(message.from_user.id, text='History command here')


@bot.message_handler(commands='lowest_price')
async def lowest_price(message):
    """
    Message handler which launches questioning to make a corresponding request
    """
    await Form(bot, message).begin(bot, message, 'PRICE')


@bot.message_handler(content_types=['form_text'])
async def form_processing(message):
    """
    Method which responsible for following  questioning
    """
    await Form(bot, message).operate()


@bot.message_handler(commands=['stop_chat'])
async def stop_chat(message):
    """
    Method which stops questioning by clearing state
    :param message:
    :return:
    """
    await bot.delete_state(message.from_user.id, message.chat.id)
    print('stopped')

if __name__ == '__main__':
    asyncio.run(bot.infinity_polling())
