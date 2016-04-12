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

input_path = "C:\\Users\\gmasetti\\AppData\Local\\HydrOffice\\Sound Speed 0.1.0\\atlases\\woa13"
output_path = "C:\\Users\\gmasetti\\AppData\\Local\\HydrOffice\\Sound Speed 0.1.0\\atlases\\woa13_red"


def main():
    # temp annual
    file = "woa13_decav_t00_04v2.nc"
    i_path = os.path.join(input_path, "temp", file)
    i = Dataset(i_path, mode='r')
    o_path = os.path.join(output_path, "temp", file)
    if os.path.exists(o_path):
        os.remove(o_path)
    o = Dataset(o_path, mode='w')

    for name, dim in i.dimensions.iteritems():
        o.createDimension(name, len(dim) if not dim.isunlimited() else None)

    for name, var_i in i.variables.iteritems():

        if name in ['lat', 'lon', 'depth', 't_an']:
            # create variable
            var_o = o.createVariable(name, var_i.datatype, var_i.dimensions)
            # copy attributes
            var_o.setncatts({k: var_i.getncattr(k) for k in var_i.ncattrs()})
            # copy data
            var_o[:] = var_i[:]

    # temp monthly/seasonal
    for id in range(1, 17):
        file = "woa13_decav_t%02d_04v2.nc" % id
        i_path = os.path.join(input_path, "temp", file)
        i = Dataset(i_path, mode='r')
        o_path = os.path.join(output_path, "temp", file)
        if os.path.exists(o_path):
            os.remove(o_path)
        o = Dataset(o_path, mode='w')

        for name, dim in i.dimensions.iteritems():
            o.createDimension(name, len(dim) if not dim.isunlimited() else None)

        for name, var_i in i.variables.iteritems():

            if name in ['lon', 'lat', 't_an', 's_an', 't_sd', 's_sd', 'depth']:
                # create variable
                var_o = o.createVariable(name, var_i.datatype, var_i.dimensions)
                # copy attributes
                var_o.setncatts({k: var_i.getncattr(k) for k in var_i.ncattrs()})
                # copy data
                var_o[:] = var_i[:]

    # temp monthly/seasonal
    for id in range(1, 17):
        file = "woa13_decav_s%02d_04v2.nc" % id
        i_path = os.path.join(input_path, "sal", file)
        i = Dataset(i_path, mode='r')
        o_path = os.path.join(output_path, "sal", file)
        if os.path.exists(o_path):
            os.remove(o_path)
        o = Dataset(o_path, mode='w')

        for name, dim in i.dimensions.iteritems():
            o.createDimension(name, len(dim) if not dim.isunlimited() else None)

        for name, var_i in i.variables.iteritems():

            if name in ['lon', 'lat', 't_an', 's_an', 't_sd', 's_sd', 'depth']:
                # create variable
                var_o = o.createVariable(name, var_i.datatype, var_i.dimensions)
                # copy attributes
                var_o.setncatts({k: var_i.getncattr(k) for k in var_i.ncattrs()})
                # copy data
                var_o[:] = var_i[:]


if __name__ == "__main__":
    main()