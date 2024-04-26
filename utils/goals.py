from datetime import datetime
from aiogram import types
from db import sqlite_db
from keyboards.client_kb import user_goals_kb, user_goals_all_kb


async def get_goals_all(user_id: int):

    goals: list = await sqlite_db.get_user_goals(user_id)

    return user_goals_all_kb(goals)


async def get_goals(user_id: int):
    goals: list = await sqlite_db.get_user_goals(user_id)

    return user_goals_kb(goals)


async def about_goal_info(goal_id: int):

    goal_info = await sqlite_db.about_goal(goal_id)

    new_text = (f"🎯 <b>Подробности о вашей финансовой цели:</b>\n"
                f"-------------------------------------------- \n"
                f"🔹 <b>Идентификатор цели:</b> {goal_info[0]}\n"
                f"🔹 <b>Название цели:</b> {goal_info[1]}\n"
                f"🔹 <b>Текущая сумма:</b> {goal_info[2]} руб.\n"
                f"🔹 <b>Нужная сумма:</b> {goal_info[3]} руб.\n"
                f"🔹 <b>Прогресс:</b> {round((goal_info[2] / goal_info[3]) * 100, 2)}% \n"
                f"🔹 <b>Дата окончания цели:</b> {goal_info[4]} \n")

    if not goal_info[2] >= goal_info[3]:

        days = ((datetime.strptime(goal_info[4], '%Y-%m-%d') - datetime.now()).days + 1)

        value_day = (goal_info[3] - goal_info[2]) / days

        value_week = int(value_day * 7) if days >= 7 else int(goal_info[3] - goal_info[2])

        new_text += f"🔹 <b>Еженедельно нужно откладывать примерно </b> {value_week} руб.\n"

    else:

        new_text += "\n<b>Поздравляем, вы достигли конечной суммы цели!🎉</b>\n" \
                    "Удаление цели произойдет в дату окончания. Либо сделайте это самостоятельно.\n"

    return new_text


def is_valid_future_date(date_str):
    try:
        # Парсинг введенной даты
        input_date = datetime.strptime(date_str, '%Y-%m-%d')

        # Получение текущей даты
        current_date = datetime.now()

        # Сравнение дат
        if input_date >= current_date:
            return True
        else:
            return False
    except ValueError:
        # Если произошла ошибка при парсинге даты, она не является валидной
        return False


def get_goal_id(message: types.Message):
    return int(message.text.split('🔹 Название цели')[0].split('Идентификатор цели: ')[1])