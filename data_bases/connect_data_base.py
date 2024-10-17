import sqlite3
import pandas as pd

DB_NAME1 = "users.db"
DB_NAME2 = "parents.db"
DB_NAME3 = "results.db"
DB_NAME4 = "leaderboard.db"
POLL_RESULTS = {
    'option_1': 0,
    'option_2': 0,
    'option_3': 0,
    'option_4': 0
}
VOTERS_ID = []
DF = pd.read_csv('files/swim_schedule.csv', parse_dates=['Дата'])
# Установка столбца с датой в качестве индекса
DF.set_index('Дата', inplace=True)
ADMIN = 1372933011

def connect_db(db_name):
    connect = sqlite3.connect(db_name)
    cursor = connect.cursor()
    return (connect, cursor)