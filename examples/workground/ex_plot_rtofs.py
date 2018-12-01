from hyo2.soundspeedmanager import AppInfo
from PySide2 import QtWidgets
from mpl_toolkits.basemap import Basemap
import numpy as np
import matplotlib.pyplot as plt
from pylab import *
import netCDF4

plt.figure()

nc = r'C:\code\hyo\soundspeed\hyo_soundspeed\data\download\rtofs_glo_3dz_f048_daily_3ztio.nc'

# Extract the surface temperature field from the model
file = netCDF4.Dataset(nc)
lat = file.variables['Latitude'][:]
lon = file.variables['Longitude'][:]
data = file.variables['temperature'][0, 0, :, :]
file.close()

# There is a quirk to the global NetCDF files that isn't in the NOMADS data, namely that there are junk values of longitude (lon>500) in the rightmost column of the longitude array (they are ignored by the model itself). So we have to work around them a little with NaN substitution.
lon = np.where(np.greater_equal(lon, 500), np.nan, lon)

# Plot the field using Basemap. Start with setting the map projection using the limits of the lat/lon data itself
m = Basemap(projection='mill', lat_ts=10, llcrnrlon=np.nanmin(lon), urcrnrlon=np.nanmax(lon),
            llcrnrlat=lat.min(), urcrnrlat=lat.max(), resolution='c')

# Convert geographic to projected coords
x, y = m(lon, lat)

# Plot using the fast pcolormesh
cs = m.pcolormesh(x, y, data, shading='flat', cmap=plt.cm.viridis)

# Add lines and grids
m.drawcoastlines()
m.fillcontinents()
m.drawmapboundary()
m.drawparallels(np.arange(-90., 120., 30.), labels=[1, 0, 0, 0])
m.drawmeridians(np.arange(-180., 180., 60.), labels=[0, 0, 0, 1])

# Add a colorbar and title
colorbar(cs)
plt.title('Global RTOFS - Sea Surface Temperature - 20181016')

plt.show()
