from datetime import datetime, timedelta
from aiogram.filters import Command, CommandObject
from data_bases.connect_data_base import connect_db, DB_NAME1, DB_NAME2, DF
from aiogram import types
from aiogram import Router

router = Router()

# get users id
@router.message(Command("get_users_info"))
async def get_users_info(message: types.Message):
    connect, cursor = connect_db(DB_NAME1)
    cursor.execute("SELECT user_id, swimmer_name, swimmer_surname FROM users")
    data = cursor.fetchall()
    for i in data:
        await message.answer(f"id - {i[0]}\n"
                             f"{i[1]} {i[2]}")

# get parents id
@router.message(Command("get_parents_info"))
async def get_users_info(message: types.Message):
    connect, cursor = connect_db(DB_NAME2)
    cursor.execute("SELECT user_id, parent_name, parent_surname FROM parents")
    data = cursor.fetchall()
    for i in data:
        await message.answer(f"id - {i[0]}\n"
                             f"{i[1]} {i[2]}")

# day statistic
@router.message(Command("day_stat"))
async def get_day_stat(message: types.Message):
    count = DF.loc[str(datetime.now().date())].count() - 6
    await message.answer(f"{count}")

# last week statistic
@router.message(Command("last_week_stat"))
async def get_last_week_stats(message: types.Message):
    start_date = datetime.now().date()
    total_workouts = -61
    start_of_last_week = start_date - timedelta(days=start_date.weekday() + 7)
    for i in range(7):
        date = start_of_last_week + timedelta(days=i)
        total_workouts += DF.loc[date.strftime('%Y-%m-%d')].count()
    await message.answer(f"Количесво тренировок за прошлую неделю - {total_workouts}")

# week statistic
@router.message(Command("week_stat"))
async def get_week_stats(message: types.Message):
    current_date = datetime.now()
    total_workouts = 0
    start_of_current_week = current_date - timedelta(days=current_date.weekday())
    for i in range(current_date.weekday() + 1):
        date = start_of_current_week + timedelta(days=i)
        total_workouts += DF.loc[date.strftime('%Y-%m-%d')].count()
    await message.answer(f"Количество тренировок за эту неделю - {total_workouts}")

# today schedule
@router.message(Command('today_schedule'))
async def get_user_writes(message: types.Message, command: CommandObject):
    try:
        i = int(command.args)
    except:
        i = 0
    msg = ''
    await message.answer(f"Запись на {str(datetime.now().date() + timedelta(days=i))} число")
    for k, v in dict(DF.loc[str(datetime.now().date()+timedelta(days=i))]).items():
        msg += f"{k} - {v}\n"
    await message.answer(msg)


