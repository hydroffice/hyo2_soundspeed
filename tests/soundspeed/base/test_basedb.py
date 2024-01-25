import unittest
import os

from hyo2.ssm2.lib.base.basedb import BaseDb


class TestSoundSpeedBaseDbPoint(unittest.TestCase):

    def setUp(self):
        self.x = 10.
        self.y = 10.

    def test_Point_creation(self):
        point = BaseDb.Point(x=self.x, y=self.y)
        self.assertEqual(point.x, self.x)
        self.assertEqual(point.y, self.y)

    def test_if_adapt_point_works(self):
        point = BaseDb.Point(x=self.x, y=self.y)
        self.assertEqual(BaseDb.adapt_point(point), "%f;%f" % (self.x, self.y))

    def test_if_convert_point_works(self):
        point = BaseDb.Point(x=self.x, y=self.y)
        self.assertAlmostEqual(BaseDb.convert_point("%f;%f" % (self.x, self.y)).x, point.x)
        self.assertAlmostEqual(BaseDb.convert_point("%f;%f" % (self.x, self.y)).y, point.y)


class TestSoundSpeedBaseDb(unittest.TestCase):

    CREATE_DUMMY = """ CREATE TABLE IF NOT EXISTS dummytable(
         id integer PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
         dummy text NOT NULL DEFAULT "dummy"
         ) """

    class DummyDb(BaseDb):
        def build_tables(self):
            import sqlite3

            if not self.conn:
                return False

            try:
                with self.conn:
                    if self.conn.execute(""" PRAGMA foreign_keys """):
                        # logger.info("foreign keys active")
                        pass
                    else:
                        return False
                    self.conn.execute(TestSoundSpeedBaseDb.CREATE_DUMMY)
                return True

            except sqlite3.Error as e:
                print("error: during building tables, %s: %s" % (type(e), e))
                return False

    def setUp(self):
        self.db_path = os.path.abspath(os.path.join(os.curdir, "dummy.db"))
        self.db = TestSoundSpeedBaseDb.DummyDb(self.db_path)

    def tearDown(self):
        self.db.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_if_clean_name_works(self):
        clean_name = "a1"
        self.assertEqual(BaseDb.clean_name(clean_name), clean_name)
        dirty_name = "a;1"
        self.assertNotEqual(BaseDb.clean_name(dirty_name), dirty_name)

    def test_db_creation_reconnection(self):
        self.assertEqual(self.db.db_path, self.db_path)

        # first creation
        self.db.reconnect_or_create()
        self.assertNotEqual(self.db.conn, None)
        self.db.disconnect()
        self.assertEqual(self.db.conn, None)

        # check if the file was created
        self.assertTrue(os.path.exists(self.db_path))

        # now do reconnection
        self.db.reconnect_or_create()
        self.assertNotEqual(self.db.conn, None)
        self.db.close()
        self.assertEqual(self.db.conn, None)

    def test_check_table_rows_and_cols(self):
        self.assertEqual(self.db.db_path, self.db_path)

        # creation
        self.db.reconnect_or_create()
        self.assertNotEqual(self.db.conn, None)

        self.assertEqual(self.db.check_table_total_rows('dummyTable'), 0)

        infos = self.db.check_table_cols_settings('dummyTable')
        for info in infos:
            # logger.debug("%s" % info[1])
            self.assertTrue(info[1] in ("id", "dummy"))  # the name of the fields

        counts = self.db.check_tables_values_in_cols('dummyTable')
        # logger.debug("%s" % counts)
        for key in counts.keys():
            self.assertEqual(counts[key], 0)  # since the dummy table is empty

        # close
        self.db.close()
        self.assertEqual(self.db.conn, None)


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSoundSpeedBaseDbPoint))
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSoundSpeedBaseDb))
    return s
