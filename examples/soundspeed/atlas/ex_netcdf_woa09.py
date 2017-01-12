from __future__ import absolute_import, division, print_function, unicode_literals

from netCDF4 import Dataset
import os

# logging settings
import logging
logger = logging.getLogger()
logger.setLevel(logging.NOTSET)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)  # change to WARNING to reduce verbosity, DEBUG for high verbosity
ch_formatter = logging.Formatter('%(levelname)-9s %(name)s.%(funcName)s:%(lineno)d > %(message)s')
ch.setFormatter(ch_formatter)
logger.addHandler(ch)

input_path = "C:\\Users\\gmasetti\\AppData\Local\\HydrOffice\\Sound Speed 0.1.0\\atlases\\woa09"
output_path = "C:\\Users\\gmasetti\\AppData\\Local\\HydrOffice\\Sound Speed 0.1.0\\atlases\\woa09_red"


def main():
    """USED TO REDUCE THE SIZE OF THE FULL WOA09 DATABASE"""

    # temp annual
    file = "temperature_annual_1deg.nc"
    i_path = os.path.join(input_path, file)
    i = Dataset(i_path, mode='r')
    o_path = os.path.join(output_path, file)
    if os.path.exists(o_path):
        os.remove(o_path)
    o = Dataset(o_path, mode='w')

    for name, dim in i.dimensions.iteritems():
        o.createDimension(name, len(dim) if not dim.isunlimited() else None)

    for name, var_i in i.variables.iteritems():

        if name in ['t_an', 'depth']:
            # create variable
            var_o = o.createVariable(name, var_i.datatype, var_i.dimensions)
            # copy attributes
            var_o.setncatts({k: var_i.getncattr(k) for k in var_i.ncattrs()})
            # copy data
            var_o[:] = var_i[:]

    # temp monthly
    file = "temperature_monthly_1deg.nc"
    i_path = os.path.join(input_path, file)
    i = Dataset(i_path, mode='r')
    o_path = os.path.join(output_path, file)
    if os.path.exists(o_path):
        os.remove(o_path)
    o = Dataset(o_path, mode='w')

    for name, dim in i.dimensions.iteritems():
        o.createDimension(name, len(dim) if not dim.isunlimited() else None)

    for name, var_i in i.variables.iteritems():

        if name in ['t_an', 't_sd', 'lat', 'lon', 'time']:
            # create variable
            var_o = o.createVariable(name, var_i.datatype, var_i.dimensions)
            # copy attributes
            var_o.setncatts({k: var_i.getncattr(k) for k in var_i.ncattrs()})
            # copy data
            var_o[:] = var_i[:]

    # sal monthly
    file = "salinity_monthly_1deg.nc"
    i_path = os.path.join(input_path, file)
    i = Dataset(i_path, mode='r')
    o_path = os.path.join(output_path, file)
    if os.path.exists(o_path):
        os.remove(o_path)
    o = Dataset(o_path, mode='w')

    for name, dim in i.dimensions.iteritems():
        o.createDimension(name, len(dim) if not dim.isunlimited() else None)

    for name, var_i in i.variables.iteritems():

        if name in ['s_an', 's_sd']:
            # create variable
            var_o = o.createVariable(name, var_i.datatype, var_i.dimensions)
            # copy attributes
            var_o.setncatts({k: var_i.getncattr(k) for k in var_i.ncattrs()})
            # copy data
            var_o[:] = var_i[:]

    # temp seasonal
    file = "temperature_seasonal_1deg.nc"
    i_path = os.path.join(input_path, file)
    i = Dataset(i_path, mode='r')
    o_path = os.path.join(output_path, file)
    if os.path.exists(o_path):
        os.remove(o_path)
    o = Dataset(o_path, mode='w')

    for name, dim in i.dimensions.iteritems():
        o.createDimension(name, len(dim) if not dim.isunlimited() else None)

    for name, var_i in i.variables.iteritems():

        if name in ['depth', 'time', 't_an', 't_sd']:
            # create variable
            var_o = o.createVariable(name, var_i.datatype, var_i.dimensions)
            # copy attributes
            var_o.setncatts({k: var_i.getncattr(k) for k in var_i.ncattrs()})
            # copy data
            var_o[:] = var_i[:]

    # sal seasonal
    file = "salinity_seasonal_1deg.nc"
    i_path = os.path.join(input_path, file)
    i = Dataset(i_path, mode='r')
    o_path = os.path.join(output_path, file)
    if os.path.exists(o_path):
        os.remove(o_path)
    o = Dataset(o_path, mode='w')

    for name, dim in i.dimensions.iteritems():
        o.createDimension(name, len(dim) if not dim.isunlimited() else None)

    for name, var_i in i.variables.iteritems():

        if name in ['s_an', 's_sd']:
            # create variable
            var_o = o.createVariable(name, var_i.datatype, var_i.dimensions)
            # copy attributes
            var_o.setncatts({k: var_i.getncattr(k) for k in var_i.ncattrs()})
            # copy data
            var_o[:] = var_i[:]

    print(i)
    print(o)

if __name__ == "__main__":
    main()