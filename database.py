import sqlite3 as sql
from sqlite3 import Error

def register_database():

    try:
        con = sql.connect('test_database.db')
        return con
    except:
        print(Error)

def init_cursor():

    try:
        cursor = con.cursor()
        return cursor
    except:
        print(Error)

    
def create_table():

    cursor.execute("""
                   create table if not exists users (user_name, tgm_name, cf_handle)
                   """)
    con.commit()

def insert_into_users(user_data):

    user_created = is_in_table(user_data[0][1])
    if (user_created):
        return
    cursor.executemany("""INSERT INTO users VALUES(?, ?, ?)""", user_data)
    con.commit()

def user_data_struct(user_name, tgm_name, cf_handle):

    return [(user_name, tgm_name, cf_handle)]

def user_data_by_tgm_name(tgm_name):

    sql = "SELECT * FROM users WHERE tgm_name = ?"
    cursor.execute(sql, [(tgm_name)])
    return cursor.fetchall()

def add_user(user_name, tgm_name, cf_handle = ""):

    user = user_data_struct(user_name, tgm_name, cf_handle)
    insert_into_users(user)

def is_in_table(tgm_name):

    return bool(len(user_data_by_tgm_name(tgm_name))) 

def update_cf_handle(tgm_name, new_handle):

    cursor.execute('UPDATE users SET cf_handle = ? where tgm_name = ?', [(new_handle), (tgm_name)])
    con.commit()
    
con = register_database()
cursor = init_cursor()
create_table()


