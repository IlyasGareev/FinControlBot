import os
from aiogram import Bot, Dispatcher
from dotenv import find_dotenv, load_dotenv

# Токен бота
load_dotenv(find_dotenv())

# Создание бота
bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher()







