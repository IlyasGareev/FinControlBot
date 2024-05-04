from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Клавиатура для выбора валюты
currency_buttons = [[
        InlineKeyboardButton(text='🇷🇺 RUB/ 🇺🇸 USD', callback_data='RUB/USD'),
        InlineKeyboardButton(text='🇷🇺 RUB/ 🇪🇺 EUR', callback_data='RUB/EUR'),
    ], [
        InlineKeyboardButton(text='🇺🇸 USD/ 🇪🇺 EUR', callback_data='USD/EUR'),
        InlineKeyboardButton(text='Другая пара валют', callback_data='else_convert'),
    ], [
        InlineKeyboardButton(text='Ввести другую сумму', callback_data='another_sum')
    ], [
    InlineKeyboardButton(text='❌ Закончить конвертацию ❌', callback_data='convert_end')
    ]]
currency_keyboard = InlineKeyboardMarkup(inline_keyboard=currency_buttons)


def navigation_report_keyboard(cur_date: bool):
    if not cur_date:
        # Клавиатура навигации по отчетам
        nav_btns = [[
            InlineKeyboardButton(text='<<', callback_data='nav_back_btn'),
            InlineKeyboardButton(text='Текущий месяц', callback_data='cur_date'),
            InlineKeyboardButton(text='>>', callback_data='nav_forward_btn')
        ]]
    else:
        nav_btns = [[
            InlineKeyboardButton(text='<<', callback_data='nav_back_btn')
        ]]
    navigation_report_keyboard = InlineKeyboardMarkup(inline_keyboard=nav_btns)

    return navigation_report_keyboard


# Кнопка для отмены
cancel_button = InlineKeyboardButton(text='🚫 Отмена', callback_data='Отмена')


def user_goals_all_kb(goals: list):
    builder = InlineKeyboardBuilder()

    for item in goals:
        btn_text = f"{item[1]} - {str(item[2])} / {str(item[3])}"
        builder.button(text=f"{btn_text}", callback_data=f"goal_{item[0]}_{item[1]}")
    builder.button(text=f"➕ Добавить цель", callback_data=f"add_goal")
    builder.adjust(1)
    return builder.as_markup()


def user_goals_kb(goals: list):
    builder = InlineKeyboardBuilder()

    for item in goals:
        btn_text = f"{item[1]} - {str(item[2])} / {str(item[3])}"
        builder.button(text=f"{btn_text}", callback_data=f"add_sum_goal_{item[0]}_{item[1]}")
    builder.button(text=f"<< Назад", callback_data=f"К расходам")
    builder.adjust(1)
    return builder.as_markup()


def about_goal_kb(goal_id: int):
    btns = [
        [
            InlineKeyboardButton(text='💲 Изменить сумму', callback_data='Изменить сумму'),
            InlineKeyboardButton(text='📆 Изменить дату', callback_data='Изменить дату цели'),
        ], [
            InlineKeyboardButton(text='<< Назад', callback_data='back_goal'),
            InlineKeyboardButton(text='🗑 Удалить цель', callback_data='Отмена')
        ]
    ]
    cancel_keyboard_markup = InlineKeyboardMarkup(inline_keyboard=btns)

    return cancel_keyboard_markup


# Клавиатура с категориями расходов для ввода вручную
categories_buttons = [[
        InlineKeyboardButton(text = '🛒Продукты/хозтовары',
                           callback_data= '🛒Продукты/хозтовары'),
        InlineKeyboardButton(text = '🍔Рестораны и кафе',
                           callback_data='🍔Рестораны и кафе'),
    ], [
        InlineKeyboardButton(text='🙋Красота и уход',
                            callback_data='🙋Красота и уход'),
        InlineKeyboardButton(text='💊Здоровье',
                           callback_data='💊Здоровье'),
    ], [
        InlineKeyboardButton(text='🚇Транспорт',
                           callback_data='🚇Транспорт'),
        InlineKeyboardButton(text='👚Одежда и обувь',
                           callback_data='👚Одежда и обувь'),
    ], [
        InlineKeyboardButton(text='🚰Коммунальные',
                           callback_data='🚰Коммунальные'),
        InlineKeyboardButton(text='🌐Интернет, связь',
                           callback_data='🌐Интернет, связь'),
    ], [
        InlineKeyboardButton(text='📚Образование',
                           callback_data='📚Образование'),
        InlineKeyboardButton(text='📺Подписки',
                           callback_data='📺Подписки'),
    ], [
        InlineKeyboardButton(text='🎢Развлечение',
                           callback_data='🎢Развлечение'),
        InlineKeyboardButton(text='🛍Интернет-покупки',
                           callback_data='🛍Интернет-покупки'),
    ], [
        InlineKeyboardButton(text='🎯 К целям',
                           callback_data='К целям')
    ], [
        cancel_button,
        InlineKeyboardButton(text='💰 К доходам',
                           callback_data='К доходам'),
        InlineKeyboardButton(text='Еще >>',
                           callback_data='Еще')
    ]
]

expense_categories_keyboard = InlineKeyboardMarkup(inline_keyboard=categories_buttons)


# Клавиатура с категориями расходов для ввода по фото
categories_buttons = [[
        InlineKeyboardButton(text = '🛒Продукты/хозтовары',
                               callback_data= '🛒Продукты/хозтовары'),
        InlineKeyboardButton(text = '🍔Рестораны и кафе',
                               callback_data='🍔Рестораны и кафе'),
    ], [
        InlineKeyboardButton(text='🙋Красота и уход',
                                callback_data='🙋Красота и уход'),
        InlineKeyboardButton(text='💊Здоровье',
                               callback_data='💊Здоровье'),
    ], [
        InlineKeyboardButton(text='🚇Транспорт',
                               callback_data='🚇Транспорт'),
        InlineKeyboardButton(text='👚Одежда и обувь',
                               callback_data='👚Одежда и обувь'),
    ], [
        InlineKeyboardButton(text='🚰Коммунальные',
                               callback_data='🚰Коммунальные'),
        InlineKeyboardButton(text='🌐Интернет, связь',
                               callback_data='🌐Интернет, связь'),
    ], [
        InlineKeyboardButton(text='📚Образование',
                               callback_data='📚Образование'),
        InlineKeyboardButton(text='📺Подписки',
                               callback_data='📺Подписки'),
    ], [
        InlineKeyboardButton(text='🎢Развлечение',
                               callback_data='🎢Развлечение'),
        InlineKeyboardButton(text='🛍Интернет-покупки',
                               callback_data='🛍Интернет-покупки'),
    ], [
        cancel_button,
        InlineKeyboardButton(text='Еще >>',
                           callback_data='Еще')
    ]
]

expense_photo_categories_keyboard = InlineKeyboardMarkup(inline_keyboard=categories_buttons)


# Клавиатура с категориями доходов
income_buttons = [
    [
        InlineKeyboardButton(text='💵Зарплата', callback_data='💵Зарплата'),
        InlineKeyboardButton(text='🧑‍💻Фриланс', callback_data='💻Фриланс'),
        ], [
        InlineKeyboardButton(text='🤝Услуги', callback_data='🤝Услуги'),
        InlineKeyboardButton(text='📈Дивиденды', callback_data='📈Дивиденды'),
        ], [
        InlineKeyboardButton(text='💸Крипта', callback_data='💸Крипта'),
        InlineKeyboardButton(text='🏭Бизнес', callback_data='🏭Бизнес'),
        ], [
        InlineKeyboardButton(text='🏦Депозиты', callback_data='🏦Депозиты'),
        InlineKeyboardButton(text='🏨Аренда', callback_data='🏨Аренда'),
        ], [
        InlineKeyboardButton(text='💳Переводы от людей', callback_data='💳Переводы от людей'),
        InlineKeyboardButton(text='🌏Другое', callback_data='🌏Другое'),
        ], [
        InlineKeyboardButton(text='К расходам', callback_data='К расходам')
]]

income_categories_keyboard = InlineKeyboardMarkup(inline_keyboard=income_buttons)


# Клавиатура с дополнительными категориями расходов

more_categories_buttons = [
    [
        InlineKeyboardButton(text='🌊Путешествия и отпуск',
                           callback_data='🌊Путешествия и отпуск'),
        InlineKeyboardButton(text='🎁Подарки и праздники',
                           callback_data='🎁Подарки и праздники'),
    ], [
        InlineKeyboardButton(text='🦮Домашние животные',
                           callback_data='🦮Домашние животные'),
        InlineKeyboardButton(text='⛹‍♂Спорт и фитнес',
                           callback_data='⛹‍Спорт и фитнес'),
    ], [
        InlineKeyboardButton(text='📱Техника и электроника',
                           callback_data='📱Техника и электроника'),
        InlineKeyboardButton(text='🏠Дом, ремонт',
                           callback_data='🏠Дом, ремонт'),
    ], [
        InlineKeyboardButton(text='🚙Автомобиль',
                           callback_data='🚙Автомобиль'),
        InlineKeyboardButton(text='👶Дети',
                           callback_data='👶Дети'),
    ], [
        InlineKeyboardButton(text='🏦Банковские услуги',
                           callback_data='🏦Банковские услуги'),
        InlineKeyboardButton(text='💼Страхование',
                           callback_data='💼Страхование'),
    ], [
        InlineKeyboardButton(text='🎨Хобби и творчество',
                           callback_data='🎨Хобби и творчество'),
        InlineKeyboardButton(text='🌏Прочее',
                           callback_data='🌏Прочее'),
    ], [
        InlineKeyboardButton(text='<< Назад',
                           callback_data='Назад'),
        cancel_button
    ]]
more_exp_categories_keyboard = InlineKeyboardMarkup(inline_keyboard=more_categories_buttons)


# Клавиатура для отмены
def cancel_keyboard(receipt):
    if not receipt:
        btns = [[
                InlineKeyboardButton(text='📆 Изменить дату', callback_data='Изменить дату'),
                InlineKeyboardButton(text='💬 Комментарий', callback_data='Добавить комментарий'),
             ], [
                cancel_button
        ]]
        cancel_keyboard_markup = InlineKeyboardMarkup(inline_keyboard=btns)
    else:
        cancel_keyboard_markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='💬 Комментарий', callback_data='Добавить комментарий'), cancel_button]])

    return cancel_keyboard_markup