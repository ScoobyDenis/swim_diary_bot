from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State, default_state
from aiogram.filters import Command, StateFilter
from aiogram import F
from aiogram import Router
from aiogram.types import Message, CallbackQuery, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from my_functions.my_functions import *
from aiogram.types import InlineKeyboardButton

router = Router()

# state machine for fillform
class FSMFillForm(StatesGroup):
    fill_role = State()
    fill_name_parent = State()
    fill_surname_parent = State()
    fill_name_swimmer = State()
    fill_surname_swimmer = State()
    fill_year_swimmer = State()
    fill_day_swimmer = State()
    fill_month_swimmer = State()

# registration new users
@router.message(Command('fillform'), StateFilter(default_state))
async def process_fillform_command(message: Message, state: FSMContext):
    if (not await check_id_in_parents(message.from_user.id) or not await check_id_in_users(message.from_user.id)) and message.from_user.id != ADMIN:
        await message.answer("Вы уже зарегистрированы")
    else:
        builder = InlineKeyboardBuilder()
        builder.add(InlineKeyboardButton(text="👨‍🍼 Родитель", callback_data="parent"))
        builder.add(InlineKeyboardButton(text="🏊 Пловец", callback_data="swimmer"))
        await message.answer(text='Выберите, пожалуйста, родитель вы или пловец', reply_markup=builder.as_markup())
        await state.set_state(FSMFillForm.fill_role)

# filter for parent registr
@router.callback_query(F.data == 'parent', StateFilter(FSMFillForm.fill_role))
async def process_role_parent_sent(callback: CallbackQuery, state: FSMContext):
    await state.update_data(role=callback.data)
    await create_new_parent(callback.from_user.id)
    await callback.message.edit_text(text='Пожалуйста, введите ваше имя')
    await state.set_state(FSMFillForm.fill_name_parent)

# save parent name and ask surname
@router.message(StateFilter(FSMFillForm.fill_name_parent), F.text.isalpha())
async def process_name_parent_sent(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    connect, cursor = connect_db(DB_NAME2)
    cursor.execute(f"UPDATE parents SET parent_name = '{message.text}' WHERE user_id = {message.from_user.id}")
    connect.commit()
    await message.answer(text='Спасибо!\n\nА теперь введите фамилию')
    await state.set_state(FSMFillForm.fill_surname_parent)

# end registr parent
@router.message(StateFilter(FSMFillForm.fill_surname_parent),  F.text.isalpha())
async def process_surname_parent_sent(message: Message, state: FSMContext):
    await state.update_data(surname=message.text)
    connect, cursor = connect_db(DB_NAME2)
    cursor.execute(f"UPDATE parents SET parent_surname = '{message.text}' WHERE user_id = {message.from_user.id}")
    connect.commit()
    await message.answer("Отлично, Вы зарегистрированы!✅\n"
                         "Меню там↙️")
    await msg_to_admin(f"Родитель {message.text} зарегистрирован")
    await state.clear()

# filter for swimmer registr
@router.callback_query(F.data=='swimmer', StateFilter(FSMFillForm.fill_role))
async def process_role_swimmer_sent(callback: CallbackQuery, state: FSMContext):
    await state.update_data(role=callback.data)
    if callback.from_user.id != ADMIN:
        id = callback.from_user.id
        username = callback.from_user.username
        await create_new_swimmer(id, username)
        await create_new_leaderboard_user(id)
    await callback.message.edit_text(text='Пожалуйста, введите ваше имя')
    await state.set_state(FSMFillForm.fill_name_swimmer)

# save swimmer name and ask surname
@router.message(StateFilter(FSMFillForm.fill_name_swimmer), F.text.isalpha())
async def process_name_swimmer_sent(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    id = await get_id_from_txt()
    name = message.text
    if message.from_user.id == ADMIN:
        await create_new_swimmer(id, name)
        await create_new_leaderboard_user(id)
        await set_swimmer_name_to_users(name, id)
        await set_swimmer_name_to_results(name, id)
        await set_swimmer_name_to_leaderboard(name, id)
    else:
        if not await check_id_in_users(message.from_user.id):
            connect, cursor = connect_db(DB_NAME2)
            cursor.execute(f"UPDATE parents SET parent_name = '{message.text}' WHERE user_id = {message.from_user.id}")
            connect.commit()
        await set_swimmer_name_to_users(name, message.from_user.id)
        await set_swimmer_name_to_results(name, message.from_user.id)
        await set_swimmer_name_to_leaderboard(name, message.from_user.id)
    await message.answer(text='Спасибо!\n\nА теперь введите фамилию')
    await state.set_state(FSMFillForm.fill_surname_swimmer)

# save swimmer surname and ask year
@router.message(StateFilter(FSMFillForm.fill_surname_swimmer),  F.text.isalpha())
async def process_surname_swimmer__sent(message: Message, state: FSMContext):
    await state.update_data(surname=message.text)
    surname = message.text
    if message.from_user.id == ADMIN:
        id = await get_id_from_txt()
        await set_swimmer_surname_to_users(surname, id)
        await set_swimmer_surname_to_leaderboard(surname, id)
    else:
        id = message.from_user.id
        if not await check_id_in_users(message.from_user.id):
            connect, cursor = connect_db(DB_NAME2)
            cursor.execute(
                f"UPDATE parents SET parent_surname = '{message.text}' WHERE user_id = {id}")
            connect.commit()
        await set_swimmer_surname_to_users(surname, id)
        await set_swimmer_surname_to_leaderboard(surname, id)
    await message.answer("А теперь введите ваш год рождения(например, <b>2010</b>)", parse_mode="html")
    await state.set_state(FSMFillForm.fill_year_swimmer)

# save swimmer year and ask month
@router.message(StateFilter(FSMFillForm.fill_year_swimmer),  F.text.isdigit())
async def process_year_swimmer_sent(message: Message, state: FSMContext):
    if 1950 <= int(message.text) <= 2024:
        await state.update_data(year=message.text)
        connect, cursor = connect_db(DB_NAME1)
        if message.from_user.id == ADMIN:
            id = await get_id_from_txt()
            cursor.execute(f"UPDATE users SET year = '{message.text}' WHERE user_id = {id}")
        else:
            cursor.execute(f"UPDATE users SET year = '{message.text}' WHERE user_id = {message.from_user.id}")
        connect.commit()
        buttons = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']
        kb = ReplyKeyboardBuilder()
        for month in buttons:
            kb.add(KeyboardButton(text=month))
        kb.adjust(4)
        await message.answer("Выберите месяц рождения", reply_markup=kb.as_markup(resize_keyboard=True))
        await state.set_state(FSMFillForm.fill_month_swimmer)
    else:
        await message.answer("Введите корректный год рождения")

# save month and ask swimmer day
@router.message(StateFilter(FSMFillForm.fill_month_swimmer))
async def process_month_swimmer(message: Message, state: FSMContext):
        await state.update_data(month=message.text)
        connect, cursor = connect_db(DB_NAME1)
        if message.from_user.id == ADMIN:
            id = await get_id_from_txt()
            cursor.execute(f"UPDATE users SET month = '{message.text}' WHERE user_id = {id}")
        else:
            cursor.execute(f"UPDATE users SET month = '{message.text}' WHERE user_id = {message.from_user.id}")
        connect.commit()
        kb = ReplyKeyboardBuilder()
        for i in range(1, 32):
            kb.add(KeyboardButton(text=str(i)))
        kb.adjust(5)
        await message.answer("Выберите день рождения", reply_markup=kb.as_markup())
        await state.set_state(FSMFillForm.fill_day_swimmer)

# end swimmer's registr
@router.message(StateFilter(FSMFillForm.fill_day_swimmer))
async def process_day_swimmer(message: Message, state: FSMContext):
    await state.update_data(day=message.text)
    connect, cursor = connect_db(DB_NAME1)
    if message.from_user.id == ADMIN:
        id = await get_id_from_txt()
        cursor.execute(f"UPDATE users SET day = '{message.text}' WHERE user_id = {id}")
        with open('files/id.txt', 'w') as file:
            file.write(str(id + 1))
    else:
        cursor.execute(f"UPDATE users SET day = '{message.text}' WHERE user_id = {message.from_user.id}")
    connect.commit()
    await message.answer("Отлично, Вы зарегистрированы!✅\nМеню там↙️", reply_markup=ReplyKeyboardRemove())
    await msg_to_admin(f"Пловец {message.from_user.id} зарегистрирован")
    await state.clear()

# check correct swimmer name
@router.message(StateFilter(FSMFillForm.fill_name_swimmer))
async def warning_not_name_swimmer(message: Message):
    await message.answer(
        text='То, что вы отправили не похоже на имя\n\n'
             'Пожалуйста, введите ваше имя\n\n')

# check correct parent name
@router.message(StateFilter(FSMFillForm.fill_name_parent))
async def warning_not_name_parent(message: Message):
    await message.answer(
        text='То, что вы отправили не похоже на имя\n\n'
             'Пожалуйста, введите ваше имя\n\n')

# check correct swimmer surname
@router.message(StateFilter(FSMFillForm.fill_surname_swimmer))
async def warning_not_surname_swimmer(message: Message):
    await message.answer(
        text='То, что вы отправили не похоже на фамилию\n\n'
             'Пожалуйста, введите вашу фамилию\n\n')

# check correct parent surname
@router.message(StateFilter(FSMFillForm.fill_surname_parent))
async def warning_not_surname_parent(message: Message):
    await message.answer(
        text='То, что вы отправили не похоже на фамилию\n\n'
             'Пожалуйста, введите вашу фамилию\n\n')






