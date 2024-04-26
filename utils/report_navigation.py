import tempfile
from aiogram import types
from aiogram.types import FSInputFile
from keyboards.client_kb import navigation_report_keyboard


# Функция для навигации назад по отчетам
async def navigate_to_previous_month(user_id):
    current_year, current_month = user_id['report_date']
    new_month = str(int(current_month) - 1).zfill(2) if current_month != '01' else '12'
    new_year = str(int(current_year) - 1) if current_month == '01' else current_year
    user_id['report_date'] = new_year, new_month
    return False


# Функция для навигации вперед по отчетам
async def navigate_to_next_month(user_id, cur_date):
    current_year, current_month = user_id['report_date']
    new_month = str(int(current_month) + 1).zfill(2) if current_month != '12' else '01'
    new_year = str(int(current_year) + 1) if current_month == '12' else current_year
    user_id['report_date'] = new_year, new_month
    return True if new_month == str(cur_date.month).zfill(2) and new_year == str(cur_date.year) else False



# Функция для обновления отчета по месяцам
async def update_report_chart(callback: types.CallbackQuery, result, vals, labels, bot_instance, cur_date):
    import matplotlib.pyplot as plt

    plt.figure(figsize=(8, 8))
    plt.pie(vals, labels=labels, autopct='%1.1f%%')
    plt.title('Расходы')

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
    plt.savefig(temp_file.name)
    plt.close()

    photo = FSInputFile(temp_file.name)
    if callback.message.content_type == 'photo':
        await callback.message.edit_media(types.InputMediaPhoto(media=photo))
        await callback.message.edit_caption(caption=result, parse_mode='html',
                                            reply_markup=navigation_report_keyboard(cur_date))
    else:
        await bot_instance.delete_message(callback.from_user.id, callback.message.message_id)
        await bot_instance.send_photo(chat_id=callback.from_user.id, photo=photo, caption=result,
                                 reply_markup=navigation_report_keyboard(cur_date), parse_mode='html')


# Функция для обработки пустого отчета
async def handle_empty_report(user_id, message_id, result, bot_instance, cur_date):
    await bot_instance.delete_message(user_id, message_id)
    await bot_instance.send_message(user_id, result, parse_mode='html', reply_markup=navigation_report_keyboard(cur_date))
