EasyTravel Bot

The EasyTravel Bot is a bot that allows you to search for hotels in a city of your choice by calling an external API (RapidAPI). It uses several libraries, including pyTelegramBotAPI, asyncio, aiohttp, sqlalchemy, and alembic, to make the bot functional and efficient. The bot uses SQLite3 as its database and StatePickleStorage for cache memory.
Supports versions of Python 3.10 and above

Main Libraries

* pyTelegramBotAPI: a library for implementing the bot using long pooling method and working with the Telegram API
* asyncio: a library for implementing asynchronous functionality
* aiohttp: a library for forming requests to an external resource with 
  asynchronous functionality
* sqlalchemy: a library for working with databases, using an asynchronous 
  approach and an ORM-style database structure
* alembic: a library-addition to sqlalchemy, used for implementing migrations
* a third-party library, python-telegram-bot-calendar, is used to obtain 
  hotel visit dates. The full list of libraries is available in the requirements.txt file.

Implementation Details

When adding new models for the database, it is necessary to add their names to the REGISTERED_MODELS_FOR_BOT list in the bot_models.py module to ensure correct database checking when the bot starts.

The bot starts by checking for the presence and correctness of the database schema, using the DbChecker class in the db_checker.py module.

Usage Instruction

The bot can be launched through the main.py file. Before launching the bot, dependencies such as bot API keys and external resources must be written in the .env file. The python-decouple library is used to work with environment variables.

The contents of the .env file include:
* bot_token = ''
declared in the main.py module
* hotels_api_token = ''
declared in the requester.py module

When the /start command is pressed in the Telegram client, a welcome message is sent, and a keyboard with available commands appears. The available commands are:

/start: basic command, launches a dialog with the bot
/help: outputs a list of available commands and their brief description
/lowest_price: launches a dialog for collecting data required for obtaining hotels at the lowest price
/highest_price: launches a dialog for collecting data required for obtaining hotels at the highest price
/history: launches a dialog for collecting parameters for displaying request history
/best_deal: launches a dialog for collecting data required for obtaining hotels in a selected price range and a distance from the center
/back: interrupts any command and returns to the command selection menu
Sending a message outside of parameter collection, which is not recognized as a command, will result in sending an "echo" message. Regular expressions are used when collecting request parameters, even at a basic level.

