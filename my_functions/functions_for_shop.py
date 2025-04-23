import logging
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from data_bases.connect_data_base import connect_db, DB_NAME1, DB_NAME2, DB_NAME4
from my_functions.my_functions import check_id_in_users


async def select_swimmer_for_shop(callback: CallbackQuery, text):
    try:
        buttons = await generate_buttons(callback.message.chat.id, text)
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        await callback.message.answer("За чьи swicoins банкет?", reply_markup=keyboard)
    except Exception as e:
        logging.error(f"Произошла ошибка: {e}")

async def generate_buttons(user_id, prefix):
    buttons = []
    if not await check_id_in_users(user_id):
        swimmer_name = get_swimmer_name(user_id)
        button_data = f"{prefix}_{user_id}_{swimmer_name}"
        buttons.append([InlineKeyboardButton(text=swimmer_name, callback_data=button_data)])
    else:
        for child_id in get_children_ids(user_id):
            swimmer_name = get_swimmer_name(int(child_id))
            button_data = f"{prefix}_{child_id}_{swimmer_name}"
            buttons.append([InlineKeyboardButton(text=swimmer_name, callback_data=button_data)])
    return buttons

def get_swimmer_name(user_id):
    connect, cursor = connect_db(DB_NAME1)
    cursor.execute("SELECT swimmer_name FROM users WHERE user_id = ?", (user_id,))
    return cursor.fetchone()[0]

def get_children_ids(user_id):
    connect, cursor = connect_db(DB_NAME2)
    cursor.execute("SELECT children FROM parents WHERE user_id = ?", (user_id,))
    children = cursor.fetchone()[0]
    return children.split('_')


async def get_points(user_id):
    connect, cursor = connect_db(DB_NAME4)
    cursor.execute("SELECT season2 FROM leaderboard WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    points = result[0] if result else '-'
    return 0 if points == '-' else int(points)


# Общая функция для создания кнопок
def create_buttons(
        yes_prefix: str,
        user_id: str
) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="✅ДА", callback_data=f"{yes_prefix}_{user_id}")],
        [InlineKeyboardButton(text="❌НЕТ", callback_data="shops2")],
        [InlineKeyboardButton(text="↩️Выбрать другую награду", callback_data="shops2")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

async def handle_purchase(
        callback: CallbackQuery,
        prefix: str,
        yes_callback_prefix: str,
        price: int
):
    try:
        user_id = callback.data.split('_')[-2]
        points = await get_points(user_id)

        keyboard = create_buttons(yes_callback_prefix, user_id)

        await callback.message.answer(
            f"У вас {points} 💲swimcoins\n"
            f"Купить {prefix} за {price} 💲swimcoins?",
            reply_markup=keyboard
        )
    except Exception as e:
        logging.error(f"Ошибка при обработке покупки: {e}")


async def execute_purchase(
        callback: CallbackQuery,
        price: int,
        present_type: str,
        success_message: str
):
    user_id = callback.data.split('_')[-1]
    connect, cursor = None, None

    try:
        connect, cursor = connect_db(DB_NAME4)

        # Получаем текущий баланс
        cursor.execute("SELECT season2 FROM leaderboard WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        current_balance = int(result[0]) if result and result[0] not in ['', '-'] else 0

        if current_balance < price:
            await callback.message.answer("Недостаточно 💲swimcoins")
            return

        # Обновляем баланс
        cursor.execute(
            "UPDATE leaderboard SET season2 = season2 - ? WHERE user_id = ?",
            (price, user_id))

        # Добавляем подарок
        cursor.execute(
            "UPDATE leaderboard SET presents2 = COALESCE(presents2, '') || ? WHERE user_id = ?",
            (f"{present_type}_", user_id))

        connect.commit()

        # Получаем новый баланс
        cursor.execute("SELECT season2 FROM leaderboard WHERE user_id = ?", (user_id,))
        new_balance = cursor.fetchone()[0]

        await callback.message.answer(
            f"Спасибо за покупку!✨\n"
            f"{success_message}\n"
            f"У вас осталось {new_balance} 💲swimcoins"
        )

    except Exception as e:
        logging.error(f"Ошибка при обработке покупки: {str(e)}")
        await callback.message.answer("Произошла ошибка при обработке запроса")
    finally:
        if cursor:
            cursor.close()
        if connect:
            connect.close()