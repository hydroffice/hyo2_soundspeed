from __future__ import absolute_import, division, print_function, unicode_literals

import logging


class SettingsFilter(logging.Filter):
    def filter(self, record):
        # print(record.name, record.levelname)
        if record.name.startswith('hydroffice.ssp.settings') and (record.levelname == "INFO"):
            return False
        return True


class KmIOFilter(logging.Filter):
    def filter(self, record):
        # print(record.name, record.levelname)
        if record.name.startswith('hydroffice.ssp.io.kmio'):
            return False
        return True


# logging settings
logger = logging.getLogger()
logger.setLevel(logging.NOTSET)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)  # change to WARNING to reduce verbosity, DEBUG for high verbosity
ch_formatter = logging.Formatter('%(levelname)-9s %(name)s.%(funcName)s:%(lineno)d > %(message)s')
ch.setFormatter(ch_formatter)
ch.addFilter(SettingsFilter())
ch.addFilter(KmIOFilter())
logger.addHandler(ch)


from hydroffice.soundspeedmanager import gui
gui.gui()
