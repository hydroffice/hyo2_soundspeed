from __future__ import absolute_import, division, print_function, unicode_literals

import sqlite3
import os
from datetime import datetime as dt
import logging

logger = logging.getLogger(__name__)

from .point import Point, convert_point, adapt_point
from .plot import PlotDb
from .export import ExportDb
from ..profile.profilelist import ProfileList


class SoundSpeedDb(object):
    """Class that provides an interface to a SQLite db with Sound Speed data"""

    def __init__(self, projects_folder=None, project_name="default"):

        # in case that no data folder is passed
        if projects_folder is None:
            projects_folder = os.path.abspath(os.path.curdir)
        self.data_folder = projects_folder

        # the passed project name (lower case) is used to identify the project database to open
        self.db_path = os.path.join(projects_folder, self.clean_name(project_name.lower()) + ".db")
        logger.debug('current project db: %s' % self.db_path)

        # add plotting and exporting capabilities
        self.plot = PlotDb(db=self)
        self.export = ExportDb(db=self)

        # add variable used to store the connection to the database
        self.conn = None

        self.tmp_data = None
        self.tmp_ssp_pk = None

        self.reconnect_or_create()

    @staticmethod
    def clean_name(some_var):
        return ''.join(char for char in some_var if char.isalnum())

    def reconnect_or_create(self):
        """ Reconnection to an existing database or create a new db """
        if self.conn:
            logger.info("already connected")

        if not os.path.exists(self.db_path):
            logger.info("created a new project db")

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
            sqlite3.register_converter(b"point", convert_point)

        except sqlite3.Error as e:
            raise RuntimeError("Unable to register 'point': %s - %s" % (type(e), e))

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
                                     version text PRIMARY KEY NOT NULL,
                                     creation timestamp NOT NULL)
                                  """)
                self._add_version_if_missing()

                self.conn.execute("""
                                  CREATE TABLE IF NOT EXISTS project(
                                     project_name text PRIMARY KEY NOT NULL,
                                     project_creation timestamp NOT NULL)
                                  """)

                self.conn.execute("""
                                  CREATE TABLE IF NOT EXISTS ssp_pk(
                                     id INTEGER PRIMARY KEY,
                                     cast_datetime timestamp NOT NULL,
                                     cast_position point NOT NULL)
                                  """)

                self.conn.execute("""
                                  CREATE TABLE IF NOT EXISTS ssp(
                                     pk integer NOT NULL,
                                     project text NOT NULL,
                                     sensor_type integer NOT NULL,
                                     probe_type integer NOT NULL,
                                     original_path text,
                                     survey text,
                                     vessel text,
                                     sn text,
                                     proc_time timestamp,
                                     proc_info text,
                                     PRIMARY KEY (pk),
                                     FOREIGN KEY(project) REFERENCES project(project_name),
                                     FOREIGN KEY(pk) REFERENCES ssp_pk(id))
                                  """)

                self.conn.execute("""
                                  CREATE TABLE IF NOT EXISTS data(
                                     ssp_pk integer NOT NULL,
                                     depth real NOT NULL,
                                     speed real,
                                     temperature real,
                                     salinity real,
                                     source int NOT NULL DEFAULT  0,
                                     flag int NOT NULL DEFAULT 0,
                                     FOREIGN KEY(ssp_pk)
                                        REFERENCES ssp(pk))
                                  """)

                self.conn.execute("""
                                  CREATE TABLE IF NOT EXISTS proc(
                                     ssp_pk integer NOT NULL,
                                     depth real NOT NULL,
                                     speed real,
                                     temperature real,
                                     salinity real,
                                     source int NOT NULL DEFAULT  0,
                                     flag int NOT NULL DEFAULT 0,
                                     FOREIGN KEY(ssp_pk)
                                        REFERENCES ssp(pk))
                                  """)

                self.conn.execute("""
                                  CREATE TABLE IF NOT EXISTS sis(
                                     ssp_pk integer NOT NULL,
                                     depth real NOT NULL,
                                     speed real,
                                     temperature real,
                                     salinity real,
                                     source int NOT NULL DEFAULT  0,
                                     flag int NOT NULL DEFAULT 0,
                                     FOREIGN KEY(ssp_pk)
                                        REFERENCES ssp(pk))
                                  """)

                self.conn.execute("""
                                  CREATE VIEW IF NOT EXISTS ssp_view AS
                                     SELECT pk, cast_datetime, cast_position,
                                        sensor_type, probe_type,
                                        original_path,
                                        project,
                                        survey,
                                        vessel,
                                        sn,
                                        proc_time,
                                        proc_info
                                        FROM ssp a LEFT OUTER JOIN ssp_pk b ON a.pk=b.id
                                  """)

            return True

        except sqlite3.Error as e:
            logger.error("during building tables, %s: %s" % (type(e), e))
            return False

    def add_casts(self, ssp):
        if not isinstance(ssp, ProfileList):
            raise RuntimeError("not passed a ProfileList, but %s" % type(ssp))

        if not self.conn:
            logger.error("missing db connection")
            return False

        with self.conn:
            for self.tmp_data in ssp.l:

                # logger.info("got a new SSP to store:\n%s" % self.tmp_data)

                if not self._add_project_if_missing():
                    logger.error("unable to add project: %s" % self.tmp_data.meta.project)
                    return False

                if not self._get_ssp_pk():
                    logger.error("unable to get ssp pk: %s" % self.tmp_ssp_pk)
                    return False

                if not self._delete_old_ssp():
                    logger.error("unable to clean ssp")
                    return False

                if not self._add_ssp():
                    logger.error("unable to add ssp")
                    return False

                if not self._add_data():
                    logger.error("unable to add ssp raw data samples")
                    return False

                if not self._add_proc():
                    logger.error("unable to add ssp processed data samples")
                    return False

                if self.tmp_data.sis is not None:
                    if not self._add_sis():
                        logger.error("unable to add ssp sis data samples")
                        return False

        return True

    def _add_version_if_missing(self):
        """add library version if not present"""
        from .. import __version__ as ssp_version
        version = ssp_version

        try:
            ret = self.conn.execute("""
                                    SELECT COUNT(version) FROM library WHERE version=?
                                    """, (version, )).fetchone()
            # logger.info("found %s versions named %s" % (ret[0], version))

            if ret[0] == 0:
                new_row = (version, dt.now())
                # logger.info("inserting: %s" % ", ".join(map(str, new_row)))

                self.conn.execute("INSERT INTO library VALUES (?, ?)", new_row)

        except sqlite3.Error as e:
            logger.error("%s: %s" % (type(e), e))
            return False

        return True

    def _add_project_if_missing(self):
        """add a project row only if the project is not present"""

        project = self.tmp_data.meta.project

        try:
            ret = self.conn.execute("""
                                    SELECT COUNT(project_name) FROM project WHERE project_name=?
                                    """, (project, )).fetchone()
            # logger.info("found %s projects named %s" % (ret[0], project))

            if ret[0] == 0:
                new_row = (project, dt.now())
                logger.info("inserting: %s" % ", ".join(map(str, new_row)))

                self.conn.execute("INSERT INTO project VALUES (?, ?)", new_row)

        except sqlite3.Error as e:
            logger.error("%s: %s" % (type(e), e))
            return False

        return True

    def _get_ssp_pk(self):

        datetime = self.tmp_data.meta.utc_time
        point = Point(self.tmp_data.meta.longitude, self.tmp_data.meta.latitude)

        if not self.conn:
            logger.error("missing db connection")
            return False

        try:
            # check if the ssp key is present
            ret = self.conn.execute("""
                                    SELECT COUNT(*) FROM ssp_pk WHERE cast_datetime=? AND cast_position=?
                                    """, (datetime, point,)).fetchone()
            # if not present, add it
            if ret[0] == 0:
                # logger.info("add new spp pk for %s @ %s" % (datetime, point))
                self.conn.execute("""
                                  INSERT INTO ssp_pk VALUES (NULL, ?, ?)
                                  """, (datetime, point,))
        except sqlite3.Error as e:
            logger.error("during ssp pk check, %s: %s" % (type(e), e))
            return False

        try:
            # return the ssp pk
            ret = self.conn.execute("""
                                    SELECT rowid FROM ssp_pk WHERE cast_datetime=? AND cast_position=?
                                    """, (datetime, point,)).fetchone()
            # logger.info("spp pk: %s" % ret[b'id'])
            self.tmp_ssp_pk = ret[b'id']

        except sqlite3.Error as e:
            logger.error("during ssp pk retrieve, %s: %s" % (type(e), e))
            return False

        return True

    def _delete_old_ssp(self, full=False):
        """Delete all the entries with the selected pk, with 'full' also the pk from ssp_pk"""

        try:
            self.conn.execute("""DELETE FROM data WHERE ssp_pk=?""", (self.tmp_ssp_pk, ))
            # logger.info("deleted %s pk entries from data" % self.tmp_ssp_pk)

        except sqlite3.Error as e:
            logger.error("during deletion from data, %s: %s" % (type(e), e))
            return False

        try:
            self.conn.execute("""DELETE FROM proc WHERE ssp_pk=?""", (self.tmp_ssp_pk, ))
            # logger.info("deleted %s pk entries from proc" % self.tmp_ssp_pk)

        except sqlite3.Error as e:
            logger.error("during deletion from proc, %s: %s" % (type(e), e))
            return False

        try:
            self.conn.execute("""DELETE FROM sis WHERE ssp_pk=?""", (self.tmp_ssp_pk, ))
            # logger.info("deleted %s pk entries from sis" % self.tmp_ssp_pk)

        except sqlite3.Error as e:
            logger.error("during deletion from sis, %s: %s" % (type(e), e))
            return False

        try:
            self.conn.execute("""DELETE FROM ssp WHERE pk=?""", (self.tmp_ssp_pk, ))
            # logger.info("deleted %s pk entry from ssp" % self.tmp_ssp_pk)

        except sqlite3.Error as e:
            logger.error("during deletion from ssp, %s: %s" % (type(e), e))
            return False

        if full:
            try:
                self.conn.execute("""DELETE FROM ssp_pk WHERE id=?""", (self.tmp_ssp_pk, ))
                # logger.info("deleted %s id entry from ssp_pk" % self.tmp_ssp_pk)

            except sqlite3.Error as e:
                logger.error("during deletion from ssp_pk, %s: %s" % (type(e), e))
                return False

        return True

    def _add_ssp(self):

        try:
            self.conn.execute("""
                              INSERT INTO ssp VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                              """, (self.tmp_ssp_pk,
                                    self.tmp_data.meta.project,
                                    self.tmp_data.meta.sensor_type,
                                    self.tmp_data.meta.probe_type,
                                    self.tmp_data.meta.original_path,
                                    self.tmp_data.meta.survey,
                                    self.tmp_data.meta.vessel,
                                    self.tmp_data.meta.sn,
                                    self.tmp_data.meta.proc_time,
                                    self.tmp_data.meta.proc_info
                                    ))
            # logger.info("insert new %s pk in ssp" % self.tmp_ssp_pk)

        except sqlite3.Error as e:
            logger.error("during ssp addition, %s: %s" % (type(e), e))
            return False

        return True

    def _add_data(self):

        sz = self.tmp_data.data.num_samples
        # logger.info("num samples to add: %s" % sz)

        added_samples = 0
        for i in range(sz):

            try:
                # first check if the sample is already present with exactly the same values
                self.conn.execute("""
                                  INSERT INTO data VALUES (?, ?, ?, ?, ?, ?, ?)
                                  """, (self.tmp_ssp_pk,
                                        self.tmp_data.data.depth[i],
                                        self.tmp_data.data.speed[i],
                                        self.tmp_data.data.temp[i],
                                        self.tmp_data.data.sal[i],
                                        self.tmp_data.data.source[i],
                                        self.tmp_data.data.flag[i],
                                        ))
                added_samples += 1
            except sqlite3.IntegrityError as e:
                logger.info("skipping row #%s due to %s: %s" % (i, type(e), e))
                continue
            except sqlite3.Error as e:
                logger.error("during adding ssp raw samples, %s: %s" % (type(e), e))
                return False

        # logger.info("added %s raw samples" % added_samples)
        return True

    def _add_proc(self):

        sz = self.tmp_data.proc.num_samples
        # logger.info("max processed samples to add: %s" % sz)

        added_samples = 0
        for i in range(sz):

            try:
                # first check if the sample is already present with exactly the same values
                self.conn.execute("""
                                  INSERT INTO proc VALUES (?, ?, ?, ?, ?, ?, ?)
                                  """, (self.tmp_ssp_pk,
                                        self.tmp_data.proc.depth[i],
                                        self.tmp_data.proc.speed[i],
                                        self.tmp_data.proc.temp[i],
                                        self.tmp_data.proc.sal[i],
                                        self.tmp_data.proc.source[i],
                                        self.tmp_data.proc.flag[i],
                                        ))
                added_samples += 1

            except sqlite3.IntegrityError as e:
                logger.info("skipping row #%s due to %s: %s" % (i, type(e), e))
                continue
            except sqlite3.Error as e:
                logger.error("during adding ssp processed samples, %s: %s" % (type(e), e))
                return False

        # logger.info("added %s processed samples" % added_samples)
        return True

    def _add_sis(self):

        sz = self.tmp_data.sis.num_samples
        # logger.info("max sis samples to add: %s" % sz)

        added_samples = 0
        for i in range(sz):

            try:
                # first check if the sample is already present with exactly the same values
                self.conn.execute("""
                                  INSERT INTO sis VALUES (?, ?, ?, ?, ?, ?, ?)
                                  """, (self.tmp_ssp_pk,
                                        self.tmp_data.sis.depth[i],
                                        self.tmp_data.sis.speed[i],
                                        self.tmp_data.sis.temp[i],
                                        self.tmp_data.sis.sal[i],
                                        self.tmp_data.sis.source[i],
                                        self.tmp_data.sis.flag[i],
                                        ))
                added_samples += 1

            except sqlite3.IntegrityError as e:
                logger.info("skipping row #%s due to %s: %s" % (i, type(e), e))
                continue

            except sqlite3.Error as e:
                logger.error("during adding ssp sis samples, %s: %s" % (type(e), e))
                return False

        # logger.info("added %s sis samples" % added_samples)
        return True

    def timestamp_list(self):
        """Create and return the timestamp list (and the pk)"""

        if not self.conn:
            logger.error("missing db connection")
            return None

        with self.conn:
            try:
                # ssp spatial timestamp
                ts_list = self.conn.execute("""
                                             SELECT cast_datetime, pk FROM ssp_view ORDER BY cast_datetime
                                             """).fetchall()
                logger.info("retrieved %s timestamps from ssp view" % len(ts_list))
                return ts_list

            except sqlite3.Error as e:
                logger.error("retrieving the time stamp list, %s: %s" % (type(e), e))
                return None

    def list_profiles(self, project=None):
        if not self.conn:
            logger.error("missing db connection")
            return None

        ssp_list = list()
        if project:
            sql = self.conn.execute("SELECT * FROM ssp_view WHERE project=?", (project, ))
        else:
            sql = self.conn.execute("SELECT * FROM ssp_view")

        try:
            with self.conn:
                for row in sql:
                    ssp_list.append((row[b'pk'],  # 0
                                     row[b'cast_datetime'],  # 1
                                     row[b'cast_position'],  # 2
                                     row[b'project'],  # 3
                                     row[b'sensor_type'],  # 4
                                     row[b'probe_type'],  # 5
                                     row[b'original_path'],  # 6
                                     row[b'survey'],  # 7
                                     row[b'vessel'],  # 8
                                     row[b'sn'],  # 9
                                     row[b'proc_time'],  # 10
                                     row[b'proc_info'],  # 11
                                     ))
            return ssp_list

        except sqlite3.Error as e:
            logger.error("%s: %s" % (type(e), e))
            return ssp_list

    def profile_by_pk(self, pk):
        if not self.conn:
            logger.error("missing db connection")
            return None

        # logger.info("retrieve profile with pk: %s" % pk)

        ssp = ProfileList()
        ssp.append()

        with self.conn:
            try:
                # ssp spatial timestamp
                ssp_idx = self.conn.execute("SELECT * FROM ssp_pk WHERE id=?", (pk, )).fetchone()
                ssp.cur.meta.utc_time = ssp_idx[b'cast_datetime']
                ssp.cur.meta.longitude = ssp_idx[b'cast_position'].x
                ssp.cur.meta.latitude = ssp_idx[b'cast_position'].y

            except sqlite3.Error as e:
                logger.error("spatial timestamp for %s pk > %s: %s" % (pk, type(e), e))
                return None

            try:
                # ssp metadata
                ssp_meta = self.conn.execute("SELECT * FROM ssp WHERE pk=?", (pk, )).fetchone()
                ssp.cur.meta.project = ssp_meta[b'project']
                ssp.cur.meta.sensor_type = ssp_meta[b'sensor_type']
                ssp.cur.meta.probe_type = ssp_meta[b'probe_type']
                ssp.cur.meta.original_path = ssp_meta[b'original_path']
                ssp.cur.meta.survey = ssp_meta[b'survey']
                ssp.cur.meta.vessel = ssp_meta[b'vessel']
                ssp.cur.meta.sn = ssp_meta[b'sn']
                ssp.cur.meta.proc_time = ssp_meta[b'proc_time']
                ssp.cur.meta.proc_info = ssp_meta[b'proc_info']

            except sqlite3.Error as e:
                logger.error("ssp meta for %s pk > %s: %s" % (pk, type(e), e))
                return None

            # raw data
            try:
                ssp_samples = self.conn.execute("SELECT * FROM data WHERE ssp_pk=?", (pk, )).fetchall()
                num_samples = len(ssp_samples)
                ssp.cur.init_data(num_samples)
                # logger.debug("raw data samples: %s" % num_samples)
                for i in range(num_samples):
                    # print(ssp_samples[i])
                    ssp.cur.data.depth[i] = ssp_samples[i][b'depth']
                    ssp.cur.data.speed[i] = ssp_samples[i][b'speed']
                    ssp.cur.data.temp[i] = ssp_samples[i][b'temperature']
                    ssp.cur.data.sal[i] = ssp_samples[i][b'salinity']
                    ssp.cur.data.source[i] = ssp_samples[i][b'source']
                    ssp.cur.data.flag[i] = ssp_samples[i][b'flag']

            except sqlite3.Error as e:
                logger.error("reading raw samples for %s pk, %s: %s" % (pk, type(e), e))
                return None

            # proc data
            try:
                ssp_samples = self.conn.execute("SELECT * FROM proc WHERE ssp_pk=?", (pk, )).fetchall()
                num_samples = len(ssp_samples)
                ssp.cur.init_proc(num_samples)
                # logger.debug("proc data samples: %s" % num_samples)
                for i in range(num_samples):
                    # print(ssp_samples[i])
                    ssp.cur.proc.depth[i] = ssp_samples[i][b'depth']
                    ssp.cur.proc.speed[i] = ssp_samples[i][b'speed']
                    ssp.cur.proc.temp[i] = ssp_samples[i][b'temperature']
                    ssp.cur.proc.sal[i] = ssp_samples[i][b'salinity']
                    ssp.cur.proc.source[i] = ssp_samples[i][b'source']
                    ssp.cur.proc.flag[i] = ssp_samples[i][b'flag']

            except sqlite3.Error as e:
                logger.error("reading raw samples for %s pk, %s: %s" % (pk, type(e), e))
                return None

            # sis data
            try:
                ssp_samples = self.conn.execute("SELECT * FROM sis WHERE ssp_pk=?", (pk, )).fetchall()
                num_samples = len(ssp_samples)
                ssp.cur.init_sis(num_samples)
                # logger.debug("sis data samples: %s" % num_samples)
                for i in range(num_samples):
                    # print(ssp_samples[i])
                    ssp.cur.sis.depth[i] = ssp_samples[i][b'depth']
                    ssp.cur.sis.speed[i] = ssp_samples[i][b'speed']
                    ssp.cur.sis.temp[i] = ssp_samples[i][b'temperature']
                    ssp.cur.sis.sal[i] = ssp_samples[i][b'salinity']
                    ssp.cur.sis.source[i] = ssp_samples[i][b'source']
                    ssp.cur.sis.flag[i] = ssp_samples[i][b'flag']

            except sqlite3.Error as e:
                logger.error("reading sis samples for %s pk, %s: %s" % (pk, type(e), e))
                return None

        return ssp

    def delete_profile_by_pk(self, pk):
        """Delete all the entries related to a SSP primary key"""
        self.tmp_ssp_pk = pk

        with self.conn:
            if not self._delete_old_ssp(full=True):
                raise RuntimeError("unable to delete ssp with pk: %s" % pk)

        self.tmp_ssp_pk = None
        return  True