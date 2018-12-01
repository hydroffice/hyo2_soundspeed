import logging
from hyo2.soundspeedmanager import gui


class DebugFilter(logging.Filter):

    def filter(self, record):

        if record.name[:3] != "hyo":
            return False

        # if (record.name == 'hyo2.soundspeed.listener.sis.sis') and \
        #         (record.funcName == "parse") and (record.levelname == "INFO"):
        #     return False

        return True


# logging settings
logger = logging.getLogger()
logger.setLevel(logging.NOTSET)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)  # change to WARNING to reduce verbosity, DEBUG for high verbosity
ch_formatter = logging.Formatter('%(levelname)-9s %(name)s.%(funcName)s:%(lineno)d > %(message)s')
ch.setFormatter(ch_formatter)
ch.addFilter(DebugFilter())
logger.addHandler(ch)

gui.gui()
