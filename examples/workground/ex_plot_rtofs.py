import os
import logging

import numpy as np
import netCDF4
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

from hyo2.abc.lib.testing import Testing
from hyo2.abc.lib.logging import set_logging


ns_list = ["hyo2.abc2"]
set_logging(ns_list=ns_list)
logger = logging.getLogger(__name__)

testing = Testing(root_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))

nc_path = testing.download_test_files(ext=".nc", subfolder="rtofs")[1]

logger.debug("path: %s" % nc_path)

# Extract the surface temperature field from the model
file = netCDF4.Dataset(nc_path)
lat = file.variables['Latitude'][:]
lon = file.variables['Longitude'][:]
temp = file.variables['temperature'][0, 0, :, :]

file.close()

# Handle longitude wrapping if necessary
lon = np.where(lon > 180, lon - 360, lon)

plt.figure(dpi=100)
ax = plt.axes(projection=ccrs.PlateCarree())
ax.set_global()

# Add coastlines and gridlines
ax.coastlines(resolution='110m', linewidth=1)
ax.gridlines(draw_labels=True)

# Add land and ocean features
ax.add_feature(cfeature.LAND, zorder=0, edgecolor='black')
ax.add_feature(cfeature.OCEAN, zorder=0)

# Plot temperature (adjust cmap and vmin/vmax for better visualization if needed)
temp_plot = ax.contourf(lon, lat, temp, levels=60, transform=ccrs.PlateCarree(), cmap='coolwarm')

# Add colorbar
cbar = plt.colorbar(temp_plot, orientation='vertical', pad=0.05, aspect=30)
cbar.set_label('Temperature (°C)')

# Add title
plt.title('Sea Surface Temperature from NOAA RTOFS')

# Show the plot
plt.show()
