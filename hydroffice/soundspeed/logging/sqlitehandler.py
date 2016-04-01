from __future__ import absolute_import, division, print_function, unicode_literals

import sqlite3
import logging
import time


initial_sql = """CREATE TABLE IF NOT EXISTS log(
                    TimeStamp TEXT,
                    Source TEXT,
                    LogLevel INT,
                    LogLevelName TEXT,
                    Message TEXT,
                    Args TEXT,
                    Module TEXT,
                    FuncName TEXT,
                    LineNo INT,
                    Exception TEXT,
                    Process INT,
                    Thread TEXT,
                    ThreadName TEXT
               )"""

insertion_sql = """INSERT INTO log(
                    TimeStamp,
                    Source,
                    LogLevel,
                    LogLevelName,
                    Message,
                    Args,
                    Module,
                    FuncName,
                    LineNo,
                    Exception,
                    Process,
                    Thread,
                    ThreadName
               )
               VALUES (
                    '%(dbtime)s',
                    '%(name)s',
                    %(levelno)d,
                    '%(levelname)s',
                    '%(msg)s',
                    '%(args)s',
                    '%(module)s',
                    '%(funcName)s',
                    %(lineno)d,
                    '%(exc_text)s',
                    %(process)d,
                    '%(thread)s',
                    '%(threadName)s'
               );
               """

count_logs_sql = "SELECT COUNT(*) FROM log"

delete_logs_sql = "DELETE FROM log WHERE rowid NOT in (SELECT rowid FROM log ORDER BY rowid DESC LIMIT 3000)"


class SQLiteHandler(logging.Handler):
    """ Thread-safe logging handler for SQLite. """

    def __init__(self, db='logger.db'):
        logging.Handler.__init__(self)
        self.db = db
        conn = sqlite3.connect(self.db)
        conn.execute(initial_sql)
        logs_nr = conn.execute(count_logs_sql).fetchone()[0]
        if logs_nr > 10000:  # if there are more than 10,000 logs, delete them excepct the last 3,000
            conn.execute(delete_logs_sql)
        conn.commit()  # not efficient, but thread-safe

    def format_time(self, record):
        """ Create a time stamp """
        record.dbtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(record.created))

    def emit(self, record):
        self.format(record)
        self.format_time(record)
        if record.exc_info:  # for exceptions
            record.exc_text = logging._defaultFormatter.formatException(record.exc_info)
        else:
            record.exc_text = ""

        # Insert the log record
        sql = insertion_sql % record.__dict__
        conn = sqlite3.connect(self.db)
        conn.execute(sql)
        conn.commit()  # not efficient, but thread-safe
