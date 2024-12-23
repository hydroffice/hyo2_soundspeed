import logging
import os

from netCDF4 import Dataset

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

input_path = r"C:\Users\gmasetti\AppData\Local\HydrOffice\Sound Speed\atlases\woa23_orig"
output_path = r"C:\Users\gmasetti\AppData\Local\HydrOffice\Sound Speed\atlases\woa23"

base_name = "woa23"
var_list = ["temp", "sal"]

#  """ USED TO REDUCE THE SIZE OF THE FULL DATABASE """

# temp annual
file = "%s_decav_%s00_04.nc" % (base_name, var_list[0][0])
folder = os.path.join(input_path, var_list[0])
if not os.path.exists(folder):
    raise RuntimeError("Unable to locate %s" % folder)
i_path = os.path.join(folder, file)
i = Dataset(i_path, mode='r')
o_folder = os.path.join(output_path, var_list[0])
if not os.path.exists(o_folder):
    os.makedirs(o_folder)
o_path = os.path.join(o_folder, file)
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

for var in var_list:

    # monthly/seasonal
    for idx in range(1, 17):
        file = "%s_decav_%s%02d_04.nc" % (base_name, var[0], idx)
        folder = os.path.join(input_path, var)
        if not os.path.exists(folder):
            raise RuntimeError("Unable to locate %s" % folder)
        i_path = os.path.join(folder, file)
        i = Dataset(i_path, mode='r')
        o_folder = os.path.join(output_path, var)
        if not os.path.exists(o_folder):
            os.makedirs(o_folder)
        o_path = os.path.join(o_folder, file)
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
