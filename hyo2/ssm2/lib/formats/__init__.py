import logging

# noinspection PyUnresolvedReferences
from hyo2.ssm2.lib.formats.readers.abstract import AbstractReader
# READERS
# noinspection PyUnresolvedReferences
from hyo2.ssm2.lib.formats.readers.aml import Aml as AmlReader
# noinspection PyUnresolvedReferences
from hyo2.ssm2.lib.formats.readers.aoml import Aoml as AomlReader
# noinspection PyUnresolvedReferences
from hyo2.ssm2.lib.formats.readers.asvp import Asvp as AsvpReader
# noinspection PyUnresolvedReferences
from hyo2.ssm2.lib.formats.readers.caris import Caris as CarisReader
# noinspection PyUnresolvedReferences
from hyo2.ssm2.lib.formats.readers.castaway import Castaway as CastawayReader
# noinspection PyUnresolvedReferences
from hyo2.ssm2.lib.formats.readers.csiro_dtc import CSIRO_DTC as CSIRO_DTCReader
# noinspection PyUnresolvedReferences
from hyo2.ssm2.lib.formats.readers.digibarpro import DigibarPro as DigibarProReader
# noinspection PyUnresolvedReferences
from hyo2.ssm2.lib.formats.readers.digibars import DigibarS as DigibarSReader
# noinspection PyUnresolvedReferences
from hyo2.ssm2.lib.formats.readers.elac import Elac as ElacReader
# noinspection PyUnresolvedReferences
from hyo2.ssm2.lib.formats.readers.hypack import Hypack as HypackReader
# noinspection PyUnresolvedReferences
from hyo2.ssm2.lib.formats.readers.idronaut import Idronaut as IdronautReader
# noinspection PyUnresolvedReferences
from hyo2.ssm2.lib.formats.readers.iss import Iss as IssReader
# noinspection PyUnresolvedReferences
from hyo2.ssm2.lib.formats.readers.mvp import Mvp as MvpReader
# noinspection PyUnresolvedReferences
from hyo2.ssm2.lib.formats.readers.oceanscience import OceanScience as OceanScienceReader
# noinspection PyUnresolvedReferences
from hyo2.ssm2.lib.formats.readers.rbr import RBR as RBRReader
# noinspection PyUnresolvedReferences
from hyo2.ssm2.lib.formats.readers.saiv import Saiv as SaivReader
# noinspection PyUnresolvedReferences
from hyo2.ssm2.lib.formats.readers.sea_and_sun import SeaAndSun as SeaAndSunReader
# noinspection PyUnresolvedReferences
from hyo2.ssm2.lib.formats.readers.seabird import Seabird as SeabirdReader
# noinspection PyUnresolvedReferences
from hyo2.ssm2.lib.formats.readers.sippican import Sippican as SippicanReader
# noinspection PyUnresolvedReferences
from hyo2.ssm2.lib.formats.readers.sonardyne import Sonardyne as SonardyneReader
# noinspection PyUnresolvedReferences
from hyo2.ssm2.lib.formats.readers.tsk import TSK as TSKReader
# noinspection PyUnresolvedReferences
from hyo2.ssm2.lib.formats.readers.turo import Turo as TuroReader
# noinspection PyUnresolvedReferences
from hyo2.ssm2.lib.formats.readers.unb import Unb as UnbReader
# noinspection PyUnresolvedReferences
from hyo2.ssm2.lib.formats.readers.valeport import Valeport as ValeportReader
# WRITERS
# noinspection PyUnresolvedReferences
from hyo2.ssm2.lib.formats.writers.abstract import AbstractWriter
# noinspection PyUnresolvedReferences
from hyo2.ssm2.lib.formats.writers.asvp import Asvp as AsvpWriter
# noinspection PyUnresolvedReferences
from hyo2.ssm2.lib.formats.writers.calc import Calc as CalcWriter
# noinspection PyUnresolvedReferences
from hyo2.ssm2.lib.formats.writers.caris import Caris as CarisWriter
# noinspection PyUnresolvedReferences
from hyo2.ssm2.lib.formats.writers.csv import Csv as CsvWriter
# noinspection PyUnresolvedReferences
from hyo2.ssm2.lib.formats.writers.elac import Elac as ElacWriter
# noinspection PyUnresolvedReferences
from hyo2.ssm2.lib.formats.writers.hipap import Hipap as HipapWriter
# noinspection PyUnresolvedReferences
from hyo2.ssm2.lib.formats.writers.hypack import Hypack as HypackWriter
# noinspection PyUnresolvedReferences
from hyo2.ssm2.lib.formats.writers.ixblue import Ixblue as IxblueWriter
# noinspection PyUnresolvedReferences
from hyo2.ssm2.lib.formats.writers.ncei import Ncei as NceiWriter
# noinspection PyUnresolvedReferences
from hyo2.ssm2.lib.formats.writers.qps import Qps as QpsWriter
# noinspection PyUnresolvedReferences
from hyo2.ssm2.lib.formats.writers.sonardyne import Sonardyne as SonardyneWriter
# noinspection PyUnresolvedReferences
from hyo2.ssm2.lib.formats.writers.unb import Unb as UnbWriter

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

readers: list[AbstractReader] = list()
readers.append(AmlReader())
readers.append(AomlReader())
readers.append(CarisReader())
readers.append(CastawayReader())
readers.append(CSIRO_DTCReader())
readers.append(DigibarProReader())
readers.append(DigibarSReader())
readers.append(ElacReader())
readers.append(HypackReader())
readers.append(IdronautReader())
readers.append(IssReader())
readers.append(AsvpReader())
readers.append(MvpReader())
readers.append(OceanScienceReader())
readers.append(RBRReader())
readers.append(SaivReader())
readers.append(SeaAndSunReader())
readers.append(SeabirdReader())
readers.append(SippicanReader())
readers.append(SonardyneReader())
readers.append(TSKReader())
readers.append(TuroReader())
readers.append(UnbReader())
readers.append(ValeportReader())

name_readers: list[str] = list()
ext_readers: list[set[str]] = list()
desc_readers: list[str] = list()
for reader in readers:
    name_readers.append(reader.name)
    ext_readers.append(reader.ext)
    desc_readers.append(reader.desc)

writers: list[AbstractWriter] = list()
writers.append(CalcWriter())
writers.append(CarisWriter())
writers.append(CsvWriter())
writers.append(ElacWriter())
writers.append(HipapWriter())
writers.append(HypackWriter())
writers.append(IxblueWriter())
writers.append(AsvpWriter())
writers.append(NceiWriter())
writers.append(QpsWriter())
writers.append(SonardyneWriter())
writers.append(UnbWriter())

name_writers: list[str] = list()
ext_writers: list[set[str]] = list()
desc_writers: list[str] = list()
for writer in writers:
    if len(writer.ext):
        name_writers.append(writer.name)
        ext_writers.append(writer.ext)
        desc_writers.append(writer.desc)
