from datetime import datetime
import sqlite3 as sq


# Подключение к базе данных
base = sq.connect('firstfin.db')
cur = base.cursor()


async def sql_start():
    """
        Создает таблицы расходов и доходов, целей и пользователей, если они не существуют.
    """
    if base:
        print('Database connected OKI')

    # Создание таблицы пользователи, если она не существует
    cur.execute('''CREATE TABLE IF NOT EXISTS users ( 
                        user_id INTEGER PRIMARY KEY,
                        name TEXT 
                        )''')

    # Создание таблицы цели, если она не существует
    cur.execute('''CREATE TABLE IF NOT EXISTS goals (
                        goal_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        name TEXT,
                        balance INTEGER,
                        summ INTEGER,
                        date TEXT,
                        FOREIGN KEY(user_id) REFERENCES users(user_id))''')

    # Создание таблицы расходов, если она не существует
    cur.execute('''CREATE TABLE IF NOT EXISTS expenses (
                    msg_id INTEGER, 
                    user_id INTEGER,
                    date TEXT, 
                    category TEXT, 
                    value INTEGER, 
                    receipt BOOLEAN,
                    FOREIGN KEY(user_id) REFERENCES users(user_id))''')

    # Создание таблицы доходов, если она не существует
    cur.execute('''CREATE TABLE IF NOT EXISTS incomes (
                    msg_id INTEGER, 
                    user_id INTEGER,
                    date TEXT, 
                    category TEXT, 
                    value INTEGER,
                    FOREIGN KEY(user_id) REFERENCES users(user_id))''')

    base.commit()


async def add_user(user_id: int, name: str):
    """
    Функция для добавления пользователя в базу данных, если его еще нет там.

    Args:
        user_id (int): Идентификатор пользователя.
        name (str): Имя пользователя.

    Returns:
        None
    """
    # Если пользователя нет в БД, то добавляем его
    if not cur.execute('''SELECT * FROM users 
                                      WHERE user_id = ?''', (user_id,)).fetchone():
        cur.execute('''INSERT INTO users
                                    VALUES (?, ?)''',
                    (user_id, name))
        print(f'{name} подключился!')
        base.commit()


async def add_expense(data: dict, user_id: int):
    """
        Добавляет информацию о расходах в базу данных.

        Args:
            data (dict): Информация о расходах.
            user_id (int): Идентификатор пользователя.
    """
    for item in data['items']:
        cur.execute('''INSERT INTO expenses 
                        VALUES (?, ?, ?, ?, ?, ?)''',
                    (data['msg_id'], user_id, data['date'], item[1], item[0], data['receipt']))
        base.commit()


async def add_income(data, user_id):
    """
        Добавляет информацию о доходах в базу данных.

        Args:
            data (dict): Информация о доходах.
            user_id (int): Идентификатор пользователя.
        """
    for item in data['items']:
        cur.execute('''INSERT INTO incomes 
                        VALUES (?, ?, ?, ?, ?)''',
                    (data['msg_id'], user_id, data['date'], item[1], item[0]))
        base.commit()


async def get_user_goals(user_id: int):
    """
    Функция для получения списка финансовых целей пользователя.

    Args:
        user_id (int): Идентификатор пользователя.

    Returns:
        list: Список финансовых целей пользователя.
    """
    goals = []
    for goal_id, name, balance, summ, date in cur.execute("""SELECT goal_id, name, balance, summ, date 
    FROM goals
    WHERE user_id = ?""", (user_id,)).fetchall():
        goals.append([goal_id, name, balance, summ, date])
    return goals


async def about_goal(goal_id: int):
    """
    Функция для получения информации о финансовой цели.

    Args:
        goal_id (int): Идентификатор финансовой цели.

    Returns:
        tuple: Информация о финансовой цели (goal_id, name, balance, summ, date).
    """
    goal_info = cur.execute("""SELECT goal_id, name, balance, summ, date 
    FROM goals
    WHERE goal_id = ?""", (goal_id,)).fetchone()
    return goal_info


async def add_goal_in_db(user_id: int, name: str, summ: int, date: str):
    """
    Функция для добавления финансовой цели в базу данных.

    Args:
        user_id (int): Идентификатор пользователя.
        name (str): Название финансовой цели.
        summ (int): Сумма финансовой цели.
        date (str): Дата завершения финансовой цели в формате 'YYYY-MM-DD'.

    Returns:
        None
    """
    cur.execute('''INSERT INTO goals (user_id, name, balance, summ, date)
                    VALUES (?, ?, 0, ?, ?)''',
                (user_id, name, summ, date))
    base.commit()


async def receipt_in_db(datetm, user_id):
    """
        Проверяет наличие чека в базе данных.

        Args:
            datetm (str): Дата и время.
            user_id (int): Идентификатор пользователя.

        Returns:
            tuple or None: Запись о чеке в формате кортежа или None, если чек не найден.
        """
    # Проверяем наличие чека в таблице расходов
    receipt_expenses = cur.execute('''SELECT * FROM expenses 
                                      WHERE strftime('%Y-%m-%d %H:%M:%S', ?) = strftime('%Y-%m-%d %H:%M:%S', date) 
                                      AND user_id = ?''', (datetm, user_id)).fetchone()

    # Проверяем наличие чека в таблице доходов
    receipt_incomes = cur.execute('''SELECT * FROM incomes 
                                     WHERE strftime('%Y-%m-%d %H:%M:%S', ?) = strftime('%Y-%m-%d %H:%M:%S', date) 
                                     AND user_id = ?''', (datetm, user_id)).fetchone()

    # Возвращаем результат
    return receipt_expenses or receipt_incomes


async def delete_items(msg_id: int):
    """
        Удаляет записи из базы данных.

        Args:
            msg_id (int): Идентификатор сообщения.
        """
    # Удаляем записи из таблицы расходов по идентификатору сообщения
    cur.execute("DELETE FROM expenses WHERE msg_id = ?", (msg_id,))

    # Удаляем записи из таблицы доходов по идентификатору сообщения
    cur.execute("DELETE FROM incomes WHERE msg_id = ?", (msg_id,))

    base.commit()


async def delete_goal(goal_id: int):
    # Удаляем записи из таблицы цели по идентификатору цели
    cur.execute("DELETE FROM goals WHERE goal_id = ?", (goal_id,))

    base.commit()


async def change_goal(goal_id: int, new_value: int, part: str):
    """
    Функция для изменения значений финансовой цели.

    Args:
        goal_id (int): Идентификатор финансовой цели.
        new_value (int): Новое значение цели (сумма или дата в зависимости от 'part').
        part (str): Часть финансовой цели, которую необходимо изменить ('sum' или 'date').

    Returns:
        None
    """
    if part == 'sum':
        cur.execute("""UPDATE goals
                               SET summ = ? 
                               WHERE goal_id = ?""", (new_value, goal_id))

        base.commit()
    elif part == 'date':

        cur.execute("""UPDATE goals
                                       SET date = ? 
                                       WHERE goal_id = ?""", (new_value, goal_id))

        base.commit()


async def get_ended_goals(cur_date):
    """
    Функция для получения списка завершенных финансовых целей на текущую дату.

    Args:
        cur_date: Текущая дата.

    Returns:
        list: Список завершенных финансовых целей.
    """
    ended_goals = []

    for goal_id, user_id, name, balance, summ in cur.execute("""
            SELECT goal_id, user_id, name, balance, summ 
            FROM goals
            WHERE strftime('%Y-%m-%d', date) = ? or balance >= summ""", (cur_date,)).fetchall():
        percent = (balance / summ) * 100
        if balance < summ:
            text = f"Уважаемый пользователь,\n" \
                   f"К сожалению, вы не достигли своей финансовой цели \"{name}\" в ожидаемый срок. \n" \
                   f"Ваш текущий баланс составляет {balance} руб. из необходимых {summ:,} руб. ({percent:.2f}%). \n" \
                   f"Не расстраивайтесь! Вы можете продолжить свои усилия или пересмотреть свои финансовые планы. \n" \
                   f"Просмотреть цели: /goals"
        else:
            text = f"Уважаемый пользователь,\n" \
                   f"Поздравляем! Вы успешно достигли своей финансовой цели \"{name}\". \n" \
                   f"Ваш текущий баланс составляет {balance} руб. из необходимых {summ:,} руб. ({percent:.2f}%). \n" \
                   f"Отличная работа! Не забудьте отметить свой успех и, возможно, установить новую финансовую цель.\n" \
                   f"Просмотреть цели: /goals"
        await delete_goal(goal_id)
        ended_goals.append([user_id, text])
    return ended_goals


async def add_goal_balance(goal_id: int, new_balance: int):
    """
    Функция для добавления нового баланса к финансовой цели.

    Args:
        goal_id (int): Идентификатор финансовой цели.
        new_balance (int): Новое значение баланса.

    Returns:
        None
    """
    cur.execute("""UPDATE goals
                           SET balance = balance + ? 
                           WHERE goal_id = ?""", (new_balance, goal_id))
    base.commit()


async def delete_last_sum(goal_id: int, last_sum: int):
    """
    Функция для удаления последней суммы из баланса финансовой цели.

    Args:
        goal_id (int): Идентификатор финансовой цели.
        last_sum (int): Последняя сумма.

    Returns:
        None
    """
    cur.execute("""UPDATE goals
                               SET balance = balance - ? 
                               WHERE goal_id = ?""", (last_sum, goal_id))
    base.commit()


async def get_info(user_id, date: datetime):
    """
        Возвращает отчет о расходах и доходах за указанный месяц.

        Args:
            user_id (int): Идентификатор пользователя.
            date (datetime): Дата в формате datetime, представляющая месяц отчета.

        Returns:
            Tuple[str, List[float], List[str]]: Кортеж, содержащий текст отчета, список значений для графика расходов и список меток категорий.
        """
    # Список месяцев для отображения в отчете
    months: list[str] = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь",
              "Декабрь"]

    # Остаток
    balance: int = 0

    # Создаем заголовок отчета
    result: str = f'<b>Ваш отчет за {months[int(date[1]) - 1]} {date[0]}</b>\n'
    result += f'<b>📉 Расходы</b>\n'

    # Получаем общую сумму расходов за указанный месяц
    total_expenses = cur.execute("""SELECT sum(value) FROM expenses 
                                    WHERE '{date_year}-{date_month}' = strftime('%Y-%m', date) 
                                    AND user_id = {user_id}""".format(date_year=date[0], date_month=date[1], user_id=user_id)).fetchone()[0]

    # Создаем списки для хранения значений и меток категорий расходов
    vals_expenses: list[float] = []
    labels_expenses: list[str] = []

    # Получаем данные о категориях расходов и их сумме за указанный месяц
    for category, value in cur.execute("""SELECT category, sum(value) from expenses
    where '{date_year}-{date_month}' = strftime('%Y-%m', date) AND user_id = {user_id}
    group by category
    order by sum(value) DESC""".format(date_year=date[0], date_month=date[1], user_id=user_id)).fetchall():

        # Добавляем информацию о каждой категории расходов в результат
        percent = round(value / total_expenses * 100, 1)
        result += f'{category} - {value} руб. ({percent} %)\n'

        # Добавляем значение и метку категории в соответствующие списки
        vals_expenses.append(percent)
        labels_expenses.append(category[1:])

    # Добавляем разделитель и общую сумму расходов в отчет
    result += '---\n'
    result += f'<i>Итого: {total_expenses or 0} руб.</i> \n\n'
    balance -= total_expenses or 0

    # Добавляем разделитель и заголовок для доходов
    result += '<b>📈 Доходы </b>\n'

    # Получаем общую сумму доходов за указанный месяц
    total_incomes = cur.execute("""SELECT sum(value) from incomes 
        where '{date_year}-{date_month}' = strftime('%Y-%m', date) AND user_id = {user_id}""".format(date_year=date[0],
                                                                                                     date_month=date[1],
                                                                                                     user_id=user_id)).fetchone()[0]

    for category, value in cur.execute("""SELECT category, sum(value) 
    from incomes
    where '{date_year}-{date_month}' = strftime('%Y-%m', date) AND user_id = {user_id}
    group by category
    order by sum(value) DESC""".format(date_year=date[0], date_month=date[1], user_id=user_id)).fetchall():
        # Добавляем информацию о каждой категории доходов в результат
        percent = round(value / total_incomes * 100, 1)
        result += f'{category} - {value} руб. ({percent} %)\n'

    # Добавляем разделитель и общую сумму доходов в отчет
    result += '---\n'
    result += f'<i>Итого: {total_incomes or 0} руб.</i> \n\n'
    balance += total_incomes or 0

    if balance > 0:
        result += f'В этом месяце ваши доходы превышают расходы на {balance} руб.'
    elif balance < 0:
        result += f'К сожалению, в этом месяце ваши расходы превышают доходы на {-balance} руб.'
    else:
        result += 'В этом месяце ваши доходы и расходы совпадают.'

    # Возвращаем результат и списки значений и меток для графика расходов
    return result, vals_expenses[::-1], labels_expenses[::-1]


async def change_date(msg_id, new_date, part):
    """
        Изменяет определенную часть даты в записях о расходах и доходах.

        Args:
            msg_id (int): Идентификатор сообщения.
            new_date (str): Новое значение для части даты.
            part (str): Часть даты, которую необходимо изменить ('day', 'month' или 'year').

        Returns:
            str: Новое значение части даты.
        """
    if part == 'day':
        # Добавляем ведущий ноль, если число меньше 10
        new_date = new_date.zfill(2)
        # Обновляем день в дате для расходов
        cur.execute("""UPDATE incomes 
                       SET date = substr(date, 1, 8) || ? || substr(date, 11) 
                       WHERE msg_id = ?""", (new_date, msg_id))
        # Обновляем день в дате для доходов
        cur.execute("""UPDATE expenses 
                       SET date = substr(date, 1, 8) || ? || substr(date, 11) 
                       WHERE msg_id = ?""", (new_date, msg_id))
    elif part == 'month':
        # Обновляем месяц в дате для расходов
        cur.execute("""UPDATE incomes 
                       SET date = substr(date, 1, 5) || ? || substr(date, 8) 
                       WHERE msg_id = ?""", (new_date, msg_id))
        # Обновляем месяц в дате для доходов
        cur.execute("""UPDATE expenses 
                       SET date = substr(date, 1, 5) || ? || substr(date, 8) 
                       WHERE msg_id = ?""", (new_date, msg_id))
    elif part == 'year':
        # Обновляем год в дате для расходов
        cur.execute("""UPDATE incomes 
                       SET date = ? || substr(date, 5) 
                       WHERE msg_id = ?""", (new_date, msg_id))
        # Обновляем год в дате для доходов
        cur.execute("""UPDATE expenses 
                       SET date = ? || substr(date, 5) 
                       WHERE msg_id = ?""", (new_date, msg_id))

    base.commit()

    return new_date


async def get_inactive_users_today(cur_date: datetime):
    """
    Получает список пользователей, которые сегодня не совершали ни одной операции (ни расходов, ни доходов).

    Args:
        cur_date (datetime): Текущая дата.

    Returns:
        list: Список идентификаторов неактивных пользователей.
    """
    users: list = []

    # Форматируем месяц и день для запроса в базу данных
    month = str(cur_date.month).zfill(2)
    day = str(cur_date.day).zfill(2)

    # Поиск пользователей, которые не совершали расходы сегодня
    for ret in cur.execute("""SELECT DISTINCT user_id 
        FROM expenses
        WHERE user_id NOT IN (
        SELECT user_id 
        FROM expenses 
        WHERE strftime('%Y-%m-%d', date) = '{date_year}-{date_month}-{date_day}'
        )""".format(date_year=str(cur_date.year), date_month=month, date_day=day)).fetchall():
        users.append(ret[0])

    # Поиск пользователей, которые не совершали доходы сегодня
    for ret in cur.execute("""SELECT DISTINCT user_id 
        FROM incomes
        WHERE user_id NOT IN (
        SELECT user_id 
        FROM expenses 
        WHERE strftime('%Y-%m-%d', date) = '{date_year}-{date_month}-{date_day}'
        )""".format(date_year=str(cur_date.year), date_month=month, date_day=day)).fetchall():
        users.append(ret[0])

    base.commit()

    return list(set(users))

