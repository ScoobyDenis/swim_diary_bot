import asyncio
from aiogram import Bot, Dispatcher
from config_data.config import Config, load_config
from handlers import main_handlers, stats_handlers, registr_handlers, menu_handlers, admin_handlers, shop_handlers
from data_bases.connect_data_base import connect_db, DB_NAME1, DB_NAME2, DB_NAME3, DB_NAME4
from set_menu.parent_menu import set_parent_menu

# Функция конфигурирования и запуска бота
async def main():
    # Загружаем конфиг в переменную config
    config: Config = load_config()

    # Инициализируем бот и диспетчер
    bot = Bot(token=config.tg_bot.token)
    dp = Dispatcher()

    # Регистриуем роутеры в диспетчере
    dp.include_router(shop_handlers.router)
    dp.include_router(main_handlers.router)
    dp.include_router(registr_handlers.router)
    dp.include_router(stats_handlers.router)
    dp.include_router(menu_handlers.router)
    dp.include_router(admin_handlers.router)
    # подключаемся к базе данных
    connect, cursor = connect_db(DB_NAME1)
    cursor.execute("""CREATE TABLE IF NOT EXISTS users(
                user_id INTEGER,
                user_name TEXT,
                swimmer_name TEXT,
                swimmer_surname TEXT,
                year INT,
                month INT,
                day INT,
                freestyle_25m REAL,
                freestyle_50m REAL,
                freestyle_100m REAL,
                freestyle_400m REAL,
                backstroke_25m REAL,
                backstroke_50m REAL,
                backstroke_100m REAL,
                breaststroke_25m REAL,
                breaststroke_50m REAL,
                breaststroke_100m REAL,
                butterfly_25m REAL,
                butterfly_50m REAL,
                medley_100m REAL,
                medley_200m REAL,
                medley_400m REAL
                )
                """)
    connect, cursor = connect_db(DB_NAME2)
    cursor.execute("""CREATE TABLE IF NOT EXISTS parents(
                user_id INTEGER,
                parent_name TEXT,
                parent_surname TEXT,
                children TEXT
                )
                """)
    connect, cursor = connect_db(DB_NAME3)
    cursor.execute("""CREATE TABLE IF NOT EXISTS results(
                    user_id INTEGER,
                    swimmer_name TEXT,
                    date TEXT,
                    meteres_last TEXT,
                    mark_last TEXT,
                    comment TEXT,
                    meteres REAL,
                    mark REAL,
                    total_lessons INTEGER
                    )
                    """)
    connect, cursor = connect_db(DB_NAME4)
    cursor.execute("""CREATE TABLE IF NOT EXISTS leaderboard(
                    user_id INTEGER,
                    name TEXT,
                    surname TEXT,
                    points REAL,
                    season1 REAL,
                    season2 REAL,
                    season3 REAl,
                    season4 REAL,
                    season5 REAL,
                    season6 REAL,
                    season7 REAL,
                    season8 REAL
                    )
                    """)

    # Пропускаем накопившиеся апдейты и запускаем polling
    await set_parent_menu(bot)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

asyncio.run(main())
