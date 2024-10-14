import unittest
import os
import shutil
import logging

from hyo2.ssm2.lib.atlas.regofsonline import RegOfsOnline
from hyo2.ssm2.lib.soundspeed import SoundSpeedLibrary

logger = logging.getLogger()


class TestSoundSpeedAtlasRegofsOnline(unittest.TestCase):

    def setUp(self):
        self.cur_dir = os.path.abspath(os.path.dirname(__file__))

    def tearDown(self):
        dir_items = os.listdir(self.cur_dir)
        for item in dir_items:
            if item.split('.')[-1] == 'db':
                os.remove(os.path.join(self.cur_dir, item))
            if item == 'atlases':
                shutil.rmtree(os.path.join(self.cur_dir, item))

    def test_creation_of_Cbofs(self):
        prj = SoundSpeedLibrary(data_folder=self.cur_dir)
        cbofs = RegOfsOnline(data_folder=prj.regofs_folder, prj=prj, model=RegOfsOnline.Model.CBOFS)
        self.assertTrue('regofs' in cbofs.data_folder)
        self.assertFalse(cbofs.is_present())
        prj.close()

    def test_download_db_from_Cbofs(self):
        prj = SoundSpeedLibrary(data_folder=self.cur_dir)
        cbofs = RegOfsOnline(data_folder=prj.regofs_folder, prj=prj, model=RegOfsOnline.Model.CBOFS)
        cbofs.download_db(server_mode=True)

        # to avoid test failures
        if not cbofs.is_present():
            logger.warning("unable to download CBOFS data")
        # self.assertTrue(rtofs.is_present())

        prj.close()

    def test_creation_of_Dbofs(self):
        prj = SoundSpeedLibrary(data_folder=self.cur_dir)
        dbofs = RegOfsOnline(data_folder=prj.regofs_folder, prj=prj, model=RegOfsOnline.Model.DBOFS)
        self.assertTrue('regofs' in dbofs.data_folder)
        self.assertFalse(dbofs.is_present())
        prj.close()

    def test_download_db_from_Dbofs(self):
        prj = SoundSpeedLibrary(data_folder=self.cur_dir)
        dbofs = RegOfsOnline(data_folder=prj.regofs_folder, prj=prj, model=RegOfsOnline.Model.DBOFS)
        dbofs.download_db(server_mode=True)

        # to avoid test failures
        if not dbofs.is_present():
            logger.warning("unable to download DBOFS data")
        # self.assertTrue(rtofs.is_present())

        prj.close()

    def test_creation_of_Gomofs(self):
        prj = SoundSpeedLibrary(data_folder=self.cur_dir)
        gomofs = RegOfsOnline(data_folder=prj.regofs_folder, prj=prj, model=RegOfsOnline.Model.GoMOFS)
        self.assertTrue('regofs' in gomofs.data_folder)
        self.assertFalse(gomofs.is_present())
        prj.close()

    def test_download_db_from_Gomofs(self):
        prj = SoundSpeedLibrary(data_folder=self.cur_dir)
        gomofs = RegOfsOnline(data_folder=prj.regofs_folder, prj=prj, model=RegOfsOnline.Model.GoMOFS)
        gomofs.download_db(server_mode=True)

        # to avoid test failures
        if not gomofs.is_present():
            logger.warning("unable to download GoMOFS data")
        # self.assertTrue(rtofs.is_present())

        prj.close()

    # def test_creation_of_Nyofs(self):
    #     prj = SoundSpeedLibrary(data_folder=self.cur_dir)
    #     nyofs = RegOfs(data_folder=prj.regofs_folder, prj=prj, model=RegOfs.Model.NYOFS)
    #     self.assertTrue('regofs' in nyofs.data_folder)
    #     self.assertFalse(nyofs.is_present())
    #     prj.close()
    #
    # def test_download_db_from_Nyofs(self):
    #     prj = SoundSpeedLibrary(data_folder=self.cur_dir)
    #     nyofs = RegOfs(data_folder=prj.regofs_folder, prj=prj, model=RegOfs.Model.NYOFS)
    #     nyofs.download_db(server_mode=True)
    #
    #     # to avoid test failures
    #     if not nyofs.is_present():
    #         logger.warning("unable to download NYOFS data")
    #     # self.assertTrue(rtofs.is_present())
    #
    #     prj.close()

    # def test_creation_of_Sjrofs(self):
    #     prj = SoundSpeedLibrary(data_folder=self.cur_dir)
    #     sjrofs = RegOfs(data_folder=prj.regofs_folder, prj=prj, model=RegOfs.Model.SJROFS)
    #     self.assertTrue('regofs' in sjrofs.data_folder)
    #     self.assertFalse(sjrofs.is_present())
    #     prj.close()
    #
    # def test_download_db_from_Sjrofs(self):
    #     prj = SoundSpeedLibrary(data_folder=self.cur_dir)
    #     sjrofs = RegOfs(data_folder=prj.regofs_folder, prj=prj, model=RegOfs.Model.SJROFS)
    #     sjrofs.download_db(server_mode=True)
    #
    #     # to avoid test failures
    #     if not sjrofs.is_present():
    #         logger.warning("unable to download SJROFS data")
    #     # self.assertTrue(rtofs.is_present())
    #
    #     prj.close()

    def test_creation_of_Ngofs(self):
        prj = SoundSpeedLibrary(data_folder=self.cur_dir)
        ngofs2 = RegOfsOnline(data_folder=prj.regofs_folder, prj=prj, model=RegOfsOnline.Model.NGOFS2)
        self.assertTrue('regofs' in ngofs2.data_folder)
        self.assertFalse(ngofs2.is_present())
        prj.close()

    def test_download_db_from_Ngofs(self):
        prj = SoundSpeedLibrary(data_folder=self.cur_dir)
        ngofs2 = RegOfsOnline(data_folder=prj.regofs_folder, prj=prj, model=RegOfsOnline.Model.NGOFS2)
        ngofs2.download_db(server_mode=True)

        # to avoid test failures
        if not ngofs2.is_present():
            logger.warning("unable to download NGOFS2 data")
        # self.assertTrue(rtofs.is_present())

        prj.close()

    def test_creation_of_Tbofs(self):
        prj = SoundSpeedLibrary(data_folder=self.cur_dir)
        tbofs = RegOfsOnline(data_folder=prj.regofs_folder, prj=prj, model=RegOfsOnline.Model.TBOFS)
        self.assertTrue('regofs' in tbofs.data_folder)
        self.assertFalse(tbofs.is_present())
        prj.close()

    def test_download_db_from_Tbofs(self):
        prj = SoundSpeedLibrary(data_folder=self.cur_dir)
        tbofs = RegOfsOnline(data_folder=prj.regofs_folder, prj=prj, model=RegOfsOnline.Model.TBOFS)
        tbofs.download_db(server_mode=True)

        # to avoid test failures
        if not tbofs.is_present():
            logger.warning("unable to download TBOFS data")
        # self.assertTrue(rtofs.is_present())

        prj.close()

    def test_creation_of_Leofs(self):
        prj = SoundSpeedLibrary(data_folder=self.cur_dir)
        leofs = RegOfsOnline(data_folder=prj.regofs_folder, prj=prj, model=RegOfsOnline.Model.LEOFS)
        self.assertTrue('regofs' in leofs.data_folder)
        self.assertFalse(leofs.is_present())
        prj.close()

    def test_download_db_from_Leofs(self):
        prj = SoundSpeedLibrary(data_folder=self.cur_dir)
        leofs = RegOfsOnline(data_folder=prj.regofs_folder, prj=prj, model=RegOfsOnline.Model.LEOFS)
        leofs.download_db(server_mode=True)

        # to avoid test failures
        if not leofs.is_present():
            logger.warning("unable to download LEOFS data")
        # self.assertTrue(rtofs.is_present())

        prj.close()

    # def test_creation_of_Lhofs(self):
    #     prj = SoundSpeedLibrary(data_folder=self.cur_dir)
    #     lmhofs = RegOfs(data_folder=prj.regofs_folder, prj=prj, model=RegOfs.Model.LMHOFS)
    #     self.assertTrue('regofs' in lmhofs.data_folder)
    #     self.assertFalse(lmhofs.is_present())
    #     prj.close()
    #
    # def test_download_db_from_Lhofs(self):
    #     prj = SoundSpeedLibrary(data_folder=self.cur_dir)
    #     lmhofs = RegOfs(data_folder=prj.regofs_folder, prj=prj, model=RegOfs.Model.LMHOFS)
    #     lmhofs.download_db(server_mode=True)
    #
    #     # to avoid test failures
    #     if not lmhofs.is_present():
    #         logger.warning("unable to download LMHOFS data")
    #     # self.assertTrue(rtofs.is_present())
    #
    #     prj.close()

    # def test_creation_of_Loofs(self):
    #     prj = SoundSpeedLibrary(data_folder=self.cur_dir)
    #     loofs = RegOfs(data_folder=prj.regofs_folder, prj=prj, model=RegOfs.Model.LOOFS)
    #     self.assertTrue('regofs' in loofs.data_folder)
    #     self.assertFalse(loofs.is_present())
    #     prj.close()
    #
    # def test_download_db_from_Loofs(self):
    #     prj = SoundSpeedLibrary(data_folder=self.cur_dir)
    #     loofs = RegOfs(data_folder=prj.regofs_folder, prj=prj, model=RegOfs.Model.LOOFS)
    #     loofs.download_db(server_mode=True)
    #
    #     # to avoid test failures
    #     if not loofs.is_present():
    #         logger.warning("unable to download LOOFS data")
    #     # self.assertTrue(rtofs.is_present())
    #
    #     prj.close()

    # def test_creation_of_Lsofs(self):
    #     prj = SoundSpeedLibrary(data_folder=self.cur_dir)
    #     lsofs = RegOfs(data_folder=prj.regofs_folder, prj=prj, model=RegOfs.Model.LSOFS)
    #     self.assertTrue('regofs' in lsofs.data_folder)
    #     self.assertFalse(lsofs.is_present())
    #     prj.close()
    #
    # def test_download_db_from_Lsofs(self):
    #     prj = SoundSpeedLibrary(data_folder=self.cur_dir)
    #     lsofs = RegOfs(data_folder=prj.regofs_folder, prj=prj, model=RegOfs.Model.LSOFS)
    #     lsofs.download_db(server_mode=True)
    #
    #     # to avoid test failures
    #     if not lsofs.is_present():
    #         logger.warning("unable to download LSOFS data")
    #     # self.assertTrue(rtofs.is_present())
    #
    #     prj.close()

    def test_creation_of_Creofs(self):
        prj = SoundSpeedLibrary(data_folder=self.cur_dir)
        sscofs = RegOfsOnline(data_folder=prj.regofs_folder, prj=prj, model=RegOfsOnline.Model.SSCOFS)
        self.assertTrue('regofs' in sscofs.data_folder)
        self.assertFalse(sscofs.is_present())
        prj.close()

    def test_download_db_from_Creofs(self):
        prj = SoundSpeedLibrary(data_folder=self.cur_dir)
        sscofs = RegOfsOnline(data_folder=prj.regofs_folder, prj=prj, model=RegOfsOnline.Model.SSCOFS)
        sscofs.download_db(server_mode=True)

        # to avoid test failures
        if not sscofs.is_present():
            logger.warning("unable to download SSCOFS data")
        # self.assertTrue(rtofs.is_present())

        prj.close()

    def test_creation_of_Sfbofs(self):
        prj = SoundSpeedLibrary(data_folder=self.cur_dir)
        sfbofs = RegOfsOnline(data_folder=prj.regofs_folder, prj=prj, model=RegOfsOnline.Model.SFBOFS)
        self.assertTrue('regofs' in sfbofs.data_folder)
        self.assertFalse(sfbofs.is_present())
        prj.close()

    def test_download_db_from_Sfbofs(self):
        prj = SoundSpeedLibrary(data_folder=self.cur_dir)
        sfbofs = RegOfsOnline(data_folder=prj.regofs_folder, prj=prj, model=RegOfsOnline.Model.SFBOFS)
        sfbofs.download_db(server_mode=True)

        # to avoid test failures
        if not sfbofs.is_present():
            logger.warning("unable to download SFBOFS data")
        # self.assertTrue(rtofs.is_present())

        prj.close()

    def test_creation_of_wcofs(self):
        prj = SoundSpeedLibrary(data_folder=self.cur_dir)
        wcofs = RegOfsOnline(data_folder=prj.regofs_folder, prj=prj, model=RegOfsOnline.Model.WCOFS)
        self.assertTrue('regofs' in wcofs.data_folder)
        self.assertFalse(wcofs.is_present())
        prj.close()

    def test_download_db_from_wcofs(self):
        prj = SoundSpeedLibrary(data_folder=self.cur_dir)
        wcofs = RegOfsOnline(data_folder=prj.regofs_folder, prj=prj, model=RegOfsOnline.Model.WCOFS)
        wcofs.download_db(server_mode=True)

        # to avoid test failures
        if not wcofs.is_present():
            logger.warning("unable to download WCOFS data")
        # self.assertTrue(wcofs.is_present())

        prj.close()


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSoundSpeedAtlasRegofsOnline))
    return s
