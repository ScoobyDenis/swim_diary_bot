import logging

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, FSInputFile
from datetime import datetime, timedelta
from data_bases.connect_data_base import DF, connect_db, DB_NAME1, DB_NAME2, DB_NAME3, DB_NAME4, ADMIN
from aiogram import types, Bot
from config_data.config import Config, load_config
from lexicon.lexicon_ru import WEEKDAYS

config: Config = load_config()
bot = Bot(token=config.tg_bot.token)


# create time keyboard
async def create_time_keyboard(message: types.Message, day, mode):
    d = dict(DF.loc[day])
    inline_kb = []
    for key, val in d.items():
        if mode == 'swimmer':
            if str(val) == 'nan':
                inline_kb.append([InlineKeyboardButton(text=key, callback_data='adds_swimmer_'+day+'_'+str(key))])
        elif mode == "admin":
            if str(val) == 'nan':
                inline_kb.append([InlineKeyboardButton(text=key, callback_data='adds_admin_'+day+'_'+str(key))])
        elif mode == "parent":
            if str(val) == 'nan':
                inline_kb.append([InlineKeyboardButton(text=key, callback_data='adds_parent_' + day + '_' + str(key))])
        elif mode == "cancel":
            if str(val) != 'nan':
                inline_kb.append([InlineKeyboardButton(text=key, callback_data='adds_cancel_admin_' + day + '_' + str(key))])
        else:
            logging.info(f"Нет такого мода {mode}")
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=inline_kb
    )
    if len(keyboard.inline_keyboard) == 0:
        await message.answer("В этот день нет свободного времени")
    else:
        return keyboard

# create date keyboard
async def create_date_keyboard(mode):
    today = datetime.now().date()
    buttons = []
    if mode == 'swimmer':
        for _ in range(14):
            wd = WEEKDAYS[today.weekday()]
            button_text = f"createdateswimmer_{today.strftime('%Y-%m-%d')}"
            buttons.append([InlineKeyboardButton(text=today.strftime('%Y-%m-%d')+' '+wd, callback_data=button_text)])
            today = today + timedelta(days=1)
    elif mode =='admin':
        for _ in range(14):
            wd = WEEKDAYS[today.weekday()]
            button_text = f"createdateadmin_{today.strftime('%Y-%m-%d')}"
            buttons.append([InlineKeyboardButton(text=today.strftime('%Y-%m-%d')+' '+wd, callback_data=button_text)])
            today = today + timedelta(days=1)
    elif mode == 'parent':
        for _ in range(14):
            wd = WEEKDAYS[today.weekday()]
            button_text = f"createdateparent_{today.strftime('%Y-%m-%d')}"
            buttons.append([InlineKeyboardButton(text=today.strftime('%Y-%m-%d')+' '+wd, callback_data=button_text)])
            today = today + timedelta(days=1)
    elif mode == 'cancel':
        for _ in range(14):
            wd = WEEKDAYS[today.weekday()]
            button_text = f"createcancel_{today.strftime('%Y-%m-%d')}"
            buttons.append([InlineKeyboardButton(text=today.strftime('%Y-%m-%d')+' '+wd, callback_data=button_text)])
            today = today + timedelta(days=1)
    else:
        logging.info(f"Нет такого мода {mode}")
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=buttons
    )
    return keyboard

# get name surname from db
async def get_name_surname_from_db(user_id):
    connect, cursor = connect_db(DB_NAME1)
    cursor.execute(f"SELECT swimmer_name, swimmer_surname FROM users WHERE user_id = {user_id}")
    data = cursor.fetchone()
    return data[0] + ' ' + data[1]

# check birth
async def check_birth(id):
    connect, cursor = connect_db(DB_NAME1)
    cursor.execute(f"SELECT year, month, day FROM users WHERE user_id = {id}")
    data = cursor.fetchone()
    return data[0], data[1], data[2]

# get id from id.txt
async def get_id_from_txt():
    with open('files/id.txt', 'r') as file:
        id = int(file.readline())
    return id

# check age
async def check_age(id):
    connect, cursor = connect_db(DB_NAME1)
    cursor.execute(f"SELECT year FROM users WHERE user_id = {id}")
    year = cursor.fetchone()[0]
    return year < 2009

# reform array
async def reform_array(arr):
    new_arr = []
    for i in arr:
        new_arr.append(i[0])
    return new_arr

# get swimmer id
async def get_swimmer_id(name, surname):
    connect, cursor = connect_db(DB_NAME1)
    cursor.execute(f"SELECT user_id FROM users WHERE swimmer_name = {name} AND swimmer_surname = {surname}")
    return cursor.fetchone()[0]

# check id in users
async def check_id_in_users(id):
    connect, cursor = connect_db(DB_NAME1)
    cursor.execute("SELECT COUNT(*) FROM users WHERE user_id = ?", (id,))
    count = cursor.fetchone()[0]
    return count == 0

# check id in parents
async def check_id_in_parents(id):
    connect, cursor = connect_db(DB_NAME2)
    cursor.execute("SELECT COUNT(*) FROM parents WHERE user_id = ?", (id,))
    count = cursor.fetchone()[0]
    return count == 0

# get day and time training
async def get_kids_time_day_training(message: types.Message, mode='parent'):
    try:
        if mode == 'parent':
            connect, cursor = connect_db(DB_NAME2)
            cursor.execute(f'SELECT children FROM parents WHERE user_id = {message.from_user.id}')
            children = cursor.fetchone()[0].split('_')
            locs = []
            for child in children:
                connect, cursor = connect_db(DB_NAME1)
                cursor.execute(f"SELECT swimmer_name, swimmer_surname FROM users WHERE user_id = {int(child)}")
                data = cursor.fetchone()
                swimmer = data[0] + ' ' + data[1]
                locations = []
                for row in DF.index:
                    for col in DF.columns:
                        if DF.loc[row, col] == swimmer:
                            locations.append((row, col))
                locs.append((locations, swimmer))
            return locs
        elif mode == 'swimmer':
            connect, cursor = connect_db(DB_NAME1)
            cursor.execute(f"SELECT swimmer_name, swimmer_surname FROM users WHERE user_id = {message.from_user.id}")
            data = cursor.fetchone()
            swimmer = data[0] + ' ' + data[1]
            locations = []
            for row in DF.index:
                for col in DF.columns:
                    if DF.loc[row, col] == swimmer:
                            locations.append((row, col))
            return locations
    except:
        await message.answer("Нет записи. Чтобы записаться\n"
                             "на тренировку нажмите /registr")

# send picture
async def send_picture(message: types.Message, path):
    photo = FSInputFile(path)
    await bot.send_photo(chat_id=message.chat.id, photo=photo)

# get rate with picts
async def get_rate(message: types.Message, rate):
    if rate < 20000:
        next_lvl = int(2000 - (rate % 2000))
    else:
        next_lvl = int(5000 - (rate % 5000))
    if rate <= 2000:
        await send_picture(message,"pictures/seastar.jpeg")
        await message.answer(f"Ваш уровень - морская звезда! ⭐️\n"
                             f"До следующего уровня 'моллюск' 🦪 {next_lvl}м.")
    elif 2000 <= rate < 4000:
        await send_picture(message, "pictures/conus.jpg")
        await message.answer(f"Ваш уровень - моллюск! 🦪\n"
                             f"До следующего уровня 'медуза' {next_lvl}м.")
    elif 4000 <= rate < 6000:
        await send_picture(message, "pictures/medusa.jpeg")
        await message.answer(f"Ваш уровень - медуза!\n"
                             f"До следующего уровня 'морской конёк' {next_lvl}м.")
    elif 6000 <= rate < 8000:
        await send_picture(message, "pictures/sea_horse.jpeg")
        await message.answer(f"Ваш уровень - морской конёк!\n"
                             f"До следующего уровня 'краб' {next_lvl}м.")
    elif 8000 <= rate < 10000:
        await send_picture(message, "pictures/crub.jpeg")
        await message.answer(f"Ваш уровень - краб!\n"
                             f"До следующего уровня 'ламантин' {next_lvl}м.")
    elif 10000 <= rate < 12000:
        await send_picture(message, "pictures/lamantin.jpg")
        await message.answer(f"Ваш уровень - ламантин!\n"
                             f"До следующего уровня 'осьминог' {next_lvl}м.")
    elif 12000 <= rate < 14000:
        await send_picture(message, "pictures/octopus.jpeg")
        await message.answer(f"Ваш уровень - осьминог!\n"
                             f"До следующего уровня 'кальмар' {next_lvl}м.")
    elif 14000 <= rate < 16000:
        await send_picture(message, "pictures/calmar.jpeg")
        await message.answer(f"Ваш уровень - кальмар!\n"
                             f"До следующего уровня 'иглобрюх' {next_lvl}м.")
    elif 16000 <= rate < 18000:
        await send_picture(message, "pictures/pufferfish.jpeg")
        await message.answer(f"Ваш уровень - иглобрюх!\n"
                             f"До следующего уровня 'тюлень' {next_lvl}м.")
    elif 18000 <= rate < 20000:
        await send_picture(message, "pictures/seal.jpeg")
        await message.answer(f"Ваш уровень - тюлень!\n"
                             f"До следующего уровня 'морж' {next_lvl}м.")
    elif 20000 <= rate < 25000:
        await send_picture(message, "pictures/walrus.jpeg")
        await message.answer(f"Ваш уровень - морж!\n"
                             f"До следующего уровня 'морская черепаха' {next_lvl}м.")
    elif 25000 <= rate < 30000:
        await send_picture(message, "pictures/turtle.jpeg")
        await message.answer(f"Ваш уровень - морская черепаха!\n"
                             f"До следующего уровня 'скат' {next_lvl}м.")
    elif 30000 <= rate < 35000:
        await send_picture(message, "pictures/skat.jpeg")
        await message.answer(f"Ваш уровень - скат!\n"
                             f"До следующего уровня 'тунец' {next_lvl}м.")
    elif 35000 <= rate < 40000:
        await send_picture(message, "pictures/tuna.jpeg")
        await message.answer(f"Ваш уровень - тунец!\n"
                             f"До следующего уровня 'барракуда' {next_lvl}м.")
    elif 40000 <= rate < 45000:
        await send_picture(message, "pictures/barracuda.jpeg")
        await message.answer(f"Ваш уровень - барракуда!\n"
                             f"До следующего уровня 'марлин' {next_lvl}м.")
    elif 45000 <= rate < 50000:
        await send_picture(message, "pictures/marlin.jpeg")
        await message.answer(f"Ваш уровень - марлин!\n"
                             f"До следующего уровня 'дельфин' {next_lvl}м.")
    elif 50000 <= rate < 55000:
        await send_picture(message, "pictures/dolphin.jpeg")
        await message.answer(f"Ваш уровень - дельфин!\n"
                             f"До следующего уровня 'акула' {next_lvl}м.")
    elif 55000 <= rate < 60000:
        await send_picture(message, "pictures/shark.jpeg")
        await message.answer(f"Ваш уровень - акула!\n"
                             f"До следующего уровня 'касатка' {next_lvl}м.")
    elif 60000 <= rate < 65000:
        await send_picture(message, "pictures/killer_whale.jpeg")
        await message.answer(f"Ваш уровень - касатка!\n"
                             f"До следующего уровня 'кит' {next_lvl}м.")
    elif 65000 <= rate:
        await send_picture(message, "pictures/whale.jpeg")
        await message.answer(f"Ваш уровень - кит!")

# get mark mean
async def get_mark_mean(message: types.Message, id):
    connect, cursor = connect_db(DB_NAME3)
    cursor.execute(f"SELECT mark, total_lessons FROM results WHERE user_id = {id}")
    data = cursor.fetchone()
    mark = data[0]
    total_lessons = data[1]
    d = {0: '🐣', 1: '🐣', 2: '🐥', 3: '🤯', 4: '😕', 5: '🤨', 6: '🫡', 7: '☺️', 8: '👨‍🎓', 9: '🤓', 10: '🧠'}
    if total_lessons == 0:
        await message.answer("Пока что нет оценок")
    else:
        mean_mark = mark / total_lessons
        await message.answer(f"Средняя оценка - {round(mean_mark, 1)}{d[int(mean_mark)]}\n")

# get meteres info
async def get_meteres_info(message: types.Message, id):
    connect, cursor = connect_db(DB_NAME3)
    cursor.execute(f"SELECT meteres, total_lessons FROM results WHERE user_id = {id}")
    data = cursor.fetchone()
    meteres = int(data[0])
    lessons = data[1]
    if lessons != 0:
        await message.answer(f"Всего проплыто - {meteres}м.\n"
                             f"В среднем за тренировку - {round(meteres / lessons, 1)}м.")
        await get_rate(message, meteres)
    else:
        await message.answer("Пока нет данных.")

# select swimmer for parent
async def select_swimmer(message: types.Message, text):
    connect, cursor = connect_db(DB_NAME2)
    cursor.execute(f"SELECT children FROM parents WHERE user_id = {message.from_user.id}")
    children_id = cursor.fetchone()[0].split('_')
    buttons = []
    try:
        for id in children_id:
            connect, cursor = connect_db(DB_NAME1)
            cursor.execute(f"SELECT user_id, swimmer_name FROM users WHERE user_id = {id}")
            data = cursor.fetchone()
            button_text = f"{text}{str(data[0]) + '_' + data[1]}"
            buttons.append([InlineKeyboardButton(text=data[1], callback_data=button_text)])
        if not await check_id_in_users(message.from_user.id):
            connect, cursor = connect_db(DB_NAME1)
            cursor.execute(f"SELECT swimmer_name FROM users WHERE user_id = {message.from_user.id}")
            data = cursor.fetchone()[0]
            button_text = f"{text}{str(message.from_user.id) + '_' + data}"
            buttons.append([InlineKeyboardButton(text=data, callback_data=button_text)])
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=buttons
        )
        await message.answer("Выберите пловца", reply_markup=keyboard)
    except:
        await message.answer("Тренер ещё не добавил данные.")

# msg to admin
async def msg_to_admin(msg):
    await bot.send_message(ADMIN, msg)

# create new swimmer
async def create_new_swimmer(id, username):
    connect, cursor = connect_db(DB_NAME1)
    data = [id, username, '-', '-', '-', '-', '-', '-', '-', '-',
            '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-']
    cursor.execute(
        "INSERT INTO users (user_id, user_name, swimmer_name, swimmer_surname, year, month, day,"
        "freestyle_25m, freestyle_50m, freestyle_100m, freestyle_400m,"
        "backstroke_25m, backstroke_50m, backstroke_100m,"
        "breaststroke_25m, breaststroke_50m, breaststroke_100m,"
        "butterfly_25m, butterfly_50m, medley_100m, medley_200m, medley_400m)  VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        data)
    connect.commit()
    connect, cursor = connect_db(DB_NAME3)
    data = [id, '-', '-', '-', '-', '-', 0, 0, 0]
    cursor.execute(
        "INSERT INTO results (user_id, swimmer_name, date, meteres_last, mark_last, comment, meteres, mark, total_lessons) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)",
        data)
    connect.commit()

# set swimmer name to users
async def set_swimmer_name_to_users(name, id):
    connect, cursor = connect_db(DB_NAME1)
    cursor.execute(f"UPDATE users SET swimmer_name = '{name}' WHERE user_id = {id}")
    connect.commit()

# set swimmer name to results
async def set_swimmer_name_to_results(name, id):
    connect, cursor = connect_db(DB_NAME3)
    cursor.execute(f"UPDATE results SET swimmer_name = '{name}' WHERE user_id = {id}")
    connect.commit()

# set swimmer name to leadeboard
async def set_swimmer_name_to_leaderboard(name, id):
    connect, cursor = connect_db(DB_NAME4)
    cursor.execute(f"UPDATE leaderboard SET name = '{name}' WHERE user_id = {id}")
    connect.commit()

# set swimmer surname to leadeboard
async def set_swimmer_surname_to_leaderboard(surname, id):
    connect, cursor = connect_db(DB_NAME4)
    cursor.execute(f"UPDATE leaderboard SET surname = '{surname}' WHERE user_id = {id}")
    connect.commit()

# set swimmer surname to users
async def set_swimmer_surname_to_users(surname, id):
    connect, cursor = connect_db(DB_NAME1)
    cursor.execute(f"UPDATE users SET swimmer_surname = '{surname}' WHERE user_id = {id}")
    connect.commit()

# set swimmer surname to leaderboard
async def set_swimmer_surname_to_leaderboard(surname, id):
    connect, cursor = connect_db(DB_NAME4)
    cursor.execute(f"UPDATE leaderboard SET surname = '{surname}' WHERE user_id = {id}")
    connect.commit()

# create new parent
async def create_new_parent(id):
    connect, cursor = connect_db(DB_NAME2)
    data = [id, '-', '-', '-']
    cursor.execute("INSERT INTO parents (user_id, parent_name, parent_surname, children) VALUES(?, ?, ?, ?)", data)
    connect.commit()

# create new leaderboard user
async def create_new_leaderboard_user(id):
    connect, cursor = connect_db(DB_NAME4)
    data = [id, '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-']
    cursor.execute("INSERT INTO leaderboard (user_id, name, surname, points, season1, season2, season3, season4, season5, season6, season7, season8) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", data)
    connect.commit()

# get info from all distances
async def get_all_distances(message: types.Message, id):
    connect, cursor = connect_db(DB_NAME1)
    cursor.execute(f"SELECT freestyle_25m, freestyle_50m, freestyle_100m, "
                   f"freestyle_400m, backstroke_25m, backstroke_50m, backstroke_100m, "
                   f"breaststroke_25m, breaststroke_50m, breaststroke_100m, butterfly_25m, "
                   f"butterfly_50m, medley_200m, medley_400m FROM users WHERE user_id = {id}")
    data = cursor.fetchone()
    await message.answer(f"вольный стиль 25 м - {data[0]}\n"
                                  f"вольный стиль 50 м - {data[1]}\n"
                                  f"вольный стиль 100 м - {data[2]}\n"
                                  f"вольный стиль 400 м - {data[3]}\n"
                                  f"на спине 25 м - {data[4]}\n"
                                  f"на спине 50 м - {data[5]}\n"
                                  f"на спине 100 м - {data[6]}\n"
                                  f"брасс 25 м - {data[7]}\n"
                                  f"брасс 50 м - {data[8]}\n"
                                  f"брасс 100 м - {data[9]}\n"
                                  f"баттерфляй 25 м - {data[10]}\n"
                                  f"баттерфляй 50 м - {data[11]}\n"
                                  f"комплексное плавание 200 м - {data[12]}\n"
                                  f"комплексное плавание 400 м - {data[13]}\n")

# get kb diary
async def get_kb_diary(message: types.Message, id):
    inline_kb = []
    inline_kb.append([InlineKeyboardButton(text='🏊🏾‍♂️Последний урок', callback_data='lesson_' + str(id))])
    #inline_kb.append([InlineKeyboardButton(text='🏊🏾‍♂️5 Последних уроков', callback_data='fivelastlesson_' + str(id))])
    inline_kb.append([InlineKeyboardButton(text='🏊🏾‍♂️🏊🏾‍♂️🏊🏾‍♂️🏊🏾‍♂️🏊🏾‍♂️10 Последних уроков', callback_data='tenlastlesson_' + str(id))])
    inline_kb.append([InlineKeyboardButton(text='📈Средняя оценка', callback_data='markmean_' + str(id))])
    inline_kb.append([InlineKeyboardButton(text='🏊Общая длина проплытых метров', callback_data='meanmeteres_' + str(id))])
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=inline_kb
    )
    await message.answer(f"Выберите, что посмотреть", reply_markup=keyboard)




