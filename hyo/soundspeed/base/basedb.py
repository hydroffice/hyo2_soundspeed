from abc import ABCMeta, abstractmethod
import os
import sqlite3

import logging
logger = logging.getLogger(__name__)


class BaseDb(metaclass=ABCMeta):
    """ Abstract class that provides an interface to a SQLite db """

    class Point:
        def __init__(self, x, y):
            self.x, self.y = x, y

        def __repr__(self):
            return "(%f;%f)" % (self.x, self.y)

    @staticmethod
    def adapt_point(point):
        return "%f;%f" % (point.x, point.y)

    @staticmethod
    def convert_point(s):
        x, y = map(float, s.split(";"))
        return BaseDb.Point(x, y)

    @staticmethod
    def clean_name(some_var):
        return ''.join(char for char in some_var if char.isalnum())

    def __init__(self, db_path):
        super(BaseDb, self).__init__()

        self.name = "_DB"
        self.db_path = db_path
        self.conn = None

    def check_table_total_rows(self, table_name, print_out=False):
        """ Returns the total number of rows in the database """
        table_name = BaseDb.clean_name(table_name)

        ret = None
        for ret in self.conn.execute('SELECT COUNT(*) FROM {}'.format(table_name)):
            if print_out:
                print('\nTotal rows: {}'.format(ret[0]))

        return ret[0]

    def check_table_cols_settings(self, table_name, print_out=False):
        """ Returns column information"""
        table_name = BaseDb.clean_name(table_name)

        if print_out:
            print("\nColumn Info:\nID, Name, Type, NotNull, DefaultVal, PrimaryKey")

        info = []
        for ret in self.conn.execute('PRAGMA TABLE_INFO({})'.format(table_name)):
            if print_out:
                print(ret)
            info.append(ret)

        return info

    def check_tables_values_in_cols(self, table_name, print_out=False):
        """ Returns a dictionary with columns as keys and the number of not-null entries

        Args:
            table_name (str):      the name of the table to check
            print_out (bool):      option to print out the result of the query
        Returns:
            dict:                  dictionary with columns as keys and the number of not-null entries
        """
        table_name = BaseDb.clean_name(table_name)

        col_dict = dict()
        for ret in self.conn.execute('PRAGMA TABLE_INFO({})'.format(table_name)):
            col_dict[ret[1]] = 0

        for col in col_dict:
            for ret2 in self.conn.execute('SELECT COUNT({0}) FROM {1} WHERE {0} IS NOT NULL'.format(col, table_name)):
                col_dict[col] = ret2[0]

        if print_out:
            print("\nNumber of entries per column:")
            for i in col_dict.items():
                print('{}: {}'.format(i[0], i[1]))

        return col_dict

    def reconnect_or_create(self):
        """ Reconnection to an existing database or create a new db """
        if self.conn:
            # logger.info("Already connected")
            return

        if not os.path.exists(self.db_path):
            logger.info("New db")

        try:
            self.conn = sqlite3.connect(self.db_path,
                                        detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
            # logger.info("Connected")

        except sqlite3.Error as e:
            raise RuntimeError("Unable to connect: %s" % e)

        try:
            with self.conn:
                self.conn.execute('PRAGMA foreign_keys=ON')
                self.conn.commit()

        except sqlite3.Error as e:
            raise RuntimeError("Unable to activate foreign keys: %s" % e)

        try:
            # Set the row factory
            self.conn.row_factory = sqlite3.Row
            # Register the adapter
            sqlite3.register_adapter(BaseDb.Point, BaseDb.adapt_point)
            # Register the converter
            sqlite3.register_converter("point", BaseDb.convert_point)

        except sqlite3.Error as e:
            raise RuntimeError("Unable to register 'point': %s - %s" % (type(e), e))

        built = self.build_tables()
        if not isinstance(built, bool):
            raise RuntimeError("invalid return from 'build_tables' method, must be boolean")
        if not built:
            raise RuntimeError("Unable to build tables: the DB is encrypted or is not a database")

    @abstractmethod
    def build_tables(self):
        """ Abstract method to be implemented to create tables structure """
        pass

    def disconnect(self):
        """ Disconnect from the current database """
        if self.conn is None:
            # logger.info("Already disconnected")
            return True

        try:
            self.conn.close()
            self.conn = None
            # logger.info("Disconnected")
            return True

        except sqlite3.Error as e:
            logger.error("Unable to disconnect: %s" % e)
            return False

    def close(self):
        self.disconnect()

    def commit(self):
        if self.conn is None:
            return False

        self.conn.commit()
        return True
