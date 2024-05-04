import math

from aiogram import types

from create_bot import bot


def if_numbers_filter(message: types.Message):
    """
    Функция для проверки, является ли текст сообщения числом или математическим выражением.

    Args:
        message: Объект типа Message из aiogram.

    Returns:
        bool: True, если текст сообщения является числом или математическим выражением,
              иначе False.
    """
    try:
        # Пытаемся вычислить значение текста сообщения как числа или математического выражения
        # Если вычисление успешно и результат больше нуля, возвращаем True
        # 9223372036854775807 - предельное значение sqlite integer
        return message.text and (9223372036854775807 >= math.ceil(eval(message.text.replace(',', '.'))) > 0)
    except:
        # Если произошла ошибка (например, текст сообщения не является числом или математическим выражением),
        # возвращаем False
        return False

async def check_user_process(user_in_process, message_id):
    if not user_in_process:
        return True
    else:
        await bot.send_message(message_id, "Вы находитесь в процессе, пожалуйста завершите его и продолжайте работу.")
        return False
