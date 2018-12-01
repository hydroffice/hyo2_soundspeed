# TODO: Velocipy legacy: to be cleaned, then moved under hyo2.soundspeed.base
"""
coordinates.py
James Hiebert <james.hiebert@noaa.gov>
April 14, 2008
"""

from re import search, match
from osgeo.ogr import Geometry, wkbPoint


class FormattingException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


'''
c=coordinates.Coordinate('32/42/15n',  '079/50/00w')
c.DMS()
'32 42 15.0000N, 079 50 00.0000W'
c.DM()
'32 42.250000N, 079 50.000000W'
coordinates.Coordinate('47 41 18 N',  '47 41 18 W').DMS()
'47 41 18.0000N, 047 41 18.0000W'
coordinates.Coordinate('47/41/18 N',  '47/41/18W').DMS()
'47 41 18.0000N, 047 41 18.0000W'
coordinates.Coordinate('47/41N',  '47/41 W').DMS()
'47 41 00.0000N, 047 41 00.0000W'
coordinates.Coordinate('47 41N',  '47 41 W').DMS()
'47 41 00.0000N, 047 41 00.0000W'
coordinates.Coordinate('47.41N',  '47.41 W').DMS()
'47 24 36.0000N, 047 24 36.0000W'

'''


def LatStrToDec(latstr, assume_S=False):
    lonstr = latstr.lower().replace('n', 'e').replace('s', 'e')  # lon is fake at this point
    if assume_S:  # add a negative sign making coordinate West Longitude if preference is set that way and no leading negative sign, E or W is in the string
        if not search("(^\s*-)|([ns])", lonstr.lower()):
            latstr = '-' + latstr
    lat = Coordinate(latstr, lonstr)
    if lat:
        return lat.lat
    else:
        return None


def LonStrToDec(lonstr, assume_W=False):
    latstr = lonstr.lower().replace('e', 'n').replace('w', 'n')  # lat is fake at this point
    if assume_W:  # add a negative sign making coordinate West Longitude if preference is set that way and no leading negative sign, E or W is in the string
        if not search("(^\s*-)|([ew])", lonstr.lower()):
            lonstr = '-' + lonstr
    lon = Coordinate(latstr, lonstr)
    if lon:
        return lon.lon
    else:
        return None


def GetCoordFromUser(text_lat="Enter Latitude", text_lon="Enter Longitude", title_lat="Latitude", title_lon="Longitude",
                     def_lat='', def_lon='', parent=None, assume_W=False, assume_S=False):
    import wx
    latstr = "fail"
    lat = None
    formats = "\n".join(
        [constructor.supported_formats for constructor in (DecDegreesCoordinate, DMCoordinate, DMSCoordinate)])
    text_lat = text_lat + '\n\n' + formats
    while latstr and lat == None:  # bail out when we get a legit lat value or user cancels (returns "" for latstr)
        latstr = wx.GetTextFromUser(("" if latstr == "fail" else "Retry -- use formats below\n\n") + text_lat,
                                    title_lat, (def_lat if latstr == "fail" else latstr), parent=None)
        lat = LatStrToDec(latstr, assume_S)
    if latstr:  # user didn't cancel
        text_lon = text_lon + '\n\n' + formats
        lonstr = "fail"
        lon = None
        while lonstr and lon == None:  # bail out when we get a legit lat value or user cancels (returns "" for latstr)
            lonstr = wx.GetTextFromUser(("" if lonstr == "fail" else "Retry -- use formats below\n\n") + text_lon,
                                        title_lon, (def_lon if lonstr == "fail" else lonstr), parent=None)
            lon = LonStrToDec(lonstr, assume_W)
        if lonstr:  # user didn't cancel
            coord = BaseCoordinate(lat, lon)  # get a coordinate instance and set the lat and lon
            return coord, latstr, lonstr
    return None, None, None


def Coordinate(lat, lon, hardfail=False):
    '''Constructor of running through the supported formats and returning a BaseCoordinate derived instance if possible
    '''
    if isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
        return BaseCoordinate(lat, lon)
    # look for string coordinate formats
    for constructor in (DecDegreesCoordinate, DMCoordinate, DMSCoordinate):
        try:
            return constructor(lat, lon)
        except FormattingException:
            pass  # try next formats
    if hardfail:
        raise SyntaxError("lat and lon did not match any available formats (%s %s)" % (lat, lon))
    else:
        return None


class BaseCoordinate:
    supported_formats = "[-]D.ddd[NSEW]"
    lat = 0.0
    lon = 0.0

    def __init__(self, lat, lon):
        if isinstance(lat, (int, float)) and isinstance(lon, (int,
                                                              float)):  # pass non-string value straight through; also, avoid replacing 'e' in case of (lon) scientific notation formatting
            self.lat, self.lon = lat, lon
        else:
            self.lat, self.lon = map(float, (
            str(lat).lower().replace('n', '').replace('s', '').replace('w', '').replace('e', ''),
            str(lon).lower().replace('n', '').replace('s', '').replace('w', '').replace('e', '')))
            if 's' in str(lat).lower(): self.lat *= -1.0
            if 'w' in str(lon).lower(): self.lon *= -1.0
        self.sep = ' '  # space separation by default when printing DMS, DM formats

    def __str__(self):
        return "(%.06f, %.06f)" % (self.lat, self.lon)

    def SetSep(self, s):
        self.sep = s

    def copy(self):
        c = BaseCoordinate(self.lat, self.lon)
        c.sep = self.sep
        return c

    def DMS_Caris(self):
        latdms = list(BaseCoordinate._dms(self.lat))
        if self.lat < 0: latdms[0] *= -1
        londms = list(BaseCoordinate._dms(self.lon))
        if self.lon < 0: londms[0] *= -1
        LatStr = ('% 03d:%02d:%02d' % tuple(latdms)).strip()  # remove leading space from positive values
        LonStr = ('% 04d:%02d:%02d' % tuple(londms)).strip()  # remove leading space from positive values
        return LatStr, LonStr

    def ogrPoint(self):
        '''returns the current point as an ogr.Geometry wkbPoint
        '''
        p1 = Geometry(wkbPoint)
        p1.AddPoint_2D(self.lat, self.lon)
        return p1

    def Hemi(self):
        return ('S', 'N')[self.lat > 0], ('W', 'E')[self.lon > 0]

    @staticmethod
    def _dms(dec_deg):
        lat = abs(dec_deg)
        d = int(lat)
        m = int((lat - d) * 60)
        s = (((lat - d) * 60) - m) * 60
        if s > 59.999999:
            s = 0.0
            m += 1.0
        if m > 59.999999:
            m = 0.0
            d += 1.0
        return d, m, s

    def DMSSymb(self):
        latdir, londir = self.Hemi()
        d, m, s = BaseCoordinate._dms(self.lat)
        lat = "%02d\xba%02d'%07.4f\"" % (d, m, s)

        d, m, s = BaseCoordinate._dms(self.lon)
        lon = "%03d\xba%02d'%07.4f\"" % (d, m, s)
        return "%s%s, %s%s" % (lat, latdir, lon, londir)

    def DMS(self):
        latdir, londir = self.Hemi()
        d, m, s = BaseCoordinate._dms(self.lat)
        lat = "%02d%s%02d%s%07.4f" % (d, self.sep, m, self.sep, s)

        d, m, s = BaseCoordinate._dms(self.lon)
        lon = "%03d%s%02d%s%07.4f" % (d, self.sep, m, self.sep, s)
        return "%s%s, %s%s" % (lat, latdir, lon, londir)

    def DM(self):
        latdir, londir = self.Hemi()

        d, m, s = BaseCoordinate._dms(self.lat)
        m += s / 60.0
        lat = "%02d%s%09.6f" % (d, self.sep, m)

        d, m, s = BaseCoordinate._dms(self.lon)
        m += s / 60.0
        lon = "%03d%s%09.6f" % (d, self.sep, m)
        return "%s%s, %s%s" % (lat, latdir, lon, londir)

    def D(self):
        lat, lon = map(abs, [self.lat, self.lon])
        latdir, londir = self.Hemi()
        return "%011.8f%s, %011.8f%s" % (lat, latdir, lon, londir)

    def SignedDec(self):
        lat, lon = self.lat, self.lon
        return "%f, %f" % (lat, lon)


class DMSCoordinate(BaseCoordinate):
    supported_formats = "[-]DDD MM SS.sss[NSEW]\n[-]DDD:MM:SS.sss[NSEW]\n[-]DDD/MM/SS.sss[NSEW]"

    def __init__(self, lat, lon):
        p = r"^(\d+)[\s/:]+(\d+)[\s\'/:]+(\d+(\.\d+)?)\"?\s*([NSEWnsew])\s*$"
        ma1 = match(p, lat)
        ma2 = match(p, lon)
        if ma1 and ma2:
            d, m, s = map(float, ma1.group(1, 2, 3))
            ns = ma1.group(5)
            lat = d + m / 60.0 + s / 3600.0
            if ns.lower() == 's': lat *= -1

            d, m, s = map(float, ma2.group(1, 2, 3))
            ew = ma2.group(5)
            lon = d + m / 60.0 + s / 3600.0
            if ew.lower() == 'w': lon *= -1
        else:
            p = r"^(-?)(\d+)[\s/:]+(\d+)[\s\'/:]+(\d+(\.\d+)?)[\"]?\s*$"
            ma1 = match(p, lat)
            ma2 = match(p, lon)
            if ma1 and ma2:
                d, m, s = map(float, ma1.group(2, 3, 4))
                lat = d + m / 60.0 + s / 3600.0
                if ma1.group(1) == '-': lat *= -1

                d, m, s = map(float, ma2.group(2, 3, 4))
                lon = d + m / 60.0 + s / 3600.0
                if ma2.group(1) == '-': lon *= -1
            else:
                raise FormattingException('Not DMS')

        BaseCoordinate.__init__(self, lat, lon)

    def __str__(self):
        return self.DMS()


class DMCoordinate(BaseCoordinate):
    supported_formats = "[-]DDD MM.mmm[NSEW]\n[-]DDD:MM.mmm[NSEW]\n[-]DDD/MM.mmm[NSEW]"

    def __init__(self, lat, lon):
        for p in (
        r"^(\d{2,3})(\d{2}(\.\d+)?)\s*\'?,?\s*([NSEWnsew])\s*$",  # check for 6032.0620000,N and 14656.8280000,W
        r"^(\d{1,3})[\s/]+(\d{1,2}(\.\d+)?)\s*\'?,?\s*([NSEWnsew])\s*$"):  # check for other DD DD.ddd variants
            if match(p, lat): break
        ma = match(p, lat)
        if ma:
            d, m = map(float, ma.group(1, 2))
            lat = d + m / 60.
            if ma.group(4).lower() == 's': lat *= -1

            ma = match(p, lon)
            d, m = map(float, ma.group(1, 2))
            lon = d + m / 60.0
            if ma.group(4).lower() == 'w': lon *= -1
        else:
            p = "^(-?)(\d+)[\':]?[\s/]*(\d+(\.\d+)?)\'?\s*$"
            ma = match(p, lat)
            if ma:
                d, m = map(float, ma.group(2, 3))
                lat = d + m / 60.0
                if ma.group(1) == '-': lat *= -1

                ma = match(p, lon)
                d, m = map(float, ma.group(2, 3))
                lon = d + m / 60.0
                if ma.group(1) == '-': lon *= -1
            else:
                raise FormattingException('Not DM')
        BaseCoordinate.__init__(self, lat, lon)

    def __str__(self):
        return self.DM()


class DecDegreesCoordinate(BaseCoordinate):
    supported_formats = "[-]DD.ddd\nDD.ddd[NSEW]"

    def __init__(self, lat, lon):
        p = r"^\s*-?\d+\.?\d*\s*$"
        ma = match(p, lat)
        if ma:
            BaseCoordinate.__init__(self, lat, lon)
        else:
            p = r"^\s*\d+\.?\d*\s*([NSEWnsew])\s*$"
            ma = match(p, lat)
            if ma:
                BaseCoordinate.__init__(self, lat, lon)
            else:
                raise FormattingException('Not DDeg')

    def __str__(self):
        return "%f, %f" % (self.lat, self.lon)


class LatLonCoordinate(BaseCoordinate):
    def __str__(self):
        pass
