import logging
import os

from hyo2.abc.lib.gdal_aux import GdalAux
from hyo2.abc.lib.logging import set_logging
# noinspection PyUnresolvedReferences
from hyo2.soundspeedmanager import app_info
from hyo2.soundspeed.soundspeed import SoundSpeedLibrary

set_logging(ns_list=["hyo2.abc", "hyo2.soundspeed", "hyo2.soundspeedmanager", "hyo2.soundspeedsettings"])
logger = logging.getLogger(__name__)

# create a project
data_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
lib = SoundSpeedLibrary()

# set the current project name
lib.setup.current_project = 'default'
lib.setup.save_to_db()

# retrieve all the id profiles from db
lst = lib.db_list_profiles()
logger.info("Profiles: %s" % len(lst))

# plots/maps/exports
# - mapt
lib.map_db_profiles(show_plot=True)
lib.save_map_db_profiles()

# - aggregate plot
ssp_times = lib.db_timestamp_list()
dates = [ssp_times[0][0].date(), ssp_times[-1][0].date()]
lib.aggregate_plot(dates=dates)
lib.save_aggregate_plot(dates=dates)

# - daily plots
lib.plot_daily_db_profiles()
lib.save_daily_db_profiles()

# - exports
lib.export_db_profiles_metadata(ogr_format=GdalAux.ogr_formats['KML'])
lib.export_db_profiles_metadata(ogr_format=GdalAux.ogr_formats['CSV'])
lib.export_db_profiles_metadata(ogr_format=GdalAux.ogr_formats['ESRI Shapefile'])

logger.info('test: *** END ***')
