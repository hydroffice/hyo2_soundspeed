import os
import logging
logger = logging.getLogger()
logger.setLevel(logging.NOTSET)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)  # change to WARNING to reduce verbosity, DEBUG for high verbosity
ch_formatter = logging.Formatter('%(levelname)-9s %(name)s.%(funcName)s:%(lineno)d > %(message)s')
ch.setFormatter(ch_formatter)
logger.addHandler(ch)

from hydroffice.soundspeed.base.gdal_aux import GdalAux
from hydroffice.soundspeed.base.testing import output_data_folder

# GdalAux.list_ogr_drivers()

aux = GdalAux()

for fmt in aux.ogr_formats:

    drv = aux.get_ogr_driver(ogr_format=aux.ogr_formats[fmt])

    out_path = os.path.join(output_data_folder(), "ex_gdal_aux")
    ds = aux.create_ogr_data_source(ogr_format=aux.ogr_formats[fmt],
                                    output_path=out_path)
