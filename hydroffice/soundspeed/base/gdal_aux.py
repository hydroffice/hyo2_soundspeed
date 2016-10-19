from __future__ import absolute_import, division, print_function, unicode_literals

import os
import sys
import logging

logger = logging.getLogger(__name__)

try:
    from osgeo import gdal
except ImportError as e:
    raise ImportError("Unable to load `osgeo.gdal` module: %s" % e)

try:
    from osgeo import ogr
except ImportError as e:
    raise ImportError("Unable to load `osgeo.ogr` module: %s" % e)

try:
    from osgeo import osr
except ImportError as e:
    raise ImportError("Unable to load `osgeo.osr` module: %s" % e)


def python_path():
    """ Return the python site-specific directory prefix (the temporary folder for PyInstaller) """

    # required by PyInstaller single-file mode
    if hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS

    # check if in a virtual environment
    if hasattr(sys, 'real_prefix'):
        return sys.real_prefix

    return sys.prefix


def check_gdal_data():
    """ Check the correctness of os env GDAL_DATA """

    # if 'GDAL_DATA' in os.environ:
    #     logger.debug("original GDAL_DATA = %s" % os.environ['GDAL_DATA'])

    gdal_data_path1 = os.path.join(os.path.dirname(gdal.__file__), 'data', 'gdal')
    # logger.debug("checking GDAL_DATA as %s" % gdal_data_path)
    if os.path.exists(gdal_data_path1):
        os.environ['GDAL_DATA'] = gdal_data_path1
        logger.debug("resulting GDAL_DATA = %s" % os.environ['GDAL_DATA'])
        return

    # conda specific
    gdal_data_path2 = os.path.join(python_path(), 'Library', 'data')
    if os.path.exists(gdal_data_path2):
        os.environ['GDAL_DATA'] = gdal_data_path2
        logger.debug("resulting GDAL_DATA = %s" % os.environ['GDAL_DATA'])
        return

    # TODO: add mmore cases to find GDAL_DATA

    raise RuntimeError("Unable to locate GDAL data at %s or %s" % (gdal_data_path1, gdal_data_path2))


class GdalAux(object):
    """ Auxiliary class to manage GDAL stuff """
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
        self.push_gdal_error_handler()

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
        """Create an ESRI prj file (geographic WGS84 by default)"""
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

    @staticmethod
    def push_gdal_error_handler():
        """ Install GDAL error handler """
        gdal.PushErrorHandler(GdalAux.gdal_error_handler)

    @staticmethod
    def gdal_error_handler(err_class, err_num, err_msg):
        """ GDAL Error Handler

        To test it: gdal.Error(1, 2, b'test error')
        """
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
