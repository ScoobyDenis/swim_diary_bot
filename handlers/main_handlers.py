from aiogram.fsm.context import FSMContext
from aiogram import F
from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.types import CallbackQuery
from aiogram.fsm.state import StatesGroup, State, default_state
from my_functions.my_functions import *
import logging

config: Config = load_config()
bot = Bot(token=config.tg_bot.token)
router = Router()


# machine state for registration
class FSMRegistr(StatesGroup):
    name = State()
    surname = State()
    date = State()
    time = State()
    choose_child = State()

# start handler
@router.message(Command("start"))
async def cmd_start(message: types.Message):
    connect, cursor = connect_db(DB_NAME1)
    cursor.execute(f"SELECT * FROM users WHERE user_id = {message.from_user.id}")
    user1 = cursor.fetchone()
    connect, cursor = connect_db(DB_NAME2)
    cursor.execute(f"SELECT * FROM parents WHERE user_id = {message.from_user.id}")
    user2 = cursor.fetchone()
    if user1:
        await message.answer("Посмотреть свои результаты")
    elif user2:
        await message.answer("Чтобы записать  своего пловца\n"
                             "на тренировку нажмите /registr")
    else:
        await message.answer("Добро пожаловать!\n"
                             "чтобы зарегистрироваться\n"
                             "нажмите /fillform")

# admin resistration
@router.message(Command('admins_registr'))
async def add_info_from_admin(message: types.Message):
    kb = await create_date_keyboard(mode='admin')
    await message.answer("Выберите дату", reply_markup=kb)

# registration
@router.message(Command('registr'))
async def schedule_register(message: types.Message):
    connect, cursor = connect_db(DB_NAME2)
    cursor.execute("SELECT user_id FROM parents")
    data = cursor.fetchall()
    new_data = await reform_array(data)
    if message.from_user.id in new_data:
        kb = await create_date_keyboard(mode='parent')
    elif message.from_user.id == ADMIN:
        kb = await create_date_keyboard(mode='admin')
    else:
        if await check_age(message.from_user.id):
            kb = await create_date_keyboard(mode='swimmer')
        else:
            await message.answer("Попросите записать вас у родителя")
    try:
        await message.answer("Выберите дату", reply_markup=kb)
    except Exception as e:
        logging.error(f"Произошла ошибка: {e}")

# create keyboard with free times for swimmer
@router.callback_query(F.data.startswith('createdateswimmer_'))
async def process_button_admin_press(callback: CallbackQuery):
    message = callback.message
    kb = await create_time_keyboard(message, callback.data[18:], mode='swimmer')
    await callback.message.edit_text("Выберите время", reply_markup=kb)

# create keyboard with free times for admin
@router.callback_query(F.data.startswith('createdateadmin_'))
async def process_button_admin_press(callback: CallbackQuery):
    message = callback.message
    kb = await create_time_keyboard(message, callback.data[16:], mode='admin')
    await callback.message.edit_text("Выберите время", reply_markup=kb)

# create keyboard with free times for parent
@router.callback_query(F.data.startswith('createdateparent_'))
async def process_button_parent_press(callback: CallbackQuery):
    message = callback.message
    kb = await create_time_keyboard(message, callback.data[17:], mode='parent')
    await callback.message.edit_text("Выберите время", reply_markup=kb)

# enter date, time to csv file
@router.callback_query(F.data.startswith('adds_swimmer_'))
async def process_time_button_1_press(callback: CallbackQuery):
    date = callback.data.split('_')[2]
    time = callback.data.split('_')[3]
    DF.loc[date, time] = await get_name_surname_from_db(callback.from_user.id)
    DF.to_csv('files/swim_schedule.csv')
    await callback.message.answer(f"Вы записаны {date} числа на {time}\n"
                                  f"Тренер напишет вам, чтобы подтвердить запись\n\n"
                                  f"<em>Отменяйте запись не позднее чем за 24 часа до тренировки</em>", parse_mode="html")
    await msg_to_admin(f"Записались на {date} число в {time}")
    await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)

# admin chooses who to put on the schedule
@router.callback_query(F.data.startswith('adds_admin'), StateFilter(default_state))
async def process_add_admin_pressed(callback: CallbackQuery, state: FSMContext):
    await state.update_data(date=callback.data.split('_')[2])
    await state.update_data(time=callback.data.split('_')[3])
    connect, cursor = connect_db(DB_NAME1)
    cursor.execute(f"SELECT swimmer_name, swimmer_surname FROM users")
    data = cursor.fetchall()
    inline_kb = []
    for i in data:
        inline_kb.append([InlineKeyboardButton(text=i[0]+' '+i[1], callback_data='swimmers_'+i[0]+'_'+i[1])])
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=inline_kb
    )
    await callback.message.answer("Выберите кого записать", reply_markup=keyboard)
    await state.set_state(FSMRegistr.choose_child)

# process add swimmer from parent
@router.callback_query(F.data.startswith('adds_parent'), StateFilter(default_state))
async def process_add_parent_pressed(callback: CallbackQuery, state: FSMContext):
    date = callback.data.split('_')[2]
    time = callback.data.split('_')[3]
    await state.update_data(date=date)
    await state.update_data(time=time)
    try:
        connect, cursor = connect_db(DB_NAME2)
        cursor.execute(f"SELECT children FROM parents WHERE user_id = {callback.from_user.id}")
        children = cursor.fetchone()[0].split('_')
        if len(children) == 1:
            connect, cursor = connect_db(DB_NAME1)
            cursor.execute(f"SELECT swimmer_name, swimmer_surname FROM users WHERE user_id = {int(children[0])}")
            data = cursor.fetchone()
            DF.loc[date, time] = data[0] + ' ' + data[1]
            DF.to_csv('files/swim_schedule.csv')
            await callback.message.answer(f"{data[0]} {data[1]} записана(а) {date} на {time}\n"
                                          f"Тренер напишет вам, чтобы подтвердить запись\n\n"
                                          f"<em>Отменяйте запись не позднее чем за 24 часа до тренировки</em>", parse_mode="html")
            await msg_to_admin(f"{data[0]} {data[1]} записана(а) {date} на {time}")
            await state.clear()
        else:
            inline_kb = []
            connect, cursor = connect_db(DB_NAME1)
            for id in children:
                cursor.execute(f"SELECT swimmer_name, swimmer_surname FROM users WHERE user_id = {int(id)}")
                data = cursor.fetchone()
                inline_kb.append([InlineKeyboardButton(text=data[0]+' ' + data[1], callback_data='children_'+data[0]+'_'+data[1])])
                keyboard = InlineKeyboardMarkup(
                    inline_keyboard=inline_kb
                )
            await callback.message.answer("Выберите кого записать", reply_markup=keyboard)
            await state.set_state(FSMRegistr.choose_child)
    except:
        await callback.message.answer("Либо Ваш ребенок еще не зарегистрировался, либо тренер не прикрепил его к Вам")

# enter date, time to csv file from admin
@router.callback_query(F.data.startswith('swimmers_'), StateFilter(FSMRegistr.choose_child))
async def process_registr_by_admin(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    name = callback.data.split('_')[1]
    surname = callback.data.split('_')[-1]
    date = data['date']
    time = data['time']
    DF.loc[date, time] = name + ' ' + surname
    DF.to_csv('files/swim_schedule.csv')
    await callback.message.answer(f"{name} {surname} записан(а) {date} на {time}")
    await state.clear()

# enter date, time to csv file from parent
@router.callback_query(F.data.startswith('children_'), StateFilter(FSMRegistr.choose_child))
async def process_children_choice(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    name = callback.data.split('_')[1]
    surname = callback.data.split('_')[2]
    date = data['date']
    time = data['time']
    DF.loc[date, time] = name + ' ' + surname
    DF.to_csv('files/swim_schedule.csv')
    await callback.message.answer(f"{name} {surname} записан(а) {date} на {time}")
    await msg_to_admin(f"{name} {surname} записана(а) {date} на {time}")
    await state.clear()




