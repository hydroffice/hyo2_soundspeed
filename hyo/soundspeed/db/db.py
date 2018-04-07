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
from hyo.soundspeed.db.plot import PlotDb
from hyo.soundspeed.db.export import ExportDb
from hyo.soundspeed.profile.profilelist import ProfileList
from hyo.soundspeed.profile.dicts import Dicts


class ProjectDb:
    """Class that provides an interface to a SQLite db with Sound Speed data"""

    def __init__(self, projects_folder=None, project_name=None):

        # in case that no data folder is passed
        if projects_folder is None:
            projects_folder = os.path.abspath(os.path.curdir)
        self.data_folder = projects_folder

        # in case that none is passed as project name
        if project_name is None:
            project_name = "default"

        # the passed project name is used to identify the project database to open
        self.db_path = os.path.join(projects_folder, self.clean_project_name(project_name) + ".db")
        # logger.debug('current project db: %s' % self.db_path)

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

    @staticmethod
    def clean_project_name(some_var):
        return ''.join(char for char in some_var if char.isalnum() or char in ['-', '_', '.'])

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
                                      """, (2, "%s v.%s" % (name, version), datetime.datetime.utcnow(),))

                self.conn.execute("""
                                  CREATE TABLE IF NOT EXISTS ssp_pk(
                                     id INTEGER PRIMARY KEY,
                                     cast_datetime timestamp NOT NULL,
                                     cast_position point NOT NULL)
                                  """)

                # noinspection SqlResolve
                self.conn.execute("""
                                  CREATE TABLE IF NOT EXISTS ssp(
                                     pk integer NOT NULL,
                                     sensor_type integer NOT NULL,
                                     probe_type integer NOT NULL,
                                     original_path text,
                                     institution text,
                                     survey text,
                                     vessel text,
                                     sn text,
                                     proc_time timestamp,
                                     proc_info text,
                                     comments text,
                                     pressure_uom text,
                                     depth_uom text,
                                     speed_uom text,
                                     temperature_uom text,
                                     conductivity_uom text,
                                     salinity_uom text,
                                     PRIMARY KEY (pk),
                                     FOREIGN KEY(pk) REFERENCES ssp_pk(id))
                                  """)

                # noinspection SqlResolve
                self.conn.execute("""
                                  CREATE TABLE IF NOT EXISTS data(
                                     ssp_pk integer NOT NULL,
                                     pressure real,
                                     depth real NOT NULL,
                                     speed real,
                                     temperature real,
                                     conductivity real,
                                     salinity real,
                                     source int NOT NULL DEFAULT  0,
                                     flag int NOT NULL DEFAULT 0,
                                     FOREIGN KEY(ssp_pk)
                                        REFERENCES ssp(pk))
                                  """)

                # noinspection SqlResolve
                self.conn.execute("""
                                  CREATE TABLE IF NOT EXISTS proc(
                                     ssp_pk integer NOT NULL,
                                     pressure real,
                                     depth real NOT NULL,
                                     speed real,
                                     temperature real,
                                     conductivity real,
                                     salinity real,
                                     source int NOT NULL DEFAULT  0,
                                     flag int NOT NULL DEFAULT 0,
                                     FOREIGN KEY(ssp_pk)
                                        REFERENCES ssp(pk))
                                  """)

                # noinspection SqlResolve
                self.conn.execute("""
                                  CREATE TABLE IF NOT EXISTS sis(
                                     ssp_pk integer NOT NULL,
                                     pressure real,
                                     depth real NOT NULL,
                                     speed real,
                                     temperature real,
                                     conductivity real,
                                     salinity real,
                                     source int NOT NULL DEFAULT  0,
                                     flag int NOT NULL DEFAULT 0,
                                     FOREIGN KEY(ssp_pk)
                                        REFERENCES ssp(pk))
                                  """)

                # noinspection SqlResolve
                self.conn.execute("""
                                  CREATE VIEW IF NOT EXISTS ssp_view AS
                                     SELECT pk, cast_datetime, cast_position,
                                        sensor_type, probe_type,
                                        original_path,
                                        institution,
                                        survey,
                                        vessel,
                                        sn,
                                        proc_time,
                                        proc_info,
                                        comments,
                                        pressure_uom,
                                        depth_uom,
                                        speed_uom,
                                        temperature_uom,
                                        conductivity_uom,
                                        salinity_uom
                                        FROM ssp a LEFT OUTER JOIN ssp_pk b ON a.pk=b.id
                                  """)

            return True

        except sqlite3.Error as e:
            logger.error("during building tables, %s: %s" % (type(e), e))
            return False

    def remove_casts(self, ssp):
        if not isinstance(ssp, ProfileList):
            raise RuntimeError("not passed a ProfileList, but %s" % type(ssp))

        if not self.conn:
            logger.error("missing db connection")
            return False

        try:
            with self.conn:

                for i, self.tmp_data in enumerate(ssp.l):

                    # logger.info("got a new SSP to store:\n%s" % self.tmp_data)

                    if not self._get_ssp_pk():
                        raise sqlite3.Error("unable to get ssp pk: %s" % self.tmp_ssp_pk)

                    if not self._delete_old_ssp():
                        raise sqlite3.Error("unable to clean ssp")

            return True

        except sqlite3.Error as e:
            logger.error("during adding casts, %s: %s" % (type(e), e))
            return False

    def add_casts(self, ssp):
        if not isinstance(ssp, ProfileList):
            raise RuntimeError("not passed a ProfileList, but %s" % type(ssp))

        if not self.conn:
            logger.error("missing db connection")
            return False

        try:
            with self.conn:

                for i, self.tmp_data in enumerate(ssp.l):

                    # logger.info("got a new SSP to store:\n%s" % self.tmp_data)

                    if not self._get_ssp_pk():
                        raise sqlite3.Error("unable to get ssp pk: %s" % self.tmp_ssp_pk)

                    if not self._delete_old_ssp():
                        raise sqlite3.Error("unable to clean ssp")

                    if not self._add_ssp():
                        raise sqlite3.Error("unable to add ssp")

                    if not self._add_data():
                        raise sqlite3.Error("unable to add ssp raw data samples")

                    if not self._add_proc():
                        raise sqlite3.Error("unable to add ssp processed data samples")

                    if self.tmp_data.sis is not None:
                        if not self._add_sis():
                            raise sqlite3.Error("unable to add ssp sis data samples")

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
            logger.error("while getting db version, %s: %s" % (type(e), e))
            return None

    def _get_ssp_pk(self):

        datetime = self.tmp_data.meta.utc_time
        point = Point(self.tmp_data.meta.longitude, self.tmp_data.meta.latitude)

        if not self.conn:
            logger.error("missing db connection")
            return False

        try:
            # check if the ssp key is present
            # noinspection SqlResolve
            ret = self.conn.execute("""
                                    SELECT COUNT(*) FROM ssp_pk WHERE cast_datetime=? AND cast_position=?
                                    """, (datetime, point,)).fetchone()
            # if not present, add it
            if ret[0] == 0:
                # logger.info("add new spp pk for %s @ %s" % (datetime, point))
                # noinspection SqlResolve
                self.conn.execute("""
                                  INSERT INTO ssp_pk VALUES (NULL, ?, ?)
                                  """, (datetime, point,))
        except sqlite3.Error as e:
            logger.error("during ssp pk check, %s: %s" % (type(e), e))
            return False

        try:
            # return the ssp pk
            # noinspection SqlResolve
            ret = self.conn.execute("""
                                    SELECT rowid FROM ssp_pk WHERE cast_datetime=? AND cast_position=?
                                    """, (datetime, point,)).fetchone()
            # logger.info("spp pk: %s" % ret['id'])
            self.tmp_ssp_pk = ret['id']

        except sqlite3.Error as e:
            logger.error("during ssp pk retrieve, %s: %s" % (type(e), e))
            return False

        return True

    def _delete_old_ssp(self, full=False):
        """Delete all the entries with the selected pk, with 'full' also the pk from ssp_pk"""

        try:
            # noinspection SqlResolve
            self.conn.execute("""DELETE FROM data WHERE ssp_pk=?""", (self.tmp_ssp_pk, ))
            # logger.info("deleted %s pk entries from data" % self.tmp_ssp_pk)

        except sqlite3.Error as e:
            logger.error("during deletion from data, %s: %s" % (type(e), e))
            return False

        try:
            # noinspection SqlResolve
            self.conn.execute("""DELETE FROM proc WHERE ssp_pk=?""", (self.tmp_ssp_pk, ))
            # logger.info("deleted %s pk entries from proc" % self.tmp_ssp_pk)

        except sqlite3.Error as e:
            logger.error("during deletion from proc, %s: %s" % (type(e), e))
            return False

        try:
            # noinspection SqlResolve
            self.conn.execute("""DELETE FROM sis WHERE ssp_pk=?""", (self.tmp_ssp_pk, ))
            # logger.info("deleted %s pk entries from sis" % self.tmp_ssp_pk)

        except sqlite3.Error as e:
            logger.error("during deletion from sis, %s: %s" % (type(e), e))
            return False

        try:
            # noinspection SqlResolve
            self.conn.execute("""DELETE FROM ssp WHERE pk=?""", (self.tmp_ssp_pk, ))
            # logger.info("deleted %s pk entry from ssp" % self.tmp_ssp_pk)

        except sqlite3.Error as e:
            logger.error("during deletion from ssp, %s: %s" % (type(e), e))
            return False

        if full:
            try:
                # noinspection SqlResolve
                self.conn.execute("""DELETE FROM ssp_pk WHERE id=?""", (self.tmp_ssp_pk, ))
                # logger.info("deleted %s id entry from ssp_pk" % self.tmp_ssp_pk)

            except sqlite3.Error as e:
                logger.error("during deletion from ssp_pk, %s: %s" % (type(e), e))
                return False

        return True

    def _add_ssp(self):

        try:
            # noinspection SqlResolve
            self.conn.execute("""
                              INSERT INTO ssp VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                              """, (self.tmp_ssp_pk,
                                    self.tmp_data.meta.sensor_type,
                                    self.tmp_data.meta.probe_type,
                                    self.tmp_data.meta.original_path,
                                    self.tmp_data.meta.institution,
                                    self.tmp_data.meta.survey,
                                    self.tmp_data.meta.vessel,
                                    self.tmp_data.meta.sn,
                                    self.tmp_data.meta.proc_time,
                                    self.tmp_data.meta.proc_info,
                                    self.tmp_data.meta.comments,
                                    self.tmp_data.meta.pressure_uom,
                                    self.tmp_data.meta.depth_uom,
                                    self.tmp_data.meta.speed_uom,
                                    self.tmp_data.meta.temperature_uom,
                                    self.tmp_data.meta.conductivity_uom,
                                    self.tmp_data.meta.salinity_uom
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
                # noinspection SqlResolve
                self.conn.execute("""
                                  INSERT INTO data VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                                  """, (self.tmp_ssp_pk,
                                        self.tmp_data.data.pressure[i],
                                        self.tmp_data.data.depth[i],
                                        self.tmp_data.data.speed[i],
                                        self.tmp_data.data.temp[i],
                                        self.tmp_data.data.conductivity[i],
                                        self.tmp_data.data.sal[i],
                                        self.tmp_data.data.source[i],
                                        self.tmp_data.data.flag[i],
                                        ))
                added_samples += 1
            except sqlite3.IntegrityError as e:
                logger.info("skipping row #%s due to %s: %s" % (i, type(e), e))
                continue
            except sqlite3.Error as e:
                print(self.tmp_data.data.depth[i], type(self.tmp_data.data.depth[i]))
                # traceback.print_stack()
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
                # noinspection SqlResolve
                self.conn.execute("""
                                  INSERT INTO proc VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                                  """, (self.tmp_ssp_pk,
                                        self.tmp_data.proc.pressure[i],
                                        self.tmp_data.proc.depth[i],
                                        self.tmp_data.proc.speed[i],
                                        self.tmp_data.proc.temp[i],
                                        self.tmp_data.proc.conductivity[i],
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
                # noinspection SqlResolve
                self.conn.execute("""
                                  INSERT INTO sis VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                                  """, (self.tmp_ssp_pk,
                                        self.tmp_data.sis.pressure[i],
                                        self.tmp_data.sis.depth[i],
                                        self.tmp_data.sis.speed[i],
                                        self.tmp_data.sis.temp[i],
                                        self.tmp_data.sis.conductivity[i],
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
                # noinspection SqlResolve
                ts_list = self.conn.execute("""
                                             SELECT cast_datetime, pk FROM ssp_view ORDER BY cast_datetime
                                             """).fetchall()
                # logger.info("retrieved %s timestamps from ssp view" % len(ts_list))
                return ts_list

            except sqlite3.Error as e:
                logger.error("retrieving the time stamp list, %s: %s" % (type(e), e))
                return None

    def list_profiles(self):
        if not self.conn:
            logger.error("missing db connection")
            return None

        ssp_list = list()
        # noinspection SqlResolve
        sql = self.conn.execute("SELECT * FROM ssp_view")

        try:
            with self.conn:
                for row in sql:

                    # special handling in case of unknown future sensor type
                    sensor_type = row['sensor_type']
                    if sensor_type not in Dicts.sensor_types.values():
                        sensor_type = Dicts.sensor_types['Future']

                    # special handling in case of unknown future probe type
                    probe_type = row['probe_type']
                    if probe_type not in Dicts.probe_types.values():
                        probe_type = Dicts.probe_types['Future']

                    # special handling for surface sound speed, min depth, max depth
                    ssp_samples = self.conn.execute("SELECT * FROM proc WHERE ssp_pk=? AND flag=?", (row['pk'], Dicts.flags['valid'])).fetchall()
                    ss_at_min_depth = '%0.2f' %ssp_samples[0]['speed']
                    min_depth = '%0.2f' %ssp_samples[0]['depth']
                    max_depth = '%0.2f' %ssp_samples[-1]['depth']

                    ssp_list.append((row['pk'],  # 0
                                     row['cast_datetime'],  # 1
                                     row['cast_position'],  # 2
                                     sensor_type,  # 3
                                     probe_type,  # 4
                                     row['original_path'],  # 5
                                     row['institution'],  # 6
                                     row['survey'],  # 7
                                     row['vessel'],  # 8
                                     row['sn'],  # 9
                                     row['proc_time'],  # 10
                                     row['proc_info'],  # 11
                                     row['comments'],  # 12
                                     row['pressure_uom'],  # 13
                                     row['depth_uom'],  # 14
                                     row['speed_uom'],  # 15
                                     row['temperature_uom'],  # 16
                                     row['conductivity_uom'],  # 17
                                     row['salinity_uom'],  # 18
                                     ss_at_min_depth,  # 19
                                     min_depth,  # 20
                                     max_depth,  # 21
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
                # noinspection SqlResolve
                ssp_idx = self.conn.execute("SELECT * FROM ssp_pk WHERE id=?", (pk, )).fetchone()

                ssp.cur.meta.utc_time = ssp_idx['cast_datetime']
                ssp.cur.meta.longitude = ssp_idx['cast_position'].x
                ssp.cur.meta.latitude = ssp_idx['cast_position'].y

            except sqlite3.Error as e:
                logger.error("spatial timestamp for %s pk > %s: %s" % (pk, type(e), e))
                return None

            try:
                # ssp metadata
                # noinspection SqlResolve
                ssp_meta = self.conn.execute("SELECT * FROM ssp WHERE pk=?", (pk, )).fetchone()

                # special handling in case of unknown future sensor type
                ssp.cur.meta.sensor_type = ssp_meta['sensor_type']
                if ssp.cur.meta.sensor_type not in Dicts.sensor_types.values():
                    ssp.cur.meta.sensor_type = Dicts.sensor_types['Future']

                # special handling in case of unknown future probe type
                ssp.cur.meta.probe_type = ssp_meta['probe_type']
                if ssp.cur.meta.probe_type not in Dicts.probe_types.values():
                    ssp.cur.meta.probe_type = Dicts.probe_types['Future']

                ssp.cur.meta.original_path = ssp_meta['original_path']
                ssp.cur.meta.institution = ssp_meta['institution']
                ssp.cur.meta.survey = ssp_meta['survey']
                ssp.cur.meta.vessel = ssp_meta['vessel']
                ssp.cur.meta.sn = ssp_meta['sn']
                ssp.cur.meta.proc_time = ssp_meta['proc_time']
                ssp.cur.meta.proc_info = ssp_meta['proc_info']
                ssp.cur.meta.comments = ssp_meta['comments']

                ssp.cur.meta.pressure_uom = ssp_meta['pressure_uom']
                ssp.cur.meta.depth_uom = ssp_meta['depth_uom']
                ssp.cur.meta.speed_uom = ssp_meta['speed_uom']
                ssp.cur.meta.temperature_uom = ssp_meta['temperature_uom']
                ssp.cur.meta.conductivity_uom = ssp_meta['conductivity_uom']
                ssp.cur.meta.salinity_uom = ssp_meta['salinity_uom']

            except sqlite3.Error as e:
                logger.error("ssp meta for %s pk > %s: %s" % (pk, type(e), e))
                return None

            # raw data
            try:
                # noinspection SqlResolve
                ssp_samples = self.conn.execute("SELECT * FROM data WHERE ssp_pk=?", (pk, )).fetchall()
                num_samples = len(ssp_samples)
                ssp.cur.init_data(num_samples)
                # logger.debug("raw data samples: %s" % num_samples)
                for i in range(num_samples):
                    # print(ssp_samples[i])

                    ssp.cur.data.pressure[i] = ssp_samples[i]['pressure']
                    ssp.cur.data.depth[i] = ssp_samples[i]['depth']
                    ssp.cur.data.speed[i] = ssp_samples[i]['speed']
                    ssp.cur.data.temp[i] = ssp_samples[i]['temperature']
                    ssp.cur.data.conductivity[i] = ssp_samples[i]['conductivity']
                    ssp.cur.data.sal[i] = ssp_samples[i]['salinity']
                    ssp.cur.data.source[i] = ssp_samples[i]['source']
                    ssp.cur.data.flag[i] = ssp_samples[i]['flag']

            except sqlite3.Error as e:
                logger.error("reading raw samples for %s pk, %s: %s" % (pk, type(e), e))
                return None

            # proc data
            try:
                # noinspection SqlResolve
                ssp_samples = self.conn.execute("SELECT * FROM proc WHERE ssp_pk=?", (pk, )).fetchall()
                num_samples = len(ssp_samples)
                ssp.cur.init_proc(num_samples)
                # logger.debug("proc data samples: %s" % num_samples)
                for i in range(num_samples):
                    # print(ssp_samples[i])
                    ssp.cur.proc.pressure[i] = ssp_samples[i]['pressure']
                    ssp.cur.proc.depth[i] = ssp_samples[i]['depth']
                    ssp.cur.proc.speed[i] = ssp_samples[i]['speed']
                    ssp.cur.proc.temp[i] = ssp_samples[i]['temperature']
                    ssp.cur.proc.conductivity[i] = ssp_samples[i]['conductivity']
                    ssp.cur.proc.sal[i] = ssp_samples[i]['salinity']
                    ssp.cur.proc.source[i] = ssp_samples[i]['source']
                    ssp.cur.proc.flag[i] = ssp_samples[i]['flag']

            except sqlite3.Error as e:
                logger.error("reading raw samples for %s pk, %s: %s" % (pk, type(e), e))
                return None

            # sis data
            try:
                # noinspection SqlResolve
                ssp_samples = self.conn.execute("SELECT * FROM sis WHERE ssp_pk=?", (pk, )).fetchall()
                num_samples = len(ssp_samples)
                ssp.cur.init_sis(num_samples)
                # logger.debug("sis data samples: %s" % num_samples)
                for i in range(num_samples):
                    # print(ssp_samples[i])
                    ssp.cur.sis.pressure[i] = ssp_samples[i]['depth']
                    ssp.cur.sis.depth[i] = ssp_samples[i]['depth']
                    ssp.cur.sis.speed[i] = ssp_samples[i]['speed']
                    ssp.cur.sis.temp[i] = ssp_samples[i]['temperature']
                    ssp.cur.sis.conductivity[i] = ssp_samples[i]['conductivity']
                    ssp.cur.sis.sal[i] = ssp_samples[i]['salinity']
                    ssp.cur.sis.source[i] = ssp_samples[i]['source']
                    ssp.cur.sis.flag[i] = ssp_samples[i]['flag']

            except sqlite3.Error as e:
                logger.error("reading sis samples for %s pk, %s: %s" % (pk, type(e), e))
                return None

        # This is the only way for the library to load a profile from the project database
        ssp.loaded_from_db = True

        return ssp

    def delete_profile_by_pk(self, pk):
        """Delete all the entries related to a SSP primary key"""
        self.tmp_ssp_pk = pk

        with self.conn:
            if not self._delete_old_ssp(full=True):
                raise RuntimeError("unable to delete ssp with pk: %s" % pk)

        self.tmp_ssp_pk = None
        return True

    def __repr__(self):
        msg = "<%s>\n" % self.__class__.__name__

        msg += "  <path: %s>" % self.db_path

        return msg
