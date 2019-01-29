# TODO: Velocipy legacy: to be cleaned, then moved under hyo2.soundspeed.base

# builtins
import datetime
import re
from copy import deepcopy, copy
from warnings import warn

import hyo2.soundspeed.profile
# 3rd party libs
import numpy
from hyo2.soundspeed.profile import dicts
# our custom package
from hyo2.soundspeed.temp import coordinates

'''
This module is using a lot of Regular Expressions and numpy.fromregex to read file formats.
numpy.fromregex does not allow a nice usage of sub groups (it would want to build a data column for each group.
The fromregex also does a findall() that will search across newlines if not careful.
When it reads data that it can't convert it raises
TypeError: expected a readable buffer object
So, this typically would happen on corrupt data which we could just alert the user about, but
XBTs have a lot of corrupt lines and we want to handle this for the user.

example:
181.0,5.96,1474.41*
181.6,5.96,1474.194.8,5.82,1474.04*
when parsed with
r'\s*([\d.]+)[,\s]+([\d.]+)[,\s]+([\d.]+)[*\s]*\n'
Give three groups for the second line, note the double decimal point in the first group.
"1474.194.8","5.82","1474.04"
We'd prefer to skip this line as bad, but we can't use the start of line caret "^" in the fromregex.
Solution is to either loop the file and pass in line by line and do a match or
  use a lookbehind assertion to make sure we're at the beginning of the line
Also for a robust parse of numeric values we can use:
 (\d*|\d+\.\d* | \.\d+) #grabs integer, or a single decimal point with/without lead/trail numbers BUT requires a trail or lead so just "." doesn't work
 Something like:
 ((\d*|\d+\.\d* | \.\d+)([Ee][+\-]?\d+))? #would be nice to capture exponent and make sure it's well formed but numpy.fromregex will turn this into three data fields
 So we go with the line by line parse or use:
 (\d*[e+\-\d]*|\d+\.\d*[e+\-\d] | \.\d+[e+\-\d]) to pick up exponents, which will allow 12ee+-4e  (garbage)
So to be most stringent in the parsing of data we have to loop the lines of the file manually.



        NOTE: from World Ocean Atlas 2005 about XBT, XSV depth rate errors
        The correction for XBT T4, T6, and T7 drop-rate error (Hanawa et al., 1994) is:
        zc = 1.0417z0 - 75.906x(1-(102.063 x 10-4z0)^0.5)
        in which z0 is the originally calculated depth.
        In addition to XBT depth corrections, Johnson (1995) has shown the necessity of depth correction
        for Sippican XCTDs, while Mizuno and Watanabe (1998) give depth corrections for TSK XCTDs.
        Both corrections follow the same procedure as for XBTs.
'''

robust_re_number = r'[\-+]?(\d+(\.\d*)?|\.\d+)([Ee][+\-]?\d+)?'
named_re_number = r'(?P<%s>' + robust_re_number + ')'


def parseNumbers(txt_lines, dtype, sep, pre='', post='', ftype=''):
    '''builds a regular expression based on dtype.names and the (regex ok) separator supplied
    dtype is a numpy.dtype object describing the fieldnames and data types
    sep is the separator for the values being parsed -- ex: "(,|\s+)" for one comma or 1+ whitespaces, notice the group ( ) so the or pipe "|" doesn't affect the entire expression
    pre and post are any extra validation on either side of the values being parsed.  ex: pre="^", post = "$" would specify begin and end of line respectively.
    pre and post could also be lookahead/behind assertions for example pre="(?<=DATA:)"  post="(?=*[\d\w]{2})", pre would require "DATA:" right before the values being parsed post would want a * with two digits (perhaps a checksum)
    The assertions would be more useful if we didn't splitlines() in the next function...
    '''
    if isinstance(dtype, (list, tuple)):
        try:
            dtype = numpy.dtype(dtype)
        except TypeError:
            dtype = numpy.dtype([(str(n), t) for n, t in dtype])  # numpy in 2.7 doesn't like unicode names
    rstr = sep.join([named_re_number % n for n in dtype.names])
    expr = re.compile(pre + rstr + post)
    return parse_data(txt_lines, dtype, expr, ftype)


def parse_data(txt_lines, dtype, expr, ftype=''):
    '''Parse a file and return a numpy rec.array -- allows use of subgroups unlike the numpy.fromregex
    This allows better enforcement of numeric formatting.
    Pass in filename to read, numpy.dtype object with the names/types for the record array and a compiled regular expression
    '''
    if isinstance(dtype, (list, tuple)):
        dtype = numpy.dtype(dtype)
    data = []
    for l in txt_lines:
        m = expr.search(l)
        if m:
            data.append(tuple([m.group(n) for n in dtype.names]))  # numpy handles any string to int/float for us
    first_line = txt_lines[0].split(',')
    if ftype == 'SSP' and first_line[0] == '$' and len(first_line) > 7 + len(data[0]):  # insert the first line of SSP
        data.insert(0, tuple(first_line[-1 - len(data[0]): -1]))
    return numpy.array(data, dtype=dtype)


def getMetaFromTimeRE(m):
    '''Pass in a re.match object that has groups named yr, mon, day, hour, minute and this convienence function
    will create a metadata dictionary with the Year, Day, Time formated appropriately.
    You can then use metadata.update( Profile.getMetaFromTimeRE(m))
    to augment your existing meta or use the returned dict to start a new metadata dictionary.
    '''
    meta = {}
    meta['Year'] = m.group('yr')
    if int(meta['Year']) < 80:
        meta['Year'] = '20' + meta['Year']  # 2000 - 2079
    elif int(meta['Year']) < 100:
        meta['Year'] = '19' + meta['Year']  # 1980 - 1999
    try:
        mon, day, yr = int(m.group('mon')), int(m.group('day')), int(m.group('yr'))
        meta['Day'] = '%03d' % datetime.datetime(yr, mon, day).timetuple().tm_yday
    except:
        meta['Day'] = m.group('doy')
    meta['Time'] = m.group('hour') + ':' + m.group('minute')
    meta['timestamp'] = datetime.datetime.strptime("%s %s %s" % (meta['Year'], meta['Day'], meta['Time']),
                                                   "%Y %j %H:%M")
    return meta


def parseMetaFromDatetime(dt):
    meta = {}
    meta['Time'] = dt.strftime("%H:%M")
    meta['Year'] = dt.strftime("%Y")
    meta['Day'] = dt.strftime("%j")
    meta['timestamp'] = dt
    return meta


def getMetaFromCoord(coord):  # pass a coordinates.Coordinate and make the metadata
    meta = {}
    location = coord.copy()
    location.__class__ = coordinates.DMSCoordinate
    location.SetSep('/')
    meta['Latitude'] = str(location).split(', ')[0]
    meta['Longitude'] = str(location).split(', ')[1]
    meta['location'] = location
    return meta


# '''
# Addressing Array Columns by Name
# There are two very closely related ways to access array columns by name: recarrays and structured arrays.
# Structured arrays are just ndarrays with a complicated data type:
#         In [1]: from numpy import *
#
#         In [2]: ones(3, dtype=dtype([('foo', int), ('bar', float)]))
#         Out[2]:
#         array([(1, 1.0), (1, 1.0), (1, 1.0)],
#                     dtype=[('foo', '<i4'), ('bar', '<f8')])
#
#         In [3]: r = _
#
#         In [4]: r['foo']
#         Out[4]: array([1, 1, 1])
#
# recarray is a subclass of ndarray that just adds attribute access to structured arrays:
#         In [10]: r2 = r.view(recarray)
#
#         In [11]: r2
#         Out[11]:
#         recarray([(1, 1.0), (1, 1.0), (1, 1.0)],
#                     dtype=[('foo', '<i4'), ('bar', '<f8')])
#
#         In [12]: r2.foo
#         Out[12]: array([1, 1, 1])
#
# One downside of recarrays is that the attribute access feature slows down all field accesses,
# even the r['foo'] form, because it sticks a bunch of pure Python code in the middle.
#
# Much code won't notice this, but if you end up having to iterate over an array of records,
# this will be a hotspot for you.
# '''


class Profile(numpy.recarray):
    '''data: depths|pressures, values: soundspeed|salinity|conductivity|temperature|time
    Be careful when slicing, a recarray will be returned not a Profile.  This is good when setting data in place but problematic when trying to add/remove records
    '''
    # header_keys are based on the 13 standard headers from VelocWin Visual Basic code that were written into the edited/processed Q, B files.
    # Name_Date_SN was Header(7) in VelocWin which held name and date in a text string  -- "CREATED ON " + Date$ + " BY " + LTrim(txtName.Text)
    # or the SML/Minitroll diver gauge serial number.  Should be Name_Date only for cast data since diver gauges don't make cast profiles.
    header_keys = (
    'Ship', 'Year', 'Day', 'Time', 'Latitude', 'Longitude', 'Instrument', 'Name_Date_SN', 'Format', 'Project', 'Survey',
    'DataSetID', 'DateStamp', 'Draft')
    # the following header keys are other metadata keys added in the Python conversion that contain
    #  class instances (e.g. Coordinate) or strings used to make the standard headers (UserName, ProcessDate
    header_keys_strings = ('UserName', 'ProcessDate', 'Filename', 'Path', 'SurveyUnits', 'ImportFormat')
    # location is a coordinates.Coordinate instance for the cast location
    # timestamp is a datetime object for the cast time, as opposed to the ProcessDate which is when the user downloaded/processed the data
    header_keys_objects = ('location', 'timestamp')

    def __new__(cls, data,
                **kwargs):  # data (NxM list or array), names=('depth', 'temperature', 'soundspeed'), ymetric='depth', attribute='soundspeed', metadata={}):
        '''data should be one NxM list or array (N>=2).
        Using numpy.fromarrays -- so data that is in list form should be list of arrays [[d1,d2,d3...], [ss1,ss2,ss3...]] instead of [(d1, ss1), (d2, ss2), (d3, ss3)...] like zip would produce
        If a structured array is supplied then the names are preserved.  Otherwise an optional names list is used.
        names argument should be supplied describing the columns of the array.
        ymetric should be depth|pressure,
        attribute should be soundspeed|salinity|conductivity|temperature|time
        optional keyword argument 'metadata' can be a dictionary of metadata attributes (e.g. timestamp, location, boat, etc.)
          they should use the header_keys (or integer indices corresponding to those?) in order to write standard VelocWin output Q, A, B files.
        To change the column names -- if say a conversion operation is done to a column, replace the dtype.names like below
        >>> r.dtype.names
        ('col1', 'col2')
        >>> r.dtype.names = ('x', 'y')
        Make sure to update the ymetric/attribute names if appropriate
        '''
        # For some reason the records array doesn't seem to initialize with
        # names when taking a numpy.array for the first arg
        # Convert to a python list if it's a numpy array
        if isinstance(data, numpy.ndarray) and data.dtype.names:
            r = numpy.rec.fromarrays([data[n] for n in data.dtype.names], dtype=data.dtype)
        else:
            r = numpy.rec.fromarrays(data, names=kwargs.get('names',
                                                            ()))  # defaults to numpy f#   -- ex: dtype=[('f0', '<f8'), ('f1', '<f8')])

        r.__class__ = cls
        # FIXME: Deprecate these
        for ym in (kwargs.get('ymetric'), 'depth', 'pressure', r.dtype.names[0]):
            if ym in r.dtype.names:
                break
        for attr in (
        kwargs.get('attribute'), 'soundspeed', 'salinity', 'time', 'conductivity', 'temperature', r.dtype.names[1]):
            if attr in r.dtype.names:
                break
        r.SetAttributeName(attr)
        r.SetYMetricName(ym)
        return r

    def __init__(self, data, **kwargs):
        try:
            self.metadata = kwargs['metadata']
        except:
            warn("Creating profile without any metadata information")
            self.metadata = {}

    def get_keyargs(self):
        '''Convenience function to get all the keyword arguments needed to recreate this object
        using a different recarray.  Doesn't return names or anything related to the numpy.recarray object, just the extra
        info used by this class that is lost when operating on an instance as a numpy array.
        e.g. Profile(oldProf.compress(condition), **oldProf.get_keyargs())
        '''
        return {'ymetric': copy(self.ymetric), 'attribute': copy(self.attribute), 'metadata': deepcopy(self.metadata)}

    def SetYMetricName(self, ym):
        self.ymetric = ym

    def SetAttributeName(self, attr):
        self.attribute = attr

    def append_field(self, name, arr, dtype=None):
        arr = numpy.asarray(arr)
        if dtype is None:
            dtype = arr.dtype
        newdtype = numpy.dtype(self.dtype.descr + [(name, dtype)])
        newrec = numpy.empty(self.shape, dtype=newdtype)
        for field in self.dtype.fields:  # copy old data
            newrec[field] = self[field]
        newrec[name] = arr  # add new data
        return Profile(newrec, **self.get_keyargs())

    def items(self):
        return zip(self.keys(), self.values())

    def keys(self):
        return self[self.ymetric]

    def values(self):
        return self[self.attribute]

    getDepths = keys
    getSpeeds = values

    def mcopy(self):
        '''copy of Profile with names, ymetric, metadata retained.
        Not using "copy" since that is a method on the numpy.recarray that we may want access to.
        '''
        data = numpy.recarray.copy(self)
        return Profile(data, **self.get_keyargs())

    def AbsProfile(self, names=[]):
        p3 = self.mcopy()
        if not names:
            names = set(self.dtype.names)
        for n in names:
            p3[n] = numpy.absolute(p3[n])
        return p3

    def NegProfile(self, names=[]):
        p3 = self.mcopy()
        if not names:
            names = set(self.dtype.names)
        for n in names:
            p3[n] *= -1
        return p3

    def DiffProfile(self, p2, names=[]):
        '''Difference two profiles, use all matching field names if not specified
        returns p1 metadata and p1-p2 for all fields specifed (or matched)
        '''
        if not names:
            names = set(self.dtype.names).intersection(p2.dtype.names)
        return self.AddProfile(p2.NegProfile(names), names)

    def AddProfile(self, p2, names=[]):
        '''Sum two profiles, use all matching field names if not specified
        returns p1 metadata and p1+p2 for all fields specifed (or matched)
        '''
        p3 = self.mcopy()
        if not names:
            names = set(self.dtype.names).intersection(p2.dtype.names)
        for n in names:
            p3[n] = self[n] + p2[n]
        return p3

    @staticmethod
    def ConvertFromSoundSpeedProfile(p):
        metadata = {}

        # translate metadata
        d = {}
        for k, v in dicts.Dicts.probe_types.items():
            try:
                d[v] = k
            except:
                pass
        try:
            metadata['ImportFormat'] = d[p.meta.probe_type]
        except:
            d = {}
            for k, v in dicts.Dicts.sensor_types.items():
                try:
                    d[v] = k
                except:
                    pass
            metadata['ImportFormat'] = d.get(p.meta.sensor_type, "")
        try:
            metadata.update(Profile.getMetaFromCoord(coordinates.Coordinate(p.meta.latitude, p.meta.longitude, )))
        except:
            pass
        metadata['filename'] = p.meta.original_path
        metadata['timestamp'] = p.meta.utc_time
        # p.meta._institution = ''
        metadata['Survey'] = p.meta._survey
        metadata['Ship'] = p.meta._vessel
        metadata['Instrument'] = p.meta._sn
        # p.meta.proc_time = datetime.datetime.now()
        # p.meta.proc_info = 'imported via Velocipy'
        # translate units
        # p.meta.pressure_uom = 'dbar'
        # p.meta.depth_uom = 'm'
        # p.meta.speed_uom = 'm/s'
        # p.meta.temperature_uom = 'deg C'
        # p.meta.conductivity_uom = ''
        # p.meta.salinity_uom = ''
        # convert profile data
        p.data.num_samples = len(self)
        col_types = []
        prof_data = []
        for data, name in ((p.data.pressure, 'pressure'), (p.data.depth, 'depth')
            (p.data.speed, 'soundspeed'), (p.data.temp, 'temperature'),
                           (p.data.sal, 'salinity'), (p.data.conductivity, 'conductivity')):
            if data is not None:
                col_types.append((name, numpy.float32))
                prof_data.append(data)

        # return the finised profile
        prof_array = numpy.zeros(prof_data, dtype=col_types)
        p = Profile(prof_array, metadata=metadata)
        return p

    def ConvertToSoundSpeedProfile(self):
        p = hyo2.soundspeed.profile.profile.Profile()
        # translate metadata
        p.meta.sensor_type = dicts.Dicts.sensor_types.get(self.metadata.get('ImportFormat', ''),
                                                          dicts.Dicts.sensor_types['Unknown'])
        p.meta.probe_type = dicts.Dicts.probe_types.get(self.metadata.get('ImportFormat', ''),
                                                        dicts.Dicts.probe_types['Unknown'])

        try:
            p.meta.latitude = coordinates.LatStrToDec(self.metadata['Latitude'], assume_S=False)
            p.meta.longitude = coordinates.LonStrToDec(self.metadata['Longitude'], assume_W=False)

        except Exception:
            p.meta.latitude = None
            p.meta.longitude = None

        p.meta.original_path = self.metadata.get('filename', str())
        p.meta.utc_time = self.metadata.get('timestamp', None)
        p.meta._institution = str()
        p.meta._survey = self.metadata.get('Survey', str())
        p.meta._vessel = self.metadata.get('Ship', str())
        p.meta._sn = self.metadata.get('Instrument', str())
        p.meta.proc_time = datetime.datetime.now()
        p.meta.proc_info = 'imported via Velocipy'
        # translate units
        p.meta.pressure_uom = 'dbar'
        p.meta.depth_uom = 'm'
        p.meta.speed_uom = 'm/s'
        p.meta.temperature_uom = 'deg C'
        p.meta.conductivity_uom = str()
        p.meta.salinity_uom = 'PSU'
        # convert profile data
        p.init_data(len(self))
        try:
            p.data.pressure = self['pressure']
        except ValueError:  # no matching data column
            pass
        try:
            p.data.depth = self['depth']
        except ValueError:  # no matching data column
            pass
        try:
            p.data.speed = self['soundspeed']
        except ValueError:  # no matching data column
            pass
        try:
            p.data.temp = self['temperature']
        except ValueError:  # no matching data column
            pass
        try:
            p.data.sal = self['salinity']
        except ValueError:  # no matching data column
            pass
        try:
            p.data.conductivity = self['conductivity']
        except ValueError:  # no matching data column
            pass
        # return the finised profile
        return p
