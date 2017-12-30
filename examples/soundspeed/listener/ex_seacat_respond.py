from hyo.soundspeed.logging import test_logging

from os import path
import logging

from hyo.soundspeed.listener.seacat.seacat_emulator import raw_capture

logger = logging.getLogger()


def main():

    p = path.join(path.split(path.abspath(__file__))[0], "seacat_capture.txt")
    raw_capture(p)


if __name__ == "__main__":
    main()
