from __future__ import absolute_import, division, print_function, unicode_literals

from osgeo import ogr

import os
import logging

logger = logging.getLogger(__name__)

from hydroffice.soundspeed.base.gdal_aux import GdalAux
from hydroffice.soundspeed.profile.dicts import Dicts


class ExportDb(object):
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
        lyr = ds.CreateLayer(b'ssp', None, ogr.wkbPoint)
        if lyr is None:
            logger.error("Layer creation failed")
            return

        field = ogr.FieldDefn(b'pk', ogr.OFTInteger)
        if lyr.CreateField(field) != 0:
            raise RuntimeError("Creating field failed.")

        field = ogr.FieldDefn(b'datetime', ogr.OFTString)
        if lyr.CreateField(field) != 0:
            raise RuntimeError("Creating field failed.")

        field = ogr.FieldDefn(b'sensor', ogr.OFTString)
        field.SetWidth(254)
        if lyr.CreateField(field) != 0:
            raise RuntimeError("Creating field failed.")

        field = ogr.FieldDefn(b'probe', ogr.OFTString)
        field.SetWidth(254)
        if lyr.CreateField(field) != 0:
            raise RuntimeError("Creating field failed.")

        field = ogr.FieldDefn(b'path', ogr.OFTString)
        field.SetWidth(254)
        if lyr.CreateField(field) != 0:
            raise RuntimeError("Creating field failed.")

        field = ogr.FieldDefn(b'institution', ogr.OFTString)
        field.SetWidth(254)
        if lyr.CreateField(field) != 0:
            raise RuntimeError("Creating field failed.")

        field = ogr.FieldDefn(b'survey', ogr.OFTString)
        field.SetWidth(254)
        if lyr.CreateField(field) != 0:
            raise RuntimeError("Creating field failed.")

        field = ogr.FieldDefn(b'vessel', ogr.OFTString)
        field.SetWidth(254)
        if lyr.CreateField(field) != 0:
            raise RuntimeError("Creating field failed.")

        field = ogr.FieldDefn(b'sn', ogr.OFTString)
        field.SetWidth(254)
        if lyr.CreateField(field) != 0:
            raise RuntimeError("Creating field failed.")

        field = ogr.FieldDefn(b'proc_time', ogr.OFTString)
        field.SetWidth(254)
        if lyr.CreateField(field) != 0:
            raise RuntimeError("Creating field failed.")

        field = ogr.FieldDefn(b'proc_info', ogr.OFTString)
        field.SetWidth(254)
        if lyr.CreateField(field) != 0:
            raise RuntimeError("Creating field failed.")

        return lyr

    def export_profiles_metadata(self, project_name, output_folder, ogr_format=GdalAux.ogr_formats[b'ESRI Shapefile']):

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

            ft.SetField(b'pk', row[0])
            ft.SetField(b'datetime', row[1].isoformat())
            ft.SetField(b'sensor', Dicts.first_match(Dicts.sensor_types, row[3]).encode())
            ft.SetField(b'probe', Dicts.first_match(Dicts.probe_types, row[4]).encode())
            ft.SetField(b'path', row[5].encode())
            if row[6]:
                ft.SetField(b'institution', row[6].encode())
            if row[7]:
                ft.SetField(b'survey', row[7].encode())
            if row[8]:
                ft.SetField(b'vessel', row[8].encode())
            if row[9]:
                ft.SetField(b'sn', row[9].encode())
            ft.SetField(b'proc_time', row[10].isoformat())
            ft.SetField(b'proc_info', row[11].encode())

            pt = ogr.Geometry(ogr.wkbPoint)
            pt.SetPoint_2D(0, row[2].x, row[2].y)

            ft.SetGeometry(pt)
            if lyr.CreateFeature(ft) != 0:
                raise RuntimeError("Unable to create feature")
            ft.Destroy()

        ds = None
        return True
