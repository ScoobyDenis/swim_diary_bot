import sqlite3
from aiogram.filters import Command, CommandObject
from aiogram.types import CallbackQuery
from lexicon.lexicon_ru import ADMIN_MENU
from my_functions.functions_for_leaderboard import *
from my_functions.my_functions import *
from aiogram import Router, F

router = Router()


# get admin menu
@router.message(Command('admin'))
async def admin_menu(message: types.Message):
    if message.from_user.id == ADMIN:
        await message.answer(ADMIN_MENU)

# add time for swimmer
@router.message(Command('add_time'))
async def add_time(message: types.Message, command: CommandObject):
    args = command.args.split()
    connect, cursor = connect_db(DB_NAME1)
    try:
        cursor.execute(f"UPDATE users SET {args[1]} = {args[2]} WHERE user_id = {args[0]}")
        connect.commit()
        cursor.execute(f"SELECT swimmer_name, swimmer_surname FROM users WHERE user_id = {args[0]}")
        data = cursor.fetchone()
        await message.answer(f"Для {data[0]} {data[1]}\n"
                             f"добавлено {args[1]} = {args[2]}")
    except IndexError:
        await message.answer("Неверное количество данных")
    except sqlite3.OperationalError:
        await message.answer("Неправильное название дистанции или время не в том формате")

# add swimmer to parent
@router.message(Command("add_child_to_parent"))
async def add_child(message: types.Message, command: CommandObject):
    id_parent, id_swimmer = command.args.split()
    connect, cursor = connect_db(DB_NAME2)
    try:
        cursor.execute(f"SELECT children FROM parents WHERE user_id = {id_parent}")
        data = cursor.fetchone()
    except:
        await message.answer("Не правильное id родителя")
    try:
        if data[0] == '-':
            cursor.execute(f"UPDATE parents SET children = {id_swimmer} WHERE user_id = {id_parent}")
        else:
            cursor.execute(f"UPDATE parents SET children = '{str(data[0]) + '_' + str(id_swimmer)}' WHERE user_id = {id_parent}")
        connect.commit()

        cursor.execute(f"SELECT parent_name, parent_surname FROM parents WHERE user_id = {id_parent}")
        data2 = cursor.fetchone()
        connect, cursor = connect_db(DB_NAME1)
        cursor.execute(f"SELECT swimmer_name, swimmer_surname FROM users WHERE user_id = {id_swimmer}")
        data1 = cursor.fetchone()
        await message.answer(f"к родителю {data2[0]} {data2[1]}\n"
                             f"прикреплен {data1[0]} {data1[1]}")
    except Exception as e:
        await message.answer(f"Ошибка {e}\n"
                             f"Скорее всего неправильный id родителя")


@router.message(Command('train_result')) # id day metres mark comment
async def add_train_result(message: types.Message, command: CommandObject):
    args = command.args.split()
    id = int(args[0])
    if not await check_id_in_users(id):
        day = str(datetime.now().date() - timedelta(days=int(args[1])))
        meteres = args[2]
        mark = args[3]
        try:
            comment = ' '.join(word.strip("'") for word in args[4:])
            connect, cursor = connect_db(DB_NAME3)
            cursor.execute("UPDATE results SET date = date || '_' || ?, meteres_last = meteres_last || '_' || ?, "
                           "mark_last = mark_last || '_' || ?, "
                           "comment = comment || '_' || ?, meteres = meteres + ?, "
                           "mark = mark + ?, "
                           "total_lessons = total_lessons + 1 WHERE user_id = ?",
                           (day, meteres, mark, ',' + comment, int(meteres), int(mark), id))
            connect.commit()
            await pick_info_and_add(message, day, id, int(meteres), int(mark))
        except:
            await message.answer("Нет комментария")

        await message.answer(f"Для пловца {id} добавлено: \n"
                             f"Метров - {meteres}\n"
                             f"Оценка - {mark}\n"
                             f"Комментарий - {comment}\n"
                             f"Дата - {day}")
    else:
        await message.answer(f"Нет пловца с id {id}")
        
# delete parent
@router.message(Command("del_parent"))
async def del_parent(message: types.Message, command: CommandObject):
    id = command.args.split()[0]
    connect, cursor = connect_db(DB_NAME2)
    cursor.execute('DELETE FROM parents WHERE user_id = ?', (id,))
    connect.commit()
    await message.answer(f"Родитель с id {id} удален")

# delete swimmer
@router.message(Command("del_swimmer"))
async def del_swimmer(message: types.Message, command: CommandObject):
    try:
        id = command.args.split()[0]
        connect, cursor = connect_db(DB_NAME1)
        cursor.execute('DELETE FROM users WHERE user_id = ?', (id,))
        connect.commit()
        connect, cursor = connect_db(DB_NAME4)
        cursor.execute('DELETE FROM leaderboard WHERE user_id = ?', (id,))
        connect.commit()
        await message.answer(f"Пловец с id {id} удален")
    except:
        await message.answer("Неверное id")

# change swimmer name
@router.message(Command("change_swimmer_name"))
async def change_swimmer_name(message: types.Message, command: CommandObject):
    try:
        id, name = command.args.split()
        connect, cursor = connect_db(DB_NAME1)
        cursor.execute("UPDATE users SET swimmer_name = ? WHERE user_id = ?", (name, id))
        connect.commit()
        connect, cursor = connect_db(DB_NAME4)
        cursor.execute("UPDATE leaderboard SET name = ? WHERE user_id = ?", (name, id))
        connect.commit()
        await message.answer(f"Имя обновлено на {name}")
    except Exception as e:
        await message.answer(f"ошибка {e}")

# change swimmer surname
@router.message(Command("change_swimmer_surname"))
async def change_swimmer_name(message: types.Message, command: CommandObject):
    try:
        id, surname = command.args.split()
        connect, cursor = connect_db(DB_NAME1)
        cursor.execute("UPDATE users SET swimmer_surname = ? WHERE user_id = ?", (surname, id))
        connect.commit()
        connect, cursor = connect_db(DB_NAME4)
        cursor.execute("UPDATE leaderboard SET surname = ? WHERE user_id = ?", (surname, id))
        connect.commit()
        await message.answer(f"Фамилия обновлена на {surname}")
    except Exception as e:
        await message.answer(f"ошибка {e}")

# change swimmer's year of birth
@router.message(Command("change_swimmer_year"))
async def change_swimmer_age(message: types.Message, command: CommandObject):
    try:
        id, year = command.args.split()
        connect, cursor = connect_db(DB_NAME1)
        cursor.execute("UPDATE users SET year = ? WHERE user_id = ?", (year, id))
        connect.commit()
        await message.answer(f"Год рождения обновлен на {year}")
    except Exception as e:
        await message.answer(f"ошибка {e}")

# show text distances for admin
@router.message(Command("show_distances"))
async def show_distances(message: types.Message):
    await message.answer("freestyle_25m, freestyle_50m, \n"
                         "freestyle_100m, freestyle_400m,\n"
                         "backstroke_25m, backstroke_50m, \n"
                         "backstroke_100m, breaststroke_25m, \n"
                         "breaststroke_50m, breaststroke_100m, \n"
                         "butterfly_25m, butterfly_50m, \n"
                         "medley_100m, medley_200m, medley_400m")

# check records handler
@router.message(Command("check_time_for_admin"))
async def check_time_for_admin(message: types.Message):
    buttons = []
    connect, cursor = connect_db(DB_NAME1)
    cursor.execute("SELECT user_id, swimmer_name, swimmer_surname FROM users")
    swimmers = cursor.fetchall()
    for swimmer in swimmers:
        button_text = f"records_{swimmer[0]}"
        buttons.append([InlineKeyboardButton(text=f"{swimmer[1]} {swimmer[2]}", callback_data=button_text)])
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=buttons
    )
    await message.answer("Выбрать пловца", reply_markup=keyboard)

# get all records from swimmer
@router.callback_query(F.data.startswith('records'))
async def distances(callback: CallbackQuery):
    id = int(callback.data.split('_')[1])
    message = callback.message
    await get_all_distances(message, id)

# get keyboard with parents
@router.message(Command("get_parents_kids_info"))
async def get_parents_kids(message: types.Message):
    connect, cursor = connect_db(DB_NAME2)
    cursor.execute("SELECT user_id, parent_name, parent_surname FROM parents")
    parents = cursor.fetchall()
    buttons = []
    for parent in parents:
        button_text = f"kids_{parent[0]}"
        buttons.append([InlineKeyboardButton(text=f"{parent[1]} {parent[2]}", callback_data=button_text)])
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=buttons
    )
    await message.answer("Выберите родителя", reply_markup=keyboard)

# get kids id for admin
@router.callback_query(F.data.startswith('kids'))
async def get_parents_kid(callback: CallbackQuery):
    id = int(callback.data.split('_')[1])
    connect, cursor = connect_db(DB_NAME2)
    cursor.execute("SELECT children FROM parents WHERE user_id = ?", (id,))
    children = cursor.fetchone()[0].split('_')
    await callback.message.answer(f"id: {children}")

# get date for cancel training
@router.message(Command("cancel_admin"))
async def admin_cancel(message: types.Message):
    kb = await create_date_keyboard(mode='cancel')
    await message.answer("Выберите день", reply_markup=kb)

# get time for cancel training
@router.callback_query(F.data.startswith('createcancel_'))
async def get_time_for_admin_cancel(callback: CallbackQuery):
    message = callback.message
    kb = await create_time_keyboard(message, callback.data[13:], mode='cancel')
    await callback.message.edit_text("Выберите время", reply_markup=kb)

# cancel training from swim_schedule
@router.callback_query(F.data.startswith("adds_cancel_admin_"))
async def process_time_cancel_button_press(callback: CallbackQuery):
    date = callback.data.split('_')[3]
    time = callback.data.split('_')[4]
    DF.loc[date, time] = None
    DF.to_csv('files/swim_schedule.csv')
    await callback.message.answer(f"Запись на {date} в {time} отменена")

# send msg to parents
@router.message(Command("msg_to_parents"))
async def send_msg_to_parents(message: types.Message, command: CommandObject):
    msg = command.args
    connect, cursor = connect_db(DB_NAME2)
    cursor.execute("SELECT user_id FROM parents")
    ids = cursor.fetchall()
    for id in ids:
        await bot.send_message(id[0], msg)

# send msg to swimmers
@router.message(Command("msg_to_swimmers"))
async def send_msg_to_swimmers(message: types.Message, command: CommandObject):
    msg = command.args
    connect, cursor = connect_db(DB_NAME1)
    cursor.execute("SELECT user_id FROM users")
    ids = cursor.fetchall()
    for id in ids:
        try:
            if id[0] > 1000:
                await bot.send_message(id[0], msg)
        except Exception as e:
            logging.error(e)

@router.message(Command("add_leader"))
async def add_leader(message: types.Message, command: CommandObject):
    try:
        id = int(command.args)
        connect, cursor = connect_db(DB_NAME1)
        cursor.execute("SELECT swimmer_name, swimmer_surname FROM users WHERE user_id = ?", (id, ))
        data = cursor.fetchone()
        name = data[0]
        surname = data[1]
        await create_new_leaderboard_user(id)
        await set_swimmer_name_to_leaderboard(name, id)
        await set_swimmer_surname_to_leaderboard(surname, id)
    except Exception as e:
        logging.error(e)

@router.message(Command("add_db_res"))
async def add_leader(message: types.Message, command: CommandObject):
    try:
        id = int(command.args)
        connect, cursor = connect_db(DB_NAME1)
        cursor.execute("SELECT swimmer_name FROM users WHERE user_id = ?", (id, ))
        data = cursor.fetchone()
        name = data[0]
        connect, cursor = connect_db(DB_NAME3)
        data = [id, name, '-', '-', '-', '-', 0, 0, 0]
        cursor.execute(
            "INSERT INTO results (user_id, swimmer_name, date, meteres_last, mark_last, comment, meteres, mark, total_lessons) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)",
            data)
        connect.commit()
    except Exception as e:
        logging.error(e)

@router.message(Command("del_leader"))
async def del_swimmer(message: types.Message, command: CommandObject):
    try:
        id = command.args.split()[0]
        connect, cursor = connect_db(DB_NAME4)
        cursor.execute('DELETE FROM leaderboard WHERE user_id = ?', (id,))
        connect.commit()
        await message.answer(f"Лидер с id {id} удален")
    except:
        await message.answer("Неверное id")

@router.message(Command("change_kid_id"))
async def change_kid_id(message: types.Message, command: CommandObject):
    connect,cursor = connect_db(DB_NAME2)
    par_id, kid_id = command.args.split()
    try:
        cursor.execute("UPDATE parents SET children = ? WHERE user_id = ?", (kid_id, par_id))
        connect.commit()
    except Exception as e:
        logging.error(e)
    finally:
        connect.close()

@router.message(Command("add_swimcoins"))
async def add_swimcoins(message: types.Message, command: CommandObject):
    id, swimcoins = command.args.split()
    connect, cursor = connect_db(DB_NAME4)
    try:
        cursor.execute("UPDATE leaderboard SET season2 = ? WHERE user_id = ?", (swimcoins, id))
        connect.commit()
    except Exception as e:
        logging.error(e)
    finally:
        connect.close()

@router.message(Command("add_new_seasons"))
async def add_new_season(message: types.Message):
    connect, cursor = connect_db(DB_NAME4)
    try:
        cursor.execute("ALTER TABLE leaderboard ADD COLUMN season5 REAL")
        cursor.execute("ALTER TABLE leaderboard ADD COLUMN season6 REAL")
        connect.commit()
        print("Колонки season5-8 успешно добавлены")
    except Exception as e:
        print(f"Колонки уже существуют или ошибка: {e}")


@router.message(Command("update_seasons"))
async def update_users_season(message: types.Message):
    # Запустите эту функцию один раз
    update_existing_users_with_seasons()
    fix_existing_users()

def fix_existing_users():
    """Добавляет недостающие сезоны существующим пользователям"""
    connect, cursor = connect_db(DB_NAME4)

    try:
        # Проверяем, какие колонки есть
        cursor.execute("PRAGMA table_info(leaderboard)")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"Колонки в таблице: {columns}")

        # Проверяем и добавляем недостающие сезоны
        seasons_to_check = ['season5', 'season6', 'season7', 'season8']
        for season in seasons_to_check:
            if season not in columns:
                print(f"Добавляем колонку {season}...")
                cursor.execute(f"ALTER TABLE leaderboard ADD COLUMN {season} TEXT DEFAULT '-'")

        # Обновляем NULL значения на '-'
        for season in seasons_to_check:
            cursor.execute(f"UPDATE leaderboard SET {season} = '-' WHERE {season} IS NULL")

        # Также проверяем presents2
        cursor.execute("UPDATE leaderboard SET presents2 = '-' WHERE presents2 IS NULL")

        connect.commit()

        # Показываем статистику
        cursor.execute("SELECT COUNT(*) FROM leaderboard")
        total = cursor.fetchone()[0]

        for season in seasons_to_check:
            cursor.execute(f"SELECT COUNT(*) FROM leaderboard WHERE {season} = '-'")
            count = cursor.fetchone()[0]
            print(f"  {season}: {count}/{total} пользователей имеют '-'")

        print("✅ Существующие пользователи обновлены")

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        connect.rollback()
    finally:
        connect.close()