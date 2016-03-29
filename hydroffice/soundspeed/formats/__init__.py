from __future__ import absolute_import, division, print_function, unicode_literals

import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


# readers
from .readers.castaway import Castaway
from .readers.digibarpro import DigibarPro
from .readers.digibars import DigibarS
from .readers.idronaut import Idronaut
from .readers.kongsberg import Kongsberg
from .readers.mvp import Mvp
from .readers.saiv import Saiv
from .readers.seabird import Seabird
from .readers.sippican import Sippican
from .readers.turo import Turo
from .readers.unb import Unb
from .readers.valeport import Valeport

readers = list()
readers.append(Castaway())
readers.append(DigibarPro())
readers.append(DigibarS())
readers.append(Idronaut())
readers.append(Kongsberg())
readers.append(Mvp())
readers.append(Saiv())
readers.append(Seabird())
readers.append(Sippican())
readers.append(Turo())
readers.append(Unb())
readers.append(Valeport())


# writers
from .writers.elac import Elac
from .writers.kongsberg import Kongsberg

writers = list()
writers.append(Elac())
writers.append(Kongsberg())
