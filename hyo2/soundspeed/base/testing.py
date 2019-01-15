import os
import logging
from typing import Optional

from hyo2.abc.lib.testing import Testing
from hyo2.soundspeed import formats

logger = logging.getLogger(__name__)


class SoundSpeedTesting(Testing):

    def __init__(self, root_folder: Optional[str] = None):
        super().__init__(root_folder=root_folder)

    # -- PAIRS ---

    @classmethod
    def pair_readers_and_folders(cls, folders, inclusive_filters=None):
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

        # logger.info('pairs: %s' % pairs)
        return pairs

    @classmethod
    def dict_test_files(cls, data_folder, pairs):
        """Create a dictionary of test file and reader to use with"""
        tests = dict()

        for folder in pairs.keys():

            reader = pairs[folder]
            reader_folder = os.path.join(data_folder, folder)

            for root, _, files in os.walk(reader_folder):

                for filename in files:

                    # check the extension
                    ext = filename.split('.')[-1].lower()
                    if ext not in reader.ext:
                        continue

                    tests[os.path.join(root, filename)] = reader

        # logger.info("tests (%d): %s" % (len(tests), tests))
        return tests

    def input_dict_test_files(self, inclusive_filters=None):
        pair_dict = self.pair_readers_and_folders(folders=self.input_data_sub_folders(),
                                                  inclusive_filters=inclusive_filters)
        files_dict = self.dict_test_files(data_folder=self.input_data_folder(),
                                          pairs=pair_dict)
        return files_dict
