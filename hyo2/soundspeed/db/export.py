import os
import logging
import ogr
from typing import Optional

from hyo2.abc.lib.gdal_aux import GdalAux
from hyo2.soundspeed.profile.dicts import Dicts

logger = logging.getLogger(__name__)


class ExportDbFields:

    def __init__(self):
        self.fields = {
            'pk': True,
            'datetime': True,
            'sensor': True,
            'probe': True,
            'path': True,
            'filename': True,
            'agency': True,
            'survey': True,
            'vessel': True,
            'sn': True,
            'proc_time': True,
            'proc_info': True,
            'surveyline': True,
            'comments': True,
            'press_uom': True,
            'depth_uom': True,
            'ss_uom': True,
            'temp_uom': True,
            'cond_uom': True,
            'sal_uom': True,
            'ss_at_mind': True,
            'min_depth': True,
            'max_depth': True,
            'max_raw_d': True,
            'POINT_X': True,
            'POINT_Y': True
        }


class ExportDb:
    """Class that exports sound speed db data"""

    def __init__(self, db):
        self.db = db
        self.filter_fields = None

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

        if self.filter_fields.fields['pk']:
            field = ogr.FieldDefn('pk', ogr.OFTInteger)
            if lyr.CreateField(field) != 0:
                raise RuntimeError("Creating field failed.")

        if self.filter_fields.fields['datetime']:
            field = ogr.FieldDefn('datetime', ogr.OFTString)
            if lyr.CreateField(field) != 0:
                raise RuntimeError("Creating field failed.")

        if self.filter_fields.fields['sensor']:
            field = ogr.FieldDefn('sensor', ogr.OFTString)
            field.SetWidth(254)
            if lyr.CreateField(field) != 0:
                raise RuntimeError("Creating field failed.")

        if self.filter_fields.fields['probe']:
            field = ogr.FieldDefn('probe', ogr.OFTString)
            field.SetWidth(254)
            if lyr.CreateField(field) != 0:
                raise RuntimeError("Creating field failed.")

        if self.filter_fields.fields['path']:
            field = ogr.FieldDefn('path', ogr.OFTString)
            field.SetWidth(254)
            if lyr.CreateField(field) != 0:
                raise RuntimeError("Creating field failed.")

        if self.filter_fields.fields['filename']:
            field = ogr.FieldDefn('filename', ogr.OFTString)
            field.SetWidth(254)
            if lyr.CreateField(field) != 0:
                raise RuntimeError("Creating field failed.")

        if self.filter_fields.fields['agency']:
            field = ogr.FieldDefn('agency', ogr.OFTString)
            field.SetWidth(254)
            if lyr.CreateField(field) != 0:
                raise RuntimeError("Creating field failed.")

        if self.filter_fields.fields['survey']:
            field = ogr.FieldDefn('survey', ogr.OFTString)
            field.SetWidth(254)
            if lyr.CreateField(field) != 0:
                raise RuntimeError("Creating field failed.")

        if self.filter_fields.fields['vessel']:
            field = ogr.FieldDefn('vessel', ogr.OFTString)
            field.SetWidth(254)
            if lyr.CreateField(field) != 0:
                raise RuntimeError("Creating field failed.")

        if self.filter_fields.fields['sn']:
            field = ogr.FieldDefn('sn', ogr.OFTString)
            field.SetWidth(254)
            if lyr.CreateField(field) != 0:
                raise RuntimeError("Creating field failed.")

        if self.filter_fields.fields['proc_time']:
            field = ogr.FieldDefn('proc_time', ogr.OFTString)
            field.SetWidth(254)
            if lyr.CreateField(field) != 0:
                raise RuntimeError("Creating field failed.")

        if self.filter_fields.fields['proc_info']:
            field = ogr.FieldDefn('proc_info', ogr.OFTString)
            field.SetWidth(254)
            if lyr.CreateField(field) != 0:
                raise RuntimeError("Creating field failed.")

        if self.filter_fields.fields['surveyline']:
            field = ogr.FieldDefn('surveyline', ogr.OFTString)
            field.SetWidth(254)
            if lyr.CreateField(field) != 0:
                raise RuntimeError("Creating field failed.")

        if self.filter_fields.fields['comments']:
            field = ogr.FieldDefn('comments', ogr.OFTString)
            field.SetWidth(254)
            if lyr.CreateField(field) != 0:
                raise RuntimeError("Creating field failed.")

        if self.filter_fields.fields['press_uom']:
            field = ogr.FieldDefn('press_uom', ogr.OFTString)
            field.SetWidth(254)
            if lyr.CreateField(field) != 0:
                raise RuntimeError("Creating field failed.")

        if self.filter_fields.fields['depth_uom']:
            field = ogr.FieldDefn('depth_uom', ogr.OFTString)
            field.SetWidth(254)
            if lyr.CreateField(field) != 0:
                raise RuntimeError("Creating field failed.")

        if self.filter_fields.fields['ss_uom']:
            field = ogr.FieldDefn('ss_uom', ogr.OFTString)
            field.SetWidth(254)
            if lyr.CreateField(field) != 0:
                raise RuntimeError("Creating field failed.")

        if self.filter_fields.fields['temp_uom']:
            field = ogr.FieldDefn('temp_uom', ogr.OFTString)
            field.SetWidth(254)
            if lyr.CreateField(field) != 0:
                raise RuntimeError("Creating field failed.")

        if self.filter_fields.fields['cond_uom']:
            field = ogr.FieldDefn('cond_uom', ogr.OFTString)
            field.SetWidth(254)
            if lyr.CreateField(field) != 0:
                raise RuntimeError("Creating field failed.")

        if self.filter_fields.fields['sal_uom']:
            field = ogr.FieldDefn('sal_uom', ogr.OFTString)
            field.SetWidth(254)
            if lyr.CreateField(field) != 0:
                raise RuntimeError("Creating field failed.")

        if self.filter_fields.fields['ss_at_mind']:
            field = ogr.FieldDefn('ss_at_mind', ogr.OFTReal)
            if lyr.CreateField(field) != 0:
                raise RuntimeError("Creating field failed.")

        if self.filter_fields.fields['min_depth']:
            field = ogr.FieldDefn('min_depth', ogr.OFTReal)
            if lyr.CreateField(field) != 0:
                raise RuntimeError("Creating field failed.")

        if self.filter_fields.fields['max_depth']:
            field = ogr.FieldDefn('max_depth', ogr.OFTReal)
            if lyr.CreateField(field) != 0:
                raise RuntimeError("Creating field failed.")

        if self.filter_fields.fields['max_raw_d']:
            field = ogr.FieldDefn('max_raw_d', ogr.OFTReal)
            if lyr.CreateField(field) != 0:
                raise RuntimeError("Creating field failed.")

        if self.filter_fields.fields['POINT_X']:
            field = ogr.FieldDefn('POINT_X', ogr.OFTReal)
            if lyr.CreateField(field) != 0:
                raise RuntimeError("Creating field failed.")

        if self.filter_fields.fields['POINT_Y']:
            field = ogr.FieldDefn('POINT_Y', ogr.OFTReal)
            if lyr.CreateField(field) != 0:
                raise RuntimeError("Creating field failed.")

        return lyr

    def export_profiles_metadata(self, project_name: str, output_folder: str,
                                 ogr_format: Optional[int] = GdalAux.ogr_formats['ESRI Shapefile'],
                                 filter_fields: Optional[ExportDbFields] = None) -> bool:
        self.filter_fields = filter_fields
        if self.filter_fields is None:
            self.filter_fields = ExportDbFields()

        GdalAux()
        output = os.path.join(self.export_folder(output_folder=output_folder), project_name)

        # create the data source
        try:
            ds = GdalAux.create_ogr_data_source(ogr_format=ogr_format, output_path=output)
            lyr = self._create_ogr_lyr_and_fields(ds)

        except RuntimeError as e:
            logger.error("%s" % e)
            return False

        rows = self.db.list_profiles()
        if rows is None:
            raise RuntimeError("Unable to retrieve profiles. Empty database?")
        if len(rows) == 0:
            raise RuntimeError("Unable to retrieve profiles. Empty database?")

        for row in rows:

            ft = ogr.Feature(lyr.GetLayerDefn())

            if self.filter_fields.fields['pk']:
                ft.SetField('pk', int(row[0]))

            if self.filter_fields.fields['datetime']:
                ft.SetField('datetime', row[1].isoformat())

            if self.filter_fields.fields['sensor']:
                ft.SetField('sensor', Dicts.first_match(Dicts.sensor_types, row[3]))

            if self.filter_fields.fields['probe']:
                ft.SetField('probe', Dicts.first_match(Dicts.probe_types, row[4]))

            if self.filter_fields.fields['path']:
                ft.SetField('path', row[5])

            if self.filter_fields.fields['filename']:
                ft.SetField('filename', os.path.basename(row[5]))

            if self.filter_fields.fields['agency']:
                if row[6]:
                    ft.SetField('agency', row[6])

            if self.filter_fields.fields['survey']:
                if row[7]:
                    ft.SetField('survey', row[7])

            if self.filter_fields.fields['vessel']:
                if row[8]:
                    ft.SetField('vessel', row[8])

            if self.filter_fields.fields['sn']:
                if row[9]:
                    ft.SetField('sn', row[9])

            if self.filter_fields.fields['proc_time']:
                ft.SetField('proc_time', row[10].isoformat())

            if self.filter_fields.fields['proc_info']:
                ft.SetField('proc_info', row[11])

            if self.filter_fields.fields['surveyline']:
                if row[12]:
                    ft.SetField('surveyline', row[12])

            if self.filter_fields.fields['comments']:
                if row[13]:
                    ft.SetField('comments', row[13])

            if self.filter_fields.fields['press_uom']:
                if row[14]:
                    ft.SetField('press_uom', row[14])

            if self.filter_fields.fields['depth_uom']:
                if row[15]:
                    ft.SetField('depth_uom', row[15])

            if self.filter_fields.fields['ss_uom']:
                if row[16]:
                    ft.SetField('ss_uom', row[16])

            if self.filter_fields.fields['temp_uom']:
                if row[17]:
                    ft.SetField('temp_uom', row[17])

            if self.filter_fields.fields['cond_uom']:
                if row[18]:
                    ft.SetField('cond_uom', row[18])

            if self.filter_fields.fields['sal_uom']:
                if row[19]:
                    ft.SetField('sal_uom', row[19])

            if self.filter_fields.fields['ss_at_mind']:
                if row[20]:
                    ft.SetField('ss_at_mind', row[20])

            if self.filter_fields.fields['min_depth']:
                if row[21]:
                    ft.SetField('min_depth', row[21])

            if self.filter_fields.fields['max_depth']:
                if row[22]:
                    ft.SetField('max_depth', row[22])

            if self.filter_fields.fields['max_raw_d']:
                if row[23]:
                    ft.SetField('max_raw_d', row[23])

            pt = ogr.Geometry(ogr.wkbPoint)
            lat = row[2].y
            lon = row[2].x
            if lon > 180.0:  # Go back to negative longitude
                lon -= 360.0
            pt.SetPoint_2D(0, lon, lat)

            if self.filter_fields.fields['POINT_X']:
                ft.SetField('POINT_X', lon)

            if self.filter_fields.fields['POINT_Y']:
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
