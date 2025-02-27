import sqlite3

from datetime import datetime


def create_database() -> None:
    conn = sqlite3.connect('database/DATABASE.sql')
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS database ('
                'id INTEGER PRIMARY KEY AUTOINCREMENT,'
                'ident text,'
                'time_water text,'
                'time_electro text,'
                'personal_id int)')
    conn.commit()
    cur.close()
    conn.close()


def insert_data_and_ident(ident, time_water,time_electro):
    conn = sqlite3.connect('database/DATABASE.sql')
    cur = conn.cursor()
    cur.execute('INSERT INTO database (ident,time_water,time_electro) VALUES (?,?,?)', (ident, time_water,time_electro))
    conn.commit()
    cur.close()
    conn.close()


def get_all_personal_ids():
    conn = sqlite3.connect('database/DATABASE.sql')
    cur = conn.cursor()
    cur.execute('SELECT personal_id FROM database')
    ids_list = cur.fetchall()
    cur.close()
    conn.close()
    return ids_list


def get_id_for_premises(ident: str) -> int:
    conn = sqlite3.connect('database/DATABASE.sql')
    cur = conn.cursor()
    cur.execute(f'SELECT id FROM database WHERE ident = "{ident}"')
    id_ = cur.fetchall()
    cur.close()
    conn.close()
    return id_[0][0]


def get_premises_ident():
    conn = sqlite3.connect('database/DATABASE.sql')
    cur = conn.cursor()
    cur.execute('SELECT ident FROM database')
    ident_list = cur.fetchall()
    cur.close()
    conn.close()
    return ident_list


def check_personal(id_):
    conn = sqlite3.connect('database/DATABASE.sql')
    cur = conn.cursor()
    cur.execute(f'SELECT personal_id FROM database WHERE id = "{id_}"')
    rezult = cur.fetchone()
    cur.close()
    conn.close()
    print(rezult)
    if str(rezult[0]) == 'None':
        return True
    else:
        return False


def check_personal_without_comand(user_id):
    conn = sqlite3.connect('database/DATABASE.sql')
    cur = conn.cursor()
    cur.execute(f'SELECT ident,time_water,time_electro FROM database WHERE personal_id = "{user_id}"')
    data = cur.fetchall()
    cur.close()
    conn.close()
    if data == []:
        return False

    else:
        return data


def insert_personl_id_and(comand,user_id):
    conn = sqlite3.connect('database/DATABASE.sql')
    cur = conn.cursor()
    cur.execute(f'UPDATE database SET personal_id = "{user_id}" WHERE id = "{comand}"')
    conn.commit()
    cur.close()
    conn.close()


def check_ident(ident):
    conn = sqlite3.connect('database/DATABASE.sql')
    cur = conn.cursor()
    cur.execute(f'SELECT ident FROM database')
    data = cur.fetchall()
    cur.close()
    conn.close()
    for elem in data:
        if str(elem[0]) == ident:
            return True
    else:
        return False


def select_personal_id_by_ident(ident):
    conn = sqlite3.connect('database/DATABASE.sql')
    cur = conn.cursor()
    cur.execute(f'SELECT personal_id FROM database WHERE ident = "{ident}"')
    id = cur.fetchall()
    cur.close()
    conn.close()
    return id


def update_day_water(ident,day_water):
    conn = sqlite3.connect('database/DATABASE.sql')
    cur = conn.cursor()
    cur.execute(f'UPDATE database SET time_water = "{day_water}" WHERE ident = "{ident}"')
    conn.commit()
    cur.close()
    conn.close()

def update_day_electro(ident,day_electro):
    conn = sqlite3.connect('database/DATABASE.sql')
    cur = conn.cursor()
    cur.execute(f'UPDATE database SET time_electro = "{day_electro}" WHERE ident = "{ident}"')
    conn.commit()
    cur.close()
    conn.close()


def check_day(user_id):
    conn = sqlite3.connect('database/DATABASE.sql')
    cur = conn.cursor()
    cur.execute(f'SELECT time FROM database WHERE personal_id = "{user_id}"')
    data = cur.fetchone()
    cur.close()
    conn.close()
    return data[0]


def add_another_oject_to_personal(ident,personal_id,day_water,day_electro):
    conn = sqlite3.connect('database/DATABASE.sql')
    cur = conn.cursor()
    cur.execute(f'INSERT INTO database (ident,time_water,time_electro,personal_id) VALUES ("{ident}","{day_water}","{day_electro}","{personal_id}")')
    conn.commit()
    cur.close()
    conn.close()


def select_personal_id_by_day_water(day: str):
    conn = sqlite3.connect('database/DATABASE.sql')
    cur = conn.cursor()
    cur.execute(f'SELECT personal_id FROM database WHERE time_water = "{day}"')
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

def select_personal_id_by_day_electro(day: str):
    conn = sqlite3.connect('database/DATABASE.sql')
    cur = conn.cursor()
    cur.execute(f'SELECT personal_id FROM database WHERE time_electro = "{day}"')
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data
