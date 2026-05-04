import logging
from typing import cast

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import netCDF4
from cartopy.mpl.geoaxes import GeoAxes
from numpy import where

# noinspection PyUnresolvedReferences
from hyo2.abc2.lib.logging import set_logging
# noinspection PyUnresolvedReferences
from hyo2.abc2.lib.testing import Testing

ns_list = ["hyo2.abc2"]
set_logging(ns_list=ns_list)
logger = logging.getLogger(__name__)

testing = Testing()

nc_path = testing.download_test_files(ext=".nc", subfolder="rtofs")[1]
logger.debug("path: %s" % nc_path)

# Extract the surface temperature field from the model
with netCDF4.Dataset(nc_path) as ds:
    lat = ds.variables['Latitude'][:]
    lon = ds.variables['Longitude'][:]
    temp = ds.variables['temperature'][0, 0, :, :]

# Handle longitude wrapping if necessary
lon = where(lon > 180, lon - 360, lon)

plt.figure(dpi=100)
ax = cast(GeoAxes, plt.axes(projection=ccrs.PlateCarree()))
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
