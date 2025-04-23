from aiogram.types import CallbackQuery
from aiogram.filters import Command, CommandObject
from aiogram import F, types
from aiogram import Router

from my_functions.functions_for_shop import select_swimmer_for_shop, handle_purchase, execute_purchase
from my_functions.my_functions import *

router = Router()

@router.message(Command('shop'))
async def get_web_shop(message: types.Message):
    await message.answer(
        "🏪магазин",
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.InlineKeyboardButton(
                        text="🌐Посмотреть товары",
                        url="https://scoobydenis.github.io/swim_shop/"
                    ),
                    types.InlineKeyboardButton(
                        text="📦Начать покупки",
                        callback_data='shops2'
                    )
                ]
            ]
        )
    )

@router.callback_query(F.data.startswith('shops2'))
async def get_season2_shop(callback: CallbackQuery):
    inline_kb = []
    inline_kb.append([InlineKeyboardButton(text="🖼️1 стикер", callback_data="sticker")])
    inline_kb.append([InlineKeyboardButton(text="🖼️1 стикер на выбор", callback_data="open_sticker")])
    inline_kb.append([InlineKeyboardButton(text=" 🖼️🖼️🖼️ набор стикеров", callback_data="pack_stickers")])
    inline_kb.append([InlineKeyboardButton(text="🐥1 сквиш", callback_data="squish")])
    inline_kb.append([InlineKeyboardButton(text="🐾1 сквиш на выбор", callback_data="open_squish")])
    inline_kb.append([InlineKeyboardButton(text="🧸1 игрушка антистресс", callback_data="antistress")])
    inline_kb.append([InlineKeyboardButton(text="🧸1 антистресс на выбор🧸", callback_data="open_antistress")])
    inline_kb.append([InlineKeyboardButton(text="💳сертификат на Ozon(2000руб)", callback_data="small_sertificate")])
    inline_kb.append([InlineKeyboardButton(text="💳сертификат на Ozon(5000руб)", callback_data="big_sertificate")])
    inline_kb.append([InlineKeyboardButton(text="📱Iphone16 Pro Max 1tb", callback_data="iphone")])
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=inline_kb
    )
    await callback.message.answer("Выберите подарок", reply_markup=keyboard)

@router.callback_query(F.data.startswith('sticker'))
async def buy_sticker(callback: CallbackQuery):
    await select_swimmer_for_shop(callback, 'process_sticker')

@router.callback_query(F.data.startswith('open_sticker'))
async def buy_open_sticker(callback: CallbackQuery):
    await select_swimmer_for_shop(callback, 'open_process_sticker')

@router.callback_query(F.data.startswith('pack_stickers'))
async def buy_pack_sticker(callback: CallbackQuery):
    await select_swimmer_for_shop(callback, 'pack_process_sticker')

@router.callback_query(F.data.startswith('squish'))
async def buy_squish(callback: CallbackQuery):
    await select_swimmer_for_shop(callback, 'process_squish')

@router.callback_query(F.data.startswith('open_squish'))
async def buy_open_squish(callback: CallbackQuery):
    await select_swimmer_for_shop(callback, 'open_process_squish')

@router.callback_query(F.data.startswith('antistress'))
async def buy_antistress(callback: CallbackQuery):
    await select_swimmer_for_shop(callback, 'process_antistress')

@router.callback_query(F.data.startswith('open_antistress'))
async def buy_open_antistress(callback: CallbackQuery):
    await select_swimmer_for_shop(callback, 'open_process_antistress')

@router.callback_query(F.data.startswith('small_sertificate'))
async def buy_small_sertificate(callback: CallbackQuery):
    await select_swimmer_for_shop(callback, 'process_small_sertificate')

@router.callback_query(F.data.startswith('big_sertificate'))
async def buy_big_sertificate(callback: CallbackQuery):
    await select_swimmer_for_shop(callback, 'process_big_sertificate')

@router.callback_query(F.data.startswith('iphone'))
async def buy_iphone(callback: CallbackQuery):
    await select_swimmer_for_shop(callback, 'process_iphone')


@router.callback_query(F.data.startswith('process_sticker_'))
async def process_buy_sticker(callback: CallbackQuery):
    await handle_purchase(callback=callback, prefix='🖼️стикер', yes_callback_prefix='finish_sticker', price=700)

@router.callback_query(F.data.startswith('open_process_sticker_'))
async def process_buy_open_sticker(callback: CallbackQuery):
    await handle_purchase(callback=callback, prefix='🖼️стикер на выбор🖼️', yes_callback_prefix='finish_open_sticker', price=800)

@router.callback_query(F.data.startswith('pack_process_sticker_'))
async def process_buy_pack_sticker(callback: CallbackQuery):
    await handle_purchase(callback=callback, prefix='🖼️🖼️🖼️набор стикеров(50шт)', yes_callback_prefix='finish_pack_sticker', price=10000)

@router.callback_query(F.data.startswith('process_squish_'))
async def process_buy_squish(callback: CallbackQuery):
    await handle_purchase(callback=callback, prefix='🐥сквиш', yes_callback_prefix='finish_squish', price=2200)

@router.callback_query(F.data.startswith('open_process_squish_'))
async def process_buy_open_squish(callback: CallbackQuery):
    await handle_purchase(callback=callback, prefix='🐾сквиш на выбор', yes_callback_prefix='finish_open_squish', price=2500)

@router.callback_query(F.data.startswith('process_antistress_'))
async def process_buy_antistress(callback: CallbackQuery):
    await handle_purchase(callback=callback, prefix='🧸антистресс', yes_callback_prefix='finish_antistress', price=4000)

@router.callback_query(F.data.startswith('open_process_antistress_'))
async def process_buy_open_antistress(callback: CallbackQuery):
    await handle_purchase(callback=callback, prefix='🧸антистресс на выбор🧸', yes_callback_prefix='finish_open_antistress', price=5000)

@router.callback_query(F.data.startswith('process_small_'))
async def process_buy_small_sertificate(callback: CallbackQuery):
    await handle_purchase(callback=callback, prefix='💳сертификат(2000руб)', yes_callback_prefix='finish_small', price=30000)

@router.callback_query(F.data.startswith('process_big_'))
async def process_buy_big_sertificate(callback: CallbackQuery):
    await handle_purchase(callback=callback, prefix='💳сертификат(5000руб)', yes_callback_prefix='finish_big', price=50000)

@router.callback_query(F.data.startswith('process_iphone'))
async def process_buy_big_iphone(callback: CallbackQuery):
    await handle_purchase(callback=callback, prefix='📱Iphone16 Pro Max 1tb', yes_callback_prefix='finish_iphone', price=150000)


@router.callback_query(F.data.startswith('finish_sticker_'))
async def process_end_buy_sticker(callback: CallbackQuery):
    await callback.message.answer("Покупки возможны с 19мая")
    #await execute_purchase(callback=callback, price=700, present_type="стикер", success_message="Денис передаст стикер в ближайшее время")


@router.callback_query(F.data.startswith('finish_open_sticker_'))
async def process_end_buy_open_sticker(callback: CallbackQuery):
    await callback.message.answer("Покупки возможны с 19мая")
    #await execute_purchase(callback=callback, price=800, present_type="стикер(на выбор)",
    #                       success_message="Денис передаст стикер(на выбор) в ближайшее время")

@router.callback_query(F.data.startswith('finish_pack_sticker_'))
async def process_end_buy_pack_sticker(callback: CallbackQuery):
    await callback.message.answer("Покупки возможны с 19мая")
    #await execute_purchase(callback=callback, price=10000, present_type="набор стикеров",
    #                       success_message="Денис передаст набор стикеров в ближайшее время")


@router.callback_query(F.data.startswith('finish_squish_'))
async def process_end_buy_squish(callback: CallbackQuery):
    await callback.message.answer("Покупки возможны с 19мая")
    #await execute_purchase(callback=callback, price=2200, present_type="сквиш",
    #                       success_message="Денис передаст сквиш в ближайшее время")



@router.callback_query(F.data.startswith('finish_open_squish_'))
async def process_end_buy_open_squish(callback: CallbackQuery):
    await callback.message.answer("Покупки возможны с 19мая")
    #await execute_purchase(callback=callback, price=2500, present_type="сквиш(на выбор)",
    #                       success_message="Денис передаст сквиш(на выбор) в ближайшее время")

@router.callback_query(F.data.startswith('finish_antistress_'))
async def process_end_buy_antistress(callback: CallbackQuery):
    await callback.message.answer("Покупки возможны с 19мая")
    # await execute_purchase(callback=callback, price=4000, present_type="антистресс",
    #                     success_message="Денис передаст антистресс в ближайшее время")


@router.callback_query(F.data.startswith('finish_open_antistress_'))
async def process_end_buy_open_antistress(callback: CallbackQuery):
    await callback.message.answer("Покупки возможны с 19мая")
    #await execute_purchase(callback=callback, price=5000, present_type="антистресс(на выбор)",
    #                      success_message="Денис передаст антистресс(на выбор) в ближайшее время")

@router.callback_query(F.data.startswith('finish_small_'))
async def process_end_buy_small(callback: CallbackQuery):
    await callback.message.answer("Покупки возможны с 19мая")
    #await execute_purchase(callback=callback, price=30000, present_type="сертификат(2000руб)",
    #                      success_message="Денис передаст сертификат(2000руб) в ближайшее время")


@router.callback_query(F.data.startswith('finish_big_'))
async def process_end_buy_open_big(callback: CallbackQuery):
    await callback.message.answer("Покупки возможны с 19мая")
    #await execute_purchase(callback=callback, price=50000, present_type="антистресс(на выбор)",
    #                   success_message="Денис передаст сертификат(5000руб) в ближайшее время")

@router.callback_query(F.data.startswith('finish_iphone_'))
async def process_end_buy_iphone(callback: CallbackQuery):
    await callback.message.answer("Покупки возможны с 19мая")
    #await execute_purchase(callback=callback, price=150000, present_type="Iphone",
    #                   success_message="Денис передаст Iphone в ближайшее время")

@router.message(Command("basket"))
async def get_swimmers_presents(message: types.Message):
    try:
        if not await check_id_in_users(message.from_user.id):
            buttons = []
            connect, cursor = connect_db(DB_NAME1)
            cursor.execute(f"SELECT swimmer_name FROM users WHERE user_id = {message.from_user.id}")
            data = cursor.fetchone()[0]
            button_text = f"allpresents_{str(message.from_user.id) + '_' + data}"
            buttons.append([InlineKeyboardButton(text=data, callback_data=button_text)])
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=buttons
            )
            await message.answer("Выберите пловца", reply_markup=keyboard)
        else:
            await select_swimmer(message, 'allpresents_')
    except Exception as e:
       logging.error(f"Произошла ошибка: {e}")

@router.callback_query(F.data.startswith('allpresents_'))
async def get_all_presents(callback: CallbackQuery):
    try:
        id = str(callback.data.split('_')[1])
        connect, cursor = connect_db(DB_NAME4)
        cursor.execute("SELECT presents2 FROM leaderboard WHERE user_id = ?", (id,))
        presents = cursor.fetchone()
        if not presents or not presents[0]:
            await callback.message.answer("У вас пока нет покупок 🛍️")
            return
        presents = presents[0]
        items = [item for item in presents.split('_') if item]
        presents_dict = {}
        for item in items:
            presents_dict[item] = presents_dict.get(item, 0) + 1
        if presents_dict:
            formatted_items = [f"• {key}: {value}" for key, value in presents_dict.items()]
            result_text = "🛍️ Ваши покупки:\n" + "\n".join(formatted_items)
        else:
            result_text = "Нет данных для отображения 😢"

        await callback.message.answer(result_text)
    except Exception as e:
        await callback.message.answer(e)
    finally:
        connect.close()

@router.message(Command("mult_swimcoins"))
async def mult_swimcoins_for_leaders(message: types.Message, command: CommandObject):
    try:
        id = command.args.split()[0]
        mult = command.args.split()[1]
        connect, cursor = connect_db(DB_NAME4)
        cursor.execute('UPDATE leaderboard SET season2 = season2 * ? WHERE user_id = ?', (mult, id,))
        connect.commit()
    except Exception as e:
        logging.error(e)
    finally:
        connect.close()