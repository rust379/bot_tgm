"""
Interaction with mysql database

"""

from enum import Enum
import pymysql
from pymysql import Error


class Database:
    """database"""

    def __init__(self):
        """Connect to database"""

        self.connection = pymysql.connect(host="127.0.0.1",
                                          user="root",
                                          password="K2wnzo",
                                          database="test_mysql_db",
                                          charset="utf8mb4",
                                          cursorclass=pymysql.cursors.DictCursor)
        self.cursor = self.connection.cursor()
        self.cursor.execute("USE {};".format("test_mysql_db"))

    def create_table(self, table_name, attributes):
        """
        Create table

        :param string table_name: table name
        :param list[string] attributes: table attributes,
            consists of NAME TYPE PRIMARY KEY(optional) NOT NULL
            ex. "`user_id` INT PRIMARY KEY NOT NULL", "`user_name` TEXT NOT NULL"

        """
        try:
            block_attributes = query_block(attributes, ",")
            query = "CREATE TABLE IF NOT EXISTS {} ({});".format(table_name, block_attributes)
            self.cursor.execute(query)
            self.connection.commit()
        except Error as err:
            print("Database", err)

    def delete_table(self, table_name):
        """Delete table"""
        try:
            query = "DROP TABLE IF exists {};".format(table_name)
            self.cursor.execute(query)
            self.connection.commit()
        except Error as err:
            print("Database", err)

    def table_names(self, full: bool = False):
        """
        Get table names from the database

        :param bool full: show table type
        :return: all tables names from database
        """
        try:
            if full:
                self.cursor.execute("SHOW FULL TABLES")
            else:
                self.cursor.execute("SHOW TABLES")
            return self.cursor.fetchall()
        except Error as err:
            print("Database", err)
            return list()

    def table_info(self, table_name):
        """
        Get all columns in table

        :param string table_name: table name
        :return: table info
        """
        try:
            self.cursor.execute("SHOW COLUMNS FROM {}".format(table_name))
            return self.cursor.fetchall()
        except Error as err:
            print("Database", err)
            return list()

    def table_struct(self, table_name):
        """
        Get table struct in CREATE TABLE format

        :param string table_name: table name
        :return: table info
        """
        try:
            self.cursor.execute("SHOW CREATE TABLE {}".format(table_name))
            return self.cursor.fetchall()
        except Error as err:
            print("Database", err)
            return list()

    def rename_table(self, cur_name, new_name):
        """
        Rename table
        :param string cur_name: current table name
        :param string new_name: new table name
        """
        query = "RENAME TABLE {} to {}".format(cur_name, new_name)

        try:
            self.cursor.execute(query)
            self.connection.commit()
        except Error as err:
            print("Database", err)

    def add_column(self, table_name, column_name):
        """
        Add column to the table
        :param string table_name: table name
        :param string column_name: column name
        """
        query = "ALTER TABLE {} ADD {}".format(table_name, column_name)

        try:
            self.cursor.execute(query)
            self.connection.commit()
        except Error as err:
            print("Database", err)

    def change_column(self, table_name, old_column_name, new_column):
        """
        Change column in the table
        :param string table_name: table name
        :param string old_column_name: current column name
        :param string new_column: new column characteristics
        """
        query = "ALTER TABLE {} CHANGE COLUMN {} {}".format(table_name, old_column_name, new_column)

        try:
            self.cursor.execute(query)
            self.connection.commit()
        except Error as err:
            print("Database", err)

    def delete_column(self, table_name, column_name):
        """
        Delete column from the table

        :param string table_name: table name
        :param string column_name: column name
        """
        query = "ALTER TABLE {} DROP COLUMN {}".format(table_name, column_name)

        try:
            self.cursor.execute(query)
            self.connection.commit()
        except Error as err:
            print("Database", err)

    def insert_into_table(self, table_name, entry_data):
        """
        Write to the database

        :param string table_name: table name
        :param list entry_data: list of data records
        """
        try:
            columns = self.table_info(table_name)
            block_column = ""
            for column in columns:
                block_column += column["Field"] + ", "


            entry_data_str = []
            for data in entry_data:
                if data is None:
                    data = "NULL"
                if isinstance(data, str):
                    entry_data_str.append("'{}'".format(data))
                else:
                    entry_data_str.append("{}".format(data))

            block_column = block_column[:-2]
            data = query_block(entry_data_str, ",")
            query = "INSERT {}({}) VALUES({});".format(table_name, block_column, data)
            self.cursor.execute(query)

            self.connection.commit()
        except Error as err:
            print("Database", err)

    def remove_from_table(self, table_name, data):
        """
        Remove data from database

        :param string table_name: table name
        :param list[string] data: record key, ex. 'user = "tourist"'
        """
        cond_block = query_block(data)

        query = "DELETE FROM {} WHERE {}".format(table_name, cond_block)

        try:
            self.cursor.execute(query)
            self.connection.commit()
        except Error as err:
            print("Database", err)

    def update_record(self, table_name, key_condition, new_value):
        """
        Updating data in a table cell
        :param string table_name: table name
        :param list key_condition: Search criteria for the desired entry
            ex. ("user = 'Rust'", "cf_handle != 'tourist'")
        :param string new_value: New value of a cell, ex. "user_age = 146"
        """
        block_condition = query_block(key_condition, " AND")

        query = "UPDATE {} \nSET {} \nWHERE {}".format(table_name, new_value, block_condition)

        try:
            self.cursor.execute(query)
            self.connection.commit()
        except Error as err:
            print("Database", err)

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
        :return dictionary: column name : record value
        """
        if extra_parameter is None:
            extra_parameter = get_request_struct()

        block_attribute = query_block(extra_parameter["attributes"], ",")
        block_condition = query_block(extra_parameter["conditions"], " AND")
        block_group = query_block(extra_parameter["group"], ",")
        block_having = query_block(extra_parameter["having"], ",")
        block_order = query_block(extra_parameter["order"], ",")

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
            query = "SELECT {} FROM {} {} {} {} {}".format(
                block_attribute,
                table_name,
                block_condition,
                block_group,
                block_having,
                block_order)
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Error as err:
            print("Database", err)
            return dict()

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
            print("Database", err)
            return list()


def get_request_struct():
    """
    Get structure of sql queries

    :return: structure of sql queries
    """
    struct = {"attributes": list(),
              "conditions": list(),
              "group": list(),
              "having": list(),
              "order": list()
              }
    return struct


def query_block(block_value, union: str = ""):
    """
    Creates a query block
    :param list[strings] block_value: values
    :param string union: union in block
    :return string: block for query
    """
    block = ""
    for cur_value in block_value:
        block += str(cur_value) + union + "\n"

    length = len(union) + 1
    if block:
        block = block[:-length]

    return block


class Datatype(Enum):
    """
        Enum allowable value types
        BOOL - bool
        TEXT_100 - str, text up to 100 characters
        TEXT_200 - str, text up to 200 characters
        TEXT - str,  text up to 16 MB long
        INT  - int,  integers from -2 * 10^9 to 2 * 10^9
        U_INT - unsigned int, integers from 0 to 4 * 10^9
        BIGINT - int,  integers from -9 * 10^18 to 9 * 10^18
        FLOAT - float, fractional numbers from -3.4028 * 10^38 to 3.4028 * 10^38
        DATE - dates from January 1, 1000 to December 31, 9999, format: "yyyy-mm-dd"
        TIME - time from -838:59:59 to 838:59:59 format:"hh:mm:ss"
        DATETIME - combines TIME and DATE
        TIMESTAMP - date and time, in the range: from "1970-01-01 00: 00:01" UTC
            to "2038-01-19 03:14:07" UTC
        BLOB - binary data as a string up to 16 MB long
    """
    BOOL = "BOOL"
    TEXT_100 = "VARCHAR(100)"
    TEXT_200 = "VARCHAR(200)"
    TEXT = "MEDIUMTEXT"
    INT = "INT"
    U_INT = "INT UNSIGNED"
    BIGINT = "BIGINT"
    FLOAT = "FLOAT"
    DATE = "DATE"
    TIME = "TIME"
    DATETIME = "DATETIME"
    TIMESTAMP = "TIMESTAMP"
    BLOB = "MEDIUMBLOB"


class Column:
    """Class for table column in Database"""

    def __init__(self,
                 name: str = "",
                 datatype: Datatype = Datatype.TEXT,
                 primary_key: bool = False,
                 not_null: bool = True):
        """
        Initializing the column object
        :param str name: column name
        :param bool primary_key: if column is primary key
        :param bool not_null: False if in column could be NULL
        """
        self.name = name
        self.datatype = datatype
        self.primary_key = primary_key
        self.not_null = not_null

    def to_list(self):
        """
        converts the structure to a list
        :return list[str]: [attribute, primary_key (optional)]
        """
        if self.primary_key:
            self.not_null = True
        not_null_str = "NOT NULL"
        if not self.not_null:
            not_null_str = "NULL"
        attribute = "`{}` {} {}".format(self.name, self.datatype.value, not_null_str)
        primary_key = "PRIMARY KEY (`{}`)".format(self.name)

        if self.primary_key:
            return [attribute, primary_key]
        return [attribute]

    def to_str(self):
        """
        converts the structure to str
        :return str: "`table_name` COLUMN_TYPE PRIMARY KEY"
        """
        if self.primary_key:
            self.not_null = True
        not_null_str = "NOT NULL"
        if not self.not_null:
            not_null_str = "NULL"
        attribute = "`{}` {} {}".format(self.name, self.datatype.value, not_null_str)
        primary_key = "PRIMARY KEY (`{}`)".format(self.name)

        if self.primary_key:
            return attribute + primary_key
        return attribute
