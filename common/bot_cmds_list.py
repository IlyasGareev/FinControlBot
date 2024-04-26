from aiogram.types import BotCommand

# Определение списка команд
private = [
    BotCommand(command='start', description='Стартуем!'),
    BotCommand(command='goals', description='Цели'),
    BotCommand(command='report', description='Вывод отчета'),
    BotCommand(command='kurs', description='Курс валют'),
    BotCommand(command='convert', description='Конвертация валют'),
    BotCommand(command='advice', description='Советы'),
    BotCommand(command='help', description='Помощь')
]