import logging
import os

from PySide6 import QtWidgets

from hyo2.abc2.app.qt_progress import QtProgress
from hyo2.abc2.lib.logging import set_logging
from hyo2.abc2.lib.testing import Testing
from hyo2.ssm2.app.gui.soundspeedmanager.qt_callbacks import QtCallbacks
from hyo2.ssm2.lib.soundspeed import SoundSpeedLibrary

set_logging(ns_list=["hyo2.abc2", "hyo2.ssm2"])

logger = logging.getLogger(__name__)

testing = Testing(root_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir)))

nc_path = testing.download_test_files(ext=".nc", subfolder="sfbofs")[0]

app = QtWidgets.QApplication([])  # PySide stuff (start)
mw = QtWidgets.QMainWindow()
mw.show()

lib = SoundSpeedLibrary(progress=QtProgress(parent=mw), callbacks=QtCallbacks(parent=mw))

# Choose test location
tests = [

    # (-19.1, 74.16),              # Indian Ocean
    # (72.852028, -67.315431)      # Baffin Bay
    # (18.2648113, 16.1761115),    # in land -> middle of Africa
    # (39.725989, -104.967745)     # in land -> Denver, CO
    # (37.985427, -76.311156),     # Chesapeake Bay
    # (39.162802, -75.278057),     # Deleware Bay
    # (43.026480, -70.318824),     # offshore Portsmouth
    # (40.662218, -74.049306),     # New York Harbor
    # (30.382518, -81.573615),     # Mill Cove, St. Johns River
    # (28.976225, -92.078882),     # Offshore Louisiana
    # (27.762904, -82.557280),     # Tampa Bay
    # (41.806023, -82.393283),     # Lake Erie
    # (44.564914, -82.845794),     # Lake Huron
    # (43.138573, -86.832183),     # Lake Michigan
    # (43.753190, -76.826818),     # Lake Ontario
    # (47.457546, -89.347715),     # Lake Superior
    # (46.161403, -124.107396),    # Offshore of Colombia River
    (37.689510, -122.298514)  # San Francisco Bay
]

test = tests[0]

logger.info("Offline OFS profiles:\n%s"
            % lib.atlases.offofs.query(lat=test[0], lon=test[1], nc_path=nc_path))
