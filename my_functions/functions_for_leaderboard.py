import asyncio
import logging

from datetime import datetime
from data_bases.connect_data_base import connect_db, DB_NAME1, DB_NAME4, POLL_RESULTS
from aiogram import types, Bot
from config_data.config import Config, load_config

config: Config = load_config()
bot = Bot(token=config.tg_bot.token)


# get swimmer's year of birth
async def get_year(id):
    connect, cursor = connect_db(DB_NAME1)
    cursor.execute("SELECT year FROM users WHERE user_id = ?", (id,))
    data = cursor.fetchone()[0]
    if type(data) != int:
        return 2000
    else:
        return data

# get coef
async def get_coef(year):
    try:
        age = datetime.now().year - year
        if 0 < age < 6:
            return 2.5
        elif 6 <= age < 8:
            return 1.45
        elif 9 <= age < 11:
            return 1.1
        elif 11 <= age < 13:
            return 1
        else:
            return 0.7
    except Exception as e:
        logging.error(f"Произошла ошибка: {e}")

# set points to leaderboard
async def set_points_to_leaderboard(points, id, season='only_points'):
    connect, cursor = connect_db(DB_NAME4)
    cursor.execute("UPDATE leaderboard SET points = points + ? WHERE user_id = ?", (points, id))
    connect.commit()
    if season == 'season1':
        connect, cursor = connect_db(DB_NAME4)
        cursor.execute("UPDATE leaderboard SET season1 = season1 + ? WHERE user_id = ?", (points, id))
        connect.commit()
    elif season == 'season2':
        connect, cursor = connect_db(DB_NAME4)
        cursor.execute("UPDATE leaderboard SET season2 = season2 + ? WHERE user_id = ?", (points, id))
        connect.commit()
    elif season == 'season3':
        connect, cursor = connect_db(DB_NAME4)
        cursor.execute("UPDATE leaderboard SET season3 = season3 + ? WHERE user_id = ?", (points, id))
        connect.commit()
    elif season == 'season4':
        connect, cursor = connect_db(DB_NAME4)
        cursor.execute("UPDATE leaderboard SET season4 = season4 + ? WHERE user_id = ?", (points, id))
        connect.commit()

# get points
async def get_points(meteres, mark, coef):
    return meteres * coef * mark * 0.1

# check date to challenge
async def check_date_to_challenge(day):
    day = day.replace("'", "")
    date_format = "%Y-%m-%d"
    day = datetime.strptime(day, date_format)
    start_first_season = datetime(2024, 10, 10)
    end_first_season = datetime(2024, 12, 31)
    start_second_season = datetime(2025, 1, 1)
    end_second_season = datetime(2025, 5, 31)
    start_third_season = datetime(2025, 6, 1)
    end_trird_season = datetime(2025, 8, 31)
    start_fourth_season = datetime(2025, 9, 1)
    end_fourth_season = datetime(2025, 12, 31)
    if start_first_season <= day <= end_first_season:
        return 'season1'
    elif start_second_season <= day <= end_second_season:
        return 'season2'
    elif start_third_season <= day <= end_trird_season:
        return 'season3'
    elif start_fourth_season <= day <= end_fourth_season:
        return 'season4'
    else:
        return "Дата не попадает ни в один из периодов"

# collect info for leaderboard
async def pick_info_and_add(message: types.Message, day, id, meteres, mark):
    try:
        year = await get_year(id)
        coef = await get_coef(year)
        season = await check_date_to_challenge(day)
        points = await get_points(meteres, mark, coef)
        await set_points_to_leaderboard(points, id, season=season)
    except Exception as e:
        await message.answer(f"Error {e} в функции добавления очков")

# sort swimmers for leaderboard
async def async_sort(data):
    def custom_sort(item):
        value = item[2]
        if value == '-':
            return (1,)
        else:
            return (0, -value)
    sorted_data = await asyncio.to_thread(sorted, data, key=custom_sort)
    return sorted_data

# get swimmer username
async def get_swimmer_username(id):
    connect, cursor = connect_db(DB_NAME1)
    cursor.execute("SELECT user_name FROM users WHERE user_id = ?", (id,))
    username = cursor.fetchone()[0]
    return username

# get leaderboard table
async def get_leaderboard_table(message:types.Message, data):
    sorted_data = await async_sort(data)
    msg = ''
    place = 1
    for swimmer in sorted_data[:10]:
        point = swimmer[2]
        if isinstance(point, float):
            point = round(float(point), 1)
        if place == 1:
            msg += f'🥇 <b>{point}</b> - {swimmer[1]} @{await get_swimmer_username(swimmer[0])}\n'
        elif place == 2:
            msg += f'🥈 <b>{point}</b> - {swimmer[1]} @{await get_swimmer_username(swimmer[0])}\n'
        elif place == 3:
            msg += f'🥉 <b>{point}</b> - {swimmer[1]} @{await get_swimmer_username(swimmer[0])}\n'
        else:
            msg += f' {place}. <b>{point}</b> - {swimmer[1]} @{await get_swimmer_username(swimmer[0])}\n'
        place += 1
    await message.answer(msg, parse_mode="html")
    return sorted_data[:10]

# search swimcoins by id
async def get_data_by_id(data, id):
    for index, item in enumerate(data):
        if item[0] == id:
            return index + 1
    return None

# 11 place and lower for leaderboard
async def get_no_leaders(message:types.Message, id, data):
    try:
        sorted_data = await async_sort(data)
        place = await get_data_by_id(sorted_data, id)
        swimcoins_to_lvl = sorted_data[place-2][-1] - int(sorted_data[place-1][-1])
        return place, swimcoins_to_lvl
    except Exception as e:
        logging.error(f"Произошла ошибка: {e}")

async def get_procent(votes):
    if sum(votes) == 0:
        return [0] * len(votes)
    total_votes = sum(votes)
    percentages = [(vote / total_votes) * 100 for vote in votes]
    return [round(percentage) for percentage in percentages]

async def show_results(message: types.Message):
    pr = await get_procent([POLL_RESULTS['option_1'], POLL_RESULTS['option_2'], POLL_RESULTS['option_3'], POLL_RESULTS['option_4']])
    results_message = (
        "Текущие результаты голосования:\n"
        f"💂Шапочка с принтом: {POLL_RESULTS['option_1']}({pr[0]}%)\n"
        f"🧸Набор игрушек антистресс: {POLL_RESULTS['option_2']}({pr[1]}%)\n"
        f"💳Сертификат на озон/вб 1500руб: {POLL_RESULTS['option_3']}({pr[2]}%)\n"
        f"🍬🥚Kinder набор: {POLL_RESULTS['option_4']}({pr[3]}%)\n".ljust(10)
    )
    await message.answer(results_message)

