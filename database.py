"""
Interaction with sqlite database
"""
import sqlite3
from sqlite3 import Error


def register_database():
    """Database creation"""
    try:
        result = sqlite3.connect('test_database.db')
        return result
    except:
        return Error


def init_cursor():
    """
    Initialization of the cursor
    :rtype: object
    :return cursor:
    """
    try:
        result = CON.cursor()
        return result
    except:
        return Error


def create_table(table_name, attributes):
    """
    Create table
    :param string table_name: table name
    :param list[string] attributes: table attributes
    """
    try:
        CURSOR.execute(
            "CREATE table if not exists {} {}".format(table_name, tuple(attributes)))
        CON.commit()
    except:
        print(Error)


def delete_table(table_name):
    """Delete table"""
    try:
        CURSOR.execute("DROP table if exists {}".format(table_name))
        CON.commit()
    except:
        print(Error)


def get_tables():
    """
    :return list: all tables names from database
    """
    try:
        CURSOR.execute('SELECT name from sqlite_master where type= "table"')
        return CURSOR.fetchall()
    except:
        print(Error)
        return list()


def insert_into_table(table_name, entry_data):
    """
    Write to the database
    :param string table_name: table name
    :param list entry_data: entry data
    """
    try:
        q_marks = '?,' * (len(entry_data) - 1) + '?'
        query = "INSERT INTO {} VALUES({})".format(table_name, q_marks)
        CURSOR.execute(query, entry_data)
        CON.commit()
    except:
        print(Error)


def remove_from_table(table_name, data):
    """
    Remove data from database
    :param string table_name: table name
    :param dictionary data: key - table attribute, val - value
    """
    cond = ""
    for key, val in data.items():
        cond += "{} = {},\n".format(key, val)

    sql = "DELETE from {} WHERE {}".format(table_name, cond[:-2])
    print(sql)

    try:
        CURSOR.execute(sql)
        CON.commit()
    except:
        print(Error)


def data_from_table(table_name, attributes, conditions):
    """
    Get a selection from the database
    :param string table_name: table name
    :param list, list attributes: table attributes
    :param list, list conditions: conditions for selection
    :return : list
    """
    att = ""
    for attribute in attributes:
        att += attribute + ',\n'

    if len(att) != 0:
        att = att[:-2]
    else:
        att = "*"

    cond = ""
    for condition in conditions:
        cond += condition + ',\n'

    if len(cond) != 0:
        cond = "WHERE " + cond[:-2]

    try:
        sql = "SELECT {} FROM {} {}".format(att, table_name, cond)
        print(sql)
        CURSOR.execute(sql)
        return CURSOR.fetchall()
    except:
        print(Error)
        return list()


def customized_query(sql, all_entries):
    """
    Make customized query
    :param string sql: your query text
    :param bool all_entries: if true - return all entries, else - return one entrie
    :return: query result
    """
    try:
        CURSOR.execute(sql)
        return CURSOR.fetchall() if all_entries else CURSOR.fetchone()
    except:
        print(Error)
        return list()


CON = register_database()
CURSOR = init_cursor()