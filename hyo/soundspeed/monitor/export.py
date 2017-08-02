from osgeo import ogr
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
