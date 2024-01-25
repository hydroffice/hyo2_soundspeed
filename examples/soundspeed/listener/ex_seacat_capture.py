import logging

from hyo2.ssm2.lib.listener.seacat.seacat_emulator import respond
from hyo2.abc2.lib.logging import set_logging

set_logging(ns_list=["hyo2.abc2", "hyo2.ssm2"])

logger = logging.getLogger(__name__)


respond()
