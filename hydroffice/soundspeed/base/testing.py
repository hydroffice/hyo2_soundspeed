from __future__ import absolute_import, division, print_function, unicode_literals

import os
import logging
logger = logging.getLogger(__name__)

from hydroffice.soundspeed import formats


def root_data_folder():
    """Return the root test data folder"""
    data_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir, 'data'))
    if not os.path.exists(data_folder):
        raise RuntimeError("the root test data folder does not exist: %s" % data_folder)
    return data_folder


# INPUT

def input_data_folder():
    """Return the input test data folder"""
    input_folder = os.path.abspath(os.path.join(root_data_folder(), 'input'))
    if not os.path.exists(input_folder):
        raise RuntimeError("the input test data folder does not exist: %s" % input_folder)
    return input_folder


def input_data_sub_folders():
    """Return a list of sub-folders under the input folder"""
    folder_list = list()
    list_dir = os.listdir(input_data_folder())
    for element in list_dir:
        element_path = os.path.join(input_data_folder(), element)
        if os.path.isdir(element_path):
            folder_list.append(element_path)
    return folder_list


def input_test_files(input_sub_folder, ext):
    """Return a list of files with the given extension present in the input test data folder"""
    file_list = list()
    for root, dirs, files in os.walk(input_sub_folder):
        for f in files:
            if f.endswith(ext):
                file_list.append(os.path.join(root, f))
    return file_list


# - DOWNLOAD

def download_data_folder():
    """Return the download test data folder"""
    download_folder = os.path.abspath(os.path.join(root_data_folder(), 'download'))
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)
    return download_folder


def download_test_files(ext):
    """Return a list of files with the given extension present in the download test data folder"""
    file_list = list()
    for root, dirs, files in os.walk(download_data_folder()):
        for f in files:
            if f.endswith(ext):
                file_list.append(os.path.join(root, f))
    return file_list


# OUTPUT

def output_data_folder():
    """Return the output test data folder"""
    output_folder = os.path.abspath(os.path.join(root_data_folder(), 'output'))
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    return output_folder


# AUX methods

def pair_readers_and_folders(folders, inclusive_filters=None):
    """Create pair of folder and reader"""

    pairs = dict()

    for folder in folders:

        folder = folder.split(os.sep)[-1]
        # logger.debug('pairing folder: %s' % folder)

        for reader in formats.readers:

            if inclusive_filters:
                if reader.name.lower() not in inclusive_filters:
                    continue

            if reader.name.lower() != folder.lower():  # skip not matching readers
                continue

            pairs[folder] = reader

    logger.info('pairs: %s' % pairs)
    return pairs


def dict_test_files(data_folder, pairs):
    """Create a dictionary of test file and reader to use with"""
    tests = dict()

    for folder in pairs.keys():

        reader = pairs[folder]
        reader_folder = os.path.join(data_folder, folder)

        for root, dirs, files in os.walk(reader_folder):

            for filename in files:

                # check the extension
                ext = filename.split('.')[-1].lower()
                if ext not in reader.ext:
                    continue

                tests[os.path.join(root, filename)] = reader

    logger.info("tests (%d): %s" % (len(tests), tests))
    return tests


def input_dict_test_files(inclusive_filters=None):
    pair_dict = pair_readers_and_folders(folders=input_data_sub_folders(),
                                         inclusive_filters=inclusive_filters)
    files_dict = dict_test_files(data_folder=input_data_folder(),
                                 pairs=pair_dict)
    return files_dict
