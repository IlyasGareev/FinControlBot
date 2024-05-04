import asyncio
from datetime import datetime
from db import sqlite_db
from utils.goals import get_goals

async def send_message_to_user(bot_instance):
    # Текст сообщения
    message_text = "🕗 Пожалуйста, не забудьте внести свои расходы или доходы. \n" \
                   "Важно быть в курсе своих финансов!"
    # Получаем список пользователей, которые не вносили сегодня траты
    inactive_users: list = await sqlite_db.get_inactive_users_today(datetime.now())

    # Отправляем сообщение каждому из неактивных пользователей
    for user in inactive_users:
        await bot_instance.send_message(user, message_text)

async def scheduled(bot_instance):
    while True:
        # Получаем текущее время
        current_time = datetime.now()
        # Проверяем, если текущее время 20:20, то отправляем сообщение
        if current_time.time().hour == 20 and current_time.time().minute == 20:
            await send_message_to_user(bot_instance)
            # Проверяем, есть ли цели, у которых вышел срок, либо достигла нужная сумма
            goals = await sqlite_db.get_ended_goals(current_time.date())
            if goals:
                for goal in goals:
                    await bot_instance.send_message(chat_id=goal[0], text=goal[1])
            # Ждем до следующего дня, чтобы не отправлять сообщение больше одного раза в день
            await asyncio.sleep(86400)
        else:
            # Ждем 60 секунд перед повторной проверкой времени
            await asyncio.sleep(60)