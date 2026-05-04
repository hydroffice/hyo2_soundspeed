import logging
from enum import StrEnum

logger = logging.getLogger(__name__)


class RegOfsThreddsService(StrEnum):
    FILE_SERVER = "fileServer"
    DODS_C = "dodsC"
