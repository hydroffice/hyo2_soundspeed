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

import os, glob
import datetime, time, calendar
from warnings import warn
from copy import deepcopy, copy
from pprint import pformat
import re
import struct
import urllib2
import ast
import subprocess

import numpy
from numpy.ma import MaskedArray
from numpy import array
from netCDF4 import Dataset, stringtoarr, num2date

from . import coordinates

from . import sbe_tools as Tools
from . import sbe_constants
from . import velocipy_equations
from ...listener.seacat import sbe_serialcomms as Seacat


class UserError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class MetadataException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class DataFileError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


def parseNumbers(filename, dtype, sep, pre='', post='', ftype=''):
    '''builds a regular expression based on dtype.names and the (regex ok) separator supplied
    dtype is a numpy.dtype object describing the fieldnames and data types
    sep is the separator for the values being parsed -- ex: "(,|\s+)" for one comma or 1+ whitespaces, notice the group ( ) so the or pipe "|" doesn't affect the entire expression
    pre and post are any extra validation on either side of the values being parsed.  ex: pre="^", post = "$" would specify begin and end of line respectively.
    pre and post could also be lookahead/behind assertions for example pre="(?<=DATA:)"  post="(?=*[\d\w]{2})", pre would require "DATA:" right before the values being parsed post would want a * with two digits (perhaps a checksum)
    The assertions would be more useful if we didn't splitlines() in the next function...
    '''
    if isinstance(dtype, (list, tuple)):
        dtype=numpy.dtype(dtype)
    rstr = sep.join([sbe_constants.named_re_number%n for n in dtype.names])
    expr = re.compile(pre+rstr+post)
    return parseFile(filename, dtype, expr, ftype)

def parseFile(filename, dtype, expr, ftype=''):
    '''Parse a file and return a numpy rec.array -- allows use of subgroups unlike the numpy.fromregex
    This allows better enforcement of numeric formatting.
    Pass in filename to read, numpy.dtype object with the names/types for the record array and a compiled regular expression 
    '''
    if isinstance(dtype, (list, tuple)):
        dtype=numpy.dtype(dtype)
    data = []
    s = file(filename, 'r').read()
    for l in s.splitlines():
        m=expr.search(l)
        if m:
            data.append(tuple([m.group(n) for n in dtype.names])) #numpy handles any string to int/float for us
    first_line = s.splitlines()[0].split(',')
    if ftype == 'SSP' and s[0] == '$' and len(first_line) > 7 + len(data[0]): #insert the first line of SSP
        data.insert(0, tuple(first_line[-1-len(data[0]):-1]))
    return numpy.array(data, dtype=dtype)
def is_increasing(l):
    '''Returns True if the sequence l is monotonically increasing.
         False otherwise.
         FIXME: Can I do this faster than O(n)?
    '''
    truth = map(lambda x,y: x < y, l[:-1], l[1:])
    return truth == ( [True] * (len(l) - 1) )

#Identifier Input data    Data to be used                     Comment
ssp_fmts_doc = '''
        S00 D,c           D,c 
        S01 D,c,T,S       D,c,a(D,T,S,L)                      Same as S12, but used immediately.
        S02 D,T,S         D,c(D,T,S,L),a(D,T,S,L)             Same as S22, but used immediately.
        S03 D,T,C         D,c(D,T,C,L),a(D,T,S,L)             Same as S32,but used immediately.
        S04 P,T,S         D(P,T,S,L),c(P,T,S,L),a(P,T,S,L)    Same as S42,but used immediately.
        S05 P,T,C         D(P,T,C,L),c(P,T,C,L),a(P,T,C,L)    Same as S52,but used immediately.
        S06 D,c,a         D,c,a                               Same as S11,but used immediately.
        S10 D,c           D,c 
        S11 D,c,a         D,c,a 
        S12 D,c,T,S       D,c,a(D,T,S,L) 
        S13 D,c,a,f       D,c,a                               Frequency dependent
        S20 D,T,S         D,c(D,T,S,L) 
        S21 D,T,S,a       D,c(D,T,S,L),a 
        S22 D,T,S         D,c(D,T,S,L),a(D,T,S,L) 
        S23 D,T,S,a,f     D,c(D,T,S,L),a                      Frequency dependent
        S30 D,T,C         D,c(D,T,S,L)
        S31 D,T,C,a       D,c(D,T,S,L),a
        S32 D,T,C         D,c(D,T,S,L),a(D,T,S,L)
        S33 D,T,C,a,f     D,c(D,T,S,L),a                      Frequency dependent
        S40 P,T,S         D(P,T,S,L),c(P,T,S,L)
        S41 P,T,S,a       D(P,T,S,L),c(P,T,S,L),a
        S42 P,T,S         D(P,T,S,L),c(P,T,S,L),a(P,T,S,L)
        S43 P,T,S,a,f     D(P,T,S,L),c(P,T,S,L),a             Frequency dependent
        S50 P,T,C         D(P,T,C,L),c(P,T,C,L)
        S51 P,T,C,a       D(P,T,C,L),c(P,T,C,L),a
        S52 P,T,C         D(P,T,C,L),c(P,T,C,L),a(P,T,C,L)
        S53 P,T,C,a,f     D(P,T,C,L),c(P,T,C,L),a             Frequency dependent
'''
SSP_Formats = {}
for fmt in ssp_fmts_doc.splitlines():
    m=re.match(r'\s*(?P<fmt>S\d\d)\s*(?P<fields>[\w,]*)\s', fmt)
    if m:
        SSP_Formats[m.group('fmt')] = [t.replace('a', 'absorption').replace('c', 'soundspeed').replace('f', 'frequency').replace('D', 'depth').replace('T', 'temperature').replace('S', 'salinity') for t in m.group('fields').split(',')]

'''
Addressing Array Columns by Name
There are two very closely related ways to access array columns by name: recarrays and structured arrays. 
Structured arrays are just ndarrays with a complicated data type: 
        In [1]: from numpy import *
        
        In [2]: ones(3, dtype=dtype([('foo', int), ('bar', float)]))
        Out[2]:
        array([(1, 1.0), (1, 1.0), (1, 1.0)],
                    dtype=[('foo', '<i4'), ('bar', '<f8')])
        
        In [3]: r = _
        
        In [4]: r['foo']
        Out[4]: array([1, 1, 1])

recarray is a subclass of ndarray that just adds attribute access to structured arrays: 
        In [10]: r2 = r.view(recarray)
        
        In [11]: r2
        Out[11]:
        recarray([(1, 1.0), (1, 1.0), (1, 1.0)],
                    dtype=[('foo', '<i4'), ('bar', '<f8')])
        
        In [12]: r2.foo
        Out[12]: array([1, 1, 1])

One downside of recarrays is that the attribute access feature slows down all field accesses, 
even the r['foo'] form, because it sticks a bunch of pure Python code in the middle. 

Much code won't notice this, but if you end up having to iterate over an array of records, 
this will be a hotspot for you. 
'''

class ScipyProfile(numpy.recarray):
    '''data: depths|pressures, values: soundspeed|salinity|conductivity|temperature|time
    Be careful when slicing, a recarray will be returned not a ScipyProfile.  This is good when setting data in place but problematic when trying to add/remove records
    '''
    FLAG_BAD, FLAG_OK, FLAG_EXT_HIST, FLAG_EXT_LINEAR, FLAG_EXT_SLOPE, FLAG_EXT_MANUAL, FLAG_MOVED, FLAG_EXT_APPEND = range(-1, 7) 
    #header_keys are based on the 13 standard headers from VelocWin Visual Basic code that were written into the edited/processed Q, B files.
    #Name_Date_SN was Header(7) in VelocWin which held name and date in a text string  -- "CREATED ON " + Date$ + " BY " + LTrim(txtName.Text)
    # or the SML/Minitroll diver gauge serial number.  Should be Name_Date only for cast data since diver gauges don't make cast profiles.
    header_keys = ('Ship', 'Year', 'Day', 'Time', 'Latitude', 'Longitude', 'Instrument', 'Name_Date_SN', 'Format', 'Project', 'Survey', 'DataSetID', 'DateStamp', 'Draft')
    #teh following header keys are other metadata keys added in the Python conversion that contain 
    #  class instances (e.g. Coordinate) or strings used to make the standard headers (UserName, ProcessDate
    header_keys_strings = ('UserName', 'ProcessDate', 'Filename', 'Path', 'SurveyUnits', 'ImportFormat')
    #location is a coordinates.Coordinate instance for the cast location
    #timestamp is a datetime object for the cast time, as opposed to the ProcessDate which is when the user downloaded/processed the data
    header_keys_objects = ('location', 'timestamp')
    header_end = 'ENDHDR'
    filetypes={
               'Q':     "Velocwin processed files (*.??Q)|*.??q;*.vpq",
               'B':     "Velocwin files (*.??B)|*.??b;*.vpb",
               'CNV':   "Seabird CNV Files (*.?nv)|*.?nv",
               'HEX':   "Seabird HEX Files -- will make CNV file (*.?ex)|*.?ex",
               'CSV':   "Digibar/CastAway CSV Files (*.csv)|*.csv",
               'XSV':   "Sippican XSV Files (*.edf)|*.edf",
               'ASVP':  "Simrad/Brooke-Ocean MVP (*.asvp)|*.asvp",
               'SSP':   "Simrad/Brooke-Ocean MVP (*.ssp, *.S??)|*.ssp;*.s??",
               'ZZD':   "Cast files (*.zzd)|*.zzd",
               'NC':    "NODC netCDF files (*.nc, *.??a, *.??d)|*.nc;*.??a;*.??d",
               'CARIS': "Caris svp files (*.svp)|*.svp",
               'CALC':  "MVP 100 files (*.calc or *.*c)|*.calc;*.*c",
               'RAW':   "MVP files (*.raw)|*.raw",
               'UNB':   "UNB/OMG svp files (*.svp)|*.svp",
               'A':     "Velocwin processed files (*.??a)|*.??a;*.vpa",
               'XBT':   "Sippican XBT Files (xbt*)|xbt*",
               'ASC':   "OceanScience (*.asc)|*.asc",
               'TXT':   "Generic Text Depth v SS (*.txt)|*.txt",
    }
    export_types={
               'Q':     "Velocwin processed files (*.VPQ)|*.vpq",
               'B':     "Velocwin files (*.VPB)|*.vpb",
               'A':     "Velocwin processed - NODC files (*.VPA)|*.vpa",
               'SVA':   "Hydrostar (Elac) (*.sva)|*.sva",
               'ASVP':  "Simrad/Brooke-Ocean MVP (*.asvp)|*.asvp",
               'SSP':   "Simrad/Brooke-Ocean MVP (*.ssp)|*.ssp",
               'CARIS': "Caris svp files (*.svp)|*.svp",
                  }
    export_types['All'] = 'All Supported Formats|'+';'.join([ ft.split('|')[1] for t,ft in export_types.iteritems()])
    filetype_wildcards = { 'Sound speed':   '|'.join([filetypes['Q'],filetypes['B'],filetypes['CNV'],filetypes['HEX'],filetypes['CSV'],
                                            filetypes['XSV'],filetypes['ASVP'],filetypes['SSP'],filetypes['ZZD'],
                                            filetypes['CARIS'],filetypes['CALC'],filetypes['RAW'],filetypes['UNB'],filetypes['TXT']])+\
                                            "All files (*.*)|*.*",
                           'Salinity':      '|'.join([filetypes['A'],filetypes['CNV'],filetypes['HEX'],filetypes['UNB'],filetypes['ASC']])+\
                                            "All files (*.*)|*.*",
                           'Temperature':   '|'.join([filetypes['A'],filetypes['CNV'],filetypes['HEX'],filetypes['CSV'],filetypes['XBT'],filetypes['ASC'],
                                            filetypes['UNB']])+\
                                            "All files (*.*)|*.*",
                           'All' : 'All Supported Formats|'+';'.join([ ft.split('|')[1] for t,ft in filetypes.iteritems()])+'|'+
                                    '|'.join(filetypes.values())+'|All files (*.*)|*.*'
                        }
    
    def __new__(cls, data, **kwargs):#data (NxM list or array), names=('depth', 'temperature', 'soundspeed'), ymetric='depth', attribute='soundspeed', metadata={}):
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


        ' DEFINITIONS - Header array Header() for SV files
        
        '                             Header(0) to Header(12) appear in all Velocwin SV output files (B or Q)
        
        '                             Old DOS versions of Velocity have at least Header(0) to Header(8).
        
        '                             Header(13), the draft, appears on input form but not as a header line
        '                             in B or Q files.
        
        '                             Headers with index > 13 may also appear as self-explanatory strings.
        '                             (ex: Harmonic mean, if calculated, with corresponding draft)
        
        '                             ENDHDR signals end of headers.
        
        ' Header(0)         Ship/Unit     ex: WHITING
        ' Header(1)         Year              1999
        ' Header(2)         Day UTC           254
        ' Header(3)         Time UTC          13:53 or 13:53:25 (include seconds for AUV)
        ' Header(4)         Latitude          31/08/03.13 N
        ' Header(5)         Longitude         081/12/06.36 W
        ' Header(6)         Instrument        SEACAT S/N:1060 CD:12/31/98
        ' Header(7)         Name_Date         CREATED ON 03-20-99 BY X
        ' Header(8)         Format            FORMAT 6 (SEACAT CTD) *(see note below for Header(8)
        ' Header(9)         Project           OPR-G123-WH
        ' Header(10)        Survey            H01234
        ' Header(11)        Data set ID       00005                ' mod 4/3/02 for Simrad SSP
        '                                                             "" if not generating Simrad SSP file
        ' Header(12)        Simrad SSP Path   C:\SSP\ for input, or
        '                   DateStamp         mm-dd-yyyy for output
        ' Header(13)        Draft             .8
        ' ENDHDR                End of Headers    ENDHDR

        ' HEADER(8) SV File type
        ' Initially, retain REAL OLD values from DOS version
        ' = 1 for Manual, = 6 for SBE SEACAT
        ' 1/12/00, Nformat = 2 for DIGIBAR PRO
        ' 12/18/03, Nformat = 5 for SBE 911
        ' 03/16/05, Nformat = 3 for BOT MVP .asvp
        '                   = 4 for BOT MVP .ssp
        '                   = 7 for BOT MVP .???c (AML CALC format)
        ' 10/07/05, Nformat = 8 for SIPPICAN XBT
        ' 02/05/08, Nformat = 9 for Remus AUV CTD txt files.
        ' 09/25/08, Nformat = 10 for Sippican XSV        
        ' * modified Header(8) for Sippican XBT processing - Add on method of obtaining salinity
        '    HEADER(8) = FORMAT 8 (Sippican XBT) - ASSUMED SALINITY 35 PPT
        '    or
        '    HEADER(8) = FORMAT 8 (Sippican XBT) - SALINITIES FROM CTD YYDDDHHMM.M
        '
        ' --------------------------------------------------------------------------
        ' *** NOTE: Certain Header array elements are redefined for Diver Least Depth Report.
        ' Refer to frmSmlGauge for definitions
        '------------------------------------------------------------------------------------
        '''
        # For some reason the records array doesn't seem to initialize with
        # names when taking a numpy.array for the first arg
        # Convert to a python list if it's a numpy array
        if isinstance(data, numpy.ndarray) and data.dtype.names:
            #print 'copy2'
            #r = data.copy() #copy of the data with names and such maintained
            r = numpy.rec.fromarrays([data[n] for n in data.dtype.names], dtype= data.dtype)
        else:
            #print 'fromarrays'
            r = numpy.rec.fromarrays(data, names=kwargs.get('names', ())) #defaults to numpy f#   -- ex: dtype=[('f0', '<f8'), ('f1', '<f8')])
        #r = records.array(data, names=('y', 'z'), titles=(kwargs['ymetric'], kwargs['attribute']))
        r.__class__ = cls
        # FIXME: Deprecate these
        for ym in (kwargs.get('ymetric'), 'depth', 'pressure', r.dtype.names[0]):
            if ym in r.dtype.names: break
        for attr in (kwargs.get('attribute'), 'soundspeed','salinity','time','conductivity','temperature', r.dtype.names[1]):
            if attr in r.dtype.names: break 
        r.SetAttributeName(attr)
        r.SetYMetricName(ym)
        return r

    def __init__(self, data, **kwargs):
        #if not is_increasing(self.getDepths()):
        #    print data
        #    print data.ymetric, data.attribute
        #    print data.ymetric
        #    raise ValueError("ScipyProfile.__init__() received data in which the %s is not monotonically increasing: %s" % (self.ymetric, str(self.getDepths())))
        try:
            self.metadata = kwargs['metadata']
        except:
            warn("Creating profile without any metadata information")
            self.metadata = {}
    def get_keyargs(self):
        '''Convenience function to get all the keyword arguments needed to recreate this object 
        using a different recarray.  Doesn't return names or anything related to the numpy.recarray object, just the extra
        info used by this class that is lost when operating on an instance as a numpy array.
        e.g. ScipyProfile(oldProf.compress(condition), **oldProf.get_keyargs())
        '''
        return {'ymetric':copy(self.ymetric), 'attribute':copy(self.attribute), 'metadata':deepcopy(self.metadata)}
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
        for field in self.dtype.fields: #copy old data
            newrec[field] = self[field]
        newrec[name] = arr #add new data
        return ScipyProfile(newrec, **self.get_keyargs())
    #def compress(self, condition, axis=None, out=None):
    #    v = numpy.compress(self, condition, axis, out)
    #    return ScipyProfile(v, **self.get_keyargs())
    def items(self):
        return zip(self.keys(), self.values())

    def keys(self):
        return self[self.ymetric]

    def values(self):
        return self[self.attribute]

    getDepths = keys
    getSpeeds = values

    def reduceToWholeMeters(self):
        '''Take the current profile, sort by depth and linear interpolate soundspeeds from 0m to max depth
        '''
        new_ys = numpy.arange(int(self['depth'].max()))
        p=self.NoDupes_GoodFlags()
        new_xs = numpy.interp(new_ys, p['depth'], p['soundspeed']) # this is a piecewise-linear interpolation
        return ScipyProfile([new_ys, new_xs], names=['depth', 'soundspeed'],  **self.get_keyargs())
    def StatisticalFlagEdit(self):
        #Literal conversion from EditSV in VelocWin
        Cend = 1.3   #' Relaxed tolerance factor at endpoints.
        Zband = 33   #' Dist. from surface in which to relax error band.
        Cdepth = 1.3 #' Relaxed tolerance factor in depth interval ZBAND.
        Cspread = 2  #' # of standard deviations to use for error band.
        Sigmin = 0.2 #' Minimum standard deviation allowed.
        
        SV = self['soundspeed'] #allocate arrays
        DEPTH = self['depth']
        Sigma = SV*0.0 
        Vmean = SV*0.0
        Npts = len(SV)
        
        Vmin = self['soundspeed'].min()
        Vmax = self['soundspeed'].max()
        Vmid = 0.5 * (Vmin + Vmax)
        Vmid = int(0.5+Vmid / 10.0) * 10
        Vzero = Vmid - 50            #' Computing origin
        
        #' Edit the data statistically.  To obtain local mean and
        #' local standard deviation for point I, use 2 neighboring
        #' points on either side of point I.  Endpoints treated separately.
        #This looks to be most effective on single point fliers
        for I in range(2, Npts - 2):
            VSum = 0    
            VSumSq = 0
            for K in range(-2, 3):
                if K != 0:
                    Vdiff = SV[I + K] - Vzero        #' Use computing origin to avoid
                    VSum = VSum + Vdiff              #' very large quantities
                    VSumSq = VSumSq + Vdiff * Vdiff
        
            Variance = (VSumSq - VSum * VSum / 4) / 3
            Vmean[I] = VSum / 4 + Vzero            #' Add back computing origin
            if Variance < 0: Variance = 0
            Sigma[I] = numpy.sqrt(Variance)               #' Local standard deviation
            if Sigma[I] < Sigmin: Sigma[I] = Sigmin
        
        
        #' Endpoint treatment -- use only three neighboring points.
        #' Relax tolerance.
        #' Endpoints are the first two and last two points.
        Iend = [0,1,Npts - 2, Npts-1]
        Index = [(1,2,3),
                 (0,2,3),
                 (Npts-4, Npts-3, Npts-1),
                 (Npts-4, Npts-3, Npts-2)
                 ]
        
        for K in range(4):
            VSum = 0
            VSumSq = 0
            I = Iend[K] #                           ' Point number
            for J in range(3):
                L = Index[K][J]
                Vdiff = SV[L] - Vzero
                VSum = VSum + Vdiff
                VSumSq = VSumSq + Vdiff * Vdiff
        
            Variance = (VSumSq - VSum * VSum / 3) / 2
            Vmean[I] = VSum / 3 + Vzero
            if Variance < 0: Variance = 0
            Sigma[I] = numpy.sqrt(Variance)
            if Sigma[I] < Sigmin: Sigma[I] = Sigmin
            Sigma[I] = Sigma[I] * Cend            #' Relax tolerance for endpts
        
        Factor = Cdepth
        for I in range(Npts):
            if DEPTH[I] > Zband: Factor = 1
            DV = Factor * Cspread * Sigma[I]      #' Half allowable V interval
            if numpy.absolute(SV[I] - Vmean[I]) > DV:
                self['flag'][I] = ScipyProfile.FLAG_BAD                     #' So-called bad point
        
        #' See if there are any off-screen points not flagged as 'bad'.
        #Removing this as nothing should be greater than Vmax and Vzero is hardcoded and could fail on deep casts from Okeanos Explorer.
        #for I in range(Npts):
        #   if SV[I] < Vzero or SV[I] > Vmax:
        #         self['flag'][I] = -1
    
        
    def QC(self, bin = (), minspeed=1400, maxspeed=1700, bMinMax=False):
        '''Returns new profile with any soundspeeds outside of 1400 - 1635 removed
        If bin is specified then a bin averaging is applied.  
        bin[0][0] specifies the attribute to use for bins, the rest of the strings specify what attributes are averaged
        bin[1] specifies the bin size -- 0.1 
        or bin[1] and bin[2] the bin edges and bin values (this function uses numpy.digitize, so if the bins are supposed to be centered you have to specify the edges and then the centers -- [0,5,10,50,100], [2.5, 7.5, 30, 75, 100] -- make sure to test this as this bin[1], bin[2] example isn't quite right  
        (['depth', 'soundspeed', 'temperature'], 0.1)  

        From VB code
        ' Do bin-averaging to eliminate any duplicate depths obtained from the Digibar Pro or MVP CALC file
        ' Note that depths for both Digibar and MVP are expressed to the nearest tenth.
        ' Depth for a bin is (bin number/10) (0.1, 0.2, 0.3, ..., Nbins/10)

        '''
        d=self.mcopy()
        try:
            d = numpy.compress(d['soundspeed']>=minspeed, d) #remove less than 1400 -- oil can be as low as 1200
            d = numpy.compress(d['soundspeed']<=maxspeed, d) #really deep fake simrad cast gets to 1675
        except ValueError: pass #doesn't have soundspeed field
        if 'flag' in self.dtype.names:
            d=numpy.compress(d['flag']>=0, d)
        if bin:
            x = d[bin[0][0]]
            try:
                len(bin[1])
                edges = bin[1]
                centers = bin[2]
            except TypeError:
                start = (int(x.min()/bin[1])-2)*bin[1]
                centers = numpy.arange(start, x.max()+3*bin[1], bin[1]) #give room since the binning is b[n] <= x < b[n+1]  -- need to have top bin larger than the max() and arange may also cut off a bin  arange(0,7) give 0 to 6
                edges = numpy.arange(start+bin[1]/2.0, x.max()+4*bin[1], bin[1]) #give room since the binning is b[n] <= x < b[n+1]  -- need to have top bin larger than the max() and arange may also cut off a bin  arange(0,7) give 0 to 6
            b = numpy.digitize(x,edges)
            new_data = numpy.zeros([len(edges)], dtype = [(attr, d.dtype[attr]) for attr in bin[0]]+ [('bin_count', numpy.int32)])
            if bMinMax:
                min_data = numpy.zeros([len(edges)], dtype = [(attr, d.dtype[attr]) for attr in bin[0]]+ [('bin_count', numpy.int32)])
                max_data = numpy.zeros([len(edges)], dtype = [(attr, d.dtype[attr]) for attr in bin[0]]+ [('bin_count', numpy.int32)])
            for i, e in enumerate(centers):
                new_data[bin[0][0]][i] = e
                if bMinMax: #get min max for the binned value too (depth in general)
                    attr = bin[0][0]
                    attr_vals = numpy.compress(b==i, d[attr])
                    if len(attr_vals)>0:
                        min_data[attr][i] = attr_vals[numpy.argmin(attr_vals)] #could use min(attr_vals) but am thinking we might want other attributes from the min/max positions
                        max_data[attr][i] = attr_vals[numpy.argmax(attr_vals)]
                for attr in bin[0][1:]:
                    attr_vals = numpy.compress(b==i, d[attr])
                    new_data['bin_count'][i]=len(attr_vals)
                    if len(attr_vals)>0:
                        new_data[attr][i] = numpy.average(attr_vals)
                        if bMinMax:
                            min_data[attr][i] = attr_vals[numpy.argmin(attr_vals)] #could use min(attr_vals) but am thinking we might want other attributes from the min/max positions
                            max_data[attr][i] = attr_vals[numpy.argmax(attr_vals)]
                        
            d=numpy.compress(new_data['bin_count']>0, new_data) #remove empty bins
            if bMinMax:  
                mi=numpy.compress(new_data['bin_count']>0, min_data) #remove empty bins        
                ma=numpy.compress(new_data['bin_count']>0, max_data) #remove empty bins
        if bMinMax:
            return ScipyProfile(d, **self.get_keyargs()), ScipyProfile(mi, **self.get_keyargs()), ScipyProfile(ma, **self.get_keyargs())
        else:        
            return ScipyProfile(d, **self.get_keyargs())
    def NoDupes_GoodFlags(self, spacing = 0.1):
        '''Returns a new array with 'flag' values !=0 and the depths sorted and spaced by at least the spacing value
        '''
        d=self.mcopy()
        if 'flag' in self.dtype.names:
            d=numpy.compress(d['flag']>=0, d)
        if 'depth' in self.dtype.names:
            d.sort(order=['depth']) #must sort before taking the differences
            depths=d['depth']
            #TODO: should we use QC( ) here or just the first sample that passes the spacing check?  Depends on if averaging the other data fields is ok.
            ilist = [0]
            for i in range(len(d)):
                if depths[i]-depths[ilist[-1]]>=spacing:
                    ilist.append(i)
            d=d.take(ilist)
            #delta_depth = numpy.hstack(([spacing*2],numpy.diff(d['depth']))) #add a true value for the first difference that
            #d = numpy.compress(delta_depth>=spacing, d) #make sure duplicate depths not written
        return ScipyProfile(d, **self.get_keyargs())

    def DownSample(self, maxcnt):
        '''Returns a new array with 'flag' values !=0 and the depths sorted and spaced by at least the spacing value
        '''
        d=self.mcopy()
        keep_indices = numpy.array((numpy.arange(len(d)+1))*(maxcnt-2)/(len(d)+1), numpy.int32)
        bool_indices = numpy.diff(keep_indices)
        bool_indices[0]=1 #keep the first and last
        bool_indices[-1]=1
        d=d.compress(bool_indices)
        return ScipyProfile(d, **self.get_keyargs())

    def __str__(self):
        d = copy(self.metadata)
        try:
            d.update({'timestamp': d['timestamp'].isoformat(),
                                'location': str(d['location'])})
        except: warn("Failed to type metadata... I'll just print it verbosely.")
        return pformat(d)+str(self.shape)

    def mcopy(self):
        '''copy of ScipyProfile with names, ymetric, metadata retained.  
        Not using "copy" since that is a method on the numpy.recarray that we may want access to.
        '''
        data = numpy.recarray.copy(self)
        return ScipyProfile(data, **self.get_keyargs())
    def AbsProfile(self, names=[]):
        p3=self.mcopy()
        if not names: names = set(self.dtype.names)
        for n in names:
            p3[n]=numpy.absolute(p3[n])
        return p3
        
    def NegProfile(self, names=[]):
        p3=self.mcopy()
        if not names: names = set(self.dtype.names)
        for n in names:
            p3[n]*=-1
        return p3
    def DiffProfile(self, p2, names=[]):
        '''Difference two profiles, use all matching field names if not specified
        returns p1 metadata and p1-p2 for all fields specifed (or matched)
        '''
        if not names: names = set(self.dtype.names).intersection(p2.dtype.names)
        return self.AddProfile(p2.NegProfile(names), names)
    
    def AddProfile(self, p2, names=[]):
        '''Sum two profiles, use all matching field names if not specified
        returns p1 metadata and p1+p2 for all fields specifed (or matched)
        '''
        p3 = self.mcopy()
        if not names: names = set(self.dtype.names).intersection(p2.dtype.names)
        for n in names:
            p3[n]=self[n]+p2[n]
        return p3
    
    @staticmethod
    def ConvertFromSoundSpeedProfile(p):
        from hydroffice.soundspeed.profile import dicts
        metadata = {}
        
        #translate metadata
        d={}     
        for k,v in dicts.Dicts.probe_types.items():
            try:
                d[v] = k
            except:
                pass
        try:
            metadata['ImportFormat'] = d[p.meta.probe_type]
        except:
            d={}     
            for k,v in dicts.Dicts.sensor_types.items():
                try:
                    d[v] = k
                except:
                    pass
            metadata['ImportFormat'] = d.get(p.meta.sensor_type, "")
        try:
            metadata.update(ScipyProfile.getMetaFromCoord(coordinates.Coordinate(p.meta.latitude,  p.meta.longitude, )))
        except:
            pass
        metadata['filename'] = p.meta.original_path 
        metadata['timestamp'] = p.meta.utc_time
        #p.meta._institution = ''
        metadata['Survey'] = p.meta._survey
        metadata['Ship'] = p.meta._vessel
        metadata['Instrument'] = p.meta._sn 
        #p.meta.proc_time = datetime.datetime.now()
        #p.meta.proc_info = 'imported via Velocipy'
        #translate units
        #p.meta.pressure_uom = 'dbar'
        #p.meta.depth_uom = 'm'
        #p.meta.speed_uom = 'm/s'
        #p.meta.temperature_uom = 'deg C'
        #p.meta.conductivity_uom = ''
        #p.meta.salinity_uom = ''
        #convert profile data 
        p.data.num_samples = len(self)
        col_types=[]
        prof_data = []
        for data, name in ((p.data.pressure, 'pressure'),(p.data.depth, 'depth')
                           (p.data.speed, 'soundspeed'),(p.data.temp, 'temperature'),
                           (p.data.sal, 'salinity'),(p.data.conductivity, 'conductivity')):
            if data != None:
                col_types.append((name, numpy.float32))
                prof_data.append(data)

        #return the finised profile
        prof_array = numpy.zeros(prof_data, dtype=col_types)
        p=ScipyProfile(prof_array, metadata = metadata)
        return p
        
    def ConvertToSoundSpeedProfile(self):
        import hydroffice.soundspeed.profile
        from hydroffice.soundspeed.profile import dicts
        p = hydroffice.soundspeed.profile.profile.Profile()
        #translate metadata
        p.meta.sensor_type = dicts.Dicts.sensor_types.get(self.metadata.get('ImportFormat',''), dicts.Dicts.sensor_types['Unknown'])
        p.meta.probe_type = dicts.Dicts.probe_types.get(self.metadata.get('ImportFormat',''), dicts.Dicts.probe_types['Unknown'])

        try:
            p.meta.latitude = coordinates.LatStrToDec(self.metadata['Latitude'], assume_S=False)
            p.meta.longitude = coordinates.LonStrToDec(self.metadata['Longitude'], assume_W=False)
        except:
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
        #translate units
        p.meta.pressure_uom = 'dbar'
        p.meta.depth_uom = 'm'
        p.meta.speed_uom = 'm/s'
        p.meta.temperature_uom = 'deg C'
        p.meta.conductivity_uom = str()
        p.meta.salinity_uom = 'PSU'
        #convert profile data
        p.init_data(len(self)) 
        try:
            p.data.pressure = self['pressure']
        except ValueError: #no matching data column
            pass
        try:
            p.data.depth = self['depth']
        except ValueError: #no matching data column
            pass
        try:
            p.data.speed = self['soundspeed']
        except ValueError: #no matching data column
            pass
        try:
            p.data.temp = self['temperature']
        except ValueError: #no matching data column
            pass
        try:
            p.data.sal = self['salinity']
        except ValueError: #no matching data column
            pass
        try:
            p.data.conductivity = self['conductivity']
        except ValueError: #no matching data column
            pass
        #return the finised profile
        return p
        
    @staticmethod
    def parseProfile(filename, **opts):
        '''Parses the file and performs QC functions as appropriate per file format
        filename -- the cast profile to read and return
        optional kwargs:
        bin -- if the datafile type uses binning then this paramter can specify the bin size (default 0.1)
        upcast -- for seacat, uses the upcast QC routine rather than downcast
        '''
        extension = filename.split('.')[-1].lower()
        q = ScipyProfile.parseRawProfile(filename, bDigiDowncast=opts.get("bDigiDowncast", False))
        bRunStatCheck=True
        binsz = opts.get("bin", 0.1)
        for i, p in enumerate(q):
            if extension in ('calc', 'raw'): # Processed file from the MVP 100 (based on FA's and TJ files)
                p = p.QC(bin=(p.dtype.names, binsz))
            elif extension == 'svp': #SVP extension -- may be one of multiple formats
                if isinstance(p, list): #Caris SVP multi section file
                    q=[] #QC each cast and replace the list of profiles
                    for _p in p:
                        q.append(_p.QC())
                    p=q
                else: 
                    p = p.QC()
            elif re.match('^(nc|[zfnrt].[ad])$', extension):
                # For NODC netCDF4 files (nc, zzd, zza, n5d, n5a, raa, rad, ...)
                # these profiles are already QC'd
                bRunStatCheck=False
            elif extension in('zzd', 'ssp', 'txt'): #FIXME: who is this?
                p = p.QC()
            elif extension =='csv':
                first_line = ''
                with open(filename, 'r') as f:
                    first_line = f.readline()
                if first_line.startswith('% Device'): #For CastAway csv file
                    p = p.QC()
                else: #For Digibar csv file
                    p = p.QC(bin=(['depth', 'soundspeed', 'temperature'], 0.1)) #this type had date/time also, could change to ordinal date and seconds if we wanted to average them
            elif extension =='edf':
                p = p.QC(bin=(p.dtype.names, binsz))
            elif extension == 'asvp':
                p = p.QC(bin=(p.dtype.names, binsz))
            #Now we've checked the full extensions -- start checking the last letters
            elif extension == 'hex' or extension[-2:] == 'nv' or extension == 'asc': # Seabird CNV file
                p = p.QC(bin=(p.dtype.names, binsz))
# Removed the old conversion and QC routines.                
#                 if set(['pressure', 'salinity', 'density', 'soundspeed']).issubset(set(p.dtype.names)):
#                     p = ReadAndQC_CNV(p, upcast=opts.get("upcast", False), VelocDialogs=opts.get("VelocDialogs", None))#do special CNV processing here...
#                     #p = p.QC(bin=(p.dtype.names, 0.1))
#                     path, fname = os.path.split(filename)
#                     p.metadata['Filename']=fname
#                     p.metadata['Path'] = path
#                     if 'flag' not in p.dtype.names:
#                         p = p.append_field('flag', numpy.zeros(p.shape, numpy.int8), numpy.int8)
#                 else:
#                     if wx.YES == wx.MessageBox("The Seabird data does not have all the expected fields [density, salinity, pressure, soundspeed].\n Do you want to import anyway?",
#                           "Possibly incomplete data", wx.ICON_QUESTION | wx.YES | wx.NO | wx.CENTER, None):
#                         p = p.QC(bin=(p.dtype.names, binsz))
#                     else:
#                         raise Exception("User chose to stop import on incomplete hex/cnv file.")
                
            elif extension[-1] == 'c': # Processed file from the MVP 100 (based on FA's files)
                p = p.QC(bin=(p.dtype.names, binsz))
            elif extension[-1] in ( 'q','b','a'): #edited/unedited VelocWin file
                #these velocwin/velocipy profiles are already QC'd before writing.
                #p = p.QC()
                bRunStatCheck=False
            elif 'xbt' in filename.lower():
                p = p.QC(bin=(p.dtype.names, binsz))

            if 'flag' not in p.dtype.names: #this shouldn't happen -- flags should be retained from above
                p = p.append_field('flag', numpy.zeros(p.shape, numpy.int8), numpy.int8)
            if bRunStatCheck and 'soundspeed' in p.dtype.names and 'depth' in p.dtype.names and len(p)>3:
                p.StatisticalFlagEdit() #flags data with FLAG_BAD if it fails a standard deviation check.

            q[i] = p #set the list object with whatever modifications we made on the data

        return q

    @staticmethod
    def parseRawProfile(filename, **opts):
        '''Pass in a file and figure out what type of data it is and return a ScipyProfile
        '''
        extension = filename.split('.')[-1].lower()
        if extension == 'calc': # Processed file from the MVP 100 (based on FA's files)
            p = Profile.parseCALCFile(filename)
        elif extension == 'raw': # Processed file from the MVP 100 (based on FA's files)
            p = Profile.parseRAWMVPFile(filename)
        elif re.match('^(nc|[zfnrt].[ad])$', extension):
            # For NODC netCDF4 files (nc, zzd, zza, n5d, n5a, raa, rad, ...)
            p = Profile.parseNODCFile(filename)            
        elif extension == 'zzd': #FIXME: who is this? The ZZD file should be the older version NODC file
            p = Profile.parseZZDFile(filename)
        elif extension == 'svp': #SVP extension -- may be one of multiple formats
            p = Profile.parseSVPFile(filename)
        elif extension =='csv':
            first_line = ''
            with open(filename, 'r') as f:
                first_line = f.readline()
            if first_line.startswith('% Device'): #For CastAway csv file
                p = Profile.parseCastAwayCSV(filename)
            else: #For Digibar csv file
                p = Profile.parseDigiCSV(filename, bDigiDowncast=opts.get("bDigiDowncast", False))
        elif extension =='edf':
            try:
                p1 = Profile.parseSippicanXSV(filename) #the edf exports can be either XBT or XSV, see what we find more of --
            except:
                p1=numpy.zeros([0])
            try: 
                p2 = Profile.parseSippicanXBT(filename) # these files are prone to bad data that might get picked up as the other format
            except:
                p2 = numpy.zeros([0])
            if len(p1)==0 and len(p2)==0: raise Exception("Failed to read points from XBT or XSV format")
            p = p1 if len(p1)>len(p2) else p2 #return the longest dataset
        elif extension == 'asvp':
            p = Profile.parseASVPFile(filename)
        elif extension == 'ssp' or re.match("[sS]\d\d", extension):
            p = Profile.parseSSPFile(filename)
        elif extension == 'hex':
            filename = Seacat.ConvertHexFile(filename)
            if filename:
                p = Profile.parseCNVFile(filename)
            else:
                raise Exception("Hex file didn't convert")
        elif extension =='txt':
            p = Profile.parseGenericText(filename)
        #Now we've checked the full extensions -- start checking the last letters
        elif extension[-2:] == 'nv': # Seabird CNV file
            p = Profile.parseCNVFile(filename) 
        elif extension == 'asc':
            p = Profile.parseOceanScienceASC(filename)
        elif extension[-1] == 'c': # Processed file from the MVP 100 (based on FA's files)
            p = Profile.parseCALCFile(filename)
        elif extension == 'vpa' or extension[-1] == 'a': #Velocwin Archive with Pressure/Temp/Salinity profiles
            p = Profile.parseVelocwinNODCFile(filename)
        elif 'xbt' in filename.lower():
            p = Profile.parseSippicanXBT(filename)
        else:
            raise NotImplementedError("Unsupported data extension '%s'" % extension)
        path, fname = os.path.split(filename)
        if isinstance(p, tuple):
            q=list(p)
        if isinstance(p, list):
            q=p
        else: q=[p]
        for i, p in enumerate(q):
            p.metadata['Filename']=fname
            if len(q)>1: p.metadata['Filename']+="_prof_%d"%i
            p.metadata['Path'] = path
            if 'flag' not in p.dtype.names:
                q[i] = p = p.append_field('flag', numpy.zeros(p.shape, numpy.int8), numpy.int8) #remember to replace the data in the list and the local name "p"
        return q

    @staticmethod
    def parseCNVFile(filename):
        s = open(filename).read()
        meta = ScipyProfile.parseCNVMetadata(filename)
        meta['filename'] = filename
        col_types = []
        col_names = []
        for col in  meta['columns']: #get a list of the columns in the CNV file
            col_name = col[2].lower().replace('sound', 'soundspeed')
            try:
                if col_name[0].isdigit():
                    col_name="N_"+col_name
            except IndexError:
                col_name = col[1]
            col_names.append(col_name) 
        for col in  meta['columns']: #check for and change any duplicates
            col_name = col[2].lower().replace('sound', 'soundspeed')
            try:
                if col_name[0].isdigit():
                    col_name="N_"+col_name
            except IndexError:
                col_name = col[1]
            #see if there are duplicate names.  First try getting a second word from the column description and then add underscores if there is still duplication
            names_so_far = [coltype[0] for coltype in col_types]
            if col_name in names_so_far:
                col_name = col_name+"_"+re.search("\w+", col[3]).group().lower() #col[3].lower().replace(",", "").replace(" ", "_").replace("[", "").replace("]", "")
            while col_name in names_so_far:
                col_name=col_name+"_" 
            col_types.append((col_name, numpy.float32))
        d = parseNumbers(filename, 
                         col_types, 
                         r"\s+", pre=r'^\s*', post=r'\s*$')
        p=ScipyProfile(d, ymetric="depth", attribute="soundspeed", metadata = meta)
        return p
    @staticmethod
    def parseCNVMetadata(filename):
        s = open(filename).read()
        header, data = s.split('*END*')
        meta={}
        if sbe_constants.SeacatHex_SBE19PLUS_TYPERE.search(header):
            seacat_type = 'SBE19PLUS'
        elif sbe_constants.SeacatHex_SBE19_TYPERE.search(header):
            seacat_type = 'SBE19'
        elif sbe_constants.SeacatHex_SBE911_TYPERE.search(header):
            seacat_type = 'SBE911'
        elif sbe_constants.SeacatHex_SBE49_TYPERE.search(header):
            seacat_type = 'SBE49'
        else:
            seacat_type = ''
        if seacat_type:
            # Parsing lines like--  # name 0 = prDM: Pressure, Digiquartz [db]
            expr = r'''\#\s*name\s*       #lead pound sign, name
                        (?P<num>\d+)      #column number
                        \s*=\s*(?P<rawname>[^:]*):\s*  #spaces, equals and stuff up to the colon
                        (?P<col>\w*)      #the column name (Pressure, Conductivity, Temperature, Salinity, Density, Sound Velocity (we only get Sound as we don't allow spaces currently)
                        (?P<units>.*)     #The rest of the data -- units are embedded here if we want them later
                        '''
            matches = re.findall(expr, s, re.VERBOSE)
            for i, col in enumerate(matches):
                if int(col[0]) != i:
                    raise Exception('Not all column names read correctly, can not parse file') 
            for tag, metaname in (("CRUISE:", 'Project'), ("STATION:", 'Survey')):
                m = re.search(tag+"(.*)", header, re.IGNORECASE)
                if m:
                    meta[metaname] = m.group(1).strip()
            
            meta['columns'] = matches
            try: 
                if seacat_type == "SBE19PLUS":
                    m=sbe_constants.SEACAT_SBE19PLUS_HEX_DATE_TXTRE.search(header)
                    if m:
                        yr, mon, day = time.strptime(m.group('full'), sbe_constants.SEACAT_SBE19PLUS_HEX_DATE_TXT_FORMAT)[:3]
                    else:
                        m = sbe_constants.SEACAT_SBE19PLUS_HEX_DATE_MDYRE.search(header)
                        yr = int(m.group('year'))
                        mon = int(m.group('month'))
                        day = int(m.group('day'))
                    m=sbe_constants.SEACAT_SBE19PLUS_HEX_TIMERE.search(header) #@UndefinedVariable
                    hour, minute = int(m.group('hour')), int(m.group('minute'))
                elif seacat_type == "SBE19":
                    try: #For the SBE19s the start_time is not always cast time but can be the download time for some firmware revisions.
                        yr = int(sbe_constants.SEACAT_SBE19_HEX_YEARRE.search(header).group('year'))
                        if yr<80: yr+=2000
                        if yr<100: yr+=1900
                        m1 = sbe_constants.SEACAT_SBE19_HEX_MONTHDAYRE.search(header)
                        m2=sbe_constants.SEACAT_SBE19_HEX_TIMERE.search(header)
                    except: 
                        m1=m2=None #look for the start_time instead, the year must have failed.
                    if m1 and m2:
                        mon, day = int(m1.group('month')), int(m1.group('day'))
                        hour, minute = int(m2.group('hour')), int(m2.group('minute'))
                    else:
                        dt_match = sbe_constants.SEACAT_CNV_START_TIMERE.search(header)
                        dt = datetime.datetime(1,1,1).strptime(dt_match.group('full'), '%b %d %Y %H:%M:%S')
                        yr, mon, day = dt.year, dt.month, dt.day
                        hour, minute = dt.hour, dt.minute
                elif seacat_type in ('SBE911', 'SBE49'):
                    #* System UpLoad Time = Sep 08 2008 14:18:19
                    m=sbe_constants.SEACAT_SBE911_HEX_DATETIMERE.search(header)
                    dt = datetime.datetime(1,1,1).strptime(m.group('full'), '%b %d %Y %H:%M:%S')
                    yr, mon, day = dt.year, dt.month, dt.day
                    hour, minute = dt.hour, dt.minute
            except: #bail out and look for the "start time" message that the Seabird Data processing program makes in the CNV file -- This is the download time from the SBE instrument   
                dt_match = sbe_constants.SEACAT_CNV_START_TIMERE.search(header)
                if dt_match:
                    dt = datetime.datetime(1,1,1).strptime(dt_match.group('full'), '%b %d %Y %H:%M:%S')
                    yr, mon, day = dt.year, dt.month, dt.day
                    hour, minute = dt.hour, dt.minute

            meta['timestamp'] = datetime.datetime(yr, mon, day, hour, minute)
            meta['Time'] = "%02d:%02d" % (hour, minute)
            meta['Year'] = '%4d' % yr
            meta['Day'] = '%03d' % Tools.DayOfYear(mon, day, yr)
            lat_m = sbe_constants.SEACAT_HEX_LATRE.search(header)
            if lat_m:
                lon_m = sbe_constants.SEACAT_HEX_LONRE.search(header)
                if lon_m:
                    coord = coordinates.Coordinate(lat_m.group('lat'), lon_m.group('lon'))
                    if coord:
                        meta.update(ScipyProfile.getMetaFromCoord(coord))  # blank Latitude/Longitude will return a None coord
            m = sbe_constants.SeacatHex_SNRE.search(header)
            if m:
                meta['SerialNum'] = m.group('SN')
                meta['Instrument'] = seacat_type+' (SN:'+m.group('SN')+')'
            meta['samplerate'] = sbe_constants.SeacatCNV_INTERVALRE.search(header).group('interval')
            meta['ImportFormat'] = 'CNV'
            return meta

    @staticmethod
    def parseSVPFile(filename):
        # UNV/OMB svp file
        if ScipyProfile.isOmgSvpFile(filename):
            return ScipyProfile.parseOmgSvpFile(filename)

        # Caris concatenated SVP file
        elif ScipyProfile.isCarisSvpFile(filename):
            return ScipyProfile.parseCarisSvpFile(filename)

    @staticmethod
    def parseZZDFile(filename):
        s = open(filename).read()
        hdr, data = s.split('M/S')
        depth, speed, flag = [], [], []
        for line in data.splitlines():
            try:
                d, s = line.split()
            except ValueError:
                continue
            depth.append(float(d))
            speed.append(float(s))
            flag.append(0)
        hdr += 'M/S'
        metadata = {}  # FIXME: write the metadata parser for zzd
        metadata['filename'] = filename
        metadata['ImportFormat'] = 'ZZD'
        a = array([depth, speed]).transpose()
        return ScipyProfile(a, ymetric="depth", attribute="soundspeed", metadata=metadata)

    @staticmethod
    def parseCarisSvpFile(filename):
        ''' Return a list of profiles for Caris' multi profile format'''
        s = open(filename).read()
        rv = []

        lines = s.splitlines()
        version_string, filename, rest = lines[0], lines[1], lines[2:]

        sections = '\n'.join(rest).split('Section ')
        for section in sections:
            metadata = None
            depths, speeds = [], []

            for line in section.splitlines():
                if not metadata:  # This will be the case on the first of every line
                    metadata = ScipyProfile.parseSVPMetadata(line, filename=filename, version_string=version_string)
                    metadata['filename'] = filename
                else:
                    try:
                        d, s = line.split()
                    except ValueError:
                        continue
                    depths.append(float(d))
                    speeds.append(float(s))
            if len(depths) > 0:
                p = ScipyProfile([depths, speeds], names=('depth', 'soundspeed'), ymetric="depth", attribute="soundspeed", metadata=metadata)
                rv.append(p)
        return rv

    @staticmethod
    def parseOceanScienceMetadata(s):
        '''For old data columns were not listed in the header and had a fixed format.  Okeanos Explorer downloaded a new
        driver which changed the format.  It now lists fields in the header and since I don't know if they are user configurable
        will load them dynamically similar to the Seacat data
        '''
        meta = {}
        # lines = filedata.splitlines()[1:] #skip the header which is bad (is the download date or process date?)
        latm = re.search(r'/*\*Lat (?P<lat>[\d/]+)', s)
        lonm = re.search(r'/*\*Lon (?P<lon>[\d/]+)', s)

        try:
            location = coordinates.Coordinate(latm.group('lat'), lonm.group('lon'))
            location.lon = -location.lon  # force to West since it doesn't specify east/west in it's sample
            meta.update(ScipyProfile.getMetaFromCoord(location))
        except:
            pass  # newer format? -- or lat/lon is blank

        mDT = re.search(r'/*\*DeviceType=\s*(?P<TYPE>\w+)', s)
        mSN = re.search(r'/*\*SerialNumber=\s*(?P<SN>\w+)', s)
        if mSN and mDT:
            meta['SerialNum'] = mSN.group('SN')
            meta['Instrument'] = mDT.group('TYPE') + ' (SN:'+mSN.group('SN')+')'
        else:
            meta['Instrument']="Unknown"  # new format isn't necessarily filling out serial number

        m = re.search(r'''Cast\s+\d+\s+(?P<DATE>\d+\s+\w+\s+\d+\s+\d+:\d+:\d+)''', s, re.VERBOSE|re.DOTALL)
        if m: 
            #grab the date from the cast metadata and convert to datetime object
            dt = datetime.datetime.strptime(m.group('DATE'), "%d %b %Y %H:%M:%S")
            #turn the datetime into a string
            tm=dt.strftime("%Y %m %d %H %M")
            #turn the string into a regex grouping/match object to pass into the standard date handler
            m=re.search("(?P<yr>\d+)\s+(?P<mon>\d+)\s+(?P<day>\d+)\s+(?P<hour>\d+)\s+(?P<minute>\d+)", tm)
            #update the profile metadata with the interpreted time data 
            meta.update( ScipyProfile.getMetaFromTimeRE(m))
        return meta

    @staticmethod
    def parseOceanScienceASC(filename):
        '''OceanScience format from Nancy Foster example data.
        metadata lines start with an asterisk.

        *scan# C[S/m]  T[degC]  P[dbar]
        1  0.00000 20.948    0.031
        2  0.00000 20.952    0.031
        3  0.00000 20.958    0.031
        '''

        s = open(filename).read()
        meta = ScipyProfile.parseOceanScienceMetadata(s)
        meta['filename'] = filename

        profile_data = parseNumbers(filename, 
                         [('index', numpy.int32), ('conductivity', numpy.float32), ('temperature',numpy.float32), ('pressure', numpy.float32)], 
                         r"[\s,]+", pre=r'^\s*', post=r'\s*$')
        profile_data = numpy.compress(profile_data['temperature']>=0.0, profile_data) #remove temperatures that make SV equation fail (t<0)
        profile_data = numpy.compress(profile_data['conductivity']>=0.0, profile_data) #remove temperatures that make SV equation fail (t<0)
        #clear some of the surface noise when first entering water
        profile_data = numpy.compress(profile_data['pressure']>=0.2, profile_data) #remove temperatures that make SV equation fail (t<0)
        #lat = cnv_data.metadata['location'].lat
        p=ScipyProfile(profile_data, ymetric="depth", attribute="soundspeed", metadata = meta)

        if 'salinity' not in p.dtype.names:
            p=p.append_field('salinity',0.0)
        p['salinity'] = velocipy_equations.SalinityFromConductivity(p['conductivity'], p['temperature'], p['pressure'])

        if 'density' not in p.dtype.names:
            p=p.append_field('density',0.0)
        p['density'] = velocipy_equations.DensityFromTSP(p['temperature'], p['salinity'], p['pressure'])
        

        try:
            p=p.ComputeSV()
        except DataFileError,e:
            print e
        
        return p


    @staticmethod
    def parseSippicanXBT(filename):
        '''Note that this format only has measured depth/temp and uses an assumed salinity.  
        In VelocWin predecessor the salinity is thrown out and soundspeed recomputed based on a user supplied salinity.
        This will return all fields and it is up to the caller to determine if SV should be recomputed.
        
        NOTE: from World Ocean Atlas 2005 about XBT, XSV depth rate errors
        The correction for XBT T4, T6, and T7 drop-rate error (Hanawa et al., 1994) is:
        zc = 1.0417 z0 - 75.906x(1-(102.063 x 10-4 z0)^0.5)
        in which z0 is the originally calculated depth.
        In addition to XBT depth corrections, Johnson (1995) has shown the necessity of depth correction
        for Sippican XCTDs, while Mizuno and Watanabe (1998) give depth corrections for TSK XCTDs. 
        Both corrections follow the same procedure as for XBTs.
        
        OLD FORMAT
// This is a MK21 EXPORT DATA FILE  (EDF)
//
Date of Launch:  03/21/2013
Time of Launch:  19:01:17
Sequence #    :  5
Latitude      :  39 47.75146N
Longitude     :  69 33.53027W
Serial #      :  00000000
Ship::  NOAAS OKEANOS EXPLORER
Cruise::  EX1301
Station::  0
//
// Here are the contents of the memo fields.
//
//
// Here is some probe information for this drop.
//
Probe Type       :  Deep Blue
Terminal Depth   :  760 m
Depth Equation   :  Standard
Depth Coeff. 1   :  0.0
Depth Coeff. 2   :  6.691
Depth Coeff. 3   :  -0.00225
Depth Coeff. 4   :  0.0
Pressure Pt Correction:  100.0%
//
Raw Data Filename:  D:\2013_PROFILE_DATA\EX1301\XBT\TD_00005.RDF
//
Display Units    :  Metric
//
// This XBT export file has not been noise reduced or averaged.
//
// Sound velocity derived with assumed salinity: 34.50 ppt
//
Depth (m) - Temperature (C) - Sound Velocity (m/s)
0.0    12.17    1496.81
0.7    11.34    1493.97
1.3    11.16    1493.34
2.0    11.12    1493.23
2.7    11.12    1493.24
3.3    11.12    1493.24
4.0    11.12    1493.23
4.7    11.12    1493.24
                
NEW FORMAT                
// MK21 EXPORT DATA FILE  (EDF)
// File Information
Raw Data Filename:  D:\2013_Profile_Data\EX1301\XBT\TD_00005.RDF
// System Information
Units            :  Metric
// Probe Information
Probe Type       :  Deep Blue
Terminal Depth   :  760 m
Depth Equation   :  Standard
Depth Coeff. 1   :  0.0
Depth Coeff. 2   :  6.691
Depth Coeff. 3   :  -0.00225
Depth Coeff. 4   :  0.0
// Launch Information
Num Info Fields  :  6
Date of Launch   :  03/27/2013
Time of Launch   :  04:59:03
Sequence Number  :  5
Latitude         :  
Longitude        :  
Serial Number    :  
// Memo
// Hardware
MK21 Device      :  MK21/USB DAQ
// Information - XBT
Salinity          :  33.86 ppt
// Post-Processing
Operations       :  None
// Data Fields
Num Data Fields   :  5
Field1            :  Time (sec)
Field2            :  Resistance (ohms)
Field3            :  Depth (m)
Field4            :  Temperature (C)
Field5            :  Sound Velocity (m/s)
// Data
0.0    10843.996    0.00    8.22    1481.87
0.1    11228.227    0.67    7.50    1479.16
0.2    11342.138    1.34    7.29    1478.38
0.3    11376.206    2.01    7.23    1478.15
0.4    11382.316    2.68    7.22    1478.12
0.5    11385.697    3.34    7.21    1478.11
0.6    11384.429    4.01    7.22    1478.13
0.7    11383.240    4.68    7.22    1478.15
0.8    11382.539    5.35    7.22    1478.16
0.9    11381.910    6.02    7.22    1478.18
1.0    11382.581    6.69    7.22    1478.19
1.1    11381.654    7.36    7.22    1478.20
1.2    11380.834    8.03    7.22    1478.22
1.3    11381.446    8.69    7.22    1478.23
1.4    11381.598    9.36    7.22    1478.24
1.5    11379.907    10.03    7.23    1478.26
1.6    11376.440    10.70    7.23    1478.29
1.7    11373.672    11.37    7.24    1478.33
                
        '''
        s = open(filename).read()
        meta = ScipyProfile.parseSippicanMetadata(s)
        meta['filename'] = filename
        meta['ImportFormat'] = 'XBT'
        if meta['columns']:
            col_types = []
            col_names=[]
            for col in  meta['columns']: #get a list of the columns in the CNV file
                col_name = col[1].lower().replace('sound', 'soundspeed')
                col_names.append(col_name) 
            for col in  meta['columns']: #check for and change any duplicates
                col_name = col[1].lower().replace('sound', 'soundspeed')
                if col_names.count(col_name)>1:
                    col_name = col_name+"_"+re.search("\w+", col[2]).group().lower() #col[2].lower().replace(",", "").replace(" ", "_").replace("[", "").replace("]", "")
                col_types.append((col_name, numpy.float32))
            d = parseNumbers(filename, 
                             col_types, 
                             r"\s+", pre=r'^\s*', post=r'\s*$')
        else:
            
            d = parseNumbers(filename, 
                             [('depth', numpy.float32), ('temperature', numpy.float32), ('soundspeed',numpy.float32)], 
                             r"(,|\s+)", pre=r'^', post=r'[*\s]*$')
        d = numpy.compress(d['temperature']>=0.0, d) #remove temperatures that make SV equation fail (t<0)
        p=ScipyProfile(d, ymetric="depth", attribute="soundspeed", metadata = meta)
        p=p.append_field('salinity', 34.0) #default salinity to 34, hopefully gets replaced below and later by the user/other CTD
        p=p.append_field('xbt_soundspeed', p['soundspeed'])
        if p.metadata.get('assumed salinity',''): p['salinity']=float(p.metadata['assumed salinity'])
        try:
            p=p.ComputeSV()
        except DataFileError,e:
            print e
        return p
    def ComputeSV(self, eq=velocipy_equations.ChenMillero):
        '''Compute/create a soundspeed value.  The eq. used should take T,S,P (temperature, salinity, pressure) values, in that order.
        pressure will be calculated from depth using the metadata lat/lon coordinate if necessary and available.
        Returns new profile instance
        '''
        p=self.mcopy()
        try: pressures=p['pressure']
        except ValueError: #missing pressure -- hope we have depth and lat
            #compute from depth
            try:
                lat = self.metadata['location'].lat
                depths=p['depth']
            except:
                raise DataFileError("No enough data (no pressure or depth with latitude) to compute SoundSpeed")
            pressures = velocipy_equations.DepthToPressure(depths, lat)
        if 'soundspeed' not in p.dtype.names:
            p=p.append_field('soundspeed',0.0)
        p['soundspeed'] = eq(p['temperature'], p['salinity'], pressures)
        return p
    @staticmethod
    def parseSippicanXSV(filename):
        '''
        '// This is a MK21 EXPORT DATA FILE  (EDF)
        '//
        'Date of Launch:  09/12/2008
        'Time of Launch:  19:48:24
        'Sequence #    :  8
        'Latitude      :  47 49.732N
        'Longitude     :  125 56.617W
        'Serial #      :  00000000
        'Ship::  NOAAS OKEANOS EXPLORER
        'Cruise::  Mapping Shakedown
        'Station::  4
        '//
        '// Here are the contents of the memo fields.
        '//
        'Offshore reference surface
        '//
        '// Here is some probe information for this drop.
        '//
        'Probe Type       :  XSV-02
        'Terminal Depth   :  2000 m
        'DEPTH Equation:     Standard
        'Depth Coeff. 1   :  0.0
        'Depth Coeff. 2   :  5.5895
        'Depth Coeff. 3   :  -0.001476
        'Depth Coeff. 4   :  0.0
        'Pressure Pt Correction:  100.0%
        '//
        'Raw Data Filename:  D:\2008 Cruise Data\EX0801_MapShakedown_Leg I\Profile Data\XBT\RAW\S2_00008.RDF
        '//
        'Display Units:      Metric
        '//
        '// This XSV export file has not been noise reduced or averaged.
        '//
        'Depth (m) - Sound Velocity (m/s)
        '0.0 1445.77
        '0.6 1472.83
        '1.1 1487.53
        '1.7 1486.76
        '2.2 1486.61
        '''
        s = open(filename).read()
        meta = ScipyProfile.parseSippicanMetadata(s)
        meta['filename'] = filename
        meta['ImportFormat'] = 'XSV'
        #numbers=[('soundspeed',numpy.float32), ('depth', numpy.float32), ('temperature', numpy.float32)]
        #rstr = r"(,|\s+)".join([sbe_constants.named_re_number%n[0] for n in numbers])
        #pre=r'^\s*[\'"]?(?P<date>\d+/\d+/\d+)[\'"]?,[\'"]?(?P<time>\d+:\d+:\d+)[\'"]?,'
        #post = ''
        #expr = re.compile(pre+rstr+post)
        #d = parseFile(filename, 
        #              [('date', 'S8'), ('time', 'S8'), ]+numbers, 
        #              expr)
        d = parseNumbers(filename, [('depth', numpy.float32), ('soundspeed',numpy.float32)], r'\s*', r'^', r'\s*$')
        if len(d)>0:
            if d['soundspeed'].min()>1400*sbe_constants.METERS2FEET():
                d['soundspeed']*=sbe_constants.FEET2METERS()
                d['depth']*=sbe_constants.FEET2METERS()
        p=ScipyProfile(d, ymetric="depth", attribute="soundspeed", metadata = meta)
        return p
    @staticmethod
    def parseSippicanMetadata(s):
        '''For old data columns were not listed in the header and had a fixed format.  Okeanos Explorer downloaded a new
        driver which changed the format.  It now lists fields in the header and since I don't know if they are user configurable
        will load them dynamically similar to the Seacat data
        '''
        meta={}
        #lines = filedata.splitlines()[1:] #skip the header which is bad (is the download date or process date?)
        latm = re.search(r'/*Latitude\s*:\s*(?P<lat>[\d .NSEW]+)', s)
        lonm = re.search(r'/*Longitude\s*:\s*(?P<lon>[\d .NSEW]+)', s)
        sal = re.search(r'assumed salinity:\s*(?P<salinity>\d+[.]?\d*)\s*ppt', s)
        if sal:
            meta['assumed salinity']=sal.group('salinity')
        else:
            "Salinity          :  33.86 ppt"
            sal = re.search(r'Salinity\s*:\s*(?P<salinity>\d+[.]?\d*)\s*ppt', s)
            if sal:
                meta['assumed salinity']=sal.group('salinity')
            
        #sippican lat/lon don't pad the zeros so can get caught in the coordinate parser
        #location = coordinates.Coordinate(coordinates.LatStrToDec(latm.group('lat')), coordinates.LonStrToDec(lonm.group('lon')))
        try:
            location = coordinates.Coordinate(latm.group('lat'), lonm.group('lon'))
            meta.update(ScipyProfile.getMetaFromCoord(location))
        except:
            pass #newer format? -- or lat/lon is blank
        try:
            # Parsing lines like--  # name 0 = prDM: Pressure, Digiquartz [db]
            expr = r'''\s*Field\s*       #lead pound sign, name
                        (?P<num>\d+)      #column number
                        \s*:\s*  #spaces up to the colon
                        (?P<col>\w*)      #the column name (Pressure, Conductivity, Temperature, Salinity, Density, Sound Velocity (we only get Sound as we don't allow spaces currently)
                        (?P<units>.*)     #The rest of the data -- units are embedded here if we want them later
                        '''
            matches = re.findall(expr, s, re.VERBOSE)
            for i, col in enumerate(matches):
                if int(col[0]) != i+1:
                    raise Exception('Not all column names read correctly, is this old format?') 
            
            meta['columns'] = matches
        except:
            pass
        
        m = re.search(r'''/*Date\sof\sLaunch\s*:\s*                      #find the Date tag
                          (?P<mon>\d+)/(?P<day>\d+)/(?P<yr>\d+)          #date
                          .*?                                             #skip everything up to the time tag
                          Time\sof\sLaunch\s*:\s*                        #Time tag
                          (?P<hour>\d+):(?P<minute>\d+):(?P<second>\d+)  #Time
                          ''', s, re.VERBOSE|re.DOTALL)
        meta.update( ScipyProfile.getMetaFromTimeRE(m))
        try:
            m = re.search(r'Serial\s#\s*:\s*(?P<id>\d*)', s)
            meta['Instrument'] = m.group('id')
        except:
            meta['Instrument']="Unknown" #new format isn't necessarily filling out serial number
        return meta
    
    @staticmethod
    def parseGenericText(filename):
        s = open(filename).read()
        metadata={}
        metadata['filename'] = filename
        metadata['ImportFormat'] = 'TXT'
        profile_data = parseNumbers(filename, [('depth', numpy.float32), ('soundspeed',numpy.float32)], 
                                    r"[\s,]+", pre=r'^\s*', post=r'\s*$')

        p = ScipyProfile(profile_data, ymetric="depth", attribute="soundspeed", metadata=metadata)
        return p
        
    @staticmethod
    def parseDigiCSV(filename, bDigiDowncast=False):
        '''
        ' The Digibar Pro output type is CSV.
        ' The file has one header record and is followed by comma delimited data records
        ' containing date, time, sound velocity, depth, temperature (not used).
        
        ' Version 8.73 Change how file is read in order to handle case of quote-inclosed
        ' date and time strings.   (instead of line input #, use input #)
        '''
        s = open(filename).read()
        meta = ScipyProfile.parseDigiCSVMetadata(s)
        meta['filename'] = filename
        numbers=[('soundspeed',numpy.float32), ('depth', numpy.float32), ('temperature', numpy.float32)]
        rstr = r"((\s*,\s*)|\s+)".join([sbe_constants.named_re_number%n[0] for n in numbers])
        pre=r'^\s*[\'"]?(?P<date>\d+/\d+/\d+)[\'"]?((\s*,\s*)|\s+)[\'"]?(?P<time>\d+:\d+:\d+)[\'"]?((\s*,\s*)|\s+)'
        post = ''
        expr = re.compile(pre+rstr+post)
        d = parseFile(filename, 
                      [('date', 'S8'), ('time', 'S8'), ]+numbers, 
                      expr)
        
        if d['soundspeed'].min()>1400*sbe_constants.METERS2FEET():
            d['soundspeed']*=sbe_constants.FEET2METERS()
            d['depth']*=sbe_constants.FEET2METERS()
        if bDigiDowncast:
            # When user choose "Downcast Only" option
            d = d[0:d['depth'].argmax()+1]
        p=ScipyProfile(d, ymetric="depth", attribute="soundspeed", metadata = meta)
        return p
    @staticmethod
    def parseDigiCSVMetadata(filedata):
        lines = filedata.splitlines()[1:] #skip the header which is bad (is the download date or process date?)
        
        meta={}
        for line in lines:
            m=re.search(r'(?P<mon>\d+)/(?P<day>\d+)/(?P<yr>\d+)((\s*,\s*)|\s+)(?P<hour>\d+):(?P<minute>\d+)', line)
            if m:
                meta.update( ScipyProfile.getMetaFromTimeRE(m))
                break
        meta['ImportFormat'] = 'CSV'
        return meta

    @staticmethod
    def parseCastAwayCSV(filename):
        '''
        ' The CastAway output type is CSV.
        ' The file has header records followed by comma delimited data records
        '''
        s = open(filename).read()
        meta = ScipyProfile.parseCastAwayCSVMetadata(s)
        meta['filename'] = filename
        numbers=[('pressure',numpy.float32), ('depth', numpy.float32), ('temperature', numpy.float32), ('conductivity', numpy.float32),
                 ('conductance',numpy.float32), ('salinity', numpy.float32), ('soundspeed', numpy.float32), ('density', numpy.float32)]
        rstr = r"((\s*,\s*)|\s+)".join([sbe_constants.named_re_number%n[0] for n in numbers])
        pre=r''
        post = ''
        expr = re.compile(pre+rstr+post)
        d = parseFile(filename, numbers, expr)
        
        if d['soundspeed'].min()>1400*sbe_constants.METERS2FEET():
            d['soundspeed']*=sbe_constants.FEET2METERS()
            d['depth']*=sbe_constants.FEET2METERS()
        p=ScipyProfile(d, ymetric="depth", attribute="soundspeed", metadata = meta)
        return p
    @staticmethod
    def parseCastAwayCSVMetadata(filedata):
        lines = filedata.splitlines()
        meta={}
        for line in lines:
            if line.startswith('% Cast time (UTC)'):
                meta['timestamp'] = datetime.datetime.strptime(line.split(',')[1].strip(), '%Y-%m-%d %H:%M:%S')
                meta['Time'] = meta['timestamp'].strftime('%H:%M')
                meta['Year'] = meta['timestamp'].strftime('%Y')
                meta['Day'] = meta['timestamp'].strftime('%j')
            elif line.startswith('% Start latitude'):
                lat = line.split(',')[1].strip()
            elif line.startswith('% Start longitude'):
                lon = line.split(',')[1].strip()
            elif line.startswith('% Device'):
                meta['Instrument'] = line.split(',')[1].strip()
            elif line.startswith('% Samples per second'):
                meta['samplerate'] = '%s samples per second' %line.split(',')[1].strip()
            elif line.startswith('Pressure'):
                break
        location = coordinates.Coordinate(lat, lon)
        meta.update(ScipyProfile.getMetaFromCoord(location))
        meta['ImportFormat'] = 'CastAway'
        return meta

    @staticmethod
    def parseHYCOM(lat, lon, stime, metadata):
        
        def hycom_data(lat, lon, stime):
            #rtn = [[0.0, 3.4589999999999996, 33.049], [2.0, 3.4619999999999997, 33.049], [4.0, 3.4540000000000006, 33.049], [6.0, 3.4549999999999983, 33.049], [8.0, 3.4570000000000007, 33.049], [10.0, 3.4589999999999996, 33.049], [12.0, 3.4619999999999997, 33.049], [15.0, 3.4669999999999987, 33.049], [20.0, 3.477999999999998, 33.049], [25.0, 3.4909999999999997, 33.048], [30.0, 3.4909999999999997, 33.048]]
            #return rtn, None
            scale_factor = 0.001
            add_offset = 20.0
            rtn = []
            hycom = 'http://ncss.hycom.org/thredds/ncss/grid/'
        
            if stime >= datetime.datetime(2014,4,7,0,0,0):
                stype = 'GLBu0.08/expt_91.1'
            elif stime >= datetime.datetime(2013,8,17,0,0,0):
                stype = 'GLBu0.08/expt_91.0'
            elif stime >= datetime.datetime(2012,5,13,0,0,0):
                stype = 'GLBu0.08/expt_90.9'
            elif stime >= datetime.datetime(1995,8,1,0,0,0):
                stype = 'GLBu0.08/expt_19.1'
            elif stime >= datetime.datetime(1992,10,2,0,0,0):
                stype = 'GLBu0.08/expt_19.0'
            else:
                print 'No data available before 1992-10-02\r'
                return None, None
        
            url = r'%s%s?var=water_temp,salinity&latitude=%s&longitude=%s&time=%s&accept=csv' %(hycom, stype, lat, lon, stime.strftime('%Y-%m-%dT%H:%M:%SZ'))
            try:
                csv_data = urllib2.urlopen(url).read()
            except:
                csv_data = 'Error HTTP request: %s' %url
            if not csv_data.startswith('date'):
                print '%s\r' %csv_data
                if stime.strftime('%Y-%m-%d') == datetime.datetime.today().strftime('%Y-%m-%d'):
                    url = r'%s%s?var=water_temp,salinity&latitude=%s&longitude=%s&accept=csv' %(hycom, stype, lat, lon)
                    try:
                        csv_data = urllib2.urlopen(url).read()
                    except:
                        csv_data = 'Error HTTP request2: %s' %url
                    if not csv_data.startswith('date'):
                        print '%s\r' %csv_data
                        return None, url
                else:
                    return None, url
        
            csv_data = csv_data.split('\n')
            for line in csv_data[1:]:
                line = line.split(',')
                if len(line) > 5 and line[-1] != '-30000.0':
                    depth = float(line[-3])
                    temperature = float(line[-2]) * scale_factor + add_offset
                    salinity = float(line[-1]) * scale_factor + add_offset
                    #print depth, temperature, salinity
                    if depth >=0 and temperature >=0 and temperature <=40 and salinity >=0 and salinity <=40:
                        rtn.append((depth, temperature, salinity))
            return rtn, url

        rtn, url = hycom_data(lat, lon, stime)
        dtype = [('depth',numpy.float32),('temperature',numpy.float32),('salinity',numpy.float32),('soundspeed',numpy.float32),('flag',numpy.float32)]
        if rtn is None:
            return None
        elif len(rtn) == 0:
            print 'Error empty HYCOM data %s\r' %url
            return None
        else:
            for i in range(len(rtn)):
                depth, temperature, salinity = rtn[i]
                soundspeed = velocipy_equations._ChenMillero(temperature, salinity, velocipy_equations.DepthToPressure(depth, lat))[0]
                rtn[i] = (depth, temperature, salinity, soundspeed, 0)
        p = ScipyProfile(numpy.array(rtn, dtype=numpy.dtype(dtype)), ymetric="depth", attribute="soundspeed", metadata=metadata)
        return p.QC()
    
    @staticmethod
    def parseSSPFile(filename):
        ''' From VB Code
        ' Version 8.78 This type of file not currently visible as choice on Main Menu.
        
        ' TBD Check this routine with an actual file from Brooke-Ocean software
        ' TBD Will the lat/lon be included ???  We'll code for either case.
        
        ' This subroutine reads a Brooke-Ocean MVP output .ssp file (Kongsberg Simrad SSP Format).
        ' This file consists of one header line followed by data records.  The fields in the header
        ' line are comma-separated and of fixed length.
        
        ' Optionally, there may an additional record containing latitude and longitude
        
        ' Note that the data fields for depth and sound velocity begin after
        ' the first 7 comma-separated items.
            
        ' Example of this type of file (without the latitude/longitude record):
        ' $AAS10,00000,0015,235959,13,04,1999,5.00,1510.00,,,,
        ' 10.00,1508.00,,,,
        ' 20.00,1505.00,,,,
        ' 50.00,1500.00,,,,
        ' 75.00,1497.00,,,,
        ' 100.00,1495.00,,,,
        ' 150.00,1497.00,,,,
        ' 200.00,1499.00,,,,
        ' 250.00,1501.00,,,,
        ' 300.00,1503.00,,,,
        ' 350.00,1505.00,,,,
        ' 400.00,1507.00,,,,
        ' 450.00,1509.00,,,,
        ' 500.00,1511.00,,,,
        ' 550.00,1512.00,,,,
        ' 900.00,1521.00,,,,
        ' \
        
        ' Simrad SSP format (See EM Series 1002 Operator Manual for details):
          
        ' Start ID,                                      $              item 1
        ' Talker ID                                      AA
        ' Datagram ID,                                   S10,
        ' Data Set ID,                                   xxxxx,         item 2
        ' Number of measurements,                        xxxx,          item 3
        ' UTC time of data acquisition,                  hhmmss,        item 4
        ' Day of data acquisition,                       xx,            item 5
        ' Month of data acquisition,                     xx,            item 6
        ' Year of data acquisition,                      xxxx,          item 7
        ' First good depth in m                          x.x,
        ' Corresponding Sound Velocity in m/s,           x.x,
        ' Skip temp, sal, absorption coeff fields        ,,,
        ' End of line                                    CRLF
        ' Then, repeat good depth, sv,,,,CRLF until all NPTS are listed.
        
        From the Simrad Datagrams docs:
        Data Description Format Length Valid range Note
        Start identifier = $ Always 24h 1  
        Talker identifier aa 2 Capital letters 
        Datagram identifier Always Sxx, 4 S00to S53 1,2
        Data set identifier xxxxx, 6 00000 to 65535 
        Number of measurements = N xxxx, 5 0001 to 9999 9
        UTC time of data acquisition hhmmss, 7 000000 to 235959 3
        Day of data acquisition xx, 3 00 to 31 3
        Month of data acquisition xx, 3 00 to 12 3
        Year of data acquisition xxxx, 5 0000 to 9999 3
        N entries of the next 5 fields  See note 4
         Depth in m fromwater level or
        Pressure in MPa
        x.x, 2  0 to 12000.00 0 to
        1.0000
        4
         Sound velocity in m/s x.x, 1  1400 to 1700.00 
         Temperature in _C x.x, 1  5 to 45.00 
         Salinity in parts per thousand or
        Conductivity in S/m
        x.x, 1  0 to 45.00 0 to 7.000 
        Absorption coefficient in dB/km x.x 0 0 to 200.00 5
        Data set delimiter CRLF 2 0Dh 0Ah 
        End of repeat cycle
        Latitude in degrees and minutes, plus
        optional decimal minutes
        llll.ll, Variable 5 0000 to 9000.0... 6
        Latitude  N/S a, 2 N or S 6
        Longitude in degrees and minutes, plus
        optional decimal minutes
        yyyyy.yy, Variable 6 00000 to 18000.0... 6
        Longitude  E/W a, 2 Eor W 6
        Atmospheric pressure in MPa x.x, 1 0 to 1.0000 6
        Frequency in Hz xxxxxx, Variable  7
        User given comments c c Variable  6
        Optional checksum *hh   8
        End of datagram delimiter = \CRLF 5Ch 0Dh 0Ah 3  

        Note:
        1 The datagram identifier identifies what type of data is
        included. This is shown in the following table where D is
        depth, P is pressure, S is salinity, C is conductivity, c is
        soundspeed, 'a' is absorption coefficient, f is frequency and
        L is latitude. The notation c(T,S) indicates for example that
        the soundspeed is to be calculated from the temperature and
        salinity input data. When pressure is used, the atmospheric
        pressure must be given if the pressure is absolute, otherwise
        the pressure must be given re the sea level and the
        atmospheric pressure must be zero.
        
        See top of module ssp_fmts_doc for format specifiers.
        '''
        s = open(filename).read()
        metadata = ScipyProfile.parseSSPMetadata(s)
        metadata['filename'] = filename
        #read any of the above formats
        profile_data = parseNumbers(filename, 
                         [(n, numpy.float32) for n in SSP_Formats[metadata['fmt']]], 
                         r"\s*,\s*", pre=r'^\s*', post=r'[,.\s\d]*$', ftype='SSP')
        p = ScipyProfile(profile_data, ymetric="depth", attribute="soundspeed", metadata=metadata)
        return p
        
    @staticmethod
    def getMetaFromTimeRE(m):
        '''Pass in a re.match object that has groups named yr, mon, day, hour, minute and this convienence function
        will create a metadata dictionary with the Year, Day, Time formated appropriately.
        You can then use metadata.update( ScipyProfile.getMetaFromTimeRE(m)) 
        to augment your existing meta or use the returned dict to start a new metadata dictionary. 
        '''
        meta = {}
        meta['Year'] = m.group('yr')
        if int(meta['Year'])<80: meta['Year']='20'+meta['Year'] #2000 - 2079
        elif int(meta['Year'])<100: meta['Year']='19'+meta['Year'] #1980 - 1999
        try:
            meta['Day'] = '%03d'%Tools.DayOfYear(m.group('mon'), m.group('day'), m.group('yr'))
        except:
            meta['Day'] = m.group('doy')
        meta['Time'] = m.group('hour')+':'+m.group('minute')
        meta['timestamp'] = datetime.datetime.strptime("%s %s %s" % (meta['Year'], meta['Day'], meta['Time']), "%Y %j %H:%M")
        return meta
    @staticmethod
    def parseMetaFromDatetime(dt):
        meta={}
        meta['Time'] = dt.strftime("%H:%M")
        meta['Year'] = dt.strftime("%Y")
        meta['Day'] = dt.strftime("%j")
        meta['timestamp'] = dt
        return meta
    @staticmethod
    def parseSSPMetadata(header):
        meta= {}
        lines = header.splitlines()
        m = re.search(r'''\$[A-Z][A-Z](?P<fmt>S\d\d),  #fmt is between 00 and 53
                      (?P<id>\d+),
                      (?P<nmeasure>\d+),
                      (?P<hour>\d\d)(?P<minute>\d\d)(?P<second>\d\d),
                      (?P<day>\d\d),
                      (?P<mon>\d\d),
                      (?P<yr>\d+),
                    ''', lines[0], re.VERBOSE) #ignoring the optional fields of first line
        if m:
            meta.update( ScipyProfile.getMetaFromTimeRE(m))
            meta['DataSetID'] = m.group('id')
            meta['Format'] = "SSP "+m.group('fmt')
            meta['fmt'] = m.group('fmt')
            m = re.search(r'''(?P<lat>[\d.]+,[NS]),
                              (?P<lon>[\d.]+,[EW]),
                            ''', lines[1], re.VERBOSE) #try the optional second line
            if not m:
                m = re.search(r'''(?P<lat>[\d.]+,[NS]),
                                  (?P<lon>[\d.]+,[EW]),
                                ''', lines[-1], re.VERBOSE) #try at the end of file
            if m: 
                location = coordinates.Coordinate(m.group('lat'), m.group('lon'))
                meta.update(ScipyProfile.getMetaFromCoord(location))
        return meta
    @staticmethod
    def getMetaFromCoord(coord): #pass a coordinates.Coordinate and make the metadata
        meta={}
        location = coord.copy()
        location.__class__ = coordinates.DMSCoordinate
        location.SetSep('/')
        meta['Latitude'] = str(location).split(', ')[0]
        meta['Longitude'] = str(location).split(', ')[1]
        meta['location'] = location
        return meta

    def updateLocationFromLatLon(self):
        try:
            lat = self.metadata['Latitude']
            lon =  self.metadata['Longitude']
        except KeyError, e:
            raise MetadataException(str(e)) 
        coord = coordinates.Coordinate(lat, lon)
        if coord: 
            self.metadata['location'] = coord
    def updateNameDate(self):
        self.metadata['Name_Date_SN'] = "CREATED ON " + self.metadata['ProcessDate'] + " BY " + self.metadata['UserName'].strip() 
    @staticmethod
    def parseASVPFile(filename):
        '''From VB Code 
        ' This subroutine reads a Brooke-Ocean MVP output .asvp file (Simrad ASCII soundspeed profile).
        ' This file consists of one header line containing 12 string variables followed by
        ' data records each containing depth in m and sound velocity in m/s.
        
        ' Short example of this type of file:
        '( SoundVelocity 1.00 00012 199205290813 22.3452678 66.4483298 4500 199205290813 199206151210 SVP-16 PE 6 )
        '5.0 1484.2
        '7.0 1485.3
        '12.0 1488.1
        '20.0 1485.7
        '25.0 1484.0
        '40.0 1483.8
        
        ' #      MVP asvp Header Line Item                        Example above
         
        ' 1      Sound Velocity (Identification of file type)     ( SoundVelocity
        ' 2      Version (File format version number)             1.00
        ' 3      Id (a possible identifier)                       00012
        ' 4      Date/Time (of creation for this file)            199205290813
        ' 5      Lat (Latitude of profile location,dec. deg.      22.3452678
        ' 6      Long (Longitude of profile loc. in dec. deg.)    66.4483298
        ' 7      Radius (in m, profile valid within circle)       4500
        ' 8      Valid_from (date/time)                           199205290813
        ' 9      Valid_to (date/time)                             199212312359
        ' 10     Src (probe name)                                 SVP-16
        ' 11     Hist (history of modifications)                  PE
        ' 12     No_val (number of values)                        6 )
        ' CRLF
               
        ' Data records:
        
        ' Depth in m                                       5.0
        ' Sound Velocity in m/s                            1484.2
        ' CRLF
        ' The last 3 items are repeated until all data points are listed.
        
        ' NOTE for the Hist item: P = probe, E = Edited, M = merged, N = new
        '''
        s = open(filename).read()
        metadata = ScipyProfile.parseASVPMetadata(s.splitlines()[0])
        metadata['filename'] = filename
        profile_data = parseNumbers(filename, [('depth', numpy.float32), ('soundspeed',numpy.float32)], 
                                    r"[\s,]+", pre=r'^\s*', post=r'\s*$')

        p = ScipyProfile(profile_data, ymetric="depth", attribute="soundspeed", metadata=metadata)
        return p
    @staticmethod
    def parseASVPMetadata(header):
        meta={}
        m= re.search(r'''[(\s]*(?P<filetype>\S*)\s+
                         (?P<version>[\d.]+)\s+
                         (?P<id>[\d.]+)\s+
                         (?P<yr>\d{4})(?P<mon>\d{2})(?P<day>\d{2})(?P<hour>\d{2})(?P<minute>\d{2})\s+
                         (?P<lat>%s)\s+
                         (?P<lon>%s)\s+ 
                         (?P<radius>[\d.]+)\s+
                         (?P<valid_from>[\d.]+)\s+
                         (?P<valid_to>[\d.]+)\s+
                         (?P<src>\S*)\s+
                         (?P<hist>\S*)\s+
                         (?P<num>[\d.]*)\s*
                         '''%(sbe_constants.robust_re_number, sbe_constants.robust_re_number), header, re.VERBOSE)
        if m:
            print m.groupdict()
            meta.update(m.groupdict()) #put all the fields into the metadata
            for k in ('mon', 'day', 'yr', 'lat', 'lon', 'hour', 'minute'): #remove the date/locations as we have more specific formats to insert
                del meta[k]
            meta.update( ScipyProfile.getMetaFromTimeRE(m))
            location = coordinates.Coordinate(m.group('lat'), m.group('lon'), True)
            meta.update(ScipyProfile.getMetaFromCoord(location))
            meta['Format'] = 'FORMAT 3 (BROOKE-OCEAN MVP .ASVP SV vs Depth)'
            meta['ImportFormat'] = 'ASVP'
        return meta
        
    @staticmethod
    def parseCALCFile(filename):
        # Processed file from the MVP 100 (based on FA's files)
        '''
        ' Get SV file header information.
        ' Headers 1, 2, 3 = Year, Day-of-Year, Time are in Digibar file
        ' Header 6 = Digibar serial number and calibration date are obtained from Registry or
        '            if not there, then in this Sub (can be modified by user).
        ' Headers 0, 4, 5, 7 = ship, lat, lon, operator name, are obtained from operator
        '                      on SV input form.
        ' Header 8 = Format # is set by code.
        ' Header(11)= Simrad Data Set ID = "" for Digibar
        ' Headers 9, 10 are obtained from Registry (can be modified by user)
        
        ' Check record 1 to make sure we have the correct type file and the correct units.
        
        From ReadMVP000cFile in VB code
        ' Modified Version 8.87 to handle a *** NAV **** footer as well as the $GPGGA string.
        ' According to Brooke-Ocean Technology, the NAV footer will be "generic" for the AML CALC format.
           
        ' This sub reads a Brooke-Ocean MVP file in AML CALC .???c format.
        ' The Public variable CFILENAMEComment will contain information about the mvp file - i.e.,
        ' if file is OK or has some problem such as missing time, date, or erroneous position data.
        ' Files with problems will not be processed in batch mode but may be processed singly under
        ' Options-Custom submenu.
        
        ' The mvp calc file has 5 header records followed by records containing depth, sv, and temperature.
        ' For the MVP with SV & P probe, the temperature is a dummy value.
        ' The record 0  0  0 indicates end of data.
        
        ' An additional $GPGGA (or ($INGGA) record contains 14 message fields including:
        ' UTC of position fix, latitude, and longitude in degrees/decimal minutes.
        ' If not available, then record is null.
        ' The last record is a PCdate record.
        
        ' New for Version 8.87:
        ' Instead of a $GPGGA record, there could be a *** NAV **** footer.
          
        ' Example file from FAIRWEATHER:  Valid 04/05/2005. Contains the $GPGGA string
        
         'CALC , 0, 4 - 5 - 2005, 1, meters
         'AML SOUND VELOCITY PROFILER S/N:04986
         'DATE:05095 TIME:1741
         'DEPTH OFFSET (M):00000.0
         'DEPTH (M) VELOCITY (M/S) TEMP (C)
         ' 3.97  1467.85  2.00
         ' 4.02  1467.87  2.00
         ' 5.10  1468.02  2.00
         ' 6.13  1468.06  2.00
         ' 7.00  1468.14  2.00
         ' ..................................>etc
         ' 0  0  0
         '$GPGGA,174142,5621.2482,N,13208.7504,W,1,9,1.6,15,M,,M,,*5D
         'PCdate: 04-05-2005
        
         ' Example file from THOMAS JEFFERSON: Valid 06/05/2007. Contains the generic footer
        
         'CALC,0006,05-19-2007,1,meters
         'AML SOUND VELOCITY PROFILER S/N:04988
         'DATE:07139 TIME:2256
         'DEPTH OFFSET (M):00000.0
         'DEPTH (M) VELOCITY (M/S) TEMP (C)
         '    2.5  1500.02   5.000
         '    2.6  1500.06   5.000
         '    2.6  1500.40   5.000
         '    2.7  1500.01   5.000
         '    2.7  1500.31   5.000
         ' ..................................>etc
         ' 0  0  0
         '*** NAV ****
         'Bottom Depth (m): 13.0
         'Ship 's Log (N): 7.6
         'LAT ( ddmm.mmmmmmm,N):  3701.8858300,N
         'LON (dddmm.mmmmmmm,E): 07548.0070200,W
         'Time [hh:mm:ss.ss]: 22:56:54.00
         'Date [dd/mm/yyyy]:  19/05/2007        
        '''
        s = open(filename).read()
        try:
            top, bottom = s.split('*** NAV ****')
        except ValueError:
            try:
                top, bottom = s.split('$GPGGA')
                bottom =  '$GPGGA'+bottom
            except ValueError:
                top = s
                bottom = ''
        header = top.splitlines()[:5]
        data = top.splitlines()[5:]

        meta = header+bottom.splitlines()
        meta = [m for m in meta if m.strip()]
        metadata = ScipyProfile.parseCALCMetadata(meta)
        metadata['filename'] = filename

        conv = metadata['conv_factor']
        profile_data = parseNumbers(filename, 
                         [('depth', numpy.float32), ('soundspeed',numpy.float32), ('temperature', numpy.float32)], 
                         r"[\s,]+", pre=r'^\s*', post=r'\s*$')
        #if profile_data[-1]['depth']==0.0 or profile_data[-1]['soundspeed']==0.0: #let the QC remove the end of data 0 0 0 flag
        #    profile_data = profile_data[:-1]
        profile_data['depth']*=conv
        profile_data['soundspeed']*=conv

        p = ScipyProfile(profile_data, ymetric="depth", attribute="soundspeed", metadata=metadata)
        return p

    @staticmethod
    def parseCALCMetadata(lines):
        '''Watch out for the meta['conv_factor'] which has the units conversion to get back to meters
        '''
        meta={}
        if 'meters' in lines[0].lower():
            meta['conv_factor'] = 1.0
        elif 'feet' in lines[0].lower():
            meta['conv_factor'] = sbe_constants.FEET2METERS()
        else:
            raise Exception("Can not read MVP Calc file -- not in feet or meters, send to HSTP to fix this")
        m = re.search(r'S/N:(?P<SN>\d+)', lines[1])
        if m:
            meta['Instrument'] = m.group('SN')
        m = re.search(r'DATE:(?P<yr>\d\d)(?P<doy>\d\d\d)\s*TIME:(?P<hour>\d\d)(?P<minute>\d\d)', lines[2])
        if m:
            meta.update(ScipyProfile.getMetaFromTimeRE(m))
        location = None
        #Use the time and location from footers if available
        if len(lines)>=11: #get the bottom metadata if 
            bottom_depth, ships_log, lat, lon, time, date = lines[5:11]
            try:
                time = re.search(r'Time \[hh:mm:ss.ss\]:\s*(..:..:..)\...', time).groups()[0]
                date = re.search(r'Date \[dd\/mm\/yyyy\]:\s*(../../....)', date).groups()[0]
                bottom_depth = float(re.search(r'Bottom Depth \(m\):\s*([0-9\.]+)', bottom_depth).groups()[0])
                lat    = lat.split(':')[1].strip()
                lon    = lon.split(':')[1].strip()
                location    = coordinates.Coordinate(lat, lon)
        
                timestamp = datetime.datetime.strptime("%s %s" % (date, time), "%d/%m/%Y %H:%M:%S")
                meta['Time'] = timestamp.strftime('%H:%M')
                _, ships_log = ships_log.split(':')
                meta['Instrument']='Brooke-Ocean MVP S/N:'+meta['Instrument']
                meta.update({'timestamp': timestamp,
                                'bottom_depth': bottom_depth, 'ships_log': ships_log, })
            except AttributeError: #something didn't parse right, perhaps not an MVP with '*** NAV ****' footer
                pass
        for line in lines: #(old?) version of MVP file with GPGGA at bottom
            m = re.search(r'\$GPGGA,(?P<hour>\d\d)(?P<minute>\d\d)(?P<second>\d\d(\.\d+)?),(?P<lat>[\d.]+,[NS]),(?P<lon>[\d.]+,[EW])', line)
            if m:
                meta['Instrument']='Brooke-Ocean MVP S/N:'+meta['Instrument']
                location = coordinates.Coordinate(m.group('lat'), m.group('lon'))
                meta['Time'] = m.group('hour')+':'+m.group('minute')
                break
        
        if location:
            meta.update(ScipyProfile.getMetaFromCoord(location))        
        meta['ImportFormat'] = 'CALC'
        return meta

    @staticmethod
    def parseRAWMVPFile(filename):
        # Processed file from the MVP 100 (based on FA's files)
        '''
        ' Get SV file header information.
        ' Headers 1, 2, 3 = Year, Day-of-Year, Time are in Digibar file
        ' Header 6 = Digibar serial number and calibration date are obtained from Registry or
        '            if not there, then in this Sub (can be modified by user).
        ' Headers 0, 4, 5, 7 = ship, lat, lon, operator name, are obtained from operator
        '                      on SV input form.
        ' Header 8 = Format # is set by code.
        ' Header(11)= Simrad Data Set ID = "" for Digibar
        ' Headers 9, 10 are obtained from Registry (can be modified by user)
        
        ' Check record 1 to make sure we have the correct type file and the correct units.
        
        From ReadMVP000cFile in VB code
        ' Modified Version 8.87 to handle a *** NAV **** footer as well as the $GPGGA string.
        ' According to Brooke-Ocean Technology, the NAV footer will be "generic" for the AML CALC format.
           
        ' This sub reads a Brooke-Ocean MVP file in AML CALC .???c format.
        ' The Public variable CFILENAMEComment will contain information about the mvp file - i.e.,
        ' if file is OK or has some problem such as missing time, date, or erroneous position data.
        ' Files with problems will not be processed in batch mode but may be processed singly under
        ' Options-Custom submenu.
        
        ' The mvp calc file has 5 header records followed by records containing depth, sv, and temperature.
        ' For the MVP with SV & P probe, the temperature is a dummy value.
        ' The record 0  0  0 indicates end of data.
        
        ' An additional $GPGGA (or ($INGGA) record contains 14 message fields including:
        ' UTC of position fix, latitude, and longitude in degrees/decimal minutes.
        ' If not available, then record is null.
        ' The last record is a PCdate record.
        
        Index: 0001
        PC Time: 21:20:03
        PC Date: 06-03-2010
        Ndecimate: 0
        Version: 2.351
        **********
        Bottom Depth (m): 91.4
        Ship's Log (kt): 10.1
        LAT ( ddmm.mmmmmmm,N):  2848.4701400,N
        LON (dddmm.mmmmmmm,E): 08920.3146900,W
        Time (hh|mm|ss.s): 21:20:02.9
        Date (dd/mm/yyyy): 03/06/2010
        **********
        Serial Format: 1
        Serial Instruments: 2
        Serial Main: 1
        **********
        SER1 Type: 3, AML_SmartSVP
        SER1 FID: M
        SER1 Serial Number: 0
        SER1 Press Offset: 0.00
        SER1 Num5Vin: 1
        **********
        SER2 Type: 0, None
        SER2 FID: 
        SER2 Serial Number: 0
        SER2 Press Offset: 0.00
        SER2 Num5Vin: 0
        **********
        BOT F1: $GPGGA,212001.70,2848.47014,N,08920.31469,W,4,10,1.5,-22.6,M,,,,*3B
        BOT F2: $GPDBT,299.94,f,91.42,M,49.99,F*3A
        BOT F3: $GPVTG,169.1,T,,,10.1,N,18.6,K*2D
        BOT F4: 
        BOT F5: 
        BOT F6: 
        BOT F7: $GPGGA,212001.70,2848.47014,N,08920.31469,W,4,10,1.5,-22.6,M,,,,*3B
        BOT F8: PC UTC Date/Time
        BOT F9: $GPDBT,299.94,f,91.42,M,49.99,F*3A
        BOT F10:$GPVTG,169.1,T,,,10.1,N,18.6,K*2D
        **********
        
        
        M  0004.75  1528.46  0200 
        M  0004.55  1528.41  0200 
        M  0004.17  1528.45  0200 
        M  0003.75  1528.42  0199
        '''
        s = open(filename).read()
        end_header = re.search(r".*\*{10}", s, re.DOTALL).span()[1]
        header, data = s[:end_header].splitlines(), s[end_header:].splitlines()
        meta = [m for m in header if m.strip()]
        metadata = ScipyProfile.parseRAWMVPMetadata(meta)
        metadata['filename'] = filename

        #conv = metadata['conv_factor']
        profile_data = parseNumbers(filename, 
                         [('depth', numpy.float32), ('soundspeed',numpy.float32), ('fluorescence_turner', numpy.float32)], 
                         r"[\s,]+", pre=r'^M?\s*', post=r'\s*$')
        #if profile_data[-1]['depth']==0.0 or profile_data[-1]['soundspeed']==0.0: #let the QC remove the end of data 0 0 0 flag
        #    profile_data = profile_data[:-1]
        #profile_data['depth']*=conv
        #profile_data['soundspeed']*=conv

        p = ScipyProfile(profile_data, ymetric="depth", attribute="soundspeed", metadata=metadata)
        return p

    @staticmethod
    def parseRAWMVPMetadata(lines):
        '''Watch out for the meta['conv_factor'] which has the units conversion to get back to meters
        '''
        meta={}
        m = re.search(r'S/N:(?P<SN>\d+)', lines[1])
        if m:
            meta['Instrument'] = m.group('SN')
        else:
            meta['Instrument'] = "TJ MVP"
        m = re.search(r'DATE:(?P<yr>\d\d)(?P<doy>\d\d\d)\s*TIME:(?P<hour>\d\d)(?P<minute>\d\d)', lines[2])
        if m:
            meta.update(ScipyProfile.getMetaFromTimeRE(m))
        location = None
        #Use the time and location from footers if available
        #if len(lines)>=11: #get the bottom metadata if 
        #    bottom_depth, ships_log, lat, lon, time, date = lines[5:11]
        #    try:
        #        time = re.search(r'Time \[hh[:|]mm[:|]ss.ss\]:\s*(..:..:..)\...', time).groups()[0]
        #        date = re.search(r'Date \[dd\/mm\/yyyy\]:\s*(../../....)', date).groups()[0]
        #        bottom_depth = float(re.search(r'Bottom Depth \(m\):\s*([0-9\.]+)', bottom_depth).groups()[0])
        #        lat    = lat.split(':')[1].strip()
        #        lon    = lon.split(':')[1].strip()
        #        location    = coordinates.Coordinate(lat, lon)
        # 
        #        timestamp = datetime.datetime.strptime("%s %s" % (date, time), "%d/%m/%Y %H:%M:%S")
        #        meta['Time'] = timestamp.strftime('%H:%M')
        #        _, ships_log = ships_log.split(':')
        #        meta['Instrument']='Brooke-Ocean MVP S/N:'+meta['Instrument']
        #        meta.update({'timestamp': timestamp,
        #                        'bottom_depth': bottom_depth, 'ships_log': ships_log, })
        #    except AttributeError: #something didn't parse right, perhaps not an MVP with '*** NAV ****' footer
        #        pass
        date, time = None, None
        for line in lines: #(old?) version of MVP file with GPGGA at bottom
            m = re.search(r'\$GPGGA,(?P<hour>\d\d)(?P<minute>\d\d)(?P<second>\d\d(\.\d+)?),(?P<lat>[\d.]+,[NS]),(?P<lon>[\d.]+,[EW])', line)
            if m:
                meta['Instrument']='Brooke-Ocean MVP S/N:'+meta['Instrument']
                location = coordinates.Coordinate(m.group('lat'), m.group('lon'))
                meta['Time'] = m.group('hour')+':'+m.group('minute')
            m = re.search(r'Time\s+[\[\(]hh[:\|]mm[:\|]ss\.s+[\]\)]:\s*(\d\d:\d\d:\d\d)\..*', line)
            if m: time = m
            m = re.search(r'Date\s+[\[\(]dd\/mm\/yyyy[\]\)]:\s*(../../....)', line)
            if m: date = m
            if re.search('LAT.*:', line):
                lat    = line.split(':')[1].strip()
            if re.search('LON.*:', line):
                lon    = line.split(':')[1].strip()
            if re.search("^SER\d", line):
                ser, typ = line.split(":")
                meta[ser] = typ
        if date and time:
            date = date.groups()[0]
            time = time.groups()[0]
            timestamp = datetime.datetime.strptime("%s %s" % (date, time), "%d/%m/%Y %H:%M:%S")
            meta['Time'] = timestamp.strftime('%H:%M')
            meta['timestamp'] = timestamp
            meta.update(ScipyProfile.parseMetaFromDatetime(timestamp))
        if lat and lon:
            try:
                loc = coordinates.Coordinate(lat, lon)
                if loc: location = loc
            except:
                pass
        if location:
            meta.update(ScipyProfile.getMetaFromCoord(location))        
        meta['ImportFormat'] = 'RAW_MVP'
        return meta
    
    @staticmethod
    def isCarisSvpFile(filename):
        '''Differentiate between a Caris SVP file and an OMG SVP file
             Returns True if filename seems to be a Caris SVP file
        '''
        line = open(filename).readline()
        if "SVP_VERSION" in line: return True
        else:  return False

    @staticmethod
    def isOmgSvpFile(filename):
        '''Differentiate between an OMG SVP file and a Caris SVP File Returns
             True if filename seems to be a OMG SVP file. The version number
             should be the first character of the file, so basically this just
             returns True if the file starts with 1 or 2... cheap test.
        '''
        version = open(filename).read(1)
        if version == "1" or version == "2": return True
        else:  return False

    @staticmethod
    def parseVelocwinNODCFile(filename):
        ''' Velocwin Archive with Pressure/Temp/Salinity profiles 
        Accepts the filename of a Velocwin NODC file (extension .??a) and
        returns two profiles: salinity and temperature vs. pressure (or one if the type is given)
        '''

        lines = open(filename).read().splitlines()
        metadata = '\n'.join(lines[:10])
        metadata = ScipyProfile.parseNODCMetadata(metadata)
        metadata['filename'] = filename
        profile_data = parseNumbers(filename, 
                         [('pressure', numpy.float32), ('temperature', numpy.float32), ('salinity',numpy.float32)], 
                         r"\s+", pre=r'^\s*', post=r'\s*$')

        p = ScipyProfile(profile_data, ymetric="pressure", attribute="temperature", metadata=metadata)
        return p
    @staticmethod
    def parseOmgSvpFile(filename):
        '''
        '''
        lines = open(filename).read().splitlines()
        head, data = lines[:16], lines[16:]
        head = map(lambda s: s.split("#", 1)[0].strip(), head) # strip out everything the first pound sign

        version, observed_date, log_date, observed_location, log_location, n = head[:6]
        observed_date = re.findall("[0-9 :]+", observed_date)[0] #strip off any junk -- there was an accidental \t in some files
        timestamp = datetime.datetime.strptime(observed_date, "%Y %j %H:%M:%S")

        try:
            log_date = re.findall("[0-9 :]+", log_date)[0]
            log_timestamp = datetime.datetime.strptime(log_date, "%Y %j %H:%M:%S")
        except ValueError:
            log_timestamp = None

        location = coordinates.Coordinate(*observed_location.split())
        
        log_location = coordinates.Coordinate(*log_location.split())
        metadata = {'timestamp': timestamp, 'log_timestamp': log_timestamp, 'location': location, 'log_location': log_location, 'version': version, 'filename': filename}
        metadata['ImportFormat'] = '0mg'
        metadata.update(ScipyProfile.getMetaFromCoord(location))
        metadata.update(ScipyProfile.parseMetaFromDatetime(timestamp))

        d = parseNumbers(filename, 
                         [('index', numpy.int32), ('depth', numpy.float32), ('soundspeed',numpy.float32), ('temperature', numpy.float32), ('salinity', numpy.float32), ('unk', numpy.float32), ('flag', numpy.int32)], 
                         r"\s+", pre=r'^', post=r'\s*$')
        d=d.compress(d['flag']==0) #remove bad data
        
        p=ScipyProfile(d, ymetric="depth", attribute="soundspeed", metadata = metadata)
        return p

    @staticmethod
    def getUnionOfDepths(casts):
        s = set()
        for cast in casts:
            s |= set(cast.keys())
        return s

    @staticmethod
    def getSpeedReadingsAtEachDepth(profiles):
        '''Takes a list of casts and returns a dictionary: key = depth; value = list of speeds at each depth'''
        # Initialize lists of speed readings at each valid depth
        h = {} # h is a dictionary: key = depth; value = list of speeds at each depth
        for i in ScipyProfile.getUnionOfDepths(profiles):
            h[i] = []

        for profile in profiles:
            depths, speeds = profile.getDepths(), profile.getSpeeds()
            for i in range(len(depths)):
                h[depths[i]].append(speeds[i])
        return h

    @staticmethod
    def getSpeedsAsMaskedNumpyArray(profiles):
        '''Takes a list of profiles and returns a MaskedArray of dimensions (n_profiles, max_readings)
        '''
        maxlen = max(map(len, profiles))

        meanspeeds = numpy.empty(maxlen)
        speeds = MaskedArray(numpy.empty((len(profiles), maxlen)), mask=numpy.zeros((len(profiles), maxlen), dtype=bool))

        # Build up some numpy arrays
        for i, p in enumerate(profiles):
            # Set the used values
            speeds[i,:len(p)] = p.getSpeeds()

            # Mask out the unused valuse
            mask = [[True for _ in range(maxlen-len(p))]]
            speeds.mask[i, len(p):] = deepcopy(mask)
        return speeds
    @staticmethod
    def GetDraft(profiles):
        drafts=[0.0]
        for p in profiles:
            try:
                d=p.metadata.get('Draft', 0.0)
                d=float(d)
                drafts.append(d)
            except:
                pass
        return max(drafts)
        
    @staticmethod
    def meanSpeeds(profiles):
        '''Takes a list of profiles as the parameter and returns a synthetic profile where the attribute is actually a mean attribute
        '''
        speeds = ScipyProfile.getSpeedsAsMaskedNumpyArray(profiles)
        maxlen = speeds.shape[1]

        for p in profiles:
            if len(p) == maxlen:
                newdepths = p.getDepths()
                break

        # Calculate the stats
        mean_speeds = speeds.mean(axis=0) #speeds.filled(0).sum(axis=0) / speeds.count(axis=0)
        p=ScipyProfile((newdepths, mean_speeds), names=['depth','soundspeed'], ymetric="depth", attribute="soundspeed")
        return p

    @staticmethod
    def sigmaSpeeds(profiles):
        '''Takes a list of profiles as the parameter and returns a dict key: depth, value: sigma at depth'''
        speeds = ScipyProfile.getSpeedsAsMaskedNumpyArray(profiles)
        maxlen = speeds.shape[1]

        for p in profiles:
            if len(p) == maxlen:
                newdepths = p.getDepths()
                break

        # Calculate the stats
        std_speeds = speeds.std(axis=0) #[ speeds[:,i].compressed().std() for i in range(maxlen) ]

        return ScipyProfile((newdepths, std_speeds), names=['depth','soundspeed'], ymetric="depth", attribute="soundspeed")


    @staticmethod
    def parseVelocwinMetadata(s):
        m={}
        m['_fields_']=("depth", "soundspeed", "flag")
        lines = s.splitlines()
        try:
            n_hdr = lines.index('ENDHDR') #if we were passed the whole file, find the endhdr
        except ValueError: #entire string is header
            n_hdr = len(lines)
        is_python = False
        for l in lines[:n_hdr]:
            if 'python generated' in l.lower():
                is_python=True
                ver_number = int(re.search("\d+", l).group())
                if ver_number>1: n_hdr-=1 #subtract one since the field names are on the last line
        if is_python:
            def translate(s):
                return s.replace('<\\n>','\n').replace('<\\r>', '\r')
            for l in lines[:n_hdr]:
                if sbe_constants.XREFDELIM in l:
                    k, v = l.strip().split(sbe_constants.XREFDELIM)
                    m[k] = translate(v) #add to the metadata.  
                    #timestamp and location will get overwritten with time/coord objects after parsing is finished
            if ver_number>1:
                l = lines[n_hdr]
                m['_fields_'] = l.split(",")
        else: #VelocWin file  -- Visual Basic generated file
            for i in range(min(n_hdr, len(ScipyProfile.header_keys))): #get the standard headers, as many as exist
                m[ScipyProfile.header_keys[i]]=lines[i]
            for i in range(len(ScipyProfile.header_keys), n_hdr): #get any extra headers beyond the standard and give them integer keys
                hd = lines[i]
                m[str(i)] = hd 
        m['timestamp'] = datetime.datetime.strptime("%s %s %s" % (m['Year'], m['Day'], m['Time']), "%Y %j %H:%M")
        if m['Latitude']=='Unknown' or m['Longitude']=='Unknown':
            m['location'] = coordinates.Coordinate(0.0, 0.0)
        else:
            m['location'] = coordinates.Coordinate(m['Latitude'], m['Longitude'])
        m['ImportFormat'] = 'Q'

        return m

    @staticmethod
    def parseSVPMetadata(s, version_string="", filename=""):
        try: # This will work if it's the full header
            version_string, filename, _, date, time, lat, lon = s.split()
        except ValueError: # Partial metadata in the second part of the file (after we've split on "Section"
            date, time, lat, lon = s.split()
        try:
            timestamp = datetime.datetime.strptime("%s %s" % (date, time), "%Y-%j %H:%M:%S")
        except:
            timestamp = datetime.datetime.strptime("%s %s" % (date, time), "%Y-%j %H:%M")
        location = coordinates.Coordinate(lat, lon)
        meta = {'version_string': version_string, 'filename': filename, "timestamp": timestamp} 
        meta['Year']=date.split('-')[0]
        meta['Day'] =date.split('-')[1]
        meta['Time']=time
        meta.update(ScipyProfile.getMetaFromCoord(location))
        meta['ImportFormat'] = 'SVP'

        return meta 

    @staticmethod
    def parseNODCMetadata(s):

        #boat, project, location, date, time, lat, lon, sensor, _, _ = map(lambda s: s.split(":", 1)[-1].strip(), s.splitlines())
        meta={}
        m = re.search(r'''DATA\sCOLLECTOR:\s*(?P<Ship>.*)\n
                        PROJECT:\s*(?P<Project>.*)\n
                        SURVEY:\s*(?P<Survey>.*)\n
                        DATE:\s*(?P<yr>\d\d\d\d)-(?P<mon>\d\d)-(?P<day>\d\d)\s*\n
                        TIME:\s*(?P<hour>\d\d)(?P<minute>\d\d).*\n
                        LATITUDE[\s\w\(\)]*:\s*(?P<lat>.*)\n
                        LONGITUDE[\s\w\(\)]*:\s*(?P<lon>.*)\n
                        INSTRUMENT:\sPROFILER\s*(?P<Instrument>.*)
                    ''', s, re.VERBOSE) #ignoring the optional fields of first line
        if m:
            meta.update( ScipyProfile.getMetaFromTimeRE(m))
            meta['ImportFormat'] = 'NODC'
            meta.update( ScipyProfile.getMetaFromCoord(coordinates.Coordinate(m.group('lat'), m.group('lon'), True)))
            for h in ('Ship', 'Instrument', 'Project', 'Survey'):
                meta[h]=m.group(h)
        return meta

    @staticmethod
    def parseNODCFile(filename):
        fread = Dataset(filename, 'r')
        ncvars = [v for v in fread.variables.keys() if v not in ('profile', 'time', 'lat', 'lon')]
        d = []
        fields = []
        for key in ncvars:
            d.append(fread.variables[key][:][0])
            fields.append(key)
        meta = {}
        maps = {'draft':'Draft', 'samplerate':'samplerate', 'instrument':'Instrument', 'instrument_sn':'instrument_sn', 'creator':'UserName', 'project':'Project', 'survey':'Survey', 'ship':'Ship'}
        ncattrs = [v for v in fread.ncattrs() if maps.has_key(v)]
        for key in ncattrs:
            attr = fread.getncattr(key)
            if attr: meta[maps[key]] = attr
        location = coordinates.Coordinate(str(fread.variables['lat'][0]), str(fread.variables['lon'][0]))
        meta.update(ScipyProfile.getMetaFromCoord(location))
        meta['timestamp'] = num2date(fread.variables['time'][0], units='seconds since 1970-01-01 00:00:00', calendar='standard')
        meta['Time'] = meta['timestamp'].strftime('%H:%M')
        meta['Year'] = meta['timestamp'].strftime('%Y')
        meta['Day'] = meta['timestamp'].strftime('%j')
        meta['filename'] = filename
        meta['ImportFormat'] = 'NC4'
        try: meta['Format'] = fread.getncattr('title').replace(' data file', '')
        except: meta['Format'] = 'Sound speed'
        fread.close()
        p = ScipyProfile(d, names=fields, ymetric="depth", attribute="soundspeed", metadata = meta)
        return p
        
    def WriteNODCFile(self, filename, bDebug=False):
        '''   
        ' NOTES: Data are obtained from the Sea-Bird converted CNV data file.
        '        Pressure, temperature, salinity are averaged,
        '        reducing the number of points to not more than 4000.  Next parabolic
        '        fitting is done to obtain data at 1-decibar intervals.
        
        ' Algorithms (averaging/parabolic fitting): Dr. Lloyd Huff 3/28/1989
        '''
        ''' Communication with NODC -- their preferred format is netCDF as seen below. 
        
        Here are some useful links regarding CF compliance.

        The main link to CF metadata:
        http://cf-pcmdi.llnl.gov/
        
        There are two links on that page which are very useful (under Quick Links):
        CF Conventions Document (v1.4)
        CF Standard Name Table
        
        and the CF Compliance Checker once you start creating them.
        
        Examples of it's implementation can be found at:
        http://www.unidata.ucar.edu/software/netcdf/examples/files.html
        
        There are five files you can review under the netCDF column.
        
        Let me know if you have any questions.
        
        Regards,
        Chris
        
        -- 
        Chris Paver, Oceanographer
        NOAA/NODC E/OC1
        1315 East-West Hwy
        Silver Spring MD 20910
        Phone:  301-713-3272 ext. 118
        Fax:  301-713-3302
        http://www.nodc.noaa.gov/ 
        '''
        #raise Exception('Need to perform NodcCre QC/averaging checks')
        #f.write("DATA COLLECTOR: "+
        #        self.metadata['Ship'].replace("NRT", 'NOAA NAVIGATION RESPONSE TEAM').replace("(SHIP)", 'NOAA SHIP').replace("OTHER", 'SHIP')+'\n')
        #f.write("PROJECT: " +self.metadata['Project']+'\n')
        #f.write("SURVEY: " + self.metadata['Survey']+'\n')
        #f.write("INSTRUMENT: PROFILER "+self.metadata['Instrument']+'\n') #TODO: remove calibration date??
        #If InStr(HEADER(6), "CD") > 0 Then           ' check for calibration date

        bDigibarT = False
        title = 'Sound speed'
        iFormat = ''
        if self.metadata.has_key('ImportFormat'):
            iFormat = str(self.metadata['ImportFormat'])
            if iFormat in ['WOA', 'RTOFS', 'HYCOM']:
                if bDebug:
                    self.metadata['Ship'] = iFormat
                else:
                    print 'Could not export %s profile to NODC file\r' %iFormat
                    return ''
            elif iFormat == 'CSV':
                bDigibarT = True
                title = 'Digibar'
            elif iFormat == 'NC4':
                if self.metadata.has_key('Instrument') and self.metadata['Instrument'].lower().startswith('digibar'):
                    bDigibarT = True
                    title = 'Digibar'
                else:
                    title = self.metadata['Format']
            elif iFormat == 'CastAway' or iFormat == 'RAW_MVP':
                title = iFormat
            elif iFormat == 'CALC':
                title = 'MVP'
            elif iFormat == '0mg':
                title = 'OMG svp'
            elif iFormat == 'XBT' or iFormat == 'XSV':
                title = 'Sippican %s' %iFormat
            elif iFormat == 'CNV':
                title = 'CTD'
        if not self.metadata.has_key('Project') or not self.metadata.has_key('Survey') or not self.metadata.has_key('Instrument') or not self.metadata.has_key('Ship') \
            or not self.metadata['Project'] or not self.metadata['Survey'] or not self.metadata['Instrument'] or not self.metadata['Ship']:
            print 'Failed exporting %s to NODC file. Missing project, survey, instrument, or ship (NOAA Unit) info. Try to enter, apply, and export again.' %os.path.basename(filename)
            return ''
        if title.endswith('ound speed') and self.metadata.has_key('Instrument') and self.metadata['Instrument'].startswith('SBE'):
            title = 'CTD'
        epoch = int(calendar.timegm(time.strptime(str(self.metadata['timestamp']), '%Y-%m-%d %H:%M:%S')))
        ship_code = self.metadata['Ship'][:2] if self.metadata.has_key('Ship') else 'ZZ'
        fn_new = '%s_%s.nc' %(self.metadata['timestamp'].strftime('%Y%m%d%H%M'), ship_code)
        fn = filename.split('\\')[-1]
        filename = filename.replace(fn, fn_new)
        profile_id_str = fn_new[:-3]
        NUMCHARS = 40
        if len(profile_id_str) > NUMCHARS:
            NUMCHARS = len(profile_id_str)
        d=self.mcopy()
        if 'flag' in self.dtype.names:
            d = numpy.compress(d['flag']<=0, d)
        rootgrp = Dataset(filename, 'w', format='NETCDF4')
        rootgrp.createDimension('z', len(d))
        rootgrp.createDimension('profile', 1)
        rootgrp.createDimension('NUMCHARS', NUMCHARS)

        profile_id = rootgrp.createVariable('profile','S1',('profile','NUMCHARS',))  
        time2 = rootgrp.createVariable('time','i4',('profile',))        
        lat = rootgrp.createVariable('lat','f8',('profile',))
        lon = rootgrp.createVariable('lon','f8',('profile',))
        z = rootgrp.createVariable('depth','f4',('profile','z',))
        profile_id.long_name = 'Unique identifier for each profile'
        profile_id.cf_role = 'profile_id'
        time2.standard_name = 'time'
        time2.long_name = 'time'
        time2.units = 'seconds since 1970-01-01 00:00:00'
        time2.axis = 'T'
        lat.standard_name = 'latitude'
        lat.long_name = 'latitude'
        lat.units = 'degrees_north'
        lat.axis = 'Y'
        lon.standard_name = 'longitude'
        lon.long_name = 'longitude'
        lon.units = 'degrees_east'
        lon.axis = 'X'
        z.standard_name = 'altitude'
        z.long_name = 'depth_below_sea_level'
        z.units = 'm'
        z.axis = 'Z'
        z.positive = 'down'

        profile_id[:] = stringtoarr(profile_id_str, NUMCHARS)
        time2[:] = epoch
        lat[:] = self.metadata['location'].lat
        lon[:] = self.metadata['location'].lon
        if 'depth' in self.dtype.names:
            z[:] = d['depth']

        units = {}
        # try to get units and names from the profile
        try:
            for item in self.metadata['columns']:
                (i, name, unit) = item
                unit = unit.strip()
                if len(unit) > 0 and unit[0] == '[':
                    unit = unit[1:-1]
                unit = unit.strip(',')
                unit = unit.strip()
                units[name.lower()] = (unit, name)
        except:
            try:
                for item in ast.literal_eval(self.metadata['columns']):
                    (i, name, unit) = item
                    unit = unit.strip()
                    if len(unit) > 0 and unit[0] == '[':
                        unit = unit[1:-1]
                    unit = unit.strip(',')
                    unit = unit.strip()
                    units[name.lower()] = (unit, name)
            except:
                pass

        units['pressure'] = ('dbar', 'Pressure')
        units['conductivity'] = ('S/m', 'Conductivity')
        units['salinity'] = ('1e-3', 'Salinity')
        units['density'] = ('kg m-3', 'Density')
        units['temperature'] = ('degree_C', 'Temperature')
        units['soundspeed'] = ('m/s', 'Sound_Speed')
        units['flag'] = (None, 'Quality Flag')
        standard_names = {}
        standard_names['temperature'] = 'sea_water_temperature'
        standard_names['salinity'] = 'sea_water_salinity'
        if title == 'CTD':
            # TODO make sure all density of CTD is sigma_theta
            standard_names['density'] = 'sea_water_sigma_theta'
        elif iFormat == 'CastAway' or title.startswith('CastAway'):
            standard_names['density'] = 'sea_water_density'
            units['conductivity'] = ('MicroSiemens/cm', 'Conductivity')
            units['conductance'] = ('MicroSiemens/cm', 'Conductance')

        for name in self.dtype.names:
            if name not in ['depth', 'time']:
                if name == 'temperature' and (bDigibarT or d[name].min()==d[name].max()):
                    continue # Exclude Digibar or dummy temperature
                elif name == 'salinity' and d[name].min()==d[name].max():
                    continue # Exclude dummy salinity
                elif name == 'flag':
                    var = rootgrp.createVariable(name,'i4',('profile','z',))
                else:
                    var = rootgrp.createVariable(name,'f4',('profile','z',))
                if standard_names.has_key(name):
                    var.standard_name = standard_names[name]
                if units.has_key(name):
                    var.long_name = units[name][1]
                    if units[name][0]:
                        var.units = units[name][0]
                    if name == 'flag':
                        var.flag_values = -1, 0, 1, 2, 3, 4, 5, 6
                        var.flag_meanings = 'bad_point good_point extrapolated_using_historical_depth extrapolated_linearly ' \
                            'extrapolated_using_the_most_probable_slope extrapolated_manually moved_point extrapolated_by_appending_the_last_measured_point'
                else:
                    var.long_name = name
                    if name == 'bin_count':
                        var.comment = 'The number of measurements at the depth'
                var[:] = d[name]

        
        rootgrp.standard_name_vocabulary = 'CF-1.6'
        rootgrp.featureType = 'profile'
        rootgrp.cdm_data_type ='profile'
        rootgrp.Conventions = 'CF-1.6'
        rootgrp.title = '%s data file' %title
        rootgrp.date_created = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        if self.metadata.has_key('Ship'):
            rootgrp.ship = \
                str(self.metadata['Ship'].replace("NRT", 'NOAA NAVIGATION RESPONSE TEAM').replace("(SHIP)", 'NOAA SHIP').replace("OTHER", 'SHIP'))
        if self.metadata.has_key('Draft'):
            #rootgrp.draft = '%sm' %self.metadata['Draft']
            rootgrp.draft = str(self.metadata['Draft'])
        if self.metadata.has_key('samplerate'):
            rootgrp.samplerate = str(self.metadata['samplerate'])
        if iFormat == 'CastAway':
            rootgrp.instrument = 'CastAway'
            if self.metadata.has_key('Instrument'):
                rootgrp.instrument_sn = str(self.metadata['Instrument'])
        else:
            if self.metadata.has_key('Instrument'):
                rootgrp.instrument = str(self.metadata['Instrument'])
            if self.metadata.has_key('instrument_sn'):
                rootgrp.instrument_sn = str(self.metadata['instrument_sn'])
        if self.metadata.has_key('UserName'):
            rootgrp.creator = str(self.metadata['UserName'])
        rootgrp.creator_institution = 'NOAA Office of Coast Survey'
        if self.metadata.has_key('Project'):
            rootgrp.project = str(self.metadata['Project'])
        if self.metadata.has_key('Survey'):
            rootgrp.survey = str(self.metadata['Survey'])
        rootgrp.software_version = '2015-08-27'
        rootgrp.close()
        print '%s\r' %filename
        return filename

    def WriteVELFile(self, filename):
        d = self.mcopy()
        if 'flag' in self.dtype.names:
            d = numpy.compress(d['flag']>=0, d)
        with open(filename, 'w') as f:
            f.write('FTP NEW 2\n')
            for i in range(len(d['depth'])):
                f.write('%.1f %.1f\n' %(d['depth'][i], d['soundspeed'][i]))
        print filename
    def WriteBSVPFile(self, filename):
        if os.path.splitext(self.metadata['Filename'])[1] != os.path.splitext(self.metadata['filename'])[1]:
            profile = os.path.splitext(self.metadata['Filename'])[1][len(os.path.splitext(self.metadata['filename'])[1]):]
            filename = filename.replace('.bsvp', '%s.bsvp'%profile)
            #filename = os.path.join(os.path.dirname(filename), os.path.splitext(self.metadata['Filename'])[0] + '%s.bsvp'%profile)
        iFormat = self.metadata['ImportFormat'] if self.metadata.has_key('ImportFormat') else ''
        epoch = int(calendar.timegm(time.strptime(str(self.metadata['timestamp']), '%Y-%m-%d %H:%M:%S')))
        d = self.mcopy()
        #if 'flag' in self.dtype.names:
        #    d = numpy.compress(d['flag']>=0, d)
        condition = [True]
        pre_depth = d['depth'][0]
        for depth in d['depth'][1:]:
            condition.append(depth > pre_depth)
            if depth > pre_depth: pre_depth = depth
        d = numpy.compress(condition, d)
        with open(filename, 'wb') as f:
            data = struct.pack('dddi', epoch, self.metadata['location'].lat, self.metadata['location'].lon, len(d['depth']))
            #f.write('%i %.5f %.5f %i\n' %(epoch, self.metadata['location'].lat, self.metadata['location'].lon, len(d['depth'])))
            f.write(data)
            for i in range(len(d['depth'])):
                temperature = d['temperature'][i] if 'temperature' in self.dtype.names else 0
                salinity = d['salinity'][i] if 'salinity' in self.dtype.names else 0
                pressure = d['pressure'][i] if 'pressure' in self.dtype.names else 0
                conductivity = d['conductivity'][i] if 'conductivity' in self.dtype.names else 0
                flag = d['flag'][i] if 'flag' in self.dtype.names else 0
                flags = 2 if iFormat in ['WOA', 'RTOFS', 'HYCOM'] else 1
                if flag < 0:
                    flags += 256 # bit 8 (start from 0)
                elif flag > 0:
                    flags += 131072 # bit 17
                data = struct.pack('iffffffI', i, d['depth'][i], d['soundspeed'][i], temperature, salinity, pressure, conductivity, flags)
                #f.write('%i %.1f %.1f %.1f %.1f %.1f %.1f %i\n' %(i, d['depth'][i], d['soundspeed'][i], temperature, salinity, pressure, conductivity, flags))
                f.write(data)
        print filename

#     def WriteSimradFiles(self, path, basefname='', fmt='', default_id=0, depth = 0):
#         ''' 
#         ' This module added for Version 7.02 and modified for 7.03.
#         
#         ' For version 7.03, generate a .asvp file in addition to the ssp file.
#         ' Filename for the .asvp file is same as for the ssp file except for the extension.
#         
#         ' Version 7.02
#         ' Save the velocity profile in a Simrad SSP ASCII text file using
#         ' input variable DataSetId as the Simrad Data Set Identifier xxxxx.
#         
#         ' Version 8.81
#         ' Allow user to extend to 12000m
#         ' Get the probe name from the edited profile
#         
#         ' Version 8.82
#         ' Correct the value for number of points in profile (written in the Simrad header).
#         
#         ' References:
#         ' EM Series 1002 Operator Manual, Datagram formats, Kongsberg Simrad SSP format
#         ' Word file: soundspeed profile format.doc. (describes .asvp file format)
#         
#         ' Filename format: xxxxx_YYDDDHHM (extension ssp or asvp) where
#         '                  xxxxx is the input variable DataSetId (00000 to 65535)
#         '                  YYDDDHHMM is year/day/time from the cast file name
#            
#         ' Simrad SSP format (EM Series 1002 Operator Manual):
#           
#         ' Start ID,                                      $
#         ' Talker ID                                      AA
#         ' Datagram ID,                                   S10,
#         ' Data Set ID,                                   xxxxx,
#         ' Number of measurements,                        xxxx,
#         ' UTC time of data acquisition,                  hhmmss,
#         ' Day of data acquisition,                       xx,
#         ' Month of data acquisition,                     xx,
#         ' Year of data acquisition,                      xxxx,
#         ' First good depth in m                          x.x,
#         ' Corresponding Sound Velocity in m/s,           x.x,
#         ' Skip temp, sal, absorption coeff fields        ,,,
#         ' End of line                                    CRLF
#         ' Then, repeat good depth, sv,,,,CRLF until all NPTS are listed.
#         
#         ' Simrad ASVP format(soundspeed profile format.doc) Added for version 7.03
#         ' Item                                             Example
#         '---------------------------------------------     --------------------------------------
#         ' Sound Velocity (Identification of file type)     ( SoundVelocity
#         ' Version (File format version number)             1.01(note: hard coded)
#         ' Id (a possible identifier)                       12 (Use Data Set ID above)
#         ' Time (of creation for this file)                 200205290813  YYYYMMDDhhmm
#         ' Lat (Latitude of profile location,dec. deg.      22.3452678
#         ' Long (Longitude of profile loc. in dec. deg.)    66.4483298
#         ' Radius (in m, profile valid within circle)       4500 (note: hard coded)
#         ' Valid_from (date)                                200205290813 (same as creation time)
#         ' Valid_to (date)                                  200212312359 (mon,day,time hard coded)
#         ' Src (probe name)                                 SBE19
#         ' Hist (modification hist, Probe,Edit,Merged,New)  PE(note: hard coded)
#         ' No_val (number of values)                        6 )
#         ' CRLF
#         ' Above is the header
#         ' Depth in m                                       5.0
#         ' Sound Velocity in m/s                            1484.2
#         ' CRLF
#         ' Then repeat last 3 items until all points listed.
#         
#         ' If running custom, then read in the public arrays for
#         ' headers, depth, and sv.  If running automatic, these quantities
#         ' are already in memory.
#         '''
#         d = self.NoDupes_GoodFlags()
#         print depth, default_id
#         if depth>self['depth'].max():
#             d = d.ExtendCast(depth)
#         #' Determine the total number of "good" points for header. 
#         try:
#             try:
#                 DataSetId = "%05d"%int(self.metadata.get('DataSetID', default_id)) #Format(DataSetId, "00000")
#             except ValueError:#non-int
#                 try:
#                     DataSetId = "%05d"%int(re.search(r'(\d+)', self.metadata['DataSetID']).group(0))
#                 except:
#                     DataSetId = "%05d"%default_id
#             #' The following apply to the cast creation
#             T=self.metadata.get('Time', '00:00')
#             TimeStr = T[:2]+T[3:5] #Left(HEADER(3), 2) & Right(HEADER(3), 2)
#             YearStr = str(self.metadata['Year']) #HEADER(1)
#             MonthStr, DayStr = ['%02d'%v for v in Tools.MonthDay(YearStr, self.metadata['Day'])]
#             LatStr,LonStr = self.metadata['location'].SignedDec().split(', ')
#             ProbeStr = self.metadata['Instrument'].split()[0]
#         except KeyError, k:
#             raise MetadataException(str(k))
#         ScipyProfile.KillDuplicateSSP( path, DataSetId)
#         for datalength in [".full", ".1000"]:
#             if datalength==".1000":
#                 d = d.DownSample(1000)
#             NGoodPts = len(d['depth'])
# 
#             #TODO: We could support more formats of the SSP format, see the parseSSP function for options
#             if not fmt:
#                 for n in range(10, 54):
#                     try_fmt = 'S%0d'%n
#                     if SSP_Formats.has_key(try_fmt) and set(SSP_Formats[try_fmt]).issubset(d.dtype.names):
#                         fmt = try_fmt
#                         break
#             if not fmt:
#                 raise Exception('not enough data fields to write SSP file') #WriteProfileException -- make a custon exception class
#                 
#             SimradSSPHeader = "$AA%s,"%fmt + DataSetId + "," + \
#                  "%04d"%NGoodPts + "," + \
#                  TimeStr + "00" + "," + \
#                  DayStr + "," + \
#                  MonthStr + "," + \
#                  YearStr + "," 
#            
#             #' *** This header corrected on 05/21/02 by rlb per request of Jeremy W. on Whiting.
#             #' Modified Version 8.81 to obtain current probe name
#             SimradASVPHeader = "( SoundVelocity 1.01 " + DataSetId + " " + \
#                                YearStr + MonthStr + DayStr + TimeStr + " " + \
#                                LatStr + " " + LonStr + " 4500 " + \
#                                YearStr + MonthStr + DayStr + TimeStr + " " + \
#                                YearStr + "12312359" + " " + \
#                                ProbeStr + " PE " + \
#                                str(NGoodPts) + " )"
#           
#             if not basefname:
#                 basefname = os.path.splitext(self.metadata['Filename'])[0]
#             sspname = path+'\\'+DataSetId+'_'+basefname+datalength+'.ssp'
#             asvpname = path+'\\'+DataSetId+'_'+basefname+datalength+'.asvp'
#             print sspname, asvpname
#             #' Get rid of any SSP files with same data set identifier.
#             try: os.remove(sspname)
#             except: pass
#             try: os.remove(asvpname)
#             except: pass #file didn't exist
#             
#             SSPFile = file(sspname, 'w') #F
#             SSPFile.write(SimradSSPHeader) #first data record goes on header line
#             ASVPFile = file(path+'\\'+DataSetId+'_'+basefname+datalength+'.asvp', 'w') #G
#             ASVPFile.write(SimradASVPHeader+'\n')
#             
#             fields = SSP_Formats[fmt]
#             for r in d: #iterate the good depths
#                 ssp_rec = ','.join(['%0.2f'%r[field] for field in fields]) + ','*(6-len(fields))
#                 SSPFile.write(ssp_rec+'\n')
#                 asvp_rec = '%04.2f'%r['depth']+' '+'%07.2f'%r['soundspeed']
#                 ASVPFile.write(asvp_rec+'\n')
#                 
#             SSPFile.write('\\\n') #' Last line of ssp file     Print #F, "\"
#     @staticmethod
#     def KillDuplicateSSP(path, dataset_id):
#         asvp = glob.glob(path+"\\"+dataset_id+"_*.asvp")
#         ssp = glob.glob(path+"\\"+dataset_id+"_*.ssp")
#         all = asvp+ssp
#         if all:
#             if wx.YES == wx.MessageBox("Do you want to remove the duplicate dataset ID files:\n"+"\n".join(all),
#                           "Confirm Delete", wx.ICON_QUESTION | wx.YES | wx.NO | wx.CENTER, None):
#                 for f in all: 
#                     try:
#                         os.remove(f)
#                     except:
#                         print 'failed to remove',f 
        
        
    def WriteHydrostarFile(self, filename):
        '''
        ' New for Version 8.40
        ' Save the velocity profile in a Hydrostar (Elac) compatible text file
        ' with extension sva.
        '''

    
        #' Get latitude and longitude in proper format.
        #make sure we have all metadata necessary before overwriting file
        try:
            LatStr, LonStr = self.metadata['location'].DMS_Caris()
            header = '#Section '+self.metadata['Year']+'-'+self.metadata['Day']+'  '+self.metadata['Time']+'  '+                          LatStr+'  '+LonStr+'\n'
        except KeyError, e:
            raise MetadataException(str(e))

        SvaFile = file(filename, 'w')
        SvaFile.write("#HYDROSTAR ELAC\n")
        SvaFile.write("#" + os.path.split(filename)[1]+'\n')
        SvaFile.write(header)
        SvaFile.write('.profile 0\n')
        d = self.NoDupes_GoodFlags()
        for r in d:
            SvaFile.write('%10.1f %16.1f\n'%( r['depth'], r['soundspeed']))
    def RaiseIfNotHipsMetadata(self):
        try:
            self.metadata['location']
            self.metadata['Year']
            self.metadata['Day']
            self.metadata['Time']
        except KeyError, e:
            raise MetadataException(str(e))
        
    def WriteHipsFile(self, filename):
    
        #' Save the velocity profile in a Caris HIPS SVP text file (extension svp)
        self.RaiseIfNotHipsMetadata()
        HipsSVPFile = file(filename, 'w')
        HipsSVPFile.write("[SVP_VERSION_2]\n")
        HipsSVPFile.write(os.path.split(filename)[1]+'\n')
        self.AppendHipsFile(HipsSVPFile, sorted = False)
    @staticmethod
    def SortCarisSVPFile(HipsSVPFile):
        q = list(ScipyProfile.parseCarisSvpFile(HipsSVPFile)) #ScipyProfile.parseRawProfile(HipsSVPFile)
        def sort_prof(p1, p2):
            try:
                if p1.metadata['timestamp'] < p2.metadata['timestamp']: return -1
                return 1 if p1.metadata['timestamp'] > p2.metadata['timestamp'] else 0
            except: return -1
        q.sort(cmp=sort_prof)
        q[0].WriteHipsFile(HipsSVPFile) #overwrite the existing data with new file
        for p in q[1:]: #append the rest of the sorted profiles.
            p.AppendHipsFile(HipsSVPFile, sorted=False)
        
    def AppendHipsFile(self, HipsSVPFile, sorted=False):
        ''' HipsSVPFile is an open file object (or something with a write method) or a file path.
        If  HipsSVPFile is a path then sorted will write the data and then read/re-write the data in time sorted order
        A Hips SVP section will be written to the HipsSVPFile.
        '''
        try:
            HipsSVPFile.write #see if it's an open file object
            sort_fname='' #not sorting an open file object
        except AttributeError:
            if isinstance(HipsSVPFile, (basestring)): #try and open the filename
                sort_fname = HipsSVPFile
                if os.path.exists(HipsSVPFile): #file exists??
                    check_svp_format_data = file(HipsSVPFile, 'r').readline().upper()
                    m = re.search("SVP_VERSION", check_svp_format_data)
                    if m:
                        HipsSVPFile = file(HipsSVPFile, 'a') #open for append
                    else:
                        raise DataFileError(HipsSVPFile+" did not have SVP_VERSION in the first line of file -- may not be a Caris SVP file.  Data not written")
                else: #create a new file (needs header info) --  
                    self.WriteHipsFile(HipsSVPFile) # calls this function back with an open file object with header written
                    if sorted:
                        ScipyProfile.SortCarisSVPFile(HipsSVPFile)
                    return #the previous call does the actual write-- don't do it twice
                
        #' Get latitude and longitude in proper format for Caris.
        self.RaiseIfNotHipsMetadata()
        LatStr, LonStr = self.metadata['location'].DMS_Caris()
   
        HipsSVPFile.write("Section " + self.metadata['Year'] + "-" + self.metadata['Day'] + " " + self.metadata['Time'] + \
             " " + LatStr + " " + LonStr + '\n')
        d = self.NoDupes_GoodFlags(spacing = .01)
        for r in d:
            HipsSVPFile.write('%11.2f %17.2f\n'%( r['depth'], r['soundspeed']))
            
        if sort_fname and sorted: #should only be true if a filename was passed, in which case we can close the file handle
            HipsSVPFile.close()
            ScipyProfile.SortCarisSVPFile(sort_fname)
        

    def ExtendCast(self, depth=None):
        '''Extend a cast manually or for simard export just allows a large depth to be input
        '''
        #from Simrad function 
        '''
        ' Version 8.81  Extend further if user requests
        ' Version 8.82  Move the extension computation here so that we can determine the
        ' correct value of number of points for the Simrad file header.
        >>> numpy.hstack((profile_data[:5],numpy.array([(1,2,3)], dtype=profile_data.dtype)))
        array([(0.0, 18.239999771118164, 1513.6600341796875),
               (1.2999999523162842, 15.130000114440918, 1504.18994140625),
               (2.7000000476837158, 15.060000419616699, 1504.0),
               (4.0, 15.060000419616699, 1504.030029296875),
               (5.4000000953674316, 15.060000419616699, 1504.06005859375),
               (1.0, 2.0, 3.0)], 
              dtype=[('depth', '<f4'), ('temperature', '<f4'), ('soundspeed', '<f4')])
        '''
        #Title = "EXTEND CAST FURTHER FOR SIMRAD ??"
        #Msg = "Depth of edited/extended cast is " + str(self['depth'][-1]) + " Meters\n\n" + \
        #      "Do you want to extend cast further for Simrad system ?"
        #dep = wx.GetNumberFromUser(Msg,'Meters', Title, int(self['depth'][-1]), min=int(self['depth'][-1]), max = 12000)
        i = self['depth'].argmax()
        if depth == None: depth = self[i]['depth']*1.3 #30% extension by default
        new_data = numpy.hstack((self, self[i]))
        new_data[-1]['depth'] = depth
        #'Extrapolate linearly using slope of 0.0175 meters/sec per meters of depth.
        new_ss = self[i]['soundspeed'] + 0.0175 * (depth - self[i]['depth'])
        new_ss = min(new_ss,1700) #make sure extended value is reasonable.
        new_ss = max(new_ss, 1400)
        new_data['soundspeed'][-1] = new_ss 
        new_data['flag'][-1] = ScipyProfile.FLAG_EXT_LINEAR
        return ScipyProfile(new_data, **self.get_keyargs())
    
    def ExtendHist(self, historical, Zlast=None):
        '''
        ' Extrapolate cast using historical data as reference.
        ' Algorithm suggested by Dr. Lloyd Huff
        historical is a Profile object with depth, soundspeed and sigma columns (NODC_Climatology module supplies these) 
        '''
        self.sort(order=['depth'])
        if Zlast==None: Zlast = self['depth'].max()
        DepthHist = historical['depth']
        SVHist = historical['soundspeed']
        SigHist = historical['sigma']
        SVflag = self['flag']
        DEPTH = self['depth']
        SV = self['soundspeed']
        IMAX = numpy.searchsorted(DepthHist, Zlast)-1
        if IMAX==-1: IMAX = 0
        Dmax = DepthHist[IMAX] #' Historical depth at which the weighting function is 1.
        Dz = numpy.diff(DEPTH) #numpy.hstack(([0],numpy.diff(DEPTH))) #Delta Z
        Dz = numpy.hstack((Dz, [Dz[-1]]))
        if Zlast<=50: #'Weighting function for interval I
            W = numpy.ones(DepthHist.shape)
        else:
            W = numpy.power(DepthHist/Dmax, numpy.e)
        Vdiff = numpy.zeros(DepthHist.shape)
        R = numpy.zeros(DepthHist.shape)
        #numpy.cumsum(p['depth'])

        for I in range(IMAX+1):
            cond = DEPTH>DepthHist[I]
            if I+1<len(DepthHist):
                cond = numpy.logical_and(cond, DEPTH<DepthHist[I + 1])
            indices = numpy.argwhere(cond).transpose()[0]
            if indices[-1]<len(DEPTH)-2: indices = numpy.hstack((indices, [indices[-1]+1] )) #get one measurement in the next historical band -- not sure why VelocWin did this
            indices = indices.compress(SVflag.take(indices)>=0) #remove any bad flags
            VDZsum = (SV.take(indices)*Dz.take(indices)).sum()
            DZsum = Dz.take(indices).sum()
            Vavg = VDZsum / DZsum 
            Vdiff[I] = Vavg - SVHist[I]
            R[I] = Vdiff[I] / SigHist[I]
            
        Wsum = W[:IMAX+1].sum()
        Rsum = (W*R)[:IMAX+1].sum()
        Vdiffsum = (W*Vdiff)[:IMAX+1].sum()
        Rbar = Rsum / Wsum
        Vdiffbar = Vdiffsum / Wsum

        if IMAX == 0:
            Xbase = 0.9
        else:
            Xbase = numpy.absolute(Vdiff[IMAX] / Vdiff[IMAX - 1])
            if Xbase < 0.5: Xbase = 0.5  #     'Prevents too-fast approach
            if Xbase > 0.9: Xbase = 0.9  #     'Prevents going in wrong direction

        #' Control offset of approach
        if numpy.absolute(0.9 * Vdiffbar) > numpy.absolute(Vdiff[IMAX]): Vdiffbar = Vdiff[IMAX] / 0.9

        #' Compute extrapolated points using historical depths.
        #' Either extrapolate down to deepest historical depth or down 30%.
        newPts = []
        Zcut = DepthHist.max() if DEPTH.max()>300 else Zlast*1.3 #30% deeper if cast < 300m else full range of historical
        Icut = len(DepthHist) if DEPTH.max()>300 else numpy.searchsorted(DepthHist, Zlast*1.3) #30% deeper if cast < 300m else full range of historical
        for I in range(IMAX + 1, Icut):
            ND = DepthHist[I] #new depth
            Iexp = len(newPts)+1
            #new sound speed
            if numpy.absolute(Rbar * SigHist[I]) <= (Xbase ** Iexp) * numpy.absolute(Vdiffbar):
                NSV = SVHist[I] + Rbar * SigHist[I]
            else:
                NSV = SVHist[I] + (Xbase ** Iexp) * Vdiffbar

            NF = ScipyProfile.FLAG_EXT_HIST #new flag
            newPts.append((ND, NSV, NF))

        #add new space at end of array, duplicate all fields from last index and then overwrite SV, Depth, flag
        if newPts:
            new_data = numpy.hstack((self, self[-1].repeat(len(newPts))))
            newPts.reverse() #turn the array around and then count backwards in the array
            for index, pt in enumerate(newPts):
                d, sv, f = pt 
                new_data[-(index+1)]['depth'] = d
                new_data[-(index+1)]['soundspeed'] = sv
                new_data[-(index+1)]['flag'] = f
    
            #' Replace last point with value obtained by linear interpolation between last 2 points.
            #' Note, if we have extrapolated to deepest historical depth,
            #' this step does not change anything.
            Z2 = DEPTH[-1]; Z1 = DEPTH[-2]
            SV2 = SV[-1]; SV1 = SV[-2]
            new_data['depth'][-1] = Zcut
            new_data['soundspeed'][-1] = SV1 + (SV2 - SV1) * (Zcut - Z1) / (Z2 - Z1)
            return ScipyProfile(new_data, **self.get_keyargs())
        else:
            return self.mcopy() #nothing to extend -- just return self

    def ExtendSlope(self):
        '''
        
        ' Compute the most probable slope for a given cast and use it
        ' to extend the cast down by 30%.
        
        ' PROGRAMMER: Dr. Lloyd Huff                     DATE: 2/25/88
        
        ' Modified 9/2008 to avoid division by zero.
        '''
        
        X = self['depth'].compress(self['flag']>=0) #' Get only the good points
        Y = self['soundspeed'].compress(self['flag']>=0)
        #' RLB 9/2008 Adjustment for case of AUV processing, for which there
        #' is a possibility of duplicate max depth points.
        dx = numpy.hstack(([1],numpy.diff(X)))
        X = X.compress(dx>0)
        Y = Y.compress(dx>0)
        XM = X*0.0
        HBC = numpy.zeros([11], numpy.float32)
        CBC = numpy.zeros([11], numpy.float32)
        H = numpy.zeros([11], numpy.float32)
        
        G = len(X) - 2                     # ' Index for next to last point is G
        
        Xmid = 0.5 * (X[G] + X[G + 1]) #' Extrapolation will start from point
        Ymid = 0.5 * (Y[G] + Y[G + 1]) #' halfway between deepest 2 points
        
        NumSlopes = G+1
        for K in range(NumSlopes):
            Dx = X[K] - X[G + 1]
            Dy = Y[K] - Y[G + 1]
            #' Compute slope between last point and all others.
            XM[K] = Dy / Dx
        XMmin = XM[:NumSlopes].min() #' Find the range of slopes
        XMmax = XM[:NumSlopes].max()
        
        Hnum = 10 if NumSlopes > 10 else NumSlopes - 1 #  ' Set # of histogram bins
        HBW = (XMmax - XMmin) / Hnum          #       ' Set width of bins
        for K in range(Hnum):
            HBC[K] = XMmin + (K - 0.5) * HBW    #      ' Set centers of bins
        
        for J in range(NumSlopes):#                    ' Populate histogram
            for I in range(Hnum):#                      ' Weight by depth spacing
                if XM[J] >= HBC[I] - 0.75 * HBW and XM[J] <= HBC[I] + 0.75 * HBW :
                    H[I] = H[I] + X[J + 1] - X[J]

        Hmax = 0
        for I in range(Hnum): #             'Find largest number of entries in bins
            if H[I] >= Hmax: Hmax = H[I]
            if H[I] == Hmax: Slope = HBC[I]
        
        #' Determine if more than one bin has largest number of entries
        Count = 0
        for I in range(Hnum):
            if H[I] == Hmax: Count = Count + 1

        if Count <> 1:
            #' Find which of several bins with largest number of entries
            #' has a slope closest to that between last two points in data set.
            for J in range(Hnum):
                CBC[J] = 500
                if H[J] == Hmax: CBC[J] = numpy.absolute(XM[NumSlopes] - XM[J])

            Ref = 500
            for J in range(Hnum):
                if CBC[J] < Ref: Ref = CBC[J]
                if CBC[J] == Ref: Slope = HBC[J]

        new_data = numpy.hstack((self, self[-1]))
        new_data[-1]['depth'] = 1.3 * X[NumSlopes]  #                 ' Extend cast by 30%
        new_data[-1]['soundspeed'] = Ymid + (new_data[-1]['depth'] - Xmid) * Slope
        new_data[-1]['flag'] = ScipyProfile.FLAG_EXT_SLOPE
        return ScipyProfile(new_data, **self.get_keyargs())

#    def CosineAvg(self, name = 'pressure', binsize=1.0, binwidth=4, WWmin=1.7, WWMul=.0025):
#        '''Returns a new ScipyProfile object with all data columns cosine averaged
#        '''
#        n=list(self.dtype.names[:])
#        n.remove(name)
#        n.insert(name)
#        p = CosineAvg(self, n, binsize, binwidth, WWmin, WWMul)
#        profile_data = p[1:-1]
#        p= ScipyProfile(profile_data, names=n, ymetric="pressure", attribute="temperature", metadata=metadata)
#        return p
    def FitParab(self, Yin, NSpread=3, ymetric=None, xattr=None):
        ''' NOTE! pass in a Y value and recieve an interpolated X, a bit backwards from normal naming 
        Yin is the ymetric (depth/pressure) to get a fitted approximate value at.  
        NSpread is how many points to use around the desired dept/pressure to use in polyfit 
        ymetric and xattr will default the the profile.ymetric and profile.attribute if left as None
        
        Should add the ability to spline the data instead/in addition
        http://docs.numpy.org/doc/numpy/reference/tutorial/interpolate.html
        
        '''
        if ymetric is None: ymetric = self.ymetric
        if xattr==None: xattr = self.attribute
        d = self.NoDupes_GoodFlags()
#        indices = self.argsort(order=[ymetric]) #don't resort the original data 
#        y = self[ymetric].take(indices)
#        x = self[xattr].take(indices)
        d.sort(order=[ymetric]) 
        y = d[ymetric]
        x = d[xattr]
        index = numpy.searchsorted(y, Yin)
        I1 = index-NSpread if index-NSpread>=0 else 0
        I2 = index+NSpread #too large of index doesn't matter in python
        y=y[I1:I2]
        x=x[I1:I2]
        return numpy.poly1d(numpy.polyfit(y,x,2))(Yin)
    def DQA(self, x,y, SN='Unknown'):
        ''' DQA Test using a given depth (pressure) and SV
        x is the xattr quantity (normally sound speed)
        y is the ymetric (normally depth or pressure)
        SN is the serial number of the instrument that measured the passed in x,y
        '''
        x_cast = self.FitParab(y)
        DiffSV = numpy.absolute(x_cast - x)
        DQAResults='\n'+time.ctime()
        DQAResults += "DAILY DQA - SURFACE SOUND SPEED COMPARISON\n\n" #' Start building the Public result message
        if DiffSV > 2:
            DQAResults = DQAResults + " - TEST FAILED - Diff in sound speed > 2 m/sec\n"
        else:
            DQAResults = DQAResults + " - TEST PASSED - Diff in sound speed <= 2 m/sec\n"
         
        # ' Record DQA results
        DQAResults+='\n'
        DQAResults+="Surface sound speed instrument Serial Number: " +SN+'\n'
        DQAResults+="Surface sound speed instrument %s (m): %.1f\n"%(self.ymetric, y) #depth 
        DQAResults+="Surface sound speed Instrument reading (m/sec): %.2f\n"%x
        DQAResults+="Full sound speed profile: " + self.metadata['Filename']+'\n'
        DQAResults+="   Instrument: " + self.metadata['Instrument']+'\n'
        DQAResults+="Profile sound speed at same depth (m/sec): %.1f\n"%x_cast
        DQAResults+="Difference in sound speed (m/sec): %.2f\n"%DiffSV
        return DQAResults, DiffSV
    def AppendProfile(self, p):
        p1 = self.copy() #don't mess with the original arrays
        p2 = p.copy()
        p1.sort(order=[self.ymetric])
        p2.sort(order=[self.ymetric])
        i = numpy.searchsorted(p2[self.ymetric], p1[-1][self.ymetric], side='right')
        newPts = p2[i:]
        new_data = numpy.hstack((p1, p1[-1].repeat(len(newPts)))) #expand the array for new data and default the data to the last measured point
        
        copy_fields = set(newPts.dtype.names).intersection(new_data.dtype.names)
        for pindex in range(len(newPts)):
            index = -(pindex+1) #count backwards throught the newPts and put them in the new array, compute negative indices  
            pt = newPts[index]
            for f in copy_fields: 
                new_data[index][f] = pt[f]
            new_data[index]['flag'] = ScipyProfile.FLAG_EXT_APPEND 
        return ScipyProfile(new_data, **self.get_keyargs())
    def AppendProfileNew(self, p):
        if self[self.ymetric][-1] >= p[self.ymetric][-1]:
            print self[self.ymetric][-1], p[self.ymetric][-1]
            return self
        else:
            p1 = self.copy() #don't mess with the original arrays
            p2 = p.copy()
            p1.sort(order=[self.ymetric])
            p2.sort(order=[self.ymetric])
            i = numpy.searchsorted(p2[self.ymetric], p1[-1][self.ymetric], side='right')
            newPts = p2[i:]
            new_data = numpy.hstack((p1, p1[-1].repeat(len(newPts)))) #expand the array for new data and default the data to the last measured point

            copy_fields = set(newPts.dtype.names).intersection(new_data.dtype.names)
            for pindex in range(len(newPts)):
                index = -(pindex+1) #count backwards throught the newPts and put them in the new array, compute negative indices  
                pt = newPts[index]
                for f in copy_fields: 
                    new_data[index][f] = pt[f]
            return ScipyProfile(new_data, **self.get_keyargs())
# This defines whether everything that sources this file will use the python
# dictionary-based Profile or the numpy.recarray based Profile
# This should be "DictProfile" or "ScipyProfile"
Profile = ScipyProfile
