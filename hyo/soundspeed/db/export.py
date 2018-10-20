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
        lyr = ds.CreateLayer('ssp', None, ogr.wkbPoint)
        if lyr is None:
            logger.error("Layer creation failed")
            return

        field = ogr.FieldDefn('pk', ogr.OFTInteger)
        if lyr.CreateField(field) != 0:
            raise RuntimeError("Creating field failed.")

        field = ogr.FieldDefn('datetime', ogr.OFTString)
        if lyr.CreateField(field) != 0:
            raise RuntimeError("Creating field failed.")

        field = ogr.FieldDefn('sensor', ogr.OFTString)
        field.SetWidth(254)
        if lyr.CreateField(field) != 0:
            raise RuntimeError("Creating field failed.")

        field = ogr.FieldDefn('probe', ogr.OFTString)
        field.SetWidth(254)
        if lyr.CreateField(field) != 0:
            raise RuntimeError("Creating field failed.")

        field = ogr.FieldDefn('path', ogr.OFTString)
        field.SetWidth(254)
        if lyr.CreateField(field) != 0:
            raise RuntimeError("Creating field failed.")

        field = ogr.FieldDefn('agency', ogr.OFTString)
        field.SetWidth(254)
        if lyr.CreateField(field) != 0:
            raise RuntimeError("Creating field failed.")

        field = ogr.FieldDefn('survey', ogr.OFTString)
        field.SetWidth(254)
        if lyr.CreateField(field) != 0:
            raise RuntimeError("Creating field failed.")

        field = ogr.FieldDefn('vessel', ogr.OFTString)
        field.SetWidth(254)
        if lyr.CreateField(field) != 0:
            raise RuntimeError("Creating field failed.")

        field = ogr.FieldDefn('sn', ogr.OFTString)
        field.SetWidth(254)
        if lyr.CreateField(field) != 0:
            raise RuntimeError("Creating field failed.")

        field = ogr.FieldDefn('proc_time', ogr.OFTString)
        field.SetWidth(254)
        if lyr.CreateField(field) != 0:
            raise RuntimeError("Creating field failed.")

        field = ogr.FieldDefn('proc_info', ogr.OFTString)
        field.SetWidth(254)
        if lyr.CreateField(field) != 0:
            raise RuntimeError("Creating field failed.")

        field = ogr.FieldDefn('comments', ogr.OFTString)
        field.SetWidth(254)
        if lyr.CreateField(field) != 0:
            raise RuntimeError("Creating field failed.")

        field = ogr.FieldDefn('press_uom', ogr.OFTString)
        field.SetWidth(254)
        if lyr.CreateField(field) != 0:
            raise RuntimeError("Creating field failed.")

        field = ogr.FieldDefn('depth_uom', ogr.OFTString)
        field.SetWidth(254)
        if lyr.CreateField(field) != 0:
            raise RuntimeError("Creating field failed.")

        field = ogr.FieldDefn('ss_uom', ogr.OFTString)
        field.SetWidth(254)
        if lyr.CreateField(field) != 0:
            raise RuntimeError("Creating field failed.")

        field = ogr.FieldDefn('temp_uom', ogr.OFTString)
        field.SetWidth(254)
        if lyr.CreateField(field) != 0:
            raise RuntimeError("Creating field failed.")

        field = ogr.FieldDefn('cond_uom', ogr.OFTString)
        field.SetWidth(254)
        if lyr.CreateField(field) != 0:
            raise RuntimeError("Creating field failed.")

        field = ogr.FieldDefn('sal_uom', ogr.OFTString)
        field.SetWidth(254)
        if lyr.CreateField(field) != 0:
            raise RuntimeError("Creating field failed.")

        field = ogr.FieldDefn('ss_at_mind', ogr.OFTReal)
        if lyr.CreateField(field) != 0:
            raise RuntimeError("Creating field failed.")

        field = ogr.FieldDefn('min_depth', ogr.OFTReal)
        if lyr.CreateField(field) != 0:
            raise RuntimeError("Creating field failed.")

        field = ogr.FieldDefn('max_depth', ogr.OFTReal)
        if lyr.CreateField(field) != 0:
            raise RuntimeError("Creating field failed.")

        field = ogr.FieldDefn('max_raw_d', ogr.OFTReal)
        if lyr.CreateField(field) != 0:
            raise RuntimeError("Creating field failed.")

        field = ogr.FieldDefn('POINT_X', ogr.OFTReal)
        if lyr.CreateField(field) != 0:
            raise RuntimeError("Creating field failed.")

        field = ogr.FieldDefn('POINT_Y', ogr.OFTReal)
        if lyr.CreateField(field) != 0:
            raise RuntimeError("Creating field failed.")

        return lyr

    def export_profiles_metadata(self, project_name, output_folder, ogr_format=GdalAux.ogr_formats['ESRI Shapefile']):

        GdalAux()
        output = os.path.join(self.export_folder(output_folder=output_folder), project_name)

        # create the data source
        try:
            ds = GdalAux.create_ogr_data_source(ogr_format=ogr_format, output_path=output)
            lyr = self._create_ogr_lyr_and_fields(ds)

        except RuntimeError as e:
            logger.error("%s" % e)
            return

        rows = self.db.list_profiles()
        if rows is None:
            raise RuntimeError("Unable to retrieve profiles. Empty database?")
        if len(rows) == 0:
            raise RuntimeError("Unable to retrieve profiles. Empty database?")

        for row in rows:

            ft = ogr.Feature(lyr.GetLayerDefn())
            ft.SetField('pk', int(row[0]))
            ft.SetField('datetime', row[1].isoformat())
            ft.SetField('sensor', Dicts.first_match(Dicts.sensor_types, row[3]))
            ft.SetField('probe', Dicts.first_match(Dicts.probe_types, row[4]))
            ft.SetField('path', row[5])
            if row[6]:
                ft.SetField('agency', row[6])
            if row[7]:
                ft.SetField('survey', row[7])
            if row[8]:
                ft.SetField('vessel', row[8])
            if row[9]:
                ft.SetField('sn', row[9])
            ft.SetField('proc_time', row[10].isoformat())
            ft.SetField('proc_info', row[11])
            if row[12]:
                ft.SetField('comments', row[12])
            if row[13]:
                ft.SetField('press_uom', row[13])
            if row[14]:
                ft.SetField('depth_uom', row[14])
            if row[15]:
                ft.SetField('ss_uom', row[15])
            if row[16]:
                ft.SetField('temp_uom', row[16])
            if row[17]:
                ft.SetField('cond_uom', row[17])
            if row[18]:
                ft.SetField('sal_uom', row[18])
            if row[19]:
                ft.SetField('ss_at_mind', row[19])
            if row[20]:
                ft.SetField('min_depth', row[20])
            if row[21]:
                ft.SetField('max_depth', row[21])
            if row[22]:
                ft.SetField('max_raw_d', row[22])

            pt = ogr.Geometry(ogr.wkbPoint)
            lat = row[2].y
            lon = row[2].x
            if lon > 180.0:  # Go back to negative longitude
                lon -= 360.0
            pt.SetPoint_2D(0, lon, lat)

            ft.SetField('POINT_X', lon)
            ft.SetField('POINT_Y', lat)

            try:
                ft.SetGeometry(pt)

            except Exception as e:
                RuntimeError("%s > pt: %s, %s" % (e, lon, lat))

            if lyr.CreateFeature(ft) != 0:
                raise RuntimeError("Unable to create feature")
            ft.Destroy()

        ds = None
        return True
