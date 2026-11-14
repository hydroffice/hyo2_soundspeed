import logging
import sys

from hyo2.ssm2.app.gui.soundspeedmanager.main import main

logger = logging.getLogger(__name__)

logger.debug("initial argv: %s" % sys.argv)
sys.argv.append("--help")
logger.debug("passed argv: %s" % sys.argv)

main()
