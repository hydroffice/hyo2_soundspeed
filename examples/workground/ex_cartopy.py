import logging
import cartopy.crs as ccrs
from cartopy.feature import NaturalEarthFeature
import matplotlib.pyplot as plt
from hyo2.abc.lib.logging import set_logging

ns_list = ["hyo2.soundspeed", "hyo2.soundspeedmanager", "hyo2.soundspeedsettings"]
set_logging(ns_list=ns_list)

logger = logging.getLogger(__name__)

extent = [0, 50, 20, 60]

plt.figure("Test Map")
ax = plt.subplot(111, projection=ccrs.PlateCarree())
ax.set_extent(extent, crs=ccrs.PlateCarree())

ax.add_feature(NaturalEarthFeature('physical', 'ocean', '50m'))

plt.show()
