import math

from aiogram import types


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
        return message.text and math.ceil(eval(message.text.replace(',', '.'))) > 0
    except:
        # Если произошла ошибка (например, текст сообщения не является числом или математическим выражением),
        # возвращаем False
        return False