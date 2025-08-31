# parent_menu
LEXICON_COMMANDS_RU: dict[str, str] = {
    '/registr': '✍️запись на тренировку',
    '/diary': '📔 дневник пловца',
    '/check_results': '🗓 лучшее время',
    '/season4': '🏅 лидеры сезона',
    #'/shop': '🛍 магазин',
    #'/balance': '👛баланс SwimCoins',
    #'/basket': '🛒купленные товары',
    '/leaderboard': '🏆таблица лидеров за все время', 
    '/last_season': '🥇🥈🥉победители прошлого сезона',
    '/check': '🔍проверка записей',
    '/cancel': '❌отмена записи',
}

# for change name distance
TO_RUS_DISTANCE = {'freestyle_25m': 'вольный стиль 25 м', 'freestyle_50m': 'вольный стиль 50 м',
                    'freestyle_100m': 'вольный стиль 100 м', 'freestyle_400m': 'вольный стиль 400 м',
                    'backstroke_25m': 'на спине 25 м', 'backstroke_50m': 'на спине 50 м',
                    'backstroke_100m': 'на спине 100 м', 'breaststroke_25m': 'брасс 25 м',
                    'breaststroke_50m': 'брасс 50 м', 'breaststroke_100m': 'брасс 100 м',
                    'butterfly_25m': 'баттерфляй 25 м', 'butterfly_50m': 'баттерфляй 50 м',
                    'medley_100m': 'комплексное плавание 100 м',
                    'medley_200m': 'комплексное плавание 200 м', 'medley_400m': 'комплексное плавание 400 м'
                    }

WEEKDAYS = {0: 'Пн', 1: 'Вт', 2: 'Ср', 3: 'Чт', 4: 'Пт', 5: 'Сб', 6: 'Вс'}
BIG_WEEKDAYS = {0: 'Понедельник', 1: 'Вторник', 2: 'Среда', 3: 'Четверг', 4: 'Пятница', 5: 'Суббота', 6: 'Воскресенье'}

# admin menu
ADMIN_MENU = f"/cancel - удалить из расписания\n" \
             f"/fillform - добавление нового пловца(у которого нет телефона)\n" \
             f"/get_users_info -получить id, имена и фамилии\n" \
             f"/get_parents_info - родители\n" \
             f"/get_parents_kids_info - дети родителя\n" \
             f"/msg_to_parents msg - отправить сообщение всем родителям\n" \
             f"/msg_to_swimmers msg - отправить сообщение пловцам\n" \
             f"/day_stat -количество тренировок за день\n" \
             f"/last_week_stat - количество тренировок за прошл неделю\n" \
             f"/week_stat - количество тренировок на текущей неделе\n" \
             f"/last_month_stat - количество тренировок за прошлый месяц\n" \
             f"/month_stat - количество тренировок за текущий месяц\n" \
             f"/today_schedule - расписание на сегодня(можно передать аргумент)\n" \
             f"/show_distances - названия дистанций\n" \
             f"/add_child_to_parent id_par id_swim- прикрепить ребенка\n" \
             f"/del_parent id - удаление родителя\n" \
             f"/del_swimmer id - удаление пловца\n" \
             f"/change_kid_id par_id kid_id - заменить ребенка(id)\n" \
             f"/mult_swimcoins id mult - добавление очков 5 лидерам\n" \
             f"/change_swimmer_name id name - смена имени пловца\n" \
             f"/change_swimmer_surname id surname - смена фамилии пловца\n" \
             f"/change_swimmer_year id year - смена года рождения пловца\n" \
             f"/add_time id distance time - добавление времени\n" \
             f"/train_result id day metres mark comment- добавление результатов тренировки(day=0-сегодня)"
