import os
import logging
from hyo2.soundspeedmanager import AppInfo
from PySide2 import QtWidgets
from mpl_toolkits.basemap import Basemap
import numpy as np
from matplotlib import pyplot as plt
import netCDF4

from hyo2.abc.lib.testing import Testing

logging.basicConfig(level=logging.DEBUG,
                    format="%(levelname)-9s %(name)s.%(funcName)s:%(lineno)d > %(message)s")
logger = logging.getLogger(__name__)

testing = Testing(root_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))

nc_path = testing.download_test_files(ext=".nc", subfolder="rtofs")[1]
logger.debug("path: %s" % nc_path)

# Extract the surface temperature field from the model
file = netCDF4.Dataset(nc_path)
lat = file.variables['Latitude'][:]
lon = file.variables['Longitude'][:]
data = file.variables['temperature'][0, 0, :, :]

file.close()

# There is a quirk to the global NetCDF files that isn't in the NOMADS data, namely that there are junk values
# of longitude (lon>500) in the rightmost column of the longitude array (they are ignored by the model itself).
# So we have to work around them a little with NaN substitution.
lon = np.where(np.greater_equal(lon, 500), np.nan, lon)

# Plot the field using Basemap. Start with setting the map projection using the limits of the lat/lon data itself
plt.figure()

m = Basemap(projection='mill', lat_ts=10, llcrnrlon=np.nanmin(lon), urcrnrlon=np.nanmax(lon),
            llcrnrlat=lat.min(), urcrnrlat=lat.max(), resolution='c')

# Convert geographic to projected coords
x, y = m(lon, lat)
# # logger.debug("xs: %s" % x)
# # logger.debug("ys: %s" % y)

# Plot using the fast pcolormesh
ma_x = np.ma.array(x, mask=np.isnan(x))
ma_x = np.ma.array(ma_x, mask=np.greater_equal(ma_x, 1e30))
ma_y = np.ma.array(y, mask=np.isnan(y))
ma_y = np.ma.array(ma_y, mask=np.greater_equal(ma_y, 1e30))
# logger.debug("xs: %s" % ma_x)
# logger.debug("ys: %s" % ma_y)

cs = m.pcolor(ma_x, ma_y, data, cmap=plt.cm.viridis)

# Add lines and grids
m.drawcoastlines()
m.fillcontinents()
m.drawmapboundary()
m.drawparallels(np.arange(-90., 120., 30.), labels=[1, 0, 0, 0])
m.drawmeridians(np.arange(-180., 180., 60.), labels=[0, 0, 0, 1])

# Add a colorbar and title
plt.colorbar(cs)
plt.title('Global RTOFS - Sea Surface Temperature - 20181016')

plt.show()
