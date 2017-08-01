import time
from multiprocessing import Process, Event
import os

# logging settings
import logging
logger = logging.getLogger(__name__)

from .svpthread import SvpThread
from .replaythread import ReplayThread


class SisProcess(Process):
    """SIS simulator"""
    def __init__(self, port_in=4001, port_out=26103, ip_out="localhost",
                 target=None, name="SIS", verbose=None):
        Process.__init__(self, target=target, name=name)
        self.daemon = True
        self.verbose = verbose

        # user settings
        self.port_in = port_in
        self.port_out = port_out
        self.ip_out = ip_out

        # threads
        self.t_svp = None
        self.t_replay = None

        self.ssp = list()
        self.installation = list()
        self.runtime = list()

        self.files = list()

        self.shutdown = Event()

    def set_files(self, files):
        """set the files to be used by the simulator"""
        logger.debug("setting files")

        # clean files
        self.files = list()
        for f in files:
            if not os.path.exists(f):
                if self.verbose:
                    logger.debug("skip file: %s" % f)
                    continue

            self.files.append(f)
            logger.debug("file added: %s" % self.files[-1])

        if len(self.files) == 0:
            raise RuntimeError("Not valid file paths passed")

    def stop(self):
        """Stop the process"""
        self.shutdown.set()

    def init_thread(self):
        self.t_svp = SvpThread(runtime=self.runtime, installation=self.installation, ssp=self.ssp,
                               port_in=self.port_in, port_out=self.port_out, ip_out=self.ip_out)
        self.t_svp.start()

        self.t_replay = ReplayThread(runtime=self.runtime, installation=self.installation, ssp=self.ssp,
                                     files=self.files,
                                     port_in=self.port_in, port_out=self.port_out, ip_out=self.ip_out)
        self.t_replay.start()

    @staticmethod
    def init_logger():
        global logger
        logger = logging.getLogger()
        logger.setLevel(logging.NOTSET)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)  # change to WARNING to reduce verbosity, DEBUG for high verbosity
        ch_formatter = logging.Formatter('<PRC> %(levelname)-9s %(name)s.%(funcName)s:%(lineno)d > %(message)s')
        ch.setFormatter(ch_formatter)
        logger.addHandler(ch)
        logger = logging.getLogger(__name__)

    def run(self):
        """Start the simulation"""
        self.init_logger()
        logger.debug("%s start" % self.name)

        self.init_thread()

        count = 0
        while True:
            if self.shutdown.is_set():
                logger.debug("shutdown")
                self.t_replay.stop()
                self.t_svp.stop()
                self.t_replay.join()
                self.t_svp.join()
                break
            if (count % 100) == 0:
                logger.debug("#%04d: running" % count)

            time.sleep(0.001)
            count += 1

        logger.debug("%s end" % self.name)

