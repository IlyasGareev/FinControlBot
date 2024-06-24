import re
from datetime import datetime
from calendar import monthrange
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Кнопка "Назад" для использования в различных Inline клавиатурах
back_date = InlineKeyboardButton(text='Назад', callback_data='back_date')

# Словарь месяцев для отображения полного названия месяца
months = {
        '01': 'Январь',
        '02': 'Февраль',
        '03': 'Март',
        '04': 'Апрель',
        '05': 'Май',
        '06': 'Июнь',
        '07': 'Июль',
        '08': 'Август',
        '09': 'Сентябрь',
        '10': 'Октябрь',
        '11': 'Ноябрь',
        '12': 'Декабрь'
    }


# Функция создания Inline клавиатуры для выбора даты
async def button_ex(text: str) -> InlineKeyboardMarkup:
    date_list = text.split('-')

    day_btn = InlineKeyboardButton(text=f"{date_list[2]}", callback_data="day_btn")
    month_btn = InlineKeyboardButton(text=f"{months[date_list[1]]}", callback_data="month_btn")
    year_btn = InlineKeyboardButton(text=f"{date_list[0]}", callback_data="year_btn")
    done_btn = InlineKeyboardButton(text="Готово", callback_data="Готово")
    markup = InlineKeyboardMarkup(inline_keyboard=[[day_btn, month_btn, year_btn], [done_btn]])

    return markup


# Функция создания кнопок выбора дней в месяце
async def days_func(date):
    date_list = date.split('-')

    month = date_list[1]
    day = int(date_list[2])
    year = date_list[0]
    days = monthrange(int(year), int(month))[1]

    btns = []
    btns_list = []
    for day_tmp in range(1, days + 1):
        if day_tmp % 7 == 0:
            btns.append(btns_list)
            btns_list = []
        if not day_tmp == day:
            btns_list.append(InlineKeyboardButton(text=str(day_tmp), callback_data=str(day_tmp)))
        else:
            btns_list.append(InlineKeyboardButton(text='☑'+str(day_tmp), callback_data=str(day_tmp)))
        if day_tmp == days:
            btns.append(btns_list)
    btns.append([back_date])
    days_markup = InlineKeyboardMarkup(inline_keyboard=btns)

    return days_markup


# Функция создания кнопок выбора месяцев
async def months_func(date):
    month = date.split('-')[1]
    btns = []
    btns_list = []

    for month_tmp in months.keys():
        if month_tmp in ['05', '09']:
            btns.append(btns_list)
            btns_list = []
        if not month_tmp == month:
            btns_list.append(InlineKeyboardButton(text=months[month_tmp], callback_data=months[month_tmp]))
        else:
            btns_list.append(InlineKeyboardButton(text='☑' + months[month_tmp], callback_data=months[month_tmp]))
        if month_tmp == list(months.keys())[-1]:
            btns.append(btns_list)
    btns.append([back_date])
    month_markup = InlineKeyboardMarkup(inline_keyboard=btns)

    return month_markup


# Функция создания кнопок выбора годов
async def years_func(date):
    year = int(date.split('-')[0])

    btns = []
    btns_list = []
    year_tmp = year
    if year != datetime.now().year:
        btns_list.append(InlineKeyboardButton(text=str(datetime.now().year), callback_data=str(datetime.now().year)))
    for i in range(4):
        if not year_tmp == year:
            btns_list.append(InlineKeyboardButton(text=str(year_tmp), callback_data=str(year_tmp)))
        else:
            btns_list.append(InlineKeyboardButton(text='☑' + str(year_tmp), callback_data=str(year_tmp)))
        year_tmp -= 1
    btns.append(btns_list)
    btns.append([back_date])
    year_markup = InlineKeyboardMarkup(inline_keyboard=btns)

    return year_markup


# Функция для проверки данных обратного вызова, связанных с выбором даты
def date_check(callback: types.CallbackQuery):
    # Список разрешенных значений для callback.data
    allowed_values = ['Изменить дату', 'day_btn', 'month_btn', 'year_btn', 'Готово', 'back_date'] + [str(i) for i in
                                                                                                     range(1,
                                                                                                           32)] + list(
        months.values())

    try:
        # Проверяем, есть ли значение в списке разрешенных значений или соответствует ли шаблону даты
        return callback.data in allowed_values or re.match(r'^\d{4}$', callback.data) is not None
    except:
        return False