from aiogram.types import CallbackQuery
from aiogram.filters import Command
from aiogram import F
from aiogram import Router

from lexicon.lexicon_ru import TO_RUS_DISTANCE, BIG_WEEKDAYS
from my_functions.my_functions import *
from my_functions.functions_for_leaderboard import *
from aiogram.fsm.context import FSMContext
from data_bases.connect_data_base import connect_db, DB_NAME1, DB_NAME3, POLL_RESULTS, VOTERS_ID

router = Router()


# check schedule
@router.message(Command('check'))
async def check_kids_writes(message: types.Message):
    if not await check_id_in_users(message.from_user.id):
        locations = await get_kids_time_day_training(message, mode='swimmer')
        i = 0
        if locations:
            for loc in locations:
                if loc[0] >= datetime.now() - timedelta(days=1):
                    wd = BIG_WEEKDAYS[loc[0].date().weekday()]
                    await message.answer(f"{wd}, {loc[0].date()}\n{loc[1]}")
                    i += 1
        if i == 0:
            await message.answer("Пока что вы никуда не записаны.\n")
    else:
        locations = await get_kids_time_day_training(message, mode='parent')
        i = 0
        if locations:
            for l in locations:
                swimmer = l[1]
                for loc in l[0]:
                    if loc[0] >= datetime.now() - timedelta(days=1):
                        wd = BIG_WEEKDAYS[loc[0].date().weekday()]
                        await message.answer(f"{wd}, {loc[0].date()}\n{loc[1]} {swimmer}")
                        i += 1
            if i == 0:
                await message.answer("Пока что вы никуда не записаны.\n"
                                "Чтобы записаться нажмите - /registr")

# cancel training
@router.message(Command('cancel'))
async def cancel_trainings(message: types.Message):
    try:
        id = message.from_user.id
        inline_kb = []
        if await check_id_in_users(message.from_user.id):
            mode = 'parent'
            locations = await get_kids_time_day_training(message, mode=mode)
            for l in locations:
                swimmer = l[1]
                for loc in l[0]:
                    if loc[0] >= datetime.now() - timedelta(days=1):
                        wd = WEEKDAYS[loc[0].date().weekday()]
                        inline_kb.append([InlineKeyboardButton(text=f"{wd}, {loc[0].date()} {loc[1]} {swimmer}",
                                                               callback_data='cancel_button_' + '_' + str(
                                                                   loc[0].date()) + '_' + str(loc[1]) + '_' + str(id))])
            kb = InlineKeyboardMarkup(
                inline_keyboard=inline_kb
            )
            if kb.inline_keyboard:
                await message.answer("Отменяйте тренировку не позднее, чем за 24 часа до её начала")
                await message.answer("Выберите, какую тренировку вы хотите отменить", reply_markup=kb)
            else:
                await message.answer("У вас нет записи(нечего отменять).")
        elif not await check_age(message.from_user.id):
            await message.answer("Отменить тренировку может только родитель")
        else:
            mode = 'swimmer'
            locations = await get_kids_time_day_training(message, mode=mode)
            for l in locations:
                if l[0] >= datetime.now() - timedelta(days=1):
                    wd = WEEKDAYS[l[0].date().weekday()]
                    inline_kb.append([InlineKeyboardButton(text=f"{wd}, {l[0].date()}  {l[1]}",
                                                           callback_data='cancel_button_' + '_' + str(
                                                               l[0].date()) + '_' + str(l[1]) + '_' + str(id))])
            kb = InlineKeyboardMarkup(
                inline_keyboard=inline_kb
            )
            if kb.inline_keyboard:
                await message.answer("Отменяйте тренировку не позднее, чем за 24 часа до её начала")
                await message.answer("Выберите, какую тренировку вы хотите отменить", reply_markup=kb)
            else:
                await message.answer("У вас нет записи(нечего отменять).")
    except Exception as e:
        logging.error(e)

# cancel finisher
@router.callback_query(F.data.startswith('cancel_button_'))
async def process_button_cancel_pressed(callback: CallbackQuery):
    date = callback.data.split('_')[3]
    time = callback.data.split('_')[4]
    id = callback.data.split('_')[-1]
    DF.loc[date, time] = None
    DF.to_csv('files/swim_schedule.csv')
    await callback.message.answer(f"Запись на {date} {time} отменена")
    await msg_to_admin(f"Запись на {date} {time} отменил\n"
                       f"пользователь - {id}")

# check results
@router.message(Command('check_results'))
async def check_kids(message: types.Message):
    try:
        if not await check_id_in_users(message.from_user.id):
            connect, cursor = connect_db(DB_NAME1)
            cursor.execute(f"SELECT * FROM users WHERE user_id = {message.from_user.id}")
            id = str(message.from_user.id)
            column_names = [description[0] for description in cursor.description][7:]
            inline_kb = []
            inline_kb.append([InlineKeyboardButton(text='Все дистанции', callback_data='pathdist_' + id + '_all')])
            for distance in column_names:
                inline_kb.append(
                    [InlineKeyboardButton(text=TO_RUS_DISTANCE[distance],
                                          callback_data='pathdist_' + id + '_' + distance)])
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=inline_kb
            )
            await message.answer(f"Выберите дистанцию", reply_markup=keyboard)
        else:
            await select_swimmer(message, 'alldistance_')
    except Exception as e:
       logging.error(f"Произошла ошибка: {e}")

# check all distances
@router.callback_query(F.data.startswith('alldistance'))
async def get_all_distance(callback: CallbackQuery, state: FSMContext):
    id = str(callback.data.split('_')[1])
    connect, cursor = connect_db(DB_NAME1)
    cursor.execute("SELECT * FROM users LIMIT 1")  # Получаем одну строку, чтобы получить метаданные
    column_names = [description[0] for description in cursor.description][7:]
    inline_kb = []
    inline_kb.append([InlineKeyboardButton(text='Все дистанции', callback_data='pathdist_' + id + '_'  + 'all')])
    for distance in column_names:
        inline_kb.append([InlineKeyboardButton(text=TO_RUS_DISTANCE[distance], callback_data='pathdist_'+ id+'_'+distance)])
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=inline_kb
    )
    await callback.message.answer(f"Выберите дистанцию", reply_markup=keyboard)

# get distances
@router.callback_query(F.data.startswith('pathdist'))
async def distances(callback: CallbackQuery):
    id = callback.data.split('_')[1]
    message = callback.message
    distance = callback.data.split('_')[2:]
    connect, cursor = connect_db(DB_NAME1)
    if distance == ['all']:
        await get_all_distances(message, id)
    else:
        distance = '_'.join(map(str, distance))
        cursor.execute(f"SELECT {distance} FROM users WHERE user_id = ?", (id,))
        data = cursor.fetchone()
        await callback.message.answer(f"{TO_RUS_DISTANCE[distance]} - {data[0]}")


@router.message(Command('leaderboard'))
async def check_leaderboard(message: types.Message):
     try:
        connect, cursor = connect_db(DB_NAME4)
        cursor.execute("SELECT user_id, name, surname, points FROM leaderboard")
        data = cursor.fetchall()
        sorted_data = await get_leaderboard_table(message, data)
        if message.from_user.id not in sorted_data and message.from_user.id != ADMIN:
            cursor.execute("SELECT points FROM leaderboard WHERE user_id = ?", (message.from_user.id, ))
            swimcoin = cursor.fetchone()
            if swimcoin and swimcoin[0] != '-':
                swimcoin = int(swimcoin[0])
                place, swimcoins_to_lvl = await get_no_leaders(message, message.from_user.id, data)
                if place == 1:
                    await message.answer(f"У вас {swimcoin} swimcoin(s)🟡\n"
                                         f"Поздравляю!Ты - лидер!🥳\n"
                                         f"И любимчик тренера 😉")
                else:
                    await message.answer(f"У вас {swimcoin} swimcoin(s)🟡\n"
                                         f"Ваше место {place}\n"
                                         f"до {place-1} места {round(swimcoins_to_lvl, 1)} swimcoin(s)")
     except Exception as e:
        logging.error(f"Произошла ошибка: {e}")

@router.message(Command('last_season'))
async def check_season1(message: types.Message):
    await message.answer("Победители прошлого сезона:\n"
                         "1 место - Баландин Степан😎\n"
                         "2 место - Рзянин Артём🤟\n"
                         "3 место - Шабанов Никита👍")
    
# get season2
@router.message(Command('season2'))
async def check_season2(message: types.Message):
    try:
        connect, cursor = connect_db(DB_NAME4)
        cursor.execute("SELECT user_id, name, surname, season2 FROM leaderboard")
        data = cursor.fetchall()
        sorted_data = await get_leaderboard_table(message, data, ind=10)
        if message.from_user.id not in sorted_data and message.from_user.id != ADMIN:
            cursor.execute("SELECT season2 FROM leaderboard WHERE user_id = ?", (message.from_user.id,))
            swimcoin = cursor.fetchone()
            if swimcoin and swimcoin[0] != '-':
                swimcoin = int(swimcoin[0])
                place, swimcoins_to_lvl = await get_no_leaders(message, message.from_user.id, data)
                if place == 1:
                    await message.answer(f"У вас {swimcoin} swimcoin(s)🟡\n"
                                         f"Поздравляю!Ты - лидер!🥳")
                else:
                    await message.answer(f"У вас {swimcoin} swimcoin(s)🟡\n"
                                         f"Ваше место {place}\n"
                                         f"до {place - 1} места {round(swimcoins_to_lvl, 1)} swimcoin(s)")
        await message.answer(f"1 мая откроется магазин, где за\n"
                             f"свимкойны можно купить призы\n"
                             f"1 место свимкойны х2\n"
                             f"2 место х1.5\n"
                             f"3 место х1.3\n"
                             f"4 место х1.2\n"
                             f"5 место х1.1\n"
                             f"<em>Сезон кончается 31 мая 2025</em>", parse_mode="html")
    except Exception as e:
        logging.error(f"Произошла ошибка: {e}")



# get diary
@router.message(Command('diary'))
async def get_diary(message: types.Message):
    try:
        id = message.from_user.id
        if await check_id_in_users(id):
            await select_swimmer(message, 'kidsdiary_')
        else:
            await get_kb_diary(message, id)
    except Exception as e:
        logging.error(f"Произошла ошибка: {e}")

# get diary for parent's kid
@router.callback_query(F.data.startswith('kidsdiary'))
async def for_kb_diary(callback: CallbackQuery):
    id = str(callback.data.split('_')[1])
    message = callback.message
    await get_kb_diary(message, id)

# # check last lesson result finisher
# @router.callback_query(F.data.startswith('lesson_'))
# async def last_lesson(callback: CallbackQuery):
#     my_id = str(callback.data.split('_')[1])
#     connect, cursor = connect_db(DB_NAME3)
#     cursor.execute(f"SELECT date, meteres_last, mark_last, comment FROM results WHERE user_id = {my_id}")
#     data = cursor.fetchone()
#     day = data[0]
#     meteres = data[1]
#     mark = data[2]
#     comment = data[-1]
#     await callback.message.answer(f"На тренировке {day} числа\n"
#                                   f"🏊 Проплыто метров - {meteres}\n"
#                                   f"5️⃣ Оценка - {mark}\n"
#                                   f"📝 Комментарий тренера - '{comment}'")

# get last lesson results
@router.callback_query(F.data.startswith('lesson_'))
async def last_lesson(callback: CallbackQuery):
    my_id = str(callback.data.split('_')[1])
    connect, cursor = connect_db(DB_NAME3)
    cursor.execute(f"SELECT date, mark_last, comment, meteres_last FROM results WHERE user_id = {my_id}")
    data = cursor.fetchone()
    day = data[0].split('_')[-1]
    mark = data[1].split('_')[-1]
    comment = data[2].split('_,')[-1]
    meteres = data[3].split('_')[-1]
    await callback.message.answer(f"На тренировке {day} числа\n"
                                  f"🏊 Проплыто метров - {meteres}\n"
                                  f"5️⃣ Оценка - {mark}\n"
                                  f"📝 Комментарий тренера - '{comment}'")

# get last lesson results
@router.callback_query(F.data.startswith('tenlastlesson_'))
async def ten_last_lesson(callback: CallbackQuery):
    my_id = str(callback.data.split('_')[1])
    connect, cursor = connect_db(DB_NAME3)
    cursor.execute(f"SELECT date, mark_last, comment, meteres_last FROM results WHERE user_id = {my_id}")
    data = cursor.fetchone()
    days = data[0].split('_')[::-1]
    marks = data[1].split('_')[::-1]
    comments = data[2].split('_,')[::-1]
    meteres = data[3].split('_')[::-1]
    r = 10 if len(days) > 10 else len(days)
    for i in range(r):
        if days[i] != '-':
            await callback.message.answer(f"На тренировке {days[i]} числа\n"
                                        f"🏊 Проплыто метров - {meteres[i]}\n"
                                        f"5️⃣ Оценка - {marks[i]}\n"
                                        f"📝 Комментарий тренера - '{comments[i]}'")

# check mark mean finisher
@router.callback_query(F.data.startswith('markmean'))
async def get_all_marks(callback: CallbackQuery):
    my_id = str(callback.data.split('_')[1])
    message = callback.message
    await get_mark_mean(message, my_id)

# check meteres mean finisher
@router.callback_query(F.data.startswith('meanmeteres_'))
async def get_mean_meteres(callback: CallbackQuery):
    my_id = str(callback.data.split('_')[1])
    message = callback.message
    await get_meteres_info(message, my_id)

# vote for 1 place present
# @router.message(Command("vote"))
# async def get_vote(message: types.Message):
#     id = message.from_user.id
#     await message.answer(
#         "Выберите вариант:",
#         reply_markup=InlineKeyboardMarkup(inline_keyboard=[
#             [InlineKeyboardButton(text='💂Шапочка с оригинальным принтом', callback_data='votes_1')],
#             [InlineKeyboardButton(text='🧸Набор игрушек антистресс', callback_data='votes_2')],
#             [InlineKeyboardButton(text='💳Сертификат на озон/вб 1500руб', callback_data='votes_3')],
#             [InlineKeyboardButton(text='🍬🥚Kinder набор', callback_data='votes_4')],
#             [InlineKeyboardButton(text='📊Показать результаты голосования', callback_data='show_results')]
#         ])
#     )

# # add vote and get vote table
# @router.callback_query(F.data.startswith('votes'))
# async def add_vote(callback: CallbackQuery):
#     if callback.from_user.id not in VOTERS_ID:
#         if callback.data == 'votes_1':
#             POLL_RESULTS['option_1'] += 1
#         elif callback.data == 'votes_2':
#             POLL_RESULTS['option_2'] += 1
#         elif callback.data == 'votes_3':
#             POLL_RESULTS['option_3'] += 1
#         elif callback.data == 'votes_4':
#             POLL_RESULTS['option_4'] += 1
#         if callback.from_user.id != ADMIN:
#             VOTERS_ID.append(callback.from_user.id)
#         await callback.message.answer("Ваш голос учтен!")
#     else:
#         await callback.message.answer("Вы уже голосовали!")
#     await show_results(callback.message)

# @router.callback_query(F.data.startswith('show'))
# async def show_vote_res(callback: CallbackQuery):
#     await show_results(callback.message)


