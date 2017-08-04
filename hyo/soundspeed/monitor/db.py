import sqlite3
import os
import datetime
import traceback
import numpy as np
import logging

logger = logging.getLogger(__name__)

from hyo.soundspeed import __version__ as version
from hyo.soundspeed import __doc__ as name
from hyo.soundspeed.db.point import Point, convert_point, adapt_point
from hyo.soundspeed.monitor.export import ExportDb


class MonitorDb:
    """Class that provides an interface to a SQLite db with Sound Speed data"""

    def __init__(self, projects_folder=None, base_name=None):

        # in case that no data folder is passed
        if projects_folder is None:
            projects_folder = os.path.abspath(os.path.curdir)
        self.data_folder = projects_folder

        # in case that none is passed as project name
        if base_name is None:
            base_name = "default"
        self.base_name = self.clean_project_name(base_name)

        # the passed project name is used to identify the project database to open
        self.db_path = os.path.join(self.data_folder, self.base_name + ".mon")
        logger.debug('monitor db: %s' % self.db_path)

        # add plotting and exporting capabilities
        self.export = ExportDb(db=self)

        # add variable used to store the connection to the database
        self.conn = None

        self.tmp_data = None
        self.tmp_id = None

        self.reconnect_or_create()

    @staticmethod
    def clean_name(some_var):
        return ''.join(char for char in some_var if char.isalnum())

    @staticmethod
    def clean_project_name(some_var):
        return ''.join(char for char in some_var if char.isalnum() or char in ['-', '_', '.'])

    def reconnect_or_create(self):
        """ Reconnection to an existing database or create a new db """
        if self.conn:
            logger.info("already connected")

        if not os.path.exists(self.db_path):
            logger.info("created a new monitor db")

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
            sqlite3.register_adapter(Point, adapt_point)
            # Register the converter
            sqlite3.register_converter("point", convert_point)

        except sqlite3.Error as e:
            raise RuntimeError("Unable to register 'point': %s - %s" % (type(e), e))

        try:
            # Register the adapter
            sqlite3.register_adapter(np.float32, float)

        except sqlite3.Error as e:
            raise RuntimeError("Unable to register numpy float adapter: %s - %s" % (type(e), e))

        built = self.build_tables()
        if not isinstance(built, bool):
            raise RuntimeError("invalid return from 'build_tables' method, must be boolean")
        if not built:
            raise RuntimeError("Unable to build tables: the DB is encrypted or is not a database")

    def disconnect(self):
        """ Disconnect from the current database """
        if not self.conn:
            # logger.info("Already disconnected")
            return True

        try:
            self.conn.close()
            # logger.info("Disconnected")
            return True

        except sqlite3.Error as e:
            logger.error("Unable to disconnect: %s" % e)
            return False

    def close(self):
        self.disconnect()

    def build_tables(self):
        if not self.conn:
            logger.error("missing db connection")
            return False

        try:
            with self.conn:
                if not self.conn.execute("PRAGMA foreign_keys"):
                    # logger.error("foreign keys not active")
                    return False

                self.conn.execute("""
                                  CREATE TABLE IF NOT EXISTS library(
                                     version int PRIMARY KEY NOT NULL DEFAULT 1,
                                     creator_info text,
                                     creation timestamp NOT NULL)
                                  """)

                # check if the library table is empty
                # noinspection SqlResolve
                ret = self.conn.execute("""SELECT COUNT(*) FROM library""").fetchone()
                # if not present, add it
                if ret[0] == 0:
                    # noinspection SqlResolve
                    self.conn.execute("""
                                      INSERT INTO library VALUES (?, ?, ?)
                                      """, (1, "%s v.%s" % (name, version), datetime.datetime.utcnow(),))

                self.conn.execute("""
                                  CREATE TABLE IF NOT EXISTS data(
                                      id INTEGER PRIMARY KEY,
                                      time timestamp NOT NULL,
                                      position point NOT NULL,
                                      tss real NOT NULL,
                                      draft real NOT NULL,
                                      avg_depth real NOT NULL
                                     )
                                  """)

            return True

        except sqlite3.Error as e:
            logger.error("during building tables, %s: %s" % (type(e), e))
            return False

    def add_point(self, timestamp, long, lat, tss, draft, avg_depth):

        if not isinstance(timestamp, datetime.datetime):
            raise RuntimeError("not passed a valid timestamp: %s" % type(timestamp))
        if not isinstance(long, float):
            raise RuntimeError("not passed a valid type for longitude: %s" % type(long))
        if not isinstance(lat, float):
            raise RuntimeError("not passed a valid type for latitude: %s" % type(lat))
        if not isinstance(tss, float):
            raise RuntimeError("not passed a valid type for tss: %s" % type(tss))
        if not isinstance(draft, float):
            raise RuntimeError("not passed a valid type for draft: %s" % type(draft))
        if not isinstance(avg_depth, float):
            raise RuntimeError("not passed a valid type for avg depth: %s" % type(avg_depth))

        if (long > 180) or (long < -180.0):
            raise RuntimeError("not passed a valid longitude: %s" % long)
        if (lat > 90) or (lat < -90.0):
            raise RuntimeError("not passed a valid latitude: %s" % lat)

        if not self.conn:
            logger.error("missing db connection")
            return False

        try:
            with self.conn:

                if not self._add_point(timestamp, long, lat, tss, draft, avg_depth):
                    raise sqlite3.Error("unable to add point")

            return True

        except sqlite3.Error as e:
            logger.error("during adding casts, %s: %s" % (type(e), e))
            return False

    def get_db_version(self):
        """Get the project db version"""
        if not self.conn:
            logger.error("missing db connection")
            return False

        try:
            # noinspection SqlResolve
            ret = self.conn.execute("""SELECT * FROM library""").fetchone()
            return ret[0]

        except sqlite3.Error as e:
            logger.error("whilte getting db version, %s: %s" % (type(e), e))
            return None

    def _add_point(self, timestamp, long, lat, tss, draft, avg_depth):

        point = Point(long, lat)

        try:
            # noinspection SqlResolve
            self.conn.execute("""
                              INSERT INTO data VALUES (NULL, ?, ?, ?, ?, ?)
                              """, (timestamp,
                                    point,
                                    tss,
                                    draft,
                                    avg_depth
                                    ))
            # logger.info("insert new %s pk in ssp" % self.tmp_ssp_pk)

        except sqlite3.Error as e:
            logger.error("during point addition, %s: %s" % (type(e), e))
            return False

        return True

    def timestamp_list(self):
        """Create and return the timestamp list (and the pk)"""

        if not self.conn:
            logger.error("missing db connection")
            return None

        with self.conn:
            try:
                # ssp spatial timestamp
                # noinspection SqlResolve
                ts_list = self.conn.execute("""
                                             SELECT time, id FROM data ORDER BY time
                                             """).fetchall()
                logger.info("retrieved %s timestamps and ids from data" % len(ts_list))

                times = list()
                ids = list()
                for item in ts_list:
                    times.append(item[0])
                    ids.append(item[1])

                return times, ids

            except sqlite3.Error as e:
                logger.error("while retrieving the timestamps and ids, %s: %s" % (type(e), e))
                return None

    def list_points(self):
        if not self.conn:
            logger.error("missing db connection")
            return None

        ssp_list = list()
        # noinspection SqlResolve
        sql = self.conn.execute("SELECT * FROM data ORDER BY time")

        try:
            with self.conn:
                for row in sql:

                    ssp_list.append((row['id'],  # 0
                                     row['time'],  # 1
                                     row['position'],  # 2
                                     row['tss'],  # 3
                                     row['draft'],  # 4
                                     row['avg_depth'],  # 5
                                     ))
            return ssp_list

        except sqlite3.Error as e:
            logger.error("%s: %s" % (type(e), e))
            return ssp_list

    def point_by_id(self, id):
        if not self.conn:
            logger.error("missing db connection")
            return None

        # logger.info("retrieve point with id: %s" % id)

        with self.conn:
            try:
                # noinspection SqlResolve
                row = self.conn.execute("SELECT * FROM data WHERE id=?", (id, )).fetchone()

                timestamp = row[1]
                long = row[2].x
                lat = row[2].y
                tss = row[3]
                draft = row[4]
                avg_depth = row[5]

            except sqlite3.Error as e:
                logger.error("while retrieving %s point, %s: %s" % (id, type(e), e))
                return None

        return timestamp, long, lat, tss, draft, avg_depth

    def delete_point_by_id(self, id):
        """Delete all the entries related to a point id"""

        with self.conn:
            try:
                # noinspection SqlResolve
                self.conn.execute("""DELETE FROM data WHERE id=?""", (id, ))
                # logger.info("deleted %s id entry from data" % id)

            except sqlite3.Error as e:
                logger.error("during deletion from ssp_pk, %s: %s" % (type(e), e))
                raise RuntimeError("unable to delete point with id: %s" % id)

        return True

    # --- repr

    def __repr__(self):
        msg = "<%s>\n" % self.__class__.__name__
        msg += "  <data folder: %s>\n" % self.data_folder
        msg += "  <base name: %s>\n" % self.base_name
        return msg
