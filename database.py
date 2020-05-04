"""
Interaction with sqlite database
"""

import sqlite3
from sqlite3 import Error


class Database():
    """database"""

    def __init__(self):
        """Connect to database"""

        self.connection = sqlite3.connect("test_database.db", check_same_thread=False)
        self.cursor = self.connection.cursor()

    def create_table(self, table_name, attributes):
        """
        Create table

        :param string table_name: table name
        :param list[string] attributes: table attributes,
            consists of NAME TYPE(optional) PRIMARY KEY(optional) NOT NULL(optional)
            ex. "user_id INTEGER PRIMARY KEY", "user_name TEXT NOT NULL"
        """
        try:
            sql = "CREATE table if not exists {} {}".format(table_name, tuple(attributes))
            self.cursor.execute(sql)
            self.connection.commit()
        except Error as err:
            print(err)

    def delete_table(self, table_name):
        """Delete table"""
        try:
            self.cursor.execute("DROP table if exists {}".format(table_name))
            self.connection.commit()
        except Error as err:
            print(err)

    def table_names(self):
        """
        Get table names from the database

        :return: all tables names from database
        """
        try:
            self.cursor.execute("SELECT name from sqlite_master where type= 'table'")
            return self.cursor.fetchall()
        except Error as err:
            print(err)
            return list()

    def table_info(self, table_name):
        """
        Get all columns in table

        :param string table_name: table name
        :return: table info
        """
        try:
            self.cursor.execute("pragma table_info({})".format(table_name))
            return self.cursor.fetchall()
        except Error as err:
            print(err)
            return list()

    def insert_into_table(self, table_name, entry_data):
        """
        Write to the database

        :param string table_name: table name
        :param list entry_data: list of data records
        """
        try:
            q_marks = "?," * (len(entry_data) - 1) + "?"
            query = "INSERT INTO {} VALUES({})".format(table_name, q_marks)
            self.cursor.execute(query, entry_data)
            self.connection.commit()
        except Error as err:
            print(err)

    def remove_from_table(self, table_name, data):
        """
        Remove data from database

        :param string table_name: table name
        :param dictionary data: key - table attribute, val - value
        """
        cond = ""
        for key, val in data.items():
            cond += "{} = {},\n".format(key, val)

        sql = "DELETE from {} WHERE {}".format(table_name, cond[:-2])

        try:
            self.cursor.execute(sql)
            self.connection.commit()
        except Error as err:
            print(err)

    def update_record(self, table_name, key_condition, new_value):
        """
        Updating data in a table cell
        :param string table_name: table name
        :param list key_condition: Search criteria for the desired entry
            ex. ("user = 'Rust'", "cf_handle != 'tourist'")
        :param new_value: New value of a cell, ex. "user_age = 146"
        """
        block_condition = self.__query_block(key_condition, " AND")

        sql = "UPDATE {} \nSET {} \nWHERE {}".format(table_name, new_value, block_condition)

        try:
            self.cursor.execute(sql)
            self.connection.commit()
        except Error as err:
            print(err)

    def data_from_table(self, table_name, extra_parameter: dict = None):
        """
        Get a selection from the database

        :param string table_name: table name
        :param dictionary extra_parameter: see get_request_struct()
        ex. "attributes" : ("user_id", "user_name")
            "conditions" : ("user_id > 2", "user_name = 'Anya'")
            "group" : ("user_age")
            "having" : ("count(user_id) > 3")
            "order" : ("user_name")
        :return: list
        """
        if extra_parameter is None:
            extra_parameter = get_request_struct()

        block_attribute = self.__query_block(extra_parameter["attributes"], ",")
        block_condition = self.__query_block(extra_parameter["conditions"], " AND")
        block_group = self.__query_block(extra_parameter["group"], ",")
        block_having = self.__query_block(extra_parameter["having"], ",")
        block_order = self.__query_block(extra_parameter["order"], ",")

        if not block_attribute:
            block_attribute = "*"
        if block_condition:
            block_condition = "WHERE\n" + block_condition + "\n"
        if block_group:
            block_group = "GROUP BY\n" + block_group + "\n"
        if block_having:
            block_having = "HAVING\n" + block_having + "\n"
        if block_order:
            block_order = "ORDER BY\n" + block_order + "\n"

        try:
            sql = "SELECT {} FROM {} {} {} {} {}".format(
                block_attribute,
                table_name,
                block_condition,
                block_group,
                block_having,
                block_order)
            self.cursor.execute(sql)
            return self.cursor.fetchall()
        except Error as err:
            print(err)
            return list()

    def query(self, sql):
        """
        Make customized query
        :param string sql: your query text
        :return: query result
        """
        try:
            self.cursor.execute(sql)
            return self.cursor.fetchall()
        except Error as err:
            print(err)
            return list()

    def __query_block(self, block_value, union: str = ""):
        """
        Creates a query block
        :param list[string] condition: strings of type 'attribute'
        :param string union: union in block
        :return string: block WHERE for query
        """
        block = ""
        for cur_value in block_value:
            block += cur_value + union + "\n"

        length = len(union) + 1
        if block:
            block = block[:-length]

        return block

def get_request_struct():
    """
    Get structure of sql queries

    :return: structure of sql queries
    """
    struct = {"attributes" : list(),
              "conditions" : list(),
              "group" : list(),
              "having" : list(),
              "order" : list()
              }
    return struct
