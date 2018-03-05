import logging

logger = logging.getLogger(__name__)


class TracedProfilePlot:

    def __init__(self):
        self.old_ssp = -2
        self.new_ssp = -1

        self.new_outer_raypath = list()
        self.old_outer_raypath = list()
