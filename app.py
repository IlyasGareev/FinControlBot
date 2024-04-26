import asyncio
from aiogram import types
from create_bot import bot, dp
from db import sqlite_db  # Подключаем модуль для работы с базой данных SQLite
from utils.notifications import scheduled  # Импортируем функцию для планирования уведомлений
from handlers.client import client_router
from handlers.other import other_router
from common.bot_cmds_list import private

# Список обрабатываемых событий
ALLOWED_UPDATES = ['message', 'callback_query']

# Регистрируем роутеры
dp.include_router(client_router)
dp.include_router(other_router)


async def main():
    # Планирование уведомлений
    loop = asyncio.get_event_loop()  # Получаем цикл событий
    loop.create_task(scheduled(bot))  # Запускаем задачу для планирования уведомлений
    await bot.delete_webhook(drop_pending_updates=True)
    # await bot.delete_my_commands(scope=types.BotCommandScopeAllPrivateChats())
    await bot.set_my_commands(commands=private, scope=types.BotCommandScopeAllPrivateChats())
    # Подключаемся к базе данных SQLite
    await sqlite_db.sql_start()
    # Выводим сообщение о запуске бота
    print("Бот вышел в онлайн")
    await dp.start_polling(bot, allowed_updates=ALLOWED_UPDATES)

asyncio.run(main())