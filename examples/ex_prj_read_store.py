from __future__ import absolute_import, division, print_function, unicode_literals

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

from hydroffice.soundspeed.project import Project
from hydroffice.soundspeed.base.callbacks import TestCallbacks
from hydroffice.soundspeed.base import helper
from hydroffice.soundspeed.base.gdal_aux import GdalAux


def pair_reader_and_folder(folders, readers):
    """Create pair of folder and reader"""

    pairs = dict()

    for folder in folders:

        for reader in readers:

            if reader.name.lower() != 'valeport':  # reader filter
                continue
            if reader.name.lower() != folder.lower():  # skip not matching readers
                continue
            pairs[folder] = reader

    logger.info('pairs: %s' % pairs)
    return pairs


def list_test_files(data_input, pairs):
    """Create a dictionary of test file and reader to use with"""
    tests = dict()

    for folder in pairs.keys():

        reader = pairs[folder]
        reader_folder = os.path.join(data_input, folder)

        for root, dirs, files in os.walk(reader_folder):

            for filename in files:

                # check the extension
                ext = filename.split('.')[-1].lower()
                if ext not in reader.ext:
                    continue

                tests[os.path.join(root, filename)] = reader

    logger.info("tests (%d): %s" % (len(tests), tests))
    return tests


def main():
    # create a project
    prj = Project()
    # lib.activate_server_logger(True)
    # logger.info(lib)
    # lib.open_data_folder()

    # set callbacks
    prj.set_callbacks(TestCallbacks())
    # logger.info("test ask date: %s" % lib.cb.ask_date())
    # logger.info("test ask location: %s, %s" % lib.cb.ask_location())

    # retrieve data input/output folders
    data_input = helper.get_testing_input_folder()
    logger.info('input folder: %s' % data_input)
    data_output = helper.get_testing_output_folder()
    logger.info('output folder: %s' % data_output)

    # test readers/writers
    logger.info('test: *** START ***')
    data_sub_folders = helper.get_testing_input_subfolders()
    pairs = pair_reader_and_folder(folders=data_sub_folders, readers=prj.readers)
    tests = list_test_files(data_input=data_input, pairs=pairs)
    for idx, testfile in enumerate(tests.keys()):
        if idx > 0:
            break
        logger.info("test: * New profile: #%03d *" % idx)

        # import
        prj.import_data(data_path=testfile, data_format=tests[testfile].name)
        # print(lib.cur)
        # lib.plot_ssp(more=True, show=False)

        # store
        prj.ssp.cur.meta.project = "test"
        # lib.ssp.cur.meta.latitude += 2.
        # lib.ssp.cur.meta.longitude += 3.
        success = prj.store_data()
        logger.info("stored: %s" % success)

    # from matplotlib import pyplot as plt
    # plt.show()

    # retrieve all the id profiles from db
    lst = prj.db_list_profiles()
    logger.info("Profiles: %s" % len(lst))
    for p in lst:
        logger.info(p)

    # retrieve id profiles of a specific project from the db
    lst = prj.db_list_profiles(project='test')
    logger.info("Profiles of 'test' project: %s" % len(lst))
    for p in lst:
       logger.info(p)

    # retrieve a specific profile and delete it
    ssp_pk = lst[0][0]
    ssp = prj.db_retrieve_profile(pk=ssp_pk)
    logger.info("Retrieved profile:\n%s" % ssp)
    ret = prj.delete_db_profile(pk=ssp_pk)
    logger.info("Deleted profile: %s" % ret)

    # plots/maps/exports
    # lib.map_db_profiles()
    # lib.plot_daily_db_profiles()
    # lib.save_daily_db_profiles()
    # lib.export_db_profiles_metadata(ogr_format=GdalAux.ogr_formats[b'KML'])
    # lib.export_db_profiles_metadata(ogr_format=GdalAux.ogr_formats[b'CSV'])
    # lib.export_db_profiles_metadata(ogr_format=GdalAux.ogr_formats[b'ESRI Shapefile'])

    logger.info('test: *** END ***')


if __name__ == "__main__":
    main()
