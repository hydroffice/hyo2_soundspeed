from osgeo import gdal
from osgeo import ogr
from osgeo import osr
import pyproj

import os
import logging

logger = logging.getLogger(__name__)

from hyo.soundspeed.base.helper import python_path


class GdalAux:
    """ Auxiliary class to manage GDAL stuff """

    error_loaded = False
    gdal_data_fixed = False
    proj4_data_fixed = False

    ogr_formats = {
        'ESRI Shapefile': 0,
        'KML': 1,
        'CSV': 2,
    }

    ogr_exts = {
        'ESRI Shapefile': '.shp',
        'KML': '.kml',
        'CSV': '.csv',
    }

    def __init__(self):
        logger.debug("gdal 2: %s [%s]" % (self.is_gdal_2(), self.current_gdal_version()))
        if not self.error_loaded:
            self.check_gdal_data()
            self.check_proj4_data()

    @classmethod
    def current_gdal_version(cls):
        return int(gdal.VersionInfo('VERSION_NUM'))

    @classmethod
    def is_gdal_2(cls):
        return cls.current_gdal_version() >= 2000000

    @classmethod
    def get_ogr_driver(cls, ogr_format):

        try:
            driver_name = [key for key, value in GdalAux.ogr_formats.items() if value == ogr_format][0]

        except IndexError:
            raise RuntimeError("Unknown ogr format: %s" % ogr_format)

        drv = ogr.GetDriverByName(driver_name)
        if drv is None:
            raise RuntimeError("Ogr failure > %s driver not available" % driver_name)

        return drv

    @classmethod
    def create_ogr_data_source(cls, ogr_format, output_path, epsg=4326):
        drv = cls.get_ogr_driver(ogr_format)
        output_file = output_path + cls.ogr_exts[drv.GetName()]
        logger.debug("output: %s" % output_file)
        if os.path.exists(output_file):
            os.remove(output_file)

        ds = drv.CreateDataSource(output_file)
        if ds is None:
            raise RuntimeError("Ogr failure in creation of data source: %s" % output_path)

        if ogr_format == cls.ogr_formats['ESRI Shapefile']:
            cls.create_prj_file(output_path, epsg=epsg)

        return ds

    @classmethod
    def create_prj_file(cls, output_path, epsg=4326):
        """Create an ESRI lib file (geographic WGS84 by default)"""
        spatial_ref = osr.SpatialReference()
        spatial_ref.ImportFromEPSG(epsg)

        spatial_ref.MorphToESRI()
        fid = open(output_path + '.prj', 'w')
        fid.write(spatial_ref.ExportToWkt())
        fid.close()

    @staticmethod
    def list_ogr_drivers():
        """ Provide a list with all the available OGR drivers """

        cnt = ogr.GetDriverCount()
        driver_list = []

        for i in range(cnt):

            driver = ogr.GetDriver(i)
            driver_name = driver.GetName()
            if driver_name not in driver_list:
                driver_list.append(driver_name)

        driver_list.sort()  # Sorting the messy list of ogr drivers

        for i in range(len(driver_list)):

            print("%3s: %25s" % (i, driver_list[i]))

    @classmethod
    def gdal_error_handler(cls, err_class, err_num, err_msg):
        """GDAL Error Handler, to test it: gdal.Error(1, 2, b'test error')"""

        err_type = {
            gdal.CE_None: 'None',
            gdal.CE_Debug: 'Debug',
            gdal.CE_Warning: 'Warning',
            gdal.CE_Failure: 'Failure',
            gdal.CE_Fatal: 'Fatal'
        }
        err_msg = err_msg.replace('\n', ' ')
        err_class = err_type.get(err_class, 'None')

        raise RuntimeError("%s: gdal error %s > %s" % (err_class, err_num, err_msg))

    @classmethod
    def push_gdal_error_handler(cls):
        """ Install GDAL error handler """

        gdal.PushErrorHandler(cls.gdal_error_handler)

        gdal.UseExceptions()
        ogr.UseExceptions()
        osr.UseExceptions()

        cls.error_loaded = True

    @classmethod
    def check_gdal_data(cls):
        """ Check the correctness of os env GDAL_DATA """

        if cls.gdal_data_fixed:
            return

        if 'GDAL_DATA' in os.environ:

            logger.debug("unset original GDAL_DATA = %s" % os.environ['GDAL_DATA'])
            del os.environ['GDAL_DATA']

        gdal_data_path1 = os.path.join(os.path.dirname(gdal.__file__), 'data', 'gdal')
        gcs_csv_path1 = os.path.join(gdal_data_path1, 'gcs.csv')
        if os.path.exists(gcs_csv_path1):

            gdal.SetConfigOption('GDAL_DATA', gdal_data_path1)
            logger.debug("resulting GDAL_DATA = %s" % gdal.GetConfigOption('GDAL_DATA'))
            cls.gdal_data_fixed = True
            cls.push_gdal_error_handler()
            return

        # anaconda specific (Win)
        gdal_data_path2 = os.path.join(python_path(), 'Library', 'data')
        gcs_csv_path2 = os.path.join(gdal_data_path2, 'gcs.csv')
        if os.path.exists(gcs_csv_path2):

            gdal.SetConfigOption('GDAL_DATA', gdal_data_path2)
            logger.debug("resulting GDAL_DATA = %s" % gdal.GetConfigOption('GDAL_DATA'))
            cls.gdal_data_fixed = True
            cls.push_gdal_error_handler()
            return

        # anaconda specific (Win)
        gdal_data_path3 = os.path.join(python_path(), 'Library', 'share', 'gdal')
        gcs_csv_path3 = os.path.join(gdal_data_path3, 'gcs.csv')
        if os.path.exists(gcs_csv_path3):

            gdal.SetConfigOption('GDAL_DATA', gdal_data_path3)
            logger.debug("resulting GDAL_DATA = %s" % gdal.GetConfigOption('GDAL_DATA'))
            cls.gdal_data_fixed = True
            cls.push_gdal_error_handler()
            return

        # anaconda specific (Linux)
        gdal_data_path4 = os.path.join(python_path(), 'share', 'gdal')
        gcs_csv_path4 = os.path.join(gdal_data_path4, 'gcs.csv')
        if os.path.exists(gcs_csv_path4):

            gdal.SetConfigOption('GDAL_DATA', gdal_data_path4)
            logger.debug("resulting GDAL_DATA = %s" % gdal.GetConfigOption('GDAL_DATA'))
            cls.gdal_data_fixed = True
            cls.push_gdal_error_handler()
            return

        # TODO: add more cases to find GDAL_DATA

        raise RuntimeError("Unable to locate GDAL data at:\n- %s\n- %s\n- %s\n- %s"
                           % (gdal_data_path1, gdal_data_path2, gdal_data_path3, gdal_data_path4))

    @classmethod
    def check_proj4_data(cls):
        """ Check the correctness of os env PROJ_LIB """

        if cls.proj4_data_fixed:
            return

        if os.path.exists(os.path.join(pyproj.pyproj_datadir, "epsg")):
            return

        if 'PROJ_LIB' in os.environ:

            logger.debug("unset original PROJ_LIB = %s" % os.environ['PROJ_LIB'])
            del os.environ['PROJ_LIB']

        proj4_data_path1 = os.path.join(os.path.dirname(pyproj.__file__), 'data')
        epsg_path1 = os.path.join(proj4_data_path1, 'epsg')
        if os.path.exists(epsg_path1):

            os.environ['PROJ_LIB'] = proj4_data_path1
            pyproj.pyproj_datadir = proj4_data_path1
            logger.debug("resulting PROJ_LIB = %s" % os.environ['PROJ_LIB'])
            cls.proj4_data_fixed = True
            return

        # anaconda specific (Win)
        proj4_data_path2 = os.path.join(python_path(), 'Library', 'data')
        epsg_path2 = os.path.join(proj4_data_path2, 'epsg')
        if os.path.exists(epsg_path2):

            os.environ['PROJ_LIB'] = proj4_data_path2
            pyproj.pyproj_datadir = proj4_data_path2
            logger.debug("resulting PROJ_LIB = %s" % os.environ['PROJ_LIB'])
            cls.proj4_data_fixed = True
            return

        # anaconda specific (Win)
        proj4_data_path3 = os.path.join(python_path(), 'Library', 'share')
        epsg_path3 = os.path.join(proj4_data_path3, 'epsg')
        if os.path.exists(epsg_path3):

            os.environ['PROJ_LIB'] = proj4_data_path3
            pyproj.pyproj_datadir = proj4_data_path3
            logger.debug("resulting PROJ_LIB = %s" % os.environ['PROJ_LIB'])
            cls.proj4_data_fixed = True
            return

        # anaconda specific (Linux)
        proj4_data_path4 = os.path.join(python_path(), 'share')
        epsg_path4 = os.path.join(proj4_data_path4, 'epsg')
        if os.path.exists(epsg_path4):

            os.environ['PROJ_LIB'] = proj4_data_path4
            pyproj.pyproj_datadir = proj4_data_path4
            logger.debug("resulting PROJ_LIB = %s" % os.environ['PROJ_LIB'])
            cls.proj4_data_fixed = True
            return

        # TODO: add more cases to find GDAL_DATA

        raise RuntimeError("Unable to locate GDAL data at:\n- %s\n- %s\n- %s\n- %s"
                           % (proj4_data_path1, proj4_data_path2, proj4_data_path3, proj4_data_path4))

    @classmethod
    def lat_long_to_zone_number(cls, lat, long):
        if 56 <= lat < 64 and 3 <= long < 12:
            return 32

        if 72 <= lat <= 84 and long >= 0:
            if long < 9:
                return 31
            elif long < 21:
                return 33
            elif long < 33:
                return 35
            elif long < 42:
                return 37

        return int((long + 180) / 6) + 1


GdalAux.check_proj4_data()
