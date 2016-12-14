import re


robust_re_number = r'[\-+]?(\d+(\.\d*)?|\.\d+)([Ee][+\-]?\d+)?'
named_re_number = r'(?P<%s>' + robust_re_number + ')'

# Note that Hex header is copied into the CNV header verbatim so these can be used in either.
SEACAT_SBE19_HEX_YEAR = r'SEACAT\sPROFILER.*?(?P<day>\d+)/(?P<month>\d+)/(?P<year>\d+)'
SEACAT_SBE19_STATUS_DATETIME = r'SEACAT\sPROFILER.*?(?P<month>\d+)/(?P<day>\d+)/(?P<year>\d+)\s*(?P<hour>\d+)[\s:]*(?P<minute>\d+)[\s:]*(?P<second>\d*)'
SEACAT_SBE19_HEX_MONTHDAY = r'cast.*?(?P<month>\d+)/(?P<day>\d+)'
SEACAT_SBE19_HEX_TIME = r'cast.*?(?P<hour>\d+):(?P<minute>\d+):(?P<second>\d+)'
SEACAT_SBE19_HEX_YEARRE = re.compile(SEACAT_SBE19_HEX_YEAR)
SEACAT_SBE19_HEX_MONTHDAYRE = re.compile(SEACAT_SBE19_HEX_MONTHDAY)
SEACAT_SBE19_HEX_TIMERE = re.compile(SEACAT_SBE19_HEX_TIME)

SEACAT_SBE19PLUS_STATUS_DATETIME = r'SeacatPlus\sV.*?(?P<full>(?P<day>\d+)\s+(?P<month>\w{3})\s+(?P<year>\d{4})\s*(?P<hour>\d+)[\s:]*(?P<minute>\d+)[\s:]*(?P<second>\d*))'
SEACAT_SBE19PLUSV2_STATUS_DATETIME = r'SBE\s19plus\sV.*?(?P<full>(?P<day>\d+)\s+(?P<month>\w{3})\s+(?P<year>\d{4})\s*(?P<hour>\d+)[\s:]*(?P<minute>\d+)[\s:]*(?P<second>\d*))'
SEACAT_CNV_START_TIME = r'start_time\s*=\s*(?P<full>(?P<month>\w{3})\s+(?P<day>\d+)\s+(?P<year>\d{4})\s*(?P<hour>\d+)[\s:]*(?P<minute>\d+)[\s:]*(?P<second>\d*))'
SEACAT_CNV_START_TIMERE = re.compile(SEACAT_CNV_START_TIME)
SEACAT_SBE19PLUS_HEX_DATE_TXT = r'cast.*?(?P<full>(?P<day>\d+)\s+(?P<month>\w{3})\s+(?P<year>\d{4}))'
SEACAT_SBE19PLUS_HEX_DATE_TXT_FORMAT = "%d %b %Y"
# >>> time.strptime("30 nov 00", SEACAT_SBE19PLUS_HEX_DATE_TXT_FORMAT)
# (2000, 11, 30, 0, 0, 0, 3, 335, -1)
SEACAT_SBE19PLUS_HEX_DATE_TXTRE = re.compile(SEACAT_SBE19PLUS_HEX_DATE_TXT)

SEACAT_SBE19PLUS_HEX_DATE_MDY = r'cast.*?(?P<full>(?P<month>\d{2})\s+(?P<day>\d{2})\s+(?P<year>\d{4}))'
SEACAT_SBE19PLUS_HEX_DATE_MDY_FORMAT = "%m %d %Y"
SEACAT_SBE19PLUS_HEX_DATE_MDYRE = re.compile(SEACAT_SBE19PLUS_HEX_DATE_MDY)
# both use same time format
SEACAT_SBE19PLUS_HEX_TIME = SEACAT_SBE19_HEX_TIME
SEACAT_SBE19PLUS_HEX_TIMERE = re.compile(SEACAT_SBE19PLUS_HEX_TIME)

# * System UpLoad Time = Sep 08 2008 14:18:19
SEACAT_SBE911_HEX_DATETIME = r'System\s*UpLoad\s*Time\s*=\s*(?P<full>(?P<mon>\w*)\s*(?P<day>\d+)\s*(?P<yr>\d+)\s*(?P<hour>\d+)[\s:]*(?P<minute>\d+)[\s:]*(?P<second>\d*))'
SEACAT_SBE911_HEX_DATETIMERE = re.compile(SEACAT_SBE911_HEX_DATETIME)
SEACAT_HEX_LAT = r'Latitude\s*[:=]\s*(?P<lat>.*)'
SEACAT_HEX_LON = r'Longitude\s*[:=]\s*(?P<lon>.*)'
SEACAT_HEX_LATRE = re.compile(SEACAT_HEX_LAT)
SEACAT_HEX_LONRE = re.compile(SEACAT_HEX_LON)


SeacatHex_SBE19_NCASTS = r'(\s+ncasts[\s=]+)(?P<NumCasts>\d+)'
SeacatHex_SBE19_NCASTSRE = re.compile(SeacatHex_SBE19_NCASTS, re.IGNORECASE)
SeacatHex_SBE19PLUS_NCASTS = r'''samples  #start of line has samples
                                 .*?         #everything on the same line up to the casts =
                                 casts[\s=]+ #"casts = " including whitespace
                                 (?P<NumCasts>\d+) #the number of casts
                              '''
SeacatHex_SBE19PLUS_NCASTSRE = re.compile(SeacatHex_SBE19PLUS_NCASTS, re.VERBOSE | re.IGNORECASE)

SeacatHex_SBE19PLUS_TYPE = r'SBE\s*19\s*PLUS'  # picks up SBE19Plus and V2
SeacatHex_SBE19_TYPE = r'SBE\s*19'
SeacatHex_SBE911_TYPE = r'SBE\s*9\s*'
SeacatHex_SBE49_TYPE = r'SBE\s*49\s*'

SeacatHex_SBE19PLUS_TYPERE = re.compile(SeacatHex_SBE19PLUS_TYPE, re.IGNORECASE)
SeacatHex_SBE19_TYPERE = re.compile(SeacatHex_SBE19_TYPE, re.IGNORECASE)
SeacatHex_SBE911_TYPERE = re.compile(SeacatHex_SBE911_TYPE, re.IGNORECASE)
SeacatHex_SBE49_TYPERE = re.compile(SeacatHex_SBE49_TYPE, re.IGNORECASE)
SeacatHex_SN = r'Temperature\s*SN\s*=\s*(?P<SN>\d+)'
SeacatHex_SNRE = re.compile(SeacatHex_SN, re.IGNORECASE)

SeacatCNV_NVALUES = r'nvalues\s*=\s*(?P<nvalues>\d*)'
SeacatCNV_NVALUESRE = re.compile(SeacatCNV_NVALUES, re.IGNORECASE)
SeacatCNV_SPAN_N = r'span\s*%d\s*=\s*(?P<min>%s)\s*,\s*(?P<max>%s)'
SeacatCNV_SPAN_list, SeacatCNV_SPAN_listRE = [], []
for n in range(7):
    SeacatCNV_SPAN_list.append(SeacatCNV_SPAN_N % (n, robust_re_number, robust_re_number))
    SeacatCNV_SPAN_listRE.append(re.compile(SeacatCNV_SPAN_list[n], re.IGNORECASE))
SeacatCNV_INTERVAL = r'interval\s=\s(?P<units>\w*):\s*(?P<interval>[\d.]*)'
SeacatCNV_INTERVALRE = re.compile(SeacatCNV_INTERVAL, re.IGNORECASE)
# SeacatCNV_DATA =r'\s+(?P<pressure>[e\+\-\d.]+)\s+(?P<conductivity>[e\+\-\d.]+)\s+(?P<temperature>[e\+\-\d.]+)\s+(?P<salinity>[e\+\-\d.]+)\s+(?P<density>[e\+\-\d.]+)\s+(?P<velocity>[e\+\-\d.]+)\s+(?P<voltage>[e\+\-\d.]+)'
# SeacatCNV_DATA_types = [('P', scipy.float32), ('C', scipy.float32), ('T', scipy.float32), ('S', scipy.float32), ('D', scipy.float32), ('SV', scipy.float32), ('V', scipy.float32)]
# scipy.fromregex(fname, SeacatCNV_DATA+r'\s*\n',  SeacatCNV_DATA_types)


def DEG2RAD():
    return 0.017453292519943295  # = pi/180.0


def RAD2DEG():
    return 57.295779513082323    # = 180.0/pi


def METERS2FEET():
    return 3.280839895013123     # = 1.0/0.3048


def METERS2FATH():
    return 0.5468066491688538    # = (1.0/0.3048)/6.0


def FEET2METERS():
    return 0.3048


def FATH2METERS():               # = 1.0/METERS2FATH()
    return 1.8288

unit_conversions = {'meters': {'meters': 1.0, 'fathoms': METERS2FATH(), 'feet': METERS2FEET()},
                    'feet': {'meters': FEET2METERS(), 'fathoms': 1. / 6., 'feet': 1.0},
                    'fathoms': {'meters': FATH2METERS(), 'fathoms': 1.0, 'feet': 6.0}
                    }
