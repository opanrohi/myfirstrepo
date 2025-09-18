import sqlite3 as sql
from datetime import datetime


def create_table() -> None:
    connection = sql.connect('userbase.db')
    cursor = connection.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS users(
       user_id INT PRIMARY KEY,
       user_name TEXT,
       FIO TEXT,
       branch TEXT,
       score INT,
       time BIGINT);
       """)
    connection.commit()

    cursor.execute("""CREATE TABLE IF NOT EXISTS users_stations(
           user_id INT,
           question_id INT,
           question_group INT,
           time DATETIME,
           question_opened bit,
           CONSTRAINT [users_stations_PK] PRIMARY KEY (user_id, question_id, question_group),
           CONSTRAINT [FK_stations_users] FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE);
           """)
    connection.commit()

    cursor.execute("""CREATE TABLE IF NOT EXISTS flags(
               finished bit,
               closed bit);
               """)

    cursor.execute("insert into flags values(0, 1)")
    connection.commit()

    connection.close()


def drop_table():
    connection = sql.connect('userbase.db')
    cursor = connection.cursor()

    cursor.execute("""drop TABLE IF EXISTS users
           """)
    cursor.execute("""drop TABLE IF EXISTS users_stations
               """)

    cursor.execute("""drop TABLE IF EXISTS flags
                   """)
    connection.commit()
    connection.close()


def get_finished_flag():
    connection = sql.connect('userbase.db')
    cursor = connection.cursor()

    cursor.execute(f"""
                    select finished from flags;
                    """)
    result = cursor.fetchall()
    connection.close()
    if result[0][0] == 0:
        return False
    else:
        return True


def set_finished_flag(flag: bool):
    connection = sql.connect('userbase.db')
    cursor = connection.cursor()

    cursor.execute(f"""
                    update flags set finished = '{int(flag)}';
                    """)
    connection.commit()
    connection.close()


def get_closed_flag():
    connection = sql.connect('userbase.db')
    cursor = connection.cursor()

    cursor.execute(f"""
                    select closed from flags;
                    """)
    result = cursor.fetchall()
    connection.close()
    if result[0][0] == 0:
        return False
    else:
        return True


def set_closed_flag(flag: bool):
    connection = sql.connect('userbase.db')
    cursor = connection.cursor()

    cursor.execute(f"""
                    update flags set closed = '{int(flag)}';
                    """)
    connection.commit()
    connection.close()


def add_user(user_id: int, user_name: str) -> None:
    connection = sql.connect('userbase.db')
    cursor = connection.cursor()

    cursor.execute(f"""insert into users
    values('{user_id}', '{user_name}', '', '', 0, 0)""")
    connection.commit()
    connection.close()


def set_user_fio(user_id: int, fio: str) -> None:
    connection = sql.connect('userbase.db')
    cursor = connection.cursor()

    cursor.execute(f"""Update users
                   set FIO = '{fio}'
                   where user_id = '{user_id}';""")

    connection.commit()
    connection.close()


def set_user_branch(user_id: int, branch: str) -> None:
    connection = sql.connect('userbase.db')
    cursor = connection.cursor()

    cursor.execute(f"""Update users
                   set branch = '{branch}'
                   where user_id = '{user_id}';""")

    connection.commit()
    connection.close()


def get_auth(user_id: int) -> []:
    connection = sql.connect('userbase.db')
    cursor = connection.cursor()

    cursor.execute(f"""
                    select FIO, branch from users
                    where user_id = {user_id}
                    """)
    result = cursor.fetchall()
    connection.close()

    if len(result) > 0:
        return result[0]
    else:
        return []


def get_users_list() -> []:
    connection = sql.connect('userbase.db')
    cursor = connection.cursor()

    cursor.execute(f"SELECT * FROM users;")
    result = cursor.fetchall()
    connection.close()
    return result


def get_stations_list() -> []:
    connection = sql.connect('userbase.db')
    cursor = connection.cursor()

    cursor.execute(f"SELECT * FROM users_stations;")
    result = cursor.fetchall()
    connection.close()
    return result


def drop_user(user_id: int) -> None:
    connection = sql.connect('userbase.db')
    cursor = connection.cursor()

    cursor.execute(f"delete from users"
                   f" where user_id = '{user_id}';")

    cursor.execute(f"delete from users_stations"
                   f" where user_id = '{user_id}';")

    connection.commit()
    connection.close()


def get_first_group_stations(user_id: int) -> []:
    connection = sql.connect('userbase.db')
    cursor = connection.cursor()

    cursor.execute(f"""
    SELECT question_id, question_opened FROM users_stations where user_id = '{user_id}' and question_group = 0
    order by question_opened;""")
    string_result = cursor.fetchall()
    connection.close()

    try:
        return string_result
    except:
        return []


def get_second_group_stations(user_id: int) -> []:
    connection = sql.connect('userbase.db')
    cursor = connection.cursor()

    cursor.execute(f"""
    SELECT question_id, question_opened FROM users_stations where user_id = '{user_id}' and question_group = 1 
    order by question_opened;
""")
    string_result = cursor.fetchall()
    connection.close()

    try:
        return string_result
    except:
        return []


def get_third_group_stations(user_id: int) -> []:
    connection = sql.connect('userbase.db')
    cursor = connection.cursor()

    cursor.execute(f"""
    SELECT question_id, question_opened FROM users_stations where user_id = '{user_id}' and question_group = 2 
    order by question_opened;""")
    string_result = cursor.fetchall()
    connection.close()

    try:
        return string_result
    except:
        return []


def open_station(user_id: int, question_id: int, group: int) -> None:
    connection = sql.connect('userbase.db')
    cursor = connection.cursor()

    cursor.execute(f"""insert into users_stations
                   values('{user_id}', '{question_id}', '{group}', '{datetime.now()}', 1);""")

    connection.commit()
    connection.close()


def get_time_delt(user_id: int, question_id: int, group: int) -> int:
    connection = sql.connect('userbase.db')
    cursor = connection.cursor()

    cursor.execute(f"""
    SELECT time FROM users_stations 
    where user_id = '{user_id}' and question_group = '{group}' and question_id = '{question_id}'
    """)
    result = cursor.fetchall()
    connection.close()

    try:
        return (datetime.now() - datetime.fromisoformat(result[0][0])).seconds
    except:
        return -1


def close_station(user_id: int, question_id: int, group: int) -> None:
    connection = sql.connect('userbase.db')
    cursor = connection.cursor()

    cursor.execute(f"""Update users_stations
                   set question_opened = 0
                   where user_id = '{user_id}' and question_id = '{question_id}' and question_group = '{group}';""")

    connection.commit()
    connection.close()


def get_score(user_id: int) -> int:
    connection = sql.connect('userbase.db')
    cursor = connection.cursor()

    cursor.execute(f"SELECT score FROM users where user_id = '{user_id}';")
    string_result = cursor.fetchall()
    result = string_result[0][0]

    connection.close()
    return result


def get_oi_leaders_list() -> []:
    connection = sql.connect('userbase.db')
    cursor = connection.cursor()

    cursor.execute(f"""SELECT * FROM users where branch = 'ОИТ'
order by score desc, time;""")
    string_result = cursor.fetchall()

    connection.close()
    return string_result[:3]


def get_oe_leaders_list() -> []:
    connection = sql.connect('userbase.db')
    cursor = connection.cursor()

    cursor.execute(f"""SELECT * FROM users where branch = 'ОЭиС'
order by score desc, time;""")
    string_result = cursor.fetchall()

    connection.close()
    return string_result[:3]


def get_om_leaders_list() -> []:
    connection = sql.connect('userbase.db')
    cursor = connection.cursor()

    cursor.execute(f"""SELECT * FROM users where branch = 'ОМЭиКС'
order by score desc, time;""")
    string_result = cursor.fetchall()

    connection.close()
    return string_result[:3]


def get_oo_leaders_list() -> []:
    connection = sql.connect('userbase.db')
    cursor = connection.cursor()

    cursor.execute(f"""SELECT * FROM users where branch = 'ООПНиПТ'
order by score desc, time;""")
    string_result = cursor.fetchall()

    connection.close()
    return string_result[:3]


def add_score(user_id: int, value: int) -> None:
    connection = sql.connect('userbase.db')
    cursor = connection.cursor()

    score = int(get_score(user_id)) + value

    cursor.execute(f"""
    Update users
    set score = {score}
    where user_id = '{user_id}';
    """)

    connection.commit()
    connection.close()


def get_time(user_id: int) -> int:
    connection = sql.connect('userbase.db')
    cursor = connection.cursor()

    cursor.execute(f"SELECT time FROM users where user_id = '{user_id}';")
    string_result = cursor.fetchall()
    result = string_result[0][0]

    connection.close()
    return result


def add_time(user_id: int, value: int) -> None:
    connection = sql.connect('userbase.db')
    cursor = connection.cursor()

    time = int(get_time(user_id)) + value

    cursor.execute(f"""
    Update users
    set time = {time}
    where user_id = '{user_id}';
    """)

    connection.commit()
    connection.close()


def user_exist(user_id: int) -> bool:
    connection = sql.connect('userbase.db')
    cursor = connection.cursor()

    cursor.execute(f"SELECT * FROM users where user_id = {user_id};")
    result = cursor.fetchall()
    connection.close()

    if len(result) != 0:
        return True
    else:
        return False


def get_stat():
    connection = sql.connect('userbase.db')
    cursor = connection.cursor()

    cursor.execute(f"SELECT * FROM users where branch = 'ОИТ' order by score desc, time;")
    result = cursor.fetchall()
    connection.close()

    temp1 = get_oo_leaders_list()
    temp2 = get_oi_leaders_list()
    temp3 = get_om_leaders_list()
    temp4 = get_oe_leaders_list()

    for elem in temp4:
        print(f"{elem[2]} \t {elem[4]} \t {elem[5]}")
