from hyo.soundspeed.logging import test_logging

from os import path
import logging

from hyo.soundspeed.listener.seacat.seacat_emulator import respond

logger = logging.getLogger()


def main():

    respond()


if __name__ == "__main__":
    main()
