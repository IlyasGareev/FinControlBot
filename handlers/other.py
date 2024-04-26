from aiogram import types, Router
from aiogram.filters import StateFilter

# Роутер для прочего
other_router = Router()


# Функция для обработки неизвестных сообщений
@other_router.message(StateFilter(None))
async def answer(message: types.Message):
    await message.reply('Извините, я не могу обработать вашу команду. '
                        'Пожалуйста, проверьте правильность введенных данных и попробуйте еще раз.\n'
                        'Ознакомиться с информацией о боте - /help.')


