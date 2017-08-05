from osgeo import ogr, gdal, osr
import numpy as np
import os
import logging

logger = logging.getLogger(__name__)

from hyo.soundspeed.base.gdal_aux import GdalAux
from hyo.soundspeed.profile.dicts import Dicts


class ExportDb:
    """Class that exports sound speed db data"""

    def __init__(self, db):
        self.db = db

    @classmethod
    def export_folder(cls, output_folder):
        folder = os.path.join(output_folder, "export")
        if not os.path.exists(folder):
            os.makedirs(folder)
        return folder

    def _create_ogr_lyr_and_fields(self, ds):
        # create the only data layer
        lyr = ds.CreateLayer('soundspeed', None, ogr.wkbPoint)
        if lyr is None:
            logger.error("Layer creation failed")
            return

        field = ogr.FieldDefn('id', ogr.OFTInteger)
        if lyr.CreateField(field) != 0:
            raise RuntimeError("Creating field failed.")

        field = ogr.FieldDefn('time', ogr.OFTString)
        if lyr.CreateField(field) != 0:
            raise RuntimeError("Creating field failed.")

        field = ogr.FieldDefn('tss', ogr.OFTReal)
        if lyr.CreateField(field) != 0:
            raise RuntimeError("Creating field failed.")

        field = ogr.FieldDefn('draft', ogr.OFTReal)
        if lyr.CreateField(field) != 0:
            raise RuntimeError("Creating field failed.")

        field = ogr.FieldDefn('avg_depth', ogr.OFTReal)
        if lyr.CreateField(field) != 0:
            raise RuntimeError("Creating field failed.")

        return lyr

    def export_surface_speed_points(self, output_folder, ogr_format=GdalAux.ogr_formats['ESRI Shapefile']):

        GdalAux()
        output = os.path.join(self.export_folder(output_folder=output_folder), self.db.base_name)

        # create the data source
        try:
            ds = GdalAux.create_ogr_data_source(ogr_format=ogr_format, output_path=output)
            lyr = self._create_ogr_lyr_and_fields(ds)

        except RuntimeError as e:
            logger.error("%s" % e)
            return

        rows = self.db.list_points()
        if rows is None:
            raise RuntimeError("Unable to retrieve profiles. Empty database?")
        if len(rows) == 0:
            raise RuntimeError("Unable to retrieve profiles. Empty database?")

        for row in rows:

            ft = ogr.Feature(lyr.GetLayerDefn())
            ft.SetField('id', int(row[0]))
            ft.SetField('time', row[1].isoformat())
            ft.SetField('tss', float(row[3]))
            ft.SetField('draft', float(row[4]))
            ft.SetField('avg_depth', float(row[5]))

            pt = ogr.Geometry(ogr.wkbPoint)
            pt.SetPointZM(0, float(row[2].x), float(row[2].y), float(row[4]), float(row[3]))

            try:
                ft.SetGeometry(pt)

            except Exception as e:
                RuntimeError("%s > pt: %s, %s" % (e, row[2].x, row[2].y))

            if lyr.CreateFeature(ft) != 0:
                raise RuntimeError("Unable to create feature")
            ft.Destroy()

        ds = None
        return True

    def rasterize_surface_speed_points(self, output_folder):

        GdalAux()

        # output file
        output = os.path.join(self.export_folder(output_folder=output_folder), self.db.base_name + ".tif")
        if os.path.exists(output):
            os.remove(output)

        # first retrieve the point positions
        lats = list()
        longs = list()
        tsss = list()
        rows = self.db.list_points()
        for row in rows:
            lats.append(row[2].y)
            longs.append(row[2].x)
            tsss.append(row[3])

        # retrieve geospatial info
        min_lat, max_lat, avg_lat = min(lats), max(lats), sum(lats) / len(lats)
        range_lat = max_lat - min_lat
        min_long, max_long, avg_long = min(longs), max(longs), sum(longs) / len(longs)
        range_long = max_long - min_long
        min_tss, max_tss = min(tsss), max(tsss)
        range_tss = max_tss - min_tss
        logger.debug("lat: %s / %s / %s" % (min_lat, max_lat, range_lat))
        logger.debug("long: %s / %s / %s" % (min_long, max_long, range_long))
        logger.debug("tss: %s / %s / %s" % (min_tss, max_tss, range_tss))

        # geographic srs
        geo_srs = osr.SpatialReference()
        geo_srs.ImportFromEPSG(4326)

        # UTM srs
        utm_zone = GdalAux.lat_long_to_zone_number(lat=avg_lat, long=avg_long)
        utm_srs = osr.SpatialReference()
        utm_north = False
        if avg_lat > 0:
            utm_north = True
        utm_srs.SetUTM(utm_zone, utm_north)
        utm_srs.SetWellKnownGeogCS('WGS84')

        # from GEO to UTM
        coord_transform = osr.CoordinateTransformation(geo_srs, utm_srs)

        # geographic at poles
        use_geographic = (max_lat > 80) or (min_lat < -80)

        if use_geographic:
            logger.debug("use geographic")
            buffer = 0.05 * max(range_lat, range_long)
            x_min = min_long - buffer
            x_max = max_long + buffer
            y_min = min_lat - buffer
            y_max = max_lat + buffer

        else:
            logger.debug("use UTM")

            min_point = ogr.Geometry(ogr.wkbPoint)
            min_point.AddPoint(min_long, min_lat)
            min_point.Transform(coord_transform)
            min_E = min_point.GetX()
            min_N = min_point.GetY()

            max_point = ogr.Geometry(ogr.wkbPoint)
            max_point.AddPoint(max_long, max_lat)
            max_point.Transform(coord_transform)
            max_E = max_point.GetX()
            max_N = max_point.GetY()

            buffer = 0.05 * max(max_N - min_N, max_E - min_E)
            x_min = min_E - buffer
            x_max = max_E + buffer
            y_min = min_N - buffer
            y_max = max_N + buffer

        if len(lats) < 40:
            x_pixels = 100
        elif len(lats) < 100:
            x_pixels = 200
        elif len(lats) < 1000:
            x_pixels = 400
        else:
            x_pixels = 1000
        pixel_size = (x_max - x_min) / x_pixels
        y_pixels = int((y_max - y_min) / pixel_size) + 1
        logger.debug("pixels -> x: %s, y: %s, size: %s, samples: %s" % (x_pixels, y_pixels, pixel_size, len(lats)))

        array = np.zeros((y_pixels, x_pixels), dtype=np.float32)
        for idx, lat in enumerate(lats):

            if use_geographic:
                idx_lat = y_pixels - 1 - int((lat - y_min + pixel_size / 2.0) / pixel_size)
                idx_long = int((longs[idx] - x_min - pixel_size / 2.0) / pixel_size)
            else:
                point = ogr.Geometry(ogr.wkbPoint)
                point.AddPoint(longs[idx], lat)
                point.Transform(coord_transform)
                E = point.GetX()
                N = point.GetY()

                idx_lat = y_pixels - 1 - int((N - y_min + pixel_size / 2.0) / pixel_size)
                idx_long = int((E - x_min - pixel_size / 2.0) / pixel_size)
            array[idx_lat, idx_long] = tsss[idx]

        driver = gdal.GetDriverByName('GTiff')

        ds = driver.Create(output, x_pixels, y_pixels, 1, gdal.GDT_Float32)
        ds.SetGeoTransform([x_min, pixel_size, 0, y_max, 0, -pixel_size])

        if use_geographic:
            ds.SetProjection(geo_srs.ExportToWkt())
        else:
            ds.SetProjection(utm_srs.ExportToWkt())

        ds.GetRasterBand(1).SetNoDataValue(0.0)
        ds.GetRasterBand(1).WriteArray(array=array)

        ds.FlushCache()
