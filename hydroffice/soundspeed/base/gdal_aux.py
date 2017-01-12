from __future__ import absolute_import, division, print_function, unicode_literals

from osgeo import gdal
from osgeo import ogr
from osgeo import osr

import os
import logging

logger = logging.getLogger(__name__)

from hydroffice.soundspeed.base.helper import python_path


class GdalAux(object):
    """ Auxiliary class to manage GDAL stuff """

    error_loaded = False
    data_fixed = False

    ogr_formats = {
        b'ESRI Shapefile': 0,
        b'KML': 1,
        b'CSV': 2,
    }

    ogr_exts = {
        b'ESRI Shapefile': '.shp',
        b'KML': '.kml',
        b'CSV': '.csv',
    }

    def __init__(self):
        logger.debug("gdal version: %s" % gdal.VersionInfo(b'VERSION_NUM'))
        if not self.error_loaded:
            self.check_gdal_data()

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
        if os.path.exists(output_file):
            drv.DeleteDataSource(output_file)

        ds = drv.CreateDataSource(output_file)
        if ds is None:
            raise RuntimeError("Ogr failure in creation of data source: %s" % output_path)

        if ogr_format == cls.ogr_formats[b'ESRI Shapefile']:
            cls.create_prj_file(output_path, epsg=epsg)

        return ds

    @classmethod
    def create_prj_file(cls, output_path, epsg=4326):
        """Create an ESRI lib file (geographic WGS84 by default)"""
        spatial_ref = osr.SpatialReference()
        spatial_ref.ImportFromEPSG(epsg)

        spatial_ref.MorphToESRI()
        fid = open(output_path + '.lib', 'w')
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

        if cls.data_fixed:
            return

        if 'GDAL_DATA' in os.environ:

            logger.debug("unset original GDAL_DATA = %s" % os.environ['GDAL_DATA'])
            del os.environ['GDAL_DATA']

        gdal_data_path1 = os.path.join(os.path.dirname(gdal.__file__), 'data', 'gdal')
        gcs_csv_path1 = os.path.join(gdal_data_path1, 'gcs.csv')
        if os.path.exists(gcs_csv_path1):

            gdal.SetConfigOption(b'GDAL_DATA', gdal_data_path1.encode('utf-8'))
            logger.debug("resulting GDAL_DATA = %s" % gdal.GetConfigOption(b'GDAL_DATA'))
            cls.data_fixed = True
            cls.push_gdal_error_handler()
            return

        # anaconda specific
        gdal_data_path2 = os.path.join(python_path(), 'Library', 'data')
        gcs_csv_path2 = os.path.join(gdal_data_path2, 'gcs.csv')
        if os.path.exists(gcs_csv_path2):

            gdal.SetConfigOption(b'GDAL_DATA', gdal_data_path2.encode('utf-8'))
            logger.debug("resulting GDAL_DATA = %s" % gdal.GetConfigOption(b'GDAL_DATA'))
            cls.data_fixed = True
            cls.push_gdal_error_handler()
            return

        # anaconda specific
        gdal_data_path3 = os.path.join(python_path(), 'Library', 'share', 'gdal')
        gcs_csv_path3 = os.path.join(gdal_data_path3, 'gcs.csv')
        if os.path.exists(gcs_csv_path3):

            gdal.SetConfigOption(b'GDAL_DATA', gdal_data_path3.encode('utf-8'))
            logger.debug("resulting GDAL_DATA = %s" % gdal.GetConfigOption(b'GDAL_DATA'))
            cls.data_fixed = True
            cls.push_gdal_error_handler()
            return

        # TODO: add more cases to find GDAL_DATA

        raise RuntimeError("Unable to locate GDAL data at %s or %s" % (gdal_data_path1, gdal_data_path2))
