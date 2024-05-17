# Импорты стандартных библиотек
import math
import re
import datetime
import tempfile
from datetime import datetime

# Импорты сторонних библиотек
import cv2
import matplotlib.pyplot as plt
import numpy as np
from aiogram import types, Router, F
from aiogram.types import FSInputFile
from aiogram.filters import Command, StateFilter, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from pyzbar import pyzbar
from utils.qrcode import qrcheck

# Импорты локальных модулей
from create_bot import bot
from db import sqlite_db
from keyboards.client_kb import *
from utils.report_navigation import *
from utils.exchange_rates import get_exchange
from utils.filters import if_numbers_filter, check_user_process
from utils.converter import convert_currency_xe
from utils.edit_date import *
from utils.goals import *


#Роутер клиентов
client_router = Router()

# Словарь, в котором хранятся данные о пользователе
users: dict = {}


class FSMConvert(StatesGroup):
    """
    Конечный автомат (Finite State Machine) для конвертации валют.

    Атрибуты:
        value: Состояние для ввода суммы, которую нужно конвертировать.
        currency: Состояние для выбора валютной пары.
        currency_else: Состояние для ввода пользовательской валютной пары.
    """
    value = State()
    currency = State()
    currency_else = State()


class FSMComment(StatesGroup):
    """
    Конечный автомат (Finite State Machine) для комментариев.

    Атрибуты:
        comment: Состояние для ввода комментария.
    """
    comment = State()


class FSMGoal(StatesGroup):
    """
    Конечный автомат (Finite State Machine) для управления целями.

    Атрибуты:
        name: Состояние для ввода названия цели.
        summ: Состояние для ввода суммы цели.
        date: Состояние для ввода даты цели.
    """
    name = State()
    summ = State()
    date = State()


class FSMGoalChangeSum(StatesGroup):
    """
    Конечный автомат (Finite State Machine) для изменения суммы цели.

    Атрибуты:
        new_sum: Состояние для ввода новой суммы цели.
    """
    new_sum = State()


class FSMGoalChangeDate(StatesGroup):
    """
    Конечный автомат (Finite State Machine) для изменения даты цели.

    Атрибуты:
        new_date: Состояние для ввода новой даты цели.
    """
    new_date = State()



@client_router.message(CommandStart())
async def start_cmd(message: types.Message):
    """Обработка команды start"""

    # Если пользователь новый
    if message.from_user.id not in users:
        users[message.from_user.id]: dict = {
                'in_process': False,
                'items': [],
                'check': [],
                'receipt': None
        }
        await sqlite_db.add_user(user_id=message.from_user.id, name=message.from_user.first_name)

    await message.answer(f'{message.from_user.first_name}, приветствую вас.\n'
                             f'Для добавления расходов или доходов вводите числа,'
                             f' либо пришлите фото QR-кода с чека.\n'
                             f'Для того, чтобы ознакомиться с полной информацией - введите команду /help')


@client_router.message(StateFilter(None), Command('help'))
async def help_cmd(message: types.Message):
    """Обработка команды help - вывод информации по боту"""
    if await check_user_process(user_in_process=users[message.from_user.id]['in_process'],
                          message_id=message.from_user.id):
        # Формируем сообщение с помощью форматированной строки
        help_text = (
            "🤖  <b>Бот помогает</b> следить за доходами и расходами, а также управлять финансовыми целями.\n\n"
            "ℹ️ Чтобы добавить сведения о доходах или расходах, введите <b>число или математическое выражение</b>, "
            "например, 26*4 или 236+189.\n"
            "\t\t\t\t\t\tМожно также направить фотографию <b>QR-кода</b> на чеке.\n\n"
            "🎯 Управление <b>финансовыми целями</b> /goals.\n"
            "\t\t\t\t\t\tДля добавления суммы к целям - введите числа и выберите категорию 'К целям'.\n\n"
            "💰 Просмотр актуального <b>курса валют</b> /kurs. \n\n"
            "💡 Полезные <b>советы</b> по ведению бюджета /advice. \n\n"
            "💶 <b>Конвертация валют:</b> введите команду /convert, затем введите сумму.\n"
            "\t\t\t\t\t\tДалее выберите пару валют, либо введите самостоятельно (Другая пара валют)\n"
            "\t\t\t\t\t\tТакже можете ввести другую сумму (Ввести другую сумму).\n"
            "\t\t\t\t\t\t<b>Важно!</b> Не забудьте завершить конвертацию, иначе бот не будет воспринимать ваши сообщения!\n\n"
            "📊 <b>Отчеты</b> помогут вам контролировать расходы и доходы по категориям /report."
        )

        # Отправляем сообщение
        await message.answer(help_text, parse_mode='html')


@client_router.message(StateFilter(None), Command('advice'))
async def get_advice(message: types.Message):
    """Обработка команды get_advice - вывод полезных советов по ведению бюджета"""
    if await check_user_process(user_in_process=users[message.from_user.id]['in_process'],
                                message_id=message.from_user.id):
        # Формируем сообщение с советами
        advice_text = (
            "Вот <b>пять полезных советов</b> для ведения бюджета: \n\n"
            "1. <b>Экономьте и инвестируйте:</b> Накапливайте часть своих доходов для будущих целей и инвестируйте их для получения дополнительного дохода. "
            "Регулярное сохранение даже небольших сумм может привести к значительным результатам в будущем. \n\n"
            "2. <b>Будьте готовы к неожиданностям:</b> Создайте экстренный фонд для покрытия неожиданных расходов, "
            "таких как медицинские счета или ремонт автомобиля. Это поможет вам избежать задолженностей и "
            "сохранить финансовую стабильность. \n\n"
            "3. <b>Отслеживайте свои расходы:</b> Ведите детальный учет всех своих расходов. "
            "Это поможет вам понять, куда уходят ваши деньги, и идентифицировать области, в которых можно сэкономить. \n\n"
            "4. <b>Планируйте затраты:</b> Планируйте свои расходы заранее, чтобы иметь представление о том, сколько "
            "денег у вас останется после покрытия основных расходов. "
            "Это поможет вам избежать излишних трат и управлять финансами более эффективно. \n\n"
            "5. <b>Изучайте и совершенствуйтесь:</b> Постоянно обучайтесь финансовым навыкам, читайте книги, "
            "следите за блогами экспертов и участвуйте в образовательных мероприятиях. "
            "Чем больше вы знаете о финансах, тем лучше будете управлять своим бюджетом.\n\n"
            "Дополнительную информацию о ведении бюджета вы можете найти по следующим ссылкам:\n"
            '<a href="https://expobank.ru/blog/kak-povysit-finansovuyu-gramotnost-10-prostykh-pravil/">Как повысить финансовую грамотность: 10 простых правил</a>\n'
            '<a href="https://theoryandpractice.ru/posts/18520-30-shagov-k-finansovoy-gramotnosti">30 шагов к финансовой грамотности</a>\n'
            '<a href="https://www.vtb.ru/articles/chto-takoe-finansovaya-gramotnost/">Что такое финансовая грамотность</a>'
        )

        # Отправляем сообщение с советами
        await message.answer(advice_text, parse_mode='html')


@client_router.message(StateFilter(None), Command('kurs'))
async def exchange(message: types.Message):
    """Обработать команду /kurs для получения курсов обмена."""
    if await check_user_process(user_in_process=users[message.from_user.id]['in_process'],
                                message_id=message.from_user.id):
        # Получаем курс валют
        msg_text = get_exchange()

        # Отправить пользователю курсы обмена
        await bot.send_message(message.from_user.id, msg_text)


@client_router.message(StateFilter(None), Command('goals'))
async def goals_info(message: types.Message):
    """Обработать команду /goals для просмотра информации по целям."""
    if await check_user_process(user_in_process=users[message.from_user.id]['in_process'],
                                message_id=message.from_user.id):
        # Отправить пользователю информацию о целях
        await bot.send_message(message.from_user.id, 'Ваши финансовые цели',
                               reply_markup=await get_goals_all(message.from_user.id))


@client_router.callback_query(StateFilter(None), F.data == 'add_goal')
async def add_goal(callback: types.CallbackQuery, state: FSMContext):
    """
    Обработчик колбэка для добавления новой финансовой цели.
    При активации запрашивает у пользователя название цели.

    Args:
        message: Объект сообщения с названием цели.
        state: Состояние FSM для сохранения данных о цели.

    Returns:
        None
    """
    if await check_user_process(user_in_process=users[callback.from_user.id]['in_process'],
                                message_id=callback.from_user.id):
        # Устанавливаем флаг "в процессе" для пользователя
        users[callback.from_user.id]['in_process'] = True

        # Сохраняем сообщение, чтобы иметь доступ к нему в дальнейшем
        await state.set_data({'msg': callback.message})

        # Отправляем пользователю запрос на ввод названия цели
        await callback.message.answer(text='💭 Введите название цели',
                                      reply_markup=InlineKeyboardMarkup(inline_keyboard=[[cancel_button]]))

        # Устанавливаем состояние FSM для ввода названия
        await state.set_state(FSMGoal.name)


@client_router.message(FSMGoal.name, F.text)
async def add_goal_name(message: types.Message, state: FSMContext):
    """
    Обработчик сообщения с названием финансовой цели.
    Сохраняет название цели и сообщения для последующего удаления.
    Переходит к запросу ввода суммы цели.

    Args:
        message: Объект сообщения с названием цели.
        state: Состояние FSM для сохранения данных о цели.

    Returns:
        None
    """
    # Получаем данные из состояния FSM
    data = await state.get_data()

    # Добавляем сообщение в список удаленных
    if 'del_msg_id' not in data.keys():
        data['del_msg_id'] = [message.message_id - 1, message.message_id]
    else:
        data['del_msg_id'] += [message.message_id - 1, message.message_id]

    if len(str(message.text)) <= 25:
        # Записываем название цели и сообщения, которые потом удалим
        await state.set_data({'name': message.text,
                              'msg': data['msg']})

        # Отправляем пользователю запрос на ввод суммы
        await message.answer(text='💭 Введите сумму цели')

        # Устанавливаем состояние FSM для ввода суммы
        await state.set_state(FSMGoal.summ)
    else:
        await bot.send_message(message.chat.id,
                               "Длина названия не должна превышать 25 символов. Введите название снова.")
        await state.set_state(FSMGoal.name)
    await state.update_data(del_msg_id=data['del_msg_id'])


@client_router.message(FSMGoal.summ, F.text)
async def add_goal_summ(message: types.Message, state: FSMContext):
    """
    Обработчик сообщения с суммой финансовой цели.
    Сохраняет сумму цели и сообщения для последующего удаления.
    Переходит к запросу ввода даты окончания цели.

    Args:
        message: Объект сообщения с суммой цели.
        state: Состояние FSM для сохранения данных о цели.

    Returns:
        None
    """
    # Получаем данные из состояния FSM
    data = await state.get_data()

    # Добавляем идентификаторы сообщений для последующего удаления
    del_msg_list = data['del_msg_id']
    del_msg_list += [message.message_id - 1, message.message_id]

    if not if_numbers_filter(message):
        # В случае ошибки отправляем пользователю сообщение о необходимости ввода заново
        await message.answer(f'Что-то пошло не так. Введите положительное число, не превышающее 100.000.000.000.')
        # Устанавливаем состояние FSM для ввода даты снова
        await state.set_state(FSMGoal.summ)
    else:
        # Записываем данные о цели и сообщениях
        await state.set_data({'name': data['name'],
                              'msg': data['msg'],
                              'del_msg_id': del_msg_list,
                              'summ': math.ceil(eval(message.text.replace(',', '.').replace(' ', '')))})

        # Отправляем пользователю запрос на ввод даты окончания цели
        await message.answer(text='💭 Введите дату в формате YYYY-MM-DD (Пример - 2024-3-18)')

        # Устанавливаем состояние FSM для ввода даты
        await state.set_state(FSMGoal.date)


@client_router.message(FSMGoal.date, F.text)
async def add_goal_date(message: types.Message, state: FSMContext):
    """
    Обработчик сообщения с датой окончания финансовой цели.
    Проверяет введенную дату на корректность и на то, что она представляет будущее.
    Добавляет цель в базу данных, обновляет сообщение с целями пользователя и удаляет временные сообщения.

    Args:
        message: Объект сообщения с датой окончания цели.
        state: Состояние FSM для сохранения данных о цели.

    Returns:
        None
    """
    # Получаем данные из состояния FSM
    data = await state.get_data()

    # Добавляем идентификаторы сообщений для последующего удаления
    del_msg_list = data['del_msg_id']
    del_msg_list += [message.message_id - 1, message.message_id]

    # Проверяем корректность введенной даты и то, что она представляет будущее
    if not is_valid_future_date(message.text):
        # В случае ошибки отправляем пользователю сообщение о необходимости ввода заново
        await message.answer(f'Что-то пошло не так. '
                             f'Либо дата введена неправильно (формат YYYY-MM-DD (пример - 2024-3-18)), '
                             f'либо дата предшествует текущей. '
                             f'Пожалуйста, введите дату заново.')
        # Устанавливаем состояние FSM для ввода даты снова
        await state.set_state(FSMGoal.date)
    else:
        # Добавляем цель в базу данных
        await sqlite_db.add_goal_in_db(user_id=message.from_user.id,
                                       name=data['name'],
                                       summ=data['summ'],
                                       date=str(datetime.strptime(message.text, '%Y-%m-%d').date()))

        # Обновляем сообщение с целями пользователя
        await data['msg'].edit_reply_markup(reply_markup=await get_goals_all(message.from_user.id))


        try:
            # Удаляем временные сообщения # fixme
            for msg_id in del_msg_list:
                await bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
        finally:
            # Завершаем состояние FSM
            users[message.from_user.id]['in_process'] = False
            await state.clear()




@client_router.callback_query(StateFilter(None), F.data.startswith('goal_'))
async def about_goal(callback: types.CallbackQuery):
    """
    Обработчик нажатия на кнопку с информацией о конкретной финансовой цели.
    Получает информацию о цели из базы данных и отправляет пользователю сообщение с этой информацией.

    Args:
        callback: Объект callback-запроса, содержащий данные о цели.

    Returns:
        None
    """
    if await check_user_process(user_in_process=users[callback.from_user.id]['in_process'],
                                message_id=callback.from_user.id):
        # Получаем идентификатор цели из callback данных
        goal_id = int(re.findall(r'\d+', callback.data)[0])

        # Получаем информацию о цели
        new_text = await about_goal_info(goal_id)

        # Редактируем сообщение с новой информацией о цели
        await bot.edit_message_text(text=new_text, chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                    reply_markup=about_goal_kb(goal_id=goal_id), parse_mode='html')


@client_router.callback_query(StateFilter(None), F.data == 'Изменить сумму')
async def change_goal_sum(callback: types.CallbackQuery, state: FSMContext):
    """
    Обработчик нажатия на кнопку "Изменить сумму" для финансовой цели.
    Запускает процесс изменения суммы цели.

    Args:
        callback: Объект callback-запроса.
        state: Объект состояния FSM.

    Returns:
        None
    """
    if await check_user_process(user_in_process=users[callback.from_user.id]['in_process'],
                                message_id=callback.from_user.id):
        users[callback.from_user.id]['in_process'] = True
        await state.set_data({'msg': callback.message,
                              'del_msg_id': []})
        # Отправляем пользователю запрос на ввод новой суммы
        await callback.message.answer(text='💭 Введите новую сумму',
                                      reply_markup=InlineKeyboardMarkup(inline_keyboard=[[cancel_button]]))

        # Устанавливаем состояние FSM для ввода новой суммы
        await state.set_state(FSMGoalChangeSum.new_sum)


@client_router.message(FSMGoalChangeSum.new_sum, F.text)
async def new_goal_sum(message: types.Message, state: FSMContext):
    """
    Обработчик ввода новой суммы для финансовой цели.
    Производит изменение суммы финансовой цели и обновление сообщения с информацией о цели.

    Args:
        message: Объект сообщения пользователя.
        state: Объект состояния FSM.

    Returns:
        None
    """
    # Получаем данные из состояния FSM
    data = await state.get_data()

    # Добавляем идентификаторы сообщений для последующего удаления
    del_msg_list = data['del_msg_id']
    del_msg_list += [message.message_id - 1, message.message_id]

    if not if_numbers_filter(message):
        # В случае ошибки отправляем пользователю сообщение о необходимости ввода заново
        await message.answer(f'Что-то пошло не так. Введите положительное число, не превышающее 100.000.000.000.')
        # Устанавливаем состояние FSM для ввода даты снова
        await state.set_state(FSMGoalChangeSum.new_sum)
    else:
        # Извлекаем идентификатор цели из данных сообщения
        goal_id = get_goal_id(data['msg'])

        # Обновляем сумму цели в БД
        await sqlite_db.change_goal(goal_id=goal_id, new_value=int(eval(message.text)), part='sum')

        # Редактируем сообщение с обновленной информацией о цели
        await bot.edit_message_text(text=await about_goal_info(goal_id),
                                    chat_id=message.chat.id, message_id=data['msg'].message_id,
                                    reply_markup=about_goal_kb(goal_id=goal_id),
                                    parse_mode='html')

        try:
            # Удаляем временные сообщения # fixme
            for msg_id in del_msg_list:
                await bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
        finally:
            # Завершаем состояние FSM
            users[message.from_user.id]['in_process'] = False
            await state.clear()


@client_router.callback_query(StateFilter(None), F.data == 'Изменить дату цели')
async def change_goal_date(callback: types.CallbackQuery, state: FSMContext):
    """
    Обработчик запроса на изменение даты цели.
    Отправляет пользователю запрос на ввод новой даты цели.

    Args:
        callback: Объект callback-запроса от пользователя.
        state: Объект состояния FSM.

    Returns:
        None
    """
    if await check_user_process(user_in_process=users[callback.from_user.id]['in_process'],
                                message_id=callback.from_user.id):
        users[callback.from_user.id]['in_process'] = True
        await state.set_data({'msg': callback.message, 'del_msg_id': []})
        # Отправляем пользователю запрос на ввод новой даты цели
        await callback.message.answer(text='💭 Введите новую дату в формате YYYY-MM-DD (пример: 2024-5-31)',
                                      reply_markup=InlineKeyboardMarkup(inline_keyboard=[[cancel_button]]))

        # Устанавливаем состояние FSM для ввода новой даты
        await state.set_state(FSMGoalChangeDate.new_date)


@client_router.message(FSMGoalChangeDate.new_date, F.text)
async def new_goal_date(message: types.Message, state: FSMContext):
    """
    Обработчик ввода новой даты цели.
    Проверяет введенную дату на корректность и изменяет дату цели в БД.

    Args:
        message: Объект сообщения пользователя.
        state: Объект состояния FSM.

    Returns:
        None
    """
    # Получаем данные из состояния FSM
    data = await state.get_data()

    goal_id = get_goal_id(data['msg'])

    del_msg_list = data['del_msg_id']
    del_msg_list += [message.message_id - 1, message.message_id]
    # Сравниваем введеную дату и текущую дату цели
    new_date = str(datetime.strptime(message.text, '%Y-%m-%d').date())
    cur_date = data['msg'].text.split("Дата окончания цели: ")[1][:10]

    if not is_valid_future_date(message.text) or new_date == cur_date:
        # В случае возникновения ошибки отправляем пользователю сообщение о необходимости ввода заново
        await message.answer(f'Что-то пошло не так. '
                             f'Либо дата введена неправильно (формат - пример: 2024-4-30), либо дата предшествует текущей. '
                             f'Пожалуйста, введите дату заново.')
        # Устанавливаем состояние FSM для ввода новой даты снова
        await state.set_state(FSMGoalChangeDate.new_date)
    else:

        # Изменяем дату цели в БД
        await sqlite_db.change_goal(goal_id=goal_id, new_value=str(datetime.strptime(message.text, '%Y-%m-%d').date()),
                                    part='date')

        try:
            # Редактируем сообщение с новым текстом
            await bot.edit_message_text(text=await about_goal_info(goal_id),
                                        chat_id=message.chat.id, message_id=data['msg'].message_id,
                                        reply_markup=about_goal_kb(goal_id=goal_id),
                                        parse_mode='html')

            # Удаляем сообщения # fixme
            for msg_id in del_msg_list:
                await bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
        finally:
            # Завершаем состояние FSM
            users[message.from_user.id]['in_process'] = False
            await state.clear()


@client_router.callback_query(StateFilter(None), F.data == 'back_goal')
async def back_to_goals(callback: types.CallbackQuery):
    """
    Обработчик кнопки "Назад" для возврата к списку финансовых целей.

    Args:
        callback: Объект callback-запроса.

    Returns:
        None
    """
    # Редактирование сообщения для фин. целей с соответствующей клавиатурой
    await callback.message.edit_text('Ваши финансовые цели', reply_markup=await get_goals_all(callback.from_user.id))


@client_router.callback_query(StateFilter(None), F.data == 'К целям')
async def to_goals(callback: types.CallbackQuery):
    """
    Обработчик кнопки "К целям" для возврата к списку финансовых целей.

    Args:
        callback: Объект callback-запроса.

    Returns:
        None
    """
    # Редактирование сообщения для фин. целей с соответствующей клавиатурой
    await callback.message.edit_text('Выберите финасовую цель', reply_markup=await get_goals(callback.from_user.id))


@client_router.callback_query(StateFilter(None), F.data.startswith('add_sum_goal_'))
async def add_sum_to_goal(callback: types.CallbackQuery):
    """
    Обработчик добавления суммы к финансовой цели.

    Args:
        callback: Объект callback-запроса.

    Returns:
        None
    """
    goal_id = int(re.findall(r'\d+', callback.data)[0])

    await sqlite_db.add_goal_balance(goal_id=goal_id, new_balance=users[callback.from_user.id]['items'][0][0])

    await callback.message.answer(await about_goal_info(goal_id) +
                                  f"\n🔹 Просмотреть все цели: /goals\n"
                                  f"\n🔹 Последнее внесение: {users[callback.from_user.id]['items'][0][0]} руб.",
                                  parse_mode='html',
                                  reply_markup=InlineKeyboardMarkup(inline_keyboard=[[cancel_button]]))

    # Удаляем сообщение с кнопкой, которую нажал пользователь
    await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    # Сбрасываем флаги и данные пользователя
    users[callback.from_user.id]['in_process'] = False
    users[callback.from_user.id]['items'] = []



@client_router.message(StateFilter(None), Command('convert'))
async def convert(message: types.Message, state: FSMContext):
    """
    Обработка команды для начала конвертации валют.

    Args:
        message: Объект сообщения пользователя.

    Returns:
        None
    """
    if await check_user_process(user_in_process=users[message.from_user.id]['in_process'],
                                message_id=message.from_user.id):
        users[message.from_user.id]['in_process'] = True
        # Отправляем пользователю запрос на ввод суммы для конвертации
        await bot.send_message(message.from_user.id, 'Введите сумму для конвертации')

        # Устанавливаем состояние FSM для ввода суммы
        await state.set_state(FSMConvert.value)


@client_router.message(FSMConvert.value, F.text)
async def convert_currency(message: types.Message, state: FSMContext):
    """
    Обработка ввода суммы для конвертации и переход к выбору валюты.

    Args:
        message: Объект сообщения пользователя.
        state: Объект состояния FSM.

    Returns:
        None
    """
    if not if_numbers_filter(message):
        # В случае ошибки отправляем пользователю сообщение о необходимости ввода заново
        await message.answer(f'Что-то пошло не так. Введите положительное число, не превышающее 100.000.000.000.')
        # Устанавливаем состояние FSM для ввода даты снова
        await state.set_state(FSMConvert.value)
    else:
        # Сохраняем введенную пользователем сумму в данных, сообщения, которые потом удалим
        await state.set_data({'value': int(eval(message.text)), 'msg_id': [message.message_id + 1]})


        # Отправляем запрос пользователю на ввод пары валют
        await bot.send_message(message.from_user.id, 'Введите пару валют', reply_markup=currency_keyboard)

        # Устанавливаем состояние FSM для ввода пары валют
        await state.set_state(FSMConvert.currency)


@client_router.callback_query(StateFilter('*'), F.data == 'convert_end')
async def cancel_convert(callback: types.CallbackQuery, state: FSMContext):
    """
    Отменяет процесс конвертации валют и завершает состояние FSM.

    Args:
        callback (types.CallbackQuery): Обратный вызов, связанный с нажатием кнопки отмены.
        state (FSMContext): Контекст состояния FSM.
    """
    # Проверяем, есть ли состояние FSM
    if state is None:
        return

    # Получаем данные из состояния FSM
    data = await state.get_data()
    # Удаляем сообщения, связанные с процессом конвертации
    for i in data['msg_id']:
        await bot.delete_message(callback.from_user.id, i)

    # Завершаем состояние FSM
    await state.clear()

    users[callback.message.chat.id]['in_process'] = False

    # Отправляем сообщение о завершении конвертации
    await callback.answer('✅ Конвертация валют завершена')


@client_router.callback_query(StateFilter('*'), F.data == 'another_sum')
async def another_sum_convert(callback: types.CallbackQuery, state: FSMContext):
    """
    Обрабатывает запрос на ввод другой суммы для конвертации валюты.

    Args:
        callback (types.CallbackQuery): Обратный вызов, связанный с нажатием кнопки для ввода другой суммы.
        state (FSMContext): Контекст состояния FSM.
    """
    # Проверяем, есть ли состояние FSM
    if state is None:
        return

    # Отправляем запрос на ввод новой суммы для конвертации
    await callback.message.answer('Введите сумму для конвертации')

    # Получаем данные из состояния FSM
    data = await state.get_data()
    # Удаляем предыдущее сообщение с запросом на ввод суммы
    await bot.delete_message(callback.from_user.id, data['msg_id'][0])

    # Устанавливаем состояние FSM для ввода суммы
    await state.set_state(FSMConvert.value)


@client_router.callback_query(FSMConvert.currency)
async def convert_callback(callback: types.CallbackQuery, state: FSMContext):
    """
    Обрабатывает запрос на конвертацию валюты.

    Args:
        callback (types.CallbackQuery): Обратный вызов, связанный с нажатием кнопки конвертации.
        state (FSMContext): Контекст состояния FSM.
    """
    if callback.data != 'else_convert':
        # Разбиваем данные обратного вызова для получения валютных значений
        values = callback.data.upper().split('/')

        # Получаем данные из состояния FSM
        data = await state.get_data()
        res = "Результат конвертации:\n"
        res += str(data['value']) + " " + values[0] + " = "

        # Выполняем конвертацию с помощью внешней функции
        convert_res = convert_currency_xe(float(data['value']), values[0], values[1])
        res += str(round(convert_res, 2)) + " " + values[1]

        # Устанавливаем состояние FSM для ввода следующей пары валют
        await state.set_state(FSMConvert.currency)

        # Отправляем результат конвертации
        await callback.message.answer(f'{res}')
        await callback.answer()
    else:
        # Если выбрана опция для ввода другой пары валют, отправляем сообщение с инструкциями
        await callback.message.answer(f'Введите пару значений через /\n'
                                      f'Обозначения популярных валют:\n'
                                      f'- 🇯🇵 Японская иена: JPY\n'
                                      f'- 🇬🇧 Фунт стерлингов: GBP\n'
                                      f'- 🇨🇦 Канадский доллар: CAD\n'
                                      f'- 🇦🇺 Австралийский доллар: AUD\n'
                                      f'- 🇨🇭 Швейцарский франк: CHF\n'
                                      f'- 🇨🇳 Китайский юань: CNY\n')
        # Устанавливаем состояние FSM для ввода другой пары валют
        await state.set_state(FSMConvert.currency_else)


@client_router.message(FSMConvert.currency_else)
async def convert_else_callback(message: types.Message, state: FSMContext):
    """
    Обрабатывает запрос на конвертацию валюты с вводом другой пары валют.

    Args:
        message (types.Message): Сообщение пользователя с новой парой валют.
        state (FSMContext): Контекст состояния FSM.
    """
    try:
        # Разбиваем введенную пользователем пару валют
        values = message.text.upper().replace(' ', '').split('/')

        # Получаем данные из состояния FSM
        data = await state.get_data()
        # Добавляем идентификатор предыдущего сообщения для удаления
        data['msg_id'].append(message.message_id - 1)
        res = "Результат конвертации:\n"
        res += str(data['value']) + " " + values[0] + " = "
        # Выполняем конвертацию с помощью внешней функции
        convert_res = convert_currency_xe(float(data['value']), values[0], values[1])
        res += str(round(convert_res, 2)) + " " + values[1]

        # Устанавливаем состояние FSM для ввода следующей пары валют
        await state.set_state(FSMConvert.currency)

        # Отправляем результат конвертации
        await message.answer(f'{res}')

    except Exception:
        # В случае возникновения ошибки отправляем пользователю сообщение о необходимости ввода заново
        await message.answer(f'Что-то пошло не так. Пожалуйста, введите пару валют заново.')
        # Устанавливаем состояние FSM для ввода пары валют снова
        await state.set_state(FSMConvert.currency_else)


@client_router.callback_query(StateFilter(None), F.data == 'Добавить комментарий')
async def add_comment(callback: types.CallbackQuery, state: FSMContext):
    """
        Обработка кнопки добавления комментария

        Args:
            message: Объект сообщения пользователя.

        Returns:
            None
        """
    if await check_user_process(user_in_process=users[callback.from_user.id]['in_process'],
                                message_id=callback.from_user.id):
        users[callback.from_user.id]['in_process'] = True
        await state.set_data({'msg': callback.message, 'callback': callback})
        # Отправляем пользователю запрос на ввод комментария
        await callback.message.answer(text='💭 Введите комментарий')
        # Устанавливаем состояние FSM для ввода комментария
        await state.set_state(FSMComment.comment)


@client_router.message(FSMComment.comment, F.text)
async def add_comment_to_msg(message: types.Message, state: FSMContext):
    """
        Обработка ввода комментария и добавление его к сообщению.

        Args:
            message: Объект сообщения пользователя.
            state: Объект состояния FSM.

        Returns:
            None
        """

    # Получаем данные из состояния FSM
    data = await state.get_data()

    # Добавляем сообщение в список удаленных
    if 'del_msg_id' not in data.keys():
        await state.set_data({'del_msg_id': [message.message_id - 1, message.message_id],
                              'msg': data['msg'],
                              'callback': data['callback']})
        data['del_msg_id'] = [message.message_id - 1, message.message_id]
    else:
        data['del_msg_id'] += [message.message_id - 1, message.message_id]

    if len(str(message.text)) <= 50:
        # Формируем новый текст сообщения с комментарием
        if 'Комментарий' not in data['msg'].text:
            new_text = f"{data['msg'].text}\n\n💬 Комментарий: {message.text}"
        else:
            new_text = f"{data['msg'].text.split('Комментарий:')[0]}Комментарий: {message.text}"

        # Редактируем сообщение с новым текстом
        await bot.edit_message_text(text=new_text, chat_id=message.chat.id, message_id=data['msg'].message_id,
                                    reply_markup=data['msg'].reply_markup)

        # Удаляем сообщения
        for msg_id in data['del_msg_id']:
            await bot.delete_message(chat_id=message.chat.id, message_id=msg_id)


        await data['callback'].answer('✅ Комментарий успешно добавлен')
        # Завершаем состояние FSM
        users[message.from_user.id]['in_process'] = False
        await state.clear()
    else:
        await bot.send_message(message.chat.id, "Длина комментария не должна превышать 50 символов. Введите комментарий снова.")
        await state.set_state(FSMComment.comment)


@client_router.message(Command('report'))
async def report_cmd(message: types.Message):
    """
    Обрабатывает запрос на получение отчета по месяцам.

    Args:
        message (types.Message): Сообщение пользователя.
    """
    if await check_user_process(user_in_process=users[message.from_user.id]['in_process'],
                                message_id=message.from_user.id):
        # Получаем текущую дату и формируем строку для отчета
        date = datetime.now()
        report_month = str(date.month).zfill(2)  # Заполняем нулями, если месяц меньше 10
        report_year = str(date.year)

        # Сохраняем дату отчета в данных пользователя
        users[message.from_user.id]['report_date'] = [report_year, report_month]

        # Получаем информацию из базы данных
        result, vals, labels = await sqlite_db.get_info(message.from_user.id, users[message.from_user.id]['report_date'])

        if not vals:
            # Если информация отсутствует, отправляем сообщение об этом пользователю
            await bot.send_message(message.from_user.id, f'{result}', parse_mode='html', reply_markup=
            navigation_report_keyboard(True))
        else:
            # Если есть данные для отчета, создаем круговую диаграмму
            plt.figure(figsize=(9, 9))
            plt.pie(vals, labels=labels, autopct='%1.1f%%')
            plt.title('Расходы')

            # Сохраняем диаграмму во временный файл
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            plt.savefig(temp_file.name)
            plt.close()

            # Отправляем фото с диаграммой пользователю
            photo = FSInputFile(temp_file.name)
            await bot.send_photo(chat_id=message.from_user.id, photo=photo, caption=result,
                           reply_markup=navigation_report_keyboard(True), parse_mode='html')


@client_router.callback_query(F.data.in_({'nav_back_btn', 'cur_date', 'nav_forward_btn'}))
async def navigation_report(callback: types.CallbackQuery):
    """Навигация по отчетам по месяцам."""
    if await check_user_process(user_in_process=users[callback.from_user.id]['in_process'],
                                message_id=callback.from_user.id):
        # Обработка нажатия кнопок навигации
        if callback.data == 'nav_back_btn':
            await navigate_to_previous_month(users[callback.from_user.id])
            cur_date = False
        elif callback.data == 'cur_date':
            # Получаем текущую дату и формируем строку для отчета
            report_month = str(datetime.now().month).zfill(2)  # Заполняем нулями, если месяц меньше 10
            report_year = str(datetime.now().year)
            # Сохраняем дату отчета в данных пользователя
            users[callback.from_user.id]['report_date'] = [report_year, report_month]
            cur_date = True
        elif callback.data == 'nav_forward_btn':
            cur_date = await navigate_to_next_month(users[callback.from_user.id], datetime.now())

        # Получение отчета за текущий месяц
        result, vals, labels = await sqlite_db.get_info(callback.from_user.id, users[callback.from_user.id]['report_date'])

        if not vals:
            await handle_empty_report(callback.from_user.id, callback.message.message_id, result, bot, cur_date)
        else:
            await update_report_chart(callback, result, vals, labels, bot, cur_date)

        # Подтверждение обработки коллбэка
        await callback.answer()


@client_router.message(F.photo)
async def checkqr(message: types.Message):
    """
    Обработка QR-кода и добавление данных из чека.

    Args:
        message (types.Message): Сообщение с фотографией чека.
    """
    if await check_user_process(user_in_process=users[message.from_user.id]['in_process'],
                                message_id=message.from_user.id):
        # Получение информации о фото с чеком
        photo_info = await bot.get_file(message.photo[-1].file_id)
        photo_path = photo_info.file_path

        # Загрузка фото и декодирование
        photo = await bot.download_file(photo_path)
        photo = np.frombuffer(photo.read(), dtype=np.uint8)
        photo = cv2.imdecode(photo, cv2.IMREAD_COLOR)

        # Расшифровка QR-кода
        decoded_objects: list = pyzbar.decode(photo)

        # Обработка результатов расшифровки
        if decoded_objects and len(decoded_objects) == 1:
            # Извлечение данных из QR-кода
            qrraw = f"{str(decoded_objects[0]).split(',')[0][15:-1]}"
            try:
                pt_dict = await qrcheck(qrraw)

                receipt_date = pt_dict["data"]["json"]["dateTime"].replace('T', ' ')
                receipt_date = datetime.strptime(receipt_date, '%Y-%m-%d %H:%M:%S')

                # Проверка, есть ли чек уже в базе данных
                if await sqlite_db.receipt_in_db(receipt_date, message.from_user.id):
                    await bot.send_message(message.from_user.id, f'Вы уже внесли этот чек!')
                else:
                    # Подготовка данных пользователя для сохранения чека
                    users[message.from_user.id]['in_process'] = True
                    users[message.from_user.id]['msg_id'] = message.message_id
                    users[message.from_user.id]['date'] = receipt_date
                    users[message.from_user.id]['receipt'] = True
                    msg_to_user = ''

                    # Обработка товаров в чеке
                    for item in pt_dict["data"]["json"]["items"]:
                        users[message.from_user.id]['items'].append([int(item["sum"] / 100),''])
                        users[message.from_user.id]['check'].append([re.sub(" +", " ", item["name"]), int(item["sum"] / 100)])
                        msg_to_user += f'{re.sub(" +", " ", item["name"])}\n'

                    # Добавление общей суммы чека
                    users[message.from_user.id]['check'].append(["totalSum", int(pt_dict["data"]["json"]["totalSum"] / 100)])

                    # Отправка пользователю сообщения о выборе категории для чека
                    await bot.send_message(message.from_user.id, f'❔ Выберите категорию для чека со следующими товарами:\n\n'
                                                                 f'{msg_to_user}', reply_markup=expense_photo_categories_keyboard)
            except:
                await bot.send_message(message.from_user.id, f'Что-то пошло не так, попробуйте еще раз')
        elif len(decoded_objects) > 1:
            # Если на фото несколько чеков с QR-кодом
            await bot.send_message(message.from_user.id, '⁉️Воу-воу-воу, полегче! Давайте по одному')
        else:
            # Если QR-код не распознан
            await bot.send_message(message.from_user.id, '😕 QR-код не распознан, попробуйте еще раз')


@client_router.message(if_numbers_filter)
async def add_expense(message: types.Message):
    """
    Обработка добавления дохода/расхода.

    Args:
        message (types.Message): Сообщение с суммой дохода/расхода.
    """
    # Если не в процессе добавления
    if await check_user_process(user_in_process=users[message.from_user.id]['in_process'],
                                message_id=message.from_user.id):
        # Подготовка данных пользователя для сохранения операции
        users[message.from_user.id]['in_process'] = True
        users[message.from_user.id]['items'].append([math.ceil(eval(message.text.replace(',', '.').replace(' ', ''))), ''])
        users[message.from_user.id]['msg_id'] = message.message_id
        users[message.from_user.id]['date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        users[message.from_user.id]['receipt'] = False

        # Отправка сообщения с запросом выбора категории
        await bot.send_message(message.from_user.id, 'Выберите категорию', reply_markup=expense_categories_keyboard)


@client_router.callback_query(F.data == 'Отмена')
async def cancel_callback_query(callback: types.CallbackQuery, state: FSMContext):
    """
    Обработка отмены записи и удаление данных из БД.

    Args:
        callback (types.CallbackQuery): CallbackQuery объект.
    """
    # Если сообщение содержит информацию о времени
    if 'Время' in callback.message.text:
        # Удаление записей из базы данных
        await sqlite_db.delete_items(callback.message.message_id - 1)
        await callback.message.edit_text(callback.message.text + '\n\n🚫 Отменено!')
        await state.clear()
    elif 'Дата' in callback.message.text and 'Последнее внесение:' not in callback.message.text:
        goal_id = get_goal_id(callback.message)
        await sqlite_db.delete_goal(goal_id=goal_id)
        # Удаляем сообщение с кнопкой, которую нажал пользователь
        await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
        # Отправить пользователю информацию о целях
        await bot.send_message(callback.from_user.id, 'Ваши финансовые цели',
                               reply_markup=await get_goals_all(callback.from_user.id))
        await callback.answer('🚫 Цель удалена!')
    elif "Последнее внесение: " in callback.message.text:
        goal_id = get_goal_id(callback.message)
        last_sum = int(callback.message.text.split("Последнее внесение: ")[1].split(' руб.')[0])
        await sqlite_db.delete_last_sum(goal_id=goal_id, last_sum=last_sum)
        await callback.message.edit_text(await about_goal_info(goal_id) +
                                         f'\n\n🚫 Последнее внесение - {last_sum} руб. отменено!',
                                    parse_mode='html')

    elif 'Введите' in callback.message.text:

        # Получаем данные из состояния FSM
        data = await state.get_data()
        if 'del_msg_id' in data.keys() and data['del_msg_id']:
            for msg in data['del_msg_id']:
                await bot.delete_message(chat_id=callback.message.chat.id, message_id=msg)
            await bot.send_message(chat_id=callback.message.chat.id, text='🚫 Отменено!')
        else:
            # Отправка сообщения об отмене
            await callback.message.edit_text('🚫 Отменено!')
        # Завершаем состояние FSM
        await state.clear()

        await callback.answer()
        users[callback.from_user.id]['items'] = []
        users[callback.from_user.id]['check'] = []
        users[callback.from_user.id]['receipt'] = None
    else:
        # Отправка сообщения об отмене
        await callback.message.edit_text('🚫 Отменено!')
        await callback.answer()
        users[callback.from_user.id]['items'] = []
        users[callback.from_user.id]['check'] = []
        users[callback.from_user.id]['receipt'] = None
    # Очистка данных пользователя
    users[callback.from_user.id]['in_process'] = False


@client_router.callback_query(F.data == 'К расходам')
async def back_callback_query(callback: types.CallbackQuery):
    """
    Обработка нажатия кнопки "Назад".

    Args:
        callback (types.CallbackQuery): CallbackQuery объект.
    """
    # Редактирование сообщения для выбора категории с соответствующей клавиатурой
    await callback.message.edit_text('Выберите категорию', reply_markup=expense_categories_keyboard)


@client_router.callback_query(F.data == 'К доходам')
async def income_callback_query(callback: types.CallbackQuery):
    """
    Обработка выбора категории для дохода.

    Args:
        callback (types.CallbackQuery): CallbackQuery объект.
    """
    # Редактирование сообщения для выбора категории с соответствующей клавиатурой
    await callback.message.edit_text('Выберите категорию', reply_markup=income_categories_keyboard)


@client_router.callback_query(F.data.in_({'Еще', 'Назад'}))
async def more_expenses_callback_query(callback: types.CallbackQuery):
    """
    Обработка выбора опции "Еще" или "Назад" для категорий расходов.

    Args:
        callback (types.CallbackQuery): CallbackQuery объект.
    """
    if callback.data == 'Еще':
        # Редактирование сообщения для выбора категории с клавиатурой "Еще"
        await callback.message.edit_reply_markup(reply_markup=more_exp_categories_keyboard)
    elif callback.data == 'Назад':
        # Редактирование сообщения для выбора категории с клавиатурой "Назад"
        if 'чек' in callback.message.text:
            await callback.message.edit_reply_markup(reply_markup=expense_photo_categories_keyboard)
        else:
            await callback.message.edit_reply_markup(reply_markup=expense_categories_keyboard)


@client_router.callback_query(date_check)
async def update_button(callback: types.CallbackQuery):
    # Изменение даты
    msg_text = re.search(r'\b\d{4}-\d{2}-\d{2}\b', callback.message.text).group(0)
    if callback.data == 'day_btn':
        await callback.message.edit_reply_markup(reply_markup=await days_func(msg_text))
    elif callback.data == 'month_btn':
        await callback.message.edit_reply_markup(reply_markup=await months_func(msg_text))
    elif callback.data == 'year_btn':
        await callback.message.edit_reply_markup(reply_markup=await years_func(msg_text))
    elif callback.data in ['back_date', 'Изменить дату']:
        await callback.message.edit_reply_markup(reply_markup=await button_ex(msg_text))
    elif callback.data in [str(i) for i in range(1, 32)]:

        new_day = await sqlite_db.change_date(callback.message.message_id - 1, callback.data, 'day')

        msg1 = callback.message.text.split('Время - ')[0]
        msg2 = callback.message.text.split('Время - ')[1]
        msg2 = msg2[:8] + new_day + msg2[10:]

        await callback.message.edit_text(msg1 + 'Время - ' + msg2, reply_markup=await button_ex(msg2[:10]))
    elif callback.data in list(months.values()):
        month = list(months.keys())[list(months.values()).index(callback.data)]
        new_month = await sqlite_db.change_date(callback.message.message_id - 1, month, 'month')

        msg1 = callback.message.text.split('Время - ')[0]
        msg2 = callback.message.text.split('Время - ')[1]
        msg2 = msg2[:5] + new_month + msg2[7:]

        await callback.message.edit_text(msg1 + 'Время - ' + msg2, reply_markup=await button_ex(msg2[:10]))
    elif re.match(r'^\d{4}$', callback.data) is not None:
        new_year = await sqlite_db.change_date(callback.message.message_id - 1, callback.data, 'year')

        msg1 = callback.message.text.split('Время - ')[0]
        msg2 = callback.message.text.split('Время - ')[1]
        msg2 = new_year + msg2[4:]

        await callback.message.edit_text(msg1 + 'Время - ' + msg2, reply_markup=await button_ex(msg2[:10]))
    elif callback.data == 'Готово':
        await callback.message.edit_reply_markup(reply_markup=cancel_keyboard(users[callback.from_user.id]['receipt']))


@client_router.callback_query()
async def income_category_callback_query(callback: types.CallbackQuery):
    # Обновляем категории доходов или расходов для пользователя
    for item in users[callback.from_user.id]['items']:
        item[1] = callback.data

    # Определяем тип сообщения: доходы или расходы
    msg_index = 'расходы'
    incomes = ['Зарплата', 'Фриланс', 'Дивиденды', 'Бизнес', 'Услуги', 'Аренда', 'Депозиты', 'Крипта',
               'Переводы от людей', 'Другое']
    if callback.data[1:] in incomes:
        msg_index = 'доходы'
        await sqlite_db.add_income(users[callback.from_user.id], callback.from_user.id)
    else:
        await sqlite_db.add_expense(users[callback.from_user.id], callback.from_user.id)

    # Создаем сообщение для пользователя с результатом
    if not users[callback.from_user.id]['receipt']:
        # Если у пользователя нет чека
        await callback.message.edit_text(f'Ваши {msg_index} сохранены \n'
                                      f"Время - {users[callback.from_user.id]['date']}\n"
                                      f"{users[callback.from_user.id]['items'][0][1]} - "
                                      f"{users[callback.from_user.id]['items'][0][0]} руб.",
                                      reply_markup=cancel_keyboard(users[callback.from_user.id]['receipt']))
    else:
        # Если у пользователя есть чек
        msg_to_user = ''
        for item in users[callback.from_user.id]['check'][:-1]:
            msg_to_user += f'{item[0]} - {item[1]} руб.\n'
        await callback.message.edit_text(f'Ваши {msg_index} сохранены \n'
                                      f"Время - {users[callback.from_user.id]['date']}\n\n"
                                      f"Содержимое чека:\n"
                                      f"{msg_to_user}\n"
                                      f"{callback.data} - {users[callback.from_user.id]['check'][-1][1]} руб.", reply_markup=cancel_keyboard(users[callback.from_user.id]['receipt']))
        # await callback.message.answer(f'Ваши {msg_index} сохранены \n'
        #                               f"Время - {users[callback.from_user.id]['date']}\n\n"
        #                               f"Содержимое чека:\n"
        #                               f"{msg_to_user}\n"
        #                               f"{callback.data} - {users[callback.from_user.id]['check'][-1][1]} руб.", reply_markup=cancel_keyboard(users[callback.from_user.id]['receipt']))
        users[callback.from_user.id]['check'] = []

    # Удаляем сообщение с кнопкой, которую нажал пользователь
    # await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    # Сбрасываем флаги и данные пользователя
    users[callback.from_user.id]['in_process'] = False
    users[callback.from_user.id]['items'] = []
    users[callback.from_user.id]['receipt'] = None




