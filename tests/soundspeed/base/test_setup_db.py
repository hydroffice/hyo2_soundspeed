import unittest
import os

from hydroffice.soundspeed.base.setup_db import SetupDb


class TestSoundSpeedSetupDb(unittest.TestCase):

    def setUp(self):
        self.data_folder = os.path.abspath(os.curdir)
        self.db_name = "setup.db"
        self.db_path = os.path.join(self.data_folder, self.db_name)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_create_settings_db_and_check_db_path(self):
        db = SetupDb(data_folder=self.data_folder, db_file=self.db_name)
        self.assertEqual(db.db_path, self.db_path)
        self.assertNotEqual(db.conn, None)
        db.close()
        self.assertEqual(db.conn, None)

    def test_has_default_settings_but_not_dummy_settings(self):
        db = SetupDb(data_folder=self.data_folder, db_file=self.db_name)
        self.assertTrue(db.setup_exists('default'))
        self.assertFalse(db.setup_exists('dummy'))
        db.close()

    def test_addition_of_dummy_settings(self):
        db = SetupDb(data_folder=self.data_folder, db_file=self.db_name)
        db.add_setup('dummy')
        self.assertTrue(db.setup_exists('dummy'))
        db.close()

    def test_addition_and_deletion_of_dummy_settings(self):
        db = SetupDb(data_folder=self.data_folder, db_file=self.db_name)
        db.add_setup('dummy')
        self.assertTrue(db.setup_exists('dummy'))
        db.delete_setup('dummy')
        self.assertFalse(db.setup_exists('dummy'))
        db.close()

    def test_setup_activation(self):
        db = SetupDb(data_folder=self.data_folder, db_file=self.db_name)
        db.add_setup('dummy')
        self.assertNotEqual(db.setup_name, 'dummy')
        db.activate_setup('dummy')
        self.assertEqual(db.setup_name, 'dummy')
        db.close()

    def test_presence_of_new_activated_setup_in_list(self):
        db = SetupDb(data_folder=self.data_folder, db_file=self.db_name)
        db.add_setup('dummy')
        db.activate_setup('dummy')
        flag = False
        for setup in db.setup_list:
            if setup[0] == db.active_setup_id:
                flag = True
                break
        self.assertTrue(flag)
        db.close()

    def test_default_client_list(self):
        db = SetupDb(data_folder=self.data_folder, db_file=self.db_name)
        self.assertEqual(len(db.client_list), 1)
        db.close()

    def test_add_and_remove_client_from_client_list(self):
        db = SetupDb(data_folder=self.data_folder, db_file=self.db_name)
        self.assertEqual(len(db.client_list), 1)

        db.add_client(client_name='dummy')
        self.assertTrue(db.client_exists('dummy'))
        self.assertEqual(len(db.client_list), 2)

        db.delete_client('dummy')
        self.assertEqual(len(db.client_list), 1)
        db.close()

    def test_compare_setup_version(self):
        db = SetupDb(data_folder=self.data_folder, db_file=self.db_name)
        self.assertLessEqual(db.setup_version, 1)
        db.close()

    def test_checked_use_woa09(self):
        db = SetupDb(data_folder=self.data_folder, db_file=self.db_name)
        db.use_woa09 = False
        self.assertFalse(db.use_woa09)
        db.close()

    def test_checked_use_woa13(self):
        db = SetupDb(data_folder=self.data_folder, db_file=self.db_name)
        db.use_woa13 = True
        self.assertTrue(db.use_woa13)
        db.close()

    def test_checked_use_rtofs(self):
        db = SetupDb(data_folder=self.data_folder, db_file=self.db_name)
        db.use_rtofs = True
        self.assertTrue(db.use_rtofs)
        db.close()

    def test_set_ssp_extension_source(self):
        db = SetupDb(data_folder=self.data_folder, db_file=self.db_name)
        db.ssp_extension_source = "WOA13"
        self.assertEqual(db.ssp_extension_source, "WOA13")
        db.close()

    def test_set_ssp_salinity_source(self):
        db = SetupDb(data_folder=self.data_folder, db_file=self.db_name)
        db.ssp_salinity_source = "WOA13"
        self.assertEqual(db.ssp_salinity_source, "WOA13")
        db.close()

    def test_set_ssp_temp_sal_source(self):
        db = SetupDb(data_folder=self.data_folder, db_file=self.db_name)
        db.ssp_temp_sal_source = "WOA13"
        self.assertEqual(db.ssp_temp_sal_source, "WOA13")
        db.close()

    def test_set_ssp_up_or_down(self):
        db = SetupDb(data_folder=self.data_folder, db_file=self.db_name)
        db.ssp_up_or_down = "up"
        self.assertEqual(db.ssp_up_or_down, "up")
        db.close()

    def test_set_use_sis(self):
        db = SetupDb(data_folder=self.data_folder, db_file=self.db_name)
        db.use_sis = True
        self.assertTrue(db.use_sis)
        db.close()

    def test_set_use_sippican(self):
        db = SetupDb(data_folder=self.data_folder, db_file=self.db_name)
        db.use_sippican = True
        self.assertTrue(db.use_sippican)
        db.close()

    def test_set_use_mvp(self):
        db = SetupDb(data_folder=self.data_folder, db_file=self.db_name)
        db.use_mvp = True
        self.assertTrue(db.use_mvp)
        db.close()

    def test_set_rx_max_wait_time(self):
        db = SetupDb(data_folder=self.data_folder, db_file=self.db_name)
        db.rx_max_wait_time = 999
        self.assertEqual(db.rx_max_wait_time, 999)
        db.close()

    def test_set_append_caris_file(self):
        db = SetupDb(data_folder=self.data_folder, db_file=self.db_name)
        db.append_caris_file = True
        self.assertTrue(db.append_caris_file)
        db.close()

    def test_set_log_user_and_server(self):
        db = SetupDb(data_folder=self.data_folder, db_file=self.db_name)
        db.log_user = True
        self.assertTrue(db.log_user)
        db.log_server = True
        self.assertTrue(db.log_server)
        db.close()

    def test_set_sis_settings(self):
        db = SetupDb(data_folder=self.data_folder, db_file=self.db_name)
        db.sis_listen_timeout = 999
        self.assertEqual(db.sis_listen_timeout, 999)
        db.sis_listen_port = 999
        self.assertEqual(db.sis_listen_port, 999)
        db.sis_auto_apply_manual_casts = "True"
        self.assertTrue(db.sis_auto_apply_manual_casts)
        db.close()

    def test_set_sippican_settings(self):
        db = SetupDb(data_folder=self.data_folder, db_file=self.db_name)
        db.sippican_listen_port = 999
        self.assertEqual(db.sippican_listen_port, 999)
        db.sippican_listen_timeout = 999
        self.assertEqual(db.sippican_listen_timeout, 999)
        db.close()

    def test_set_mvp_settings(self):
        db = SetupDb(data_folder=self.data_folder, db_file=self.db_name)
        db.mvp_ip_address = '9.9.9'
        self.assertEqual(db.mvp_ip_address, '9.9.9')
        db.mvp_listen_port = 999
        self.assertEqual(db.mvp_listen_port, 999)
        db.mvp_listen_timeout = 999
        self.assertEqual(db.mvp_listen_timeout, 999)
        db.mvp_transmission_protocol = "UNDEFINED"
        self.assertEqual(db.mvp_transmission_protocol, "UNDEFINED")
        db.mvp_format = "CALC"
        self.assertEqual(db.mvp_format, "CALC")
        db.mvp_winch_port = 999
        self.assertEqual(db.mvp_winch_port, 999)
        db.mvp_fish_port = 999
        self.assertEqual(db.mvp_fish_port, 999)
        db.mvp_nav_port = 999
        self.assertEqual(db.mvp_nav_port, 999)
        db.mvp_system_port = 999
        self.assertEqual(db.mvp_system_port, 999)
        db.mvp_sw_version = '9.9.9'
        self.assertEqual(db.mvp_sw_version, '9.9.9')
        db.mvp_instrument = "Valeport_SVPT"
        self.assertEqual(db.mvp_instrument, "Valeport_SVPT")
        db.mvp_instrument_id = '999'
        self.assertEqual(db.mvp_instrument_id, '999')
        db.close()

    def test_set_sever_settings(self):
        db = SetupDb(data_folder=self.data_folder, db_file=self.db_name)
        db.server_source = "WOA13"
        self.assertEqual(db.server_source, "WOA13")
        db.server_apply_surface_sound_speed = "True"
        self.assertTrue(db.server_apply_surface_sound_speed)
        db.close()


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSoundSpeedSetupDb))
    return s
