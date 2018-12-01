import logging

from hyo2.abc.lib.gdal_aux import GdalAux
from hyo2.soundspeed.soundspeed import SoundSpeedLibrary

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def main():
    # create a project
    lib = SoundSpeedLibrary()

    # set the current project name
    lib.setup.current_project = 'test'
    lib.setup.save_to_db()

    # retrieve all the id profiles from db
    lst = lib.db_list_profiles()
    logger.info("Profiles: %s" % len(lst))

    # plots/maps/exports
    # - map
    lib.map_db_profiles()
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
    lib.export_db_profiles_metadata(ogr_format=GdalAux.ogr_formats[b'KML'])
    lib.export_db_profiles_metadata(ogr_format=GdalAux.ogr_formats[b'CSV'])
    lib.export_db_profiles_metadata(ogr_format=GdalAux.ogr_formats[b'ESRI Shapefile'])

    logger.info('test: *** END ***')


if __name__ == "__main__":
    main()
