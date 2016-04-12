from __future__ import absolute_import, division, print_function, unicode_literals

from matplotlib import pyplot as plt
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
    logger.info('pairs: %s' % pairs.keys())
    return pairs


def list_test_files(data_input, pairs):
    """Create a dictionary of test file and reader to use with"""
    tests = dict()
    for folder in pairs.keys():
        reader = pairs[folder]
        reader_folder = os.path.join(data_input, folder)

        for root, dirs, files in os.walk(reader_folder):
            for file in files:

                # check the extension
                ext = file.split('.')[-1].lower()
                if ext not in reader.ext:
                    continue

                tests[os.path.join(root, file)] = reader
    # logger.info("tests: %s" % tests)
    return tests


def main():
    # create a project
    prj = Project()
    # prj.activate_server_logger(True)
    logger.info(prj)
    # prj.open_data_folder()

    # set callbacks
    prj.set_callbacks(TestCallbacks())
    logger.info("test ask date: %s" % prj.cb.ask_date())
    logger.info("test ask location: %s, %s" % prj.cb.ask_location())

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
    for idx, test in enumerate(tests.keys()):
        if idx != 0:
            break
        logger.info("test: * NEW #%02d *" % idx)

        # import
        prj.import_data(data_path=test, data_format=tests[test].name)
        # print(prj.cur)

        # plot
        # prj.plot_ssp(more=True, show=False)

        # store
        prj.ssp.cur.meta.project = "test"
        # prj.ssp.cur.meta.latitude += 2.
        # prj.ssp.cur.meta.longitude += 3.
        success = prj.store_data()
        logger.info("stored: %s" % success)

    # plt.show()

    lst = prj.db_profiles()
    logger.info("Profiles: %s" % len(lst))
    for p in lst:
        logger.info(p)

    lst = prj.db_profiles(project='test')
    logger.info("Profiles of 'test' project: %s" % len(lst))
    for p in lst:
        logger.info(p)

    ssp_pk = lst[0][0]
    ssp = prj.db_profile(pk=ssp_pk)
    logger.info("Retrieved profile:\n%s" % ssp)
    # prj.delete_db_profile(pk=ssp_pk)

    prj.map_db_profiles()
    prj.plot_daily_db_profiles()
    prj.save_daily_db_profiles()
    prj.export_db_profiles_metadata(ogr_format=GdalAux.ogr_formats['KML'])
    prj.export_db_profiles_metadata(ogr_format=GdalAux.ogr_formats['CSV'])
    prj.export_db_profiles_metadata()

    logger.info('test: *** END ***')


if __name__ == "__main__":
    main()
