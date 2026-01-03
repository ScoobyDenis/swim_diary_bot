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
    elif season == 'season5':
        connect, cursor = connect_db(DB_NAME4)
        cursor.execute("UPDATE leaderboard SET season5 = season5 + ? WHERE user_id = ?", (points, id))
        connect.commit()
    elif season == 'season6':
        connect, cursor = connect_db(DB_NAME4)
        cursor.execute("UPDATE leaderboard SET season6 = season6 + ? WHERE user_id = ?", (points, id))
        connect.commit()
    elif season == 'season7':
        connect, cursor = connect_db(DB_NAME4)
        cursor.execute("UPDATE leaderboard SET season7 = season7 + ? WHERE user_id = ?", (points, id))
        connect.commit()
    elif season == 'season8':
        connect, cursor = connect_db(DB_NAME4)
        cursor.execute("UPDATE leaderboard SET season8 = season8 + ? WHERE user_id = ?", (points, id))
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
    end_second_season = datetime(2025, 5, 17)
    start_third_season = datetime(2025, 5, 18)
    end_trird_season = datetime(2025, 8, 31)
    start_fourth_season = datetime(2025, 8, 31)
    end_fourth_season = datetime(2025, 12, 31)
    start_five_season = datetime(2026, 1, 1)
    end_five_season = datetime(2026, 5, 31)
    start_six_season = datetime(2026, 6, 1)
    end_six_season = datetime(2026, 8, 31)
    start_seven_season = datetime(2026, 9, 1)
    end_seven_season = datetime(2026, 12, 31)
    start_eight_season = datetime(2027, 1, 1)
    end_eight_season = datetime(2027, 5, 31)
    if start_first_season <= day <= end_first_season:
        return 'season1'
    elif start_second_season <= day <= end_second_season:
        return 'season2'
    elif start_third_season <= day <= end_trird_season:
        return 'season3'
    elif start_fourth_season <= day <= end_fourth_season:
        return 'season4'
    elif start_five_season <= day <= end_five_season:
        return 'season5'
    elif start_six_season <= day <= end_six_season:
        return 'season6'
    elif start_seven_season <= day <= end_seven_season:
        return 'season7'
    elif start_eight_season <= day <= end_eight_season:
        return 'season8'
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
'''async def async_sort(data):
    def custom_sort(item):
        value = item[3]
        if value == '-':
            return (1,)
        else:
            return (0, -value)
    sorted_data = await asyncio.to_thread(sorted, data, key=custom_sort)
    return sorted_data '''


async def async_sort(data):
    def custom_sort(item):
        value = item[3]
        if value == '-' or value is None:
            return (1,)  # Отправляем в конец
        else:
            try:
                # Пытаемся преобразовать в число
                num_value = float(value)
                return (0, -num_value)
            except (ValueError, TypeError):
                # Если не получается преобразовать в число
                return (1,)

    sorted_data = await asyncio.to_thread(sorted, data, key=custom_sort)
    return sorted_data

# get leaderboard table
'''async def get_leaderboard_table(message:types.Message, data, ind=20):
    sorted_data = await async_sort(data)
    msg = ''
    place = 1
    for swimmer in sorted_data[:ind]:
        point = swimmer[3]
        if isinstance(point, float):
            point = round(float(point), 1)
        if place == 1:
            msg += f'🥇 <b>{point}</b> - {swimmer[1]} {swimmer[2]}\n' # @{await get_swimmer_username(swimmer[0])}\n'
        elif place == 2:
            msg += f'🥈 <b>{point}</b> - {swimmer[1]} {swimmer[2]}\n' # @{await get_swimmer_username(swimmer[0])}\n'
        elif place == 3:
            msg += f'🥉 <b>{point}</b> - {swimmer[1]} {swimmer[2]}\n' # @{await get_swimmer_username(swimmer[0])}\n'
        else:
            msg += f' {place}. <b>{point}</b> - {swimmer[1]} {swimmer[2]}\n' # @{await get_swimmer_username(swimmer[0])}\n'
        place += 1
    await message.answer(msg, parse_mode="html")
    return sorted_data[:ind]'''


async def get_leaderboard_table(message: types.Message, data, ind=20):
    sorted_data = await async_sort(data)
    msg = ''
    place = 1
    for swimmer in sorted_data[:ind]:
        point = swimmer[3]
        # Форматируем значение для отображения
        if point is None or point == '-':
            display_point = '-'
        elif isinstance(point, (int, float)):
            display_point = round(float(point), 1)
        else:
            # Пытаемся преобразовать строку в число
            try:
                display_point = round(float(point), 1)
            except (ValueError, TypeError):
                display_point = point

        if place == 1:
            msg += f'🥇 <b>{display_point}</b> - {swimmer[1]} {swimmer[2]}\n'
        elif place == 2:
            msg += f'🥈 <b>{display_point}</b> - {swimmer[1]} {swimmer[2]}\n'
        elif place == 3:
            msg += f'🥉 <b>{display_point}</b> - {swimmer[1]} {swimmer[2]}\n'
        else:
            msg += f' {place}. <b>{display_point}</b> - {swimmer[1]} {swimmer[2]}\n'
        place += 1

    await message.answer(msg, parse_mode="html")
    return sorted_data[:ind]

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
        if place != ' ':
            swimcoins_to_lvl = sorted_data[place-2][-1] - int(sorted_data[place-1][-1])
            return place, swimcoins_to_lvl
        else:
            swimcoins_to_lvl = sorted_data[place-2][-1] - int(sorted_data[place-1][-1])
            return ' ', swimcoins_to_lvl
    except Exception as e:
        logging.error(f"Произошла ошибка: {e}")

async def get_procent(votes):
    if sum(votes) == 0:
        return [0] * len(votes)
    total_votes = sum(votes)
    percentages = [(vote / total_votes) * 100 for vote in votes]
    return [round(percentage) for percentage in percentages]

async def get_swimcoins_balance(message:types.Message, id):
    try:
        connect, cursor = connect_db(DB_NAME4)
        cursor.execute("SELECT season2 FROM leaderboard WHERE user_id = ?", (id,))
        swimcoins = cursor.fetchone()[0]
        await message.answer(f"Ваш балансе - {swimcoins}💲swimcoins")
    except Exception as e:
        logging.error(f"Произошла ошибка: {e}")

def update_existing_users_with_seasons():
    """Добавляет season7 и season8 существующим пользователям"""
    connect, cursor = connect_db(DB_NAME4)

    try:
        # 1. Сначала добавляем колонки, если их еще нет
        try:
            cursor.execute("ALTER TABLE leaderboard ADD COLUMN season5 TEXT DEFAULT '-'")
            print("Добавлена колонка season5")
        except Exception as e:
            print(f"Колонка season5 уже существует или ошибка: {e}")

        try:
            cursor.execute("ALTER TABLE leaderboard ADD COLUMN season6 TEXT DEFAULT '-'")
            print("Добавлена колонка season6")
        except Exception as e:
            print(f"Колонка season6 уже существует или ошибка: {e}")

        try:
            cursor.execute("ALTER TABLE leaderboard ADD COLUMN season7 TEXT DEFAULT '-'")
            print("Добавлена колонка season7")
        except Exception as e:
            print(f"Колонка season7 уже существует или ошибка: {e}")

        try:
            cursor.execute("ALTER TABLE leaderboard ADD COLUMN season8 TEXT DEFAULT '-'")
            print("Добавлена колонка season8")
        except Exception as e:
            print(f"Колонка season8 уже существует или ошибка: {e}")

        # 2. Устанавливаем '-' для всех существующих записей в новых колонках
        cursor.execute("UPDATE leaderboard SET season5 = '-' WHERE season5 IS NULL")
        cursor.execute("UPDATE leaderboard SET season6 = '-' WHERE season6 IS NULL")
        cursor.execute("UPDATE leaderboard SET season7 = '-' WHERE season7 IS NULL")
        cursor.execute("UPDATE leaderboard SET season8 = '-' WHERE season8 IS NULL")


    except Exception as e:
        print(f"Ошибка при обновлении: {e}")
        connect.rollback()
    finally:
        connect.close()