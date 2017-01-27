import os
from hydroffice.soundspeed.logging import test_logging

import logging
logger = logging.getLogger()

from hydroffice.soundspeed.base.gdal_aux import GdalAux
from hydroffice.soundspeed.base.testing import output_data_folder

GdalAux.list_ogr_drivers()

aux = GdalAux()

for fmt in aux.ogr_formats:

    drv = aux.get_ogr_driver(ogr_format=aux.ogr_formats[fmt])

    out_path = os.path.join(output_data_folder(), "ex_gdal_aux")
    ds = aux.create_ogr_data_source(ogr_format=aux.ogr_formats[fmt],
                                    output_path=out_path)
