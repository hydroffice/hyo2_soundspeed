import logging
import os

from netCDF4 import Dataset

from hyo2.soundspeedmanager import AppInfo

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

input_path = r"C:\Users\gmasetti\AppData\Local\HydrOffice\Sound Speed\atlases\woa18_orig"
output_path = r"C:\Users\gmasetti\AppData\Local\HydrOffice\Sound Speed\atlases\woa18"

#  """ USED TO REDUCE THE SIZE OF THE FULL WOA13 DATABASE """

# temp annual
file = "woa18_decav_t00_04.nc"
i_path = os.path.join(input_path, "temp", file)
i = Dataset(i_path, mode='r')
o_path = os.path.join(output_path, "temp", file)
if os.path.exists(o_path):
    os.remove(o_path)
o = Dataset(o_path, mode='w')

for name, dim in i.dimensions.items():
    o.createDimension(name, len(dim) if not dim.isunlimited() else None)

for name, var_i in i.variables.items():

    if name in ['lat', 'lon', 'depth', 't_an']:
        # create variable
        var_o = o.createVariable(name, var_i.datatype, var_i.dimensions)
        # copy attributes
        var_o.setncatts({k: var_i.getncattr(k) for k in var_i.ncattrs()})
        # copy data
        var_o[:] = var_i[:]

# temp monthly/seasonal
for id in range(1, 17):
    file = "woa18_decav_t%02d_04.nc" % id
    i_path = os.path.join(input_path, "temp", file)
    i = Dataset(i_path, mode='r')
    o_path = os.path.join(output_path, "temp", file)
    if os.path.exists(o_path):
        os.remove(o_path)
    o = Dataset(o_path, mode='w')

    for name, dim in i.dimensions.items():
        o.createDimension(name, len(dim) if not dim.isunlimited() else None)

    for name, var_i in i.variables.items():

        if name in ['lon', 'lat', 't_an', 's_an', 't_sd', 's_sd', 'depth']:
            # create variable
            var_o = o.createVariable(name, var_i.datatype, var_i.dimensions)
            # copy attributes
            var_o.setncatts({k: var_i.getncattr(k) for k in var_i.ncattrs()})
            # copy data
            var_o[:] = var_i[:]

# temp monthly/seasonal
for id in range(1, 17):
    file = "woa18_decav_s%02d_04.nc" % id
    i_path = os.path.join(input_path, "sal", file)
    i = Dataset(i_path, mode='r')
    o_path = os.path.join(output_path, "sal", file)
    if os.path.exists(o_path):
        os.remove(o_path)
    o = Dataset(o_path, mode='w')

    for name, dim in i.dimensions.items():
        o.createDimension(name, len(dim) if not dim.isunlimited() else None)

    for name, var_i in i.variables.items():

        if name in ['lon', 'lat', 't_an', 's_an', 't_sd', 's_sd', 'depth']:
            # create variable
            var_o = o.createVariable(name, var_i.datatype, var_i.dimensions)
            # copy attributes
            var_o.setncatts({k: var_i.getncattr(k) for k in var_i.ncattrs()})
            # copy data
            var_o[:] = var_i[:]
