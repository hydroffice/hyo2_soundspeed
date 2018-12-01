import logging

from hyo2.soundspeed.listener.seacat.seacat_emulator import respond

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


respond()
