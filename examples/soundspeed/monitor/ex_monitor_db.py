from _datetime import datetime
from hyo.soundspeed.logging import test_logging

import logging
logger = logging.getLogger()

from hyo.soundspeed.base import testing
from hyo.soundspeed.monitor.db import MonitorDb
from hyo.soundspeed.base.gdal_aux import GdalAux

db = MonitorDb(base_name="test", projects_folder=testing.output_data_folder())

logger.debug("db version: %s" % db.get_db_version())

db.add_point(timestamp=datetime.now(), lat=30.5, long=-69.3, tss=1501.0, draft=8.4, avg_depth=1234.5)
db.add_point(timestamp=datetime.now(), lat=30.7, long=-69.5, tss=1502.0, draft=8.5, avg_depth=1235.7)
db.add_point(timestamp=datetime.now(), lat=30.45, long=-69.45, tss=1503.0, draft=8.5, avg_depth=1235.2)
db.add_point(timestamp=datetime.now(), lat=30.4, long=-69.15, tss=1501.3, draft=8.6, avg_depth=1235.4)
db.add_point(timestamp=datetime.now(), lat=30.71, long=-69.55, tss=1502.3, draft=8.6, avg_depth=1234.7)

times, ids = db.timestamp_list()
logger.debug("%s, %s" % (times, ids))

db.delete_point_by_id(1)

points = db.list_points()
logger.debug("%s" % (points, ))

timestamp, long, lat, tss, draft, avg_depth = db.point_by_id(2)
logger.debug("point: %s, %s, %s, %s, %s, %s" % (timestamp, long, lat, tss, draft, avg_depth))

db.export.export_surface_speed_points(output_folder=testing.output_data_folder())
db.export.export_surface_speed_points(output_folder=testing.output_data_folder(), ogr_format=GdalAux.ogr_formats['KML'])
db.export.export_surface_speed_points(output_folder=testing.output_data_folder(), ogr_format=GdalAux.ogr_formats['CSV'])
