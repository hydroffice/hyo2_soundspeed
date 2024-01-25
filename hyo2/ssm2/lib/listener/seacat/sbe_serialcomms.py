import os
import traceback
import re
import time
import datetime
import subprocess

try:
    import win32api
    import win32con
except:
    pass  # win32api calls will fail

import serial  # for serial/usb port communication with SBE instruments

from hyo2.ssm2.lib.formats.readers import seabird as sbe_constants
from hyo2.ssm2.app.gui.soundspeedmanager import __version__ as ssm_version

import logging

logger = logging.getLogger(__name__)


# Path to use for Velocipy source and config files
def config_directory():
    return os.path.join(os.path.dirname(__file__), "CONFIG")  # Default configuration files


class UTF8Serial(serial.Serial):
    def write(self, data):
        serial.Serial.write(self, data.encode('utf-8'))

    def read(self, cnt):
        data = serial.Serial.read(self, cnt)
        # print("raw read:", data, self.port, self.baudrate, self.stopbits, self.parity)
        try:
            data = data.decode("utf-8")  # converts from bytes in python 3.x
        except AttributeError:
            pass
        except UnicodeDecodeError:
            data = ""
        # print("decoded data", str(data))
        return str(data)  # converts to ascii for python 2.7, leaves as unicode for 3.x


class SeacatComms:
    '''It seems that the serial module does not clean up nicely.  If an exception occurs the serial port may be held
    until the program exits.
    Make sure to catch all exceptions and close( ) the comm object.
    c.close(); reload(Seacat); c=Seacat.SeacatComms.open_seacat('COM1')
    '''
    # default serial messages for Seacat intruments, override if the particular instrument is different
    INIT_LOGGING = 'IL'
    DISPLAY_STATUS = 'DS'
    DISPLAY_HEADERS = 'DH'
    DISPLAY_SCANS = 'DD'
    DISPLAY_CASTS = 'DC'
    DISPLAY_CALIBRATION = ''
    SET_BAUD = ''
    HEXFORMAT = 'outputformat=0'
    SUPPORTED_BAUDS = (
    600, 9600, 38400, 57600, 1200, 2400, 4800, 19200)  # put the most common baudrates first for auto-search

    def __init__(self, port='COM1', baud=9600, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE,
                 stopbits=serial.STOPBITS_ONE, timeout=.1, parent=None, status=None,
                 num_trys=2, quiet=False, scanbauds=True, progbar=None, prompts=['S>']):
        try:
            self.PROMPTS = prompts
            self.parent = parent
            self.num_trys = num_trys
            self.cache = {}
            if status:
                self.cache['status'] = status
            self.comlink = UTF8Serial(port, baud, bytesize=bytesize, parity=parity, stopbits=stopbits, timeout=timeout)
            # serial module expects utf8 characters
            if progbar:
                progbar.start(title="Communicating with Seacat", max_value=len(self.SUPPORTED_BAUDS) + 1,
                              text="Trying %d" % baud)
            r = self.wake()
            if not any([prompt in r for prompt in self.PROMPTS]):
                # print('prompt is:', self.PROMPTS)
                # print('r=', r)
                # print('Seacat not responding on', self.comlink.port)
                bSuccess = False
                if scanbauds:
                    if progbar:
                        progbar.update(1, text="Scanning " + str(self.SUPPORTED_BAUDS))
                    print('Going to scan bauds:', self.SUPPORTED_BAUDS)
                    for bi, baud in enumerate(self.SUPPORTED_BAUDS):
                        print('Trying ', baud)
                        self.comlink.baudrate = baud
                        r = self.wake()
                        if progbar:
                            progbar.update(value=bi + 2, text="Baud= " + str(baud))
                        # print('looking for '+str(self.PROMPTS)+' in ', r)
                        if any([prompt == r[-len(prompt):] for prompt in self.PROMPTS]):
                            bSuccess = True
                            print('Found at baud rate', baud)
                            break
                if not bSuccess:
                    self.comlink.close()
                    if not quiet:
                        logger.error(
                            "Did not get expected response from Seacat.  Is it connected?  Specified correct com port?")
            if self.comlink.isOpen() and any([prompt in r for prompt in self.PROMPTS]):
                # print('getting status')
                self.original_baud = self.comlink.baudrate
                self.get_status()  # checks and caches a legit return so we can see what kind of seacat it is
        except serial.SerialException as e:
            traceback.print_exc()
            logger.error("Could not open port %s.\nIt's most likely either in use by another program or doesn't exist")
            raise e
        except:
            traceback.print_exc()
            try:
                self.comlink.close()  # in case there is an exception after we open the comlink
            except:
                pass
        if progbar:
            progbar.end()

    def get_com_str(self):
        return self.comlink.port + ": " + ", ".join(
            [str(self.comlink.baudrate), str(self.comlink.parity), str(self.comlink.bytesize),
             str(self.comlink.stopbits)])

    @staticmethod
    def portstr(port):
        s = serial.Serial(port)  # figure out the port string in case an integer was passed in.
        ps = s.portstr
        s.close()
        return ps

    @staticmethod
    def open_seacat(port, dbaud, dbits, dparity, parent=None,
                    progbar=None):  # try and figure out what Seacat it is on the port
        # 19plus and 19plusV2 use the default 8,N,1 while the Original SBE19 uses 7,E,1
        if dbaud and dbits and dparity:  # if it was opened before then try those settings
            cat = SeacatComms(port, baud=dbaud, bytesize=dbits, parity=dparity, quiet=True, scanbauds=False,
                              prompts=["S>", '<Executed/>', "low battery voltage !!!"])  # check for SBE19
            if not cat.isOpen():
                print('did not find seacat at the last comm parameters', dbaud, dbits, dparity)
        else:
            cat = None
        if not cat or not cat.isOpen():
            if progbar:
                progbar.start(title='Scanning for SBE19')
            cat = SeacatComms(port, bytesize=serial.SEVENBITS, parity=serial.PARITY_EVEN, quiet=True,
                              progbar=progbar)  # check for SBE19
            if not cat.isOpen():
                if progbar:
                    progbar.start(title='Scanning for SBE19 Plus, V2')
                cat = SeacatComms(port, quiet=True, progbar=progbar, prompts=["S>", '<Executed/>'])  # find 19plus, V2
        sbe = cat
        if cat.isOpen():
            status = cat.get_status()
            cat.close()
            bd = cat.comlink.baudrate
            if "SBE 19plus V" in status:
                sbe = SBE19PlusV2Comm(port, baud=bd, parent=parent, status=status)
            elif "SeacatPlus V" in status:
                sbe = SBE19PlusComm(port, baud=bd, parent=parent, status=status)
            elif "SEACAT PROFILER" in status:
                sbe = SBE19Comm(port, baud=bd, parent=parent, status=status)
            else:
                print('Unsupported instument type\n', status)
        if sbe.__class__ == SeacatComms:  # last QC check that we have a real instrument
            sbe.close()
        else:
            print('found seacat', sbe.get_type_string(), sbe.comlink.baudrate, sbe.comlink.bytesize, sbe.comlink.parity)

        return sbe

    def Sleep(self):
        self.comlink.write('qs\r')

    def clear_cache(self):
        self.cache = {}

    def isOpen(self):
        return self.comlink.isOpen()

    def close(self):
        self.comlink.close()

    def send_command(self, cmd, maxwait=3.0, quiet=False):
        '''  set cmd==None to just execute a wake call.
        import Seacat; c = Seacat.SBE19PlusV2Comm('COM1', self)
        reload(Seacat); c.__class__ = Seacat.SBE19PlusV2Comm
        '''
        self.comlink.write(
            str('\r'))  # make sure the seacat isn't in standby adn clear any leftover stuff in the comport buffer
        if cmd is not None:
            self.get_response(0.2, quiet=True)  # Seacats takes between 0.5 an 2.5 seconds to wake up.
            self.comlink.write(
                '\r')  # make sure the seacat isn't in standby adn clear any leftover stuff in the comport buffer
            self.get_response(3.0, quiet=True)  # Seacats takes between 0.5 an 2.5 seconds to wake up.
            self.comlink.write(cmd + '\r')  # send our command and then get the repsonse
            print('sending command "%s"' % cmd)
        return self.get_response(maxwait, quiet=quiet)

    def get_response(self, maxwait, quiet=False):
        response = ''
        bFinished = False

        wait_time = 0.0
        while not bFinished and wait_time < maxwait:  # more data to read
            r = self.comlink.read(1000)
            # if len(r)==0: print 'No more data received, full response length = ', len(response)
            # else: print 'got ', len(r), 'characters'
            response += r
            if any([response[-len(prompt):] == prompt for prompt in self.PROMPTS]):
                bFinished = True  # recieved the prompt and nothing else
            if any([re.search(prompt + "[\n\r\s]*$", response) for prompt in self.PROMPTS]):
                bFinished = True  # recieved the prompt and nothing else
            if len(r) == 0:
                wait_time += self.comlink.timeout
            else:
                wait_time = 0.0  # restart the clock

        if bFinished:
            if not quiet:
                print('finished receiving response')
        else:
            if not quiet:
                print('Timed out waiting for seacat to respond')
        return response

    def check_message(self, msg):
        if not any([msg[-len(prompt):] != prompt for prompt in self.PROMPTS]):
            if any([re.search(prompt + "[\n\r\s]*$", msg) for prompt in
                    self.PROMPTS]):  # let there be spaces or newlines after the prompt -- this is occuring on Seacat 19 v2.1e and v2.1n
                print(
                    "WARNING!\nThere was a trailing newline or space\nThis is only expected on a Seacat 19, firmware 2.1e - 2.1n.\nIf this is not your model there may be problems\nWARNING!\n")
                return True
            else:
                print(msg)
                print(
                    "Something didn't seem right with message -- doesn't end with Seacat Prompt %s -- see above" % str(
                        self.PROMPTS))
                return False
        else:
            return True

    def wake(self):
        '''SBE19 v2.0 firmware takes up to three seconds to wake.  SBE19Plus takes about 1.5 seconds.
        SBE19Plus V2 takes about .75 seconds.  This function should return faster is the seacat
        is already awake since it will return the prompt and the send_command will read that and return immediately.
        Call send_command "\r" three times in case we changed bauds and there is some garbled stuff in the com port.
        '''
        _r = self.send_command(None, 1.0, quiet=True)
        _r = self.send_command(None, 1.0, quiet=True)
        r = self.send_command(None, 1.0)
        self.check_message(r)
        return r

    def _set_baud(self, rate, cmd):
        orig_baud = self.comlink.baudrate
        print(orig_baud, rate, cmd)
        ra = self.send_command(cmd, 0.5)  # wake the seacat and request change of baud
        self.comlink.baudrate = rate  # switch to the new baud
        # If confirmation is required (at least SBE19 V2) send the command again on the new baud
        # can't use send_command since it sends extra \r commands to make sure the seacat is awake, they interfere with the confirmation
        time.sleep(0.2)  # seems the V2 is not switching to new baud fast enough, give it a moment to change bauds.
        self.comlink.write(cmd + '\r')
        rb = self.get_response(1.0)
        r = ra + rb
        r2 = self.send_command('')  # see if we get the prompt
        if not any([prompt in r2 for prompt in self.PROMPTS]):
            print("Appears the seacat didn't change baud, staying at ", orig_baud)
            self.comlink.baudrate = orig_baud
        else:
            print("Switched to baud", rate)
        return r + r2

    def get_status(self, force=False):
        '''
        'ds\r\nSeacatPlus V 1.6b  SERIAL NO. 4677    05 Mar 2010  16:01:56\r\nvbatt = 13.4, vlith =  8.2, ioper =  60.7 ma, ipump =  45.4 ma, \r\nstatus = not logging\r\nnumber of scans to average = 1\r\nsamples = 1374, free = 761226, casts = 2\r\nmode = profile, minimum cond freq = 3258, pump delay = 40 sec\r\nautorun = no, ignore magnetic switch = no\r\nbattery type = alkaline, battery cutoff =  7.3 volts\r\npressure sensor = strain gauge, range = 508.0\r\nSBE 38 = no, Gas Tension Device = no\r\nExt Volt 0 = no, Ext Volt 1 = no, Ext Volt 2 = no, Ext Volt 3 = no\r\necho commands = yes\r\noutput format = raw HEX\r\nS>'
        '''
        if not force and self.cache.get('status', None):
            r = self.cache['status']
        else:
            r = self.send_command(self.DISPLAY_STATUS,
                                  maxwait=5.0)  # Display Status can be really slow -- Bob Ramsey was seeing a pause greater than 3sec
            if self.check_message(r):
                self.cache['status'] = r
        return r

    def init_logging(self):
        self.send_command(self.INIT_LOGGING, quiet=True)  # send init logging and get the confirm prompt
        print('Sending confirmation')
        self.comlink.write('y\r')  # send the yes confirmation
        r = self.get_response(2.0)
        return r

    def get_headers(self):
        if self.cache.get('headers', ''):
            ret = self.cache['headers']
        else:
            r = self.send_command(self.DISPLAY_HEADERS)  # split into list of headers
            if not self.check_message(r):
                logger.info("Headers didn't download correctly.  Trying to download headers again\n")
                r = self.send_command(self.DISPLAY_HEADERS)  # split into list of headers

            ret = {}
            if self.check_message(r):
                for line in r.splitlines(True):
                    m = re.search("cast\s+(?P<cn>\d+)\s+\d+", line)
                    if m:
                        ret[int(m.group('cn'))] = line
                self.cache['headers'] = ret
        return ret

    def get_calibration(self):
        if self.cache.get('calibration', None):
            r = self.cache['calibration']
        else:
            r = self.send_command(self.DISPLAY_CALIBRATION)  # split into list of headers
            self.check_message(r)
            self.cache['calibration'] = r
        return r

    def get_casts(self, cast_numbers=[1], progbar=None, cast_command='DC', nhead=1, nfoot=1):
        '''nhead is the number of header lines expected before data,
        nfoot is number of footer lines.  Typically this is one for the Seacat prompt "S>" -- it doesn't matter if there is an ending \r, \n, \r\n or nothing as the splitlines will return the S> in all cases
        '''
        h = self.get_headers()
        casts_in_device = set(h.keys())
        if not casts_in_device.issuperset(cast_numbers):
            raise ValueError(
                "There is a bad cast number in the request %s.  Number of casts in the Seabird device = %s" % (
                str(cast_numbers), str(casts_in_device)))
        ret = {}
        if progbar:
            progbar.start(min_value=0, max_value=len(cast_numbers), title='Downloading',
                          text="Download %d casts" % len(cast_numbers))
        for index, n in enumerate(cast_numbers):
            m = re.search("samples\s*(?P<start>\d+)\s*to\s*(?P<end>\d+)", h[n])
            if m:
                expected_lines = int(m.group('end')) - int(m.group('start')) + 1
            else:
                logger.info("couldn't read the header -- corrupt or unsupported format\n")
                expected_lines = -1
            if progbar:
                progbar.update(value=index, text="Downloaded %d of %d casts" % (index, len(cast_numbers)))
            ret[n] = []
            for t in range(self.num_trys):
                r = self.send_command(cast_command + str(n))  # split into list of casts
                if self.check_message(r):
                    lines = r.splitlines()[nhead:-nfoot]
                    if expected_lines < 0 or len(lines) == expected_lines:
                        if min([min(l) for l in lines]) >= '0' and max([max(l) for l in lines]) <= 'F':
                            ret[n] = lines
                            break
                        else:
                            logger.info('found corrupt data on try %d of %d\n' % (t, self.num_trys))
                    else:
                        logger.info('Did not receive right amount of data lines (%d of %d) on try %d of %d\n' % (
                        len(lines), expected_lines, t + 1, self.num_trys))
        return ret

    def set_datetime(self, dt):
        raise Exception('Overload this')

    def get_datetime(self):
        raise Exception('Overload this, return a datetime object')

    def get_scans(self):
        _r = self.send_command(self.HEXFORMAT)
        r = self.send_command(self.DISPLAY_SCANS)  # split into list of scans
        self.check_message(r)
        return r

    def get_voltages(self):
        raise Exception('Overload this')

    def GetCastTime(self, castnumber=1):
        raise Exception('Overload this')
        # return yr, doy, hour, minute, second  # return this format

    def download(self, path, cast_numbers=[1], progbar=None):
        casts = self.get_casts(cast_numbers, progbar=progbar)
        headers = self.get_headers()
        written = []
        if progbar:
            progbar.update(value=progbar.max, text='Done downloading samples -- now saving to disk')  # force to 100%
        for n in cast_numbers:
            if len(casts[n]) > 1:
                fname = os.path.join(path, "%04d_%03d_%02d%02d%02d.HEX" % (self.get_cast_time(n)))
                fname = MakeUniqueFilename(fname)[0]
                logger.info("Saving cast %d to %s\n" % (n, fname))
                f = open(fname, 'wb')

                def WriteHeaderLines(data):
                    for line in data.splitlines(True):
                        f.write(bytes(('* ' + line).encode('utf-8')))

                WriteHeaderLines(self.get_hexheader(fname))
                WriteHeaderLines(self.get_status())
                if self.DISPLAY_CALIBRATION:
                    WriteHeaderLines(self.get_calibration())  # SBE19 doesn't have this command
                WriteHeaderLines(headers[n])
                f.write(bytes('*END*\r\n'.encode('utf-8')))  # end of header marker
                f.write(bytes(("\r\n".join(casts[n])).encode('utf-8')))
                f.close()
                written.append(fname)
            else:
                logger.info(
                    'Cast %d did not contain enough data -- header is shown on the next line\n%s\n' % (n, headers[n]))
        return written

    def get_num_casts_in_device(self):
        raise Exception('Overload this function!')

    def get_type_string(self):
        raise Exception('Overload this function!')

    def get_serialnum(self):
        raise Exception('Overload this function!')

    def get_hexheader(self, fname):
        head = 'Sea-Bird %s Data File:\r\n' % self.get_type_string()
        head += 'FileName = %s\r\n' % fname
        head += 'Software Version %s\r\n' % ssm_version
        sn = int(self.get_serialnum())
        head += 'Temperature SN = %04d\r\n' % sn
        head += 'Conductivity SN = %04d\r\n' % sn
        head += 'System UpLoad Time = %s\r\n' % time.strftime("%b %d %Y %H:%M:%S")
        return head

    def RunTest(self, fname):
        f = open(fname, 'w')

        def R(func):
            try:
                f.write('Trying ' + func.__name__ + '\n')
                r = func()
                f.write(str(r))  # the data comes with newlines over the serial port
            except Exception as e:
                f.write(str(e) + '\n')

        R(self.get_status)
        R(self.get_voltages)
        R(self.get_headers)
        R(self.get_casts)
        R(self.get_scans)
        R(self.get_calibration)


class SBE19Comm(SeacatComms):
    '''Standard instruments are set to 7 data bits, even parity
    Firmware Versions Less than 3.0:
    baud rate = 9600
    upload baud rate = 9600
    Firmware Versions 3.0 or greater:
    baud rate = 600
    upload baud rate is programmable to 600, 1200, 9600, 19200, or 38400
    use slower upload baud rates with slow computers and long cables.
    use 38400 baud with short cables and 386- or 486-based PCs.

    ST(CR) Set date and time as prompted
    Example: ST(CR)
    date (MMDDYY) = 042387(CR)
    time (HHMMSS) = 191026(CR)
    The date is set to April 23, 1987. The time is set to 19:10:26.

    '''
    SET_BAUD = 'SB'
    DISPLAY_CASTS = 'DC'  # supposed to set baud to 9600 for transfer
    SUPPORTED_BAUDS = (600, 9600, 1200, 4800)
    CRTL_C = chr(3)
    CTRL_Y = chr(25)

    def __init__(self, port, baud=600, parent=None, **kywds):
        SeacatComms.__init__(self, port, baud=baud, bytesize=serial.SEVENBITS, parity=serial.PARITY_EVEN, parent=parent,
                             **kywds)
        status = self.get_status()
        m = re.search(r'SEACAT\sPROFILER\s*V(\d)(\.(\d))?', status)
        if m:
            self.firmware_major = int(m.group(1))
            self.firmware_minor = int(m.group(3) if m.group(3) is not None else 0)

    def get_num_casts_in_device(self):
        status = self.get_status()
        m = sbe_constants.SeacatHex_SBE19_NCASTSRE.search(status)
        ncasts = 0
        if m:
            ncasts = int(m.group('NumCasts'))
        return ncasts

    def get_datetime(self):
        status = self.get_status(True)  # force refresh of the clock
        m = re.search(sbe_constants.SEACAT_SBE19_STATUS_DATETIME, status)
        if m:
            mon, day, yr = int(m.group('month')), int(m.group('day')), int(m.group('year'))
            hr, minutes, sec = int(m.group('hour')), int(m.group('minute')), int(m.group('second'))
            if yr < 80:
                yr += 2000
            if yr < 100:
                yr += 1900
            dt = datetime.datetime(yr, mon, day, hr, minutes, sec)
        else:
            dt = datetime.datetime(1980, 1, 1)
        return dt

    def get_casts(self, cast_numbers=[0], progbar=None):
        if progbar:
            progbar.start(title="Download", text='Downloading headers', max_value=len(cast_numbers))
        print(self.firmware_major)
        if self.firmware_major >= 3:
            # orig_baud = self.comlink.baudrate
            # self.set_baud(max(self.SUPPORTED_BAUDS))
            ''' B = 1 600 baud    B = 2 1200 baud
                B = 3 9600 baud   B = 4 19,200 baud
                B = 5 38,400 baud
                DC[Bn](CR) Display raw data from cast n at the baud rate determined by B.
                If n is omitted, data from cast 0 displayed.
            '''
            B = {600: '1', 1200: '2', 9600: '3', 19200: '4', 38400: '5'}[self.comlink.baudrate]
            dc_command = self.DISPLAY_CASTS + B  # don't change the baud rate as I haven't tested that
        else:
            dc_command = self.DISPLAY_CASTS
        print(dc_command)
        ret = SeacatComms.get_casts(self, cast_numbers, progbar=progbar, cast_command=dc_command, nhead=2)
        if self.firmware_major >= 3:
            # self.set_baud(orig_baud)
            pass
        return ret

    def set_datetime(self, dt):
        _r = self.send_command('ST', quiet=True)
        datestr = dt.strftime('%m%d%y')
        print('Sending date', datestr)
        self.comlink.write(datestr + '\r')  # '031010'
        _r = self.get_response(2.0, quiet=True)
        timestr = dt.strftime('%H%M%S')
        print('Sending Time', timestr)
        self.comlink.write(timestr + '\r')  # '140828'
        r = self.get_response(2.0)
        return r

    def set_baud(self, rate):
        rate = int(rate)
        try:
            n = {600: '1', 1200: '2', 9600: '3'}[rate]
            r = self._set_baud(rate, self.SET_BAUD + n)
        except KeyError:
            print(rate, 'invalid rate')
            r = ''
        return r

    def init_logging(self):
        self.send_command(self.INIT_LOGGING, quiet=True)  # send init logging and get the confirm prompt
        print('Sending first confirmation')
        self.comlink.write('y\r')  # send the yes confirmation
        _r = self.get_response(2.0, quiet=True)
        print('Sending second confirmation')
        self.comlink.write(self.CTRL_Y + '\r')  # send the yes confirmation
        r = self.get_response(2.0)
        return r

    def get_type_string(self):
        return 'SBE19'

    def get_voltages(self):
        status = self.get_status()
        r = ''
        for line in status.splitlines():
            m = re.search("vmain", line, re.IGNORECASE)
            n = re.search("battery", line, re.IGNORECASE)
            if m or n:
                r += line + '\r\n'
        return r

    def get_serialnum(self):
        status = self.get_status()
        m = re.search(r'SEACAT PROFILER.*?SN\s+(?P<SN>\d+)', status)
        if m:
            sn = m.group('SN')
        else:
            sn = '0000'
        return sn

    def get_cast_time(self, castnumber=1):
        n = self.get_num_casts_in_device()
        if castnumber > n:
            raise ValueError(
                "castnumber %d is higher than the number of casts in the Seabird device %d" % (castnumber, n))
        header = self.get_headers()[castnumber]
        cur_yr, cur_mon, _cur_day = time.gmtime()[:3]
        m = sbe_constants.SEACAT_SBE19_HEX_MONTHDAYRE.search(header)
        mon, day = int(m.group('month')), int(m.group('day'))
        m = sbe_constants.SEACAT_SBE19_HEX_TIMERE.search(header)
        hour, minute, second = int(m.group('hour')), int(m.group('minute')), int(m.group('second'))
        if cur_mon < mon - 1:  # looking for December - January rollover
            yr = cur_yr - 1
        else:
            yr = cur_yr
        doy = datetime.datetime(yr, mon, day).timetuple().tm_yday
        return (yr, doy, hour, minute, second)


# status='DS\r\nSEACAT PROFILER  V2.0c  SN 219   03/28/10  18:55:10.689\r\npressure sensor: serial no = 133813,  range = 5000 psia,  tc = -131\r\nclk = 32768.172   iop = 121   vmain = 8.4   vlith = 5.4\r\nncasts = 2   samples = 0   free = 43315   lwait = 0 msec\r\nsample rate = 1 scan every 0.5 seconds\r\nbattery cutoff = 5.8 volts\r\nnumber of voltages sampled = 0\r\nS>'


class SBE19PlusComm(SeacatComms):
    '''The SBE 19plus receives setup instructions and outputs diagnostic information
    or previously recorded data via a three-wire RS-232C link, and is factoryconfigured
    for 9600 baud, 8 data bits, 1 stop bit, and no parity.
    19plus RS-232 levels are directly compatible with standard serial interface cards
    (IBM Asynchronous Communications Adapter or equal). The communications
    baud rate can be changed using Baud= (see Command Descriptions in
    Section 4: Deploying and Operating SBE 19plus).

    MMDDYY=mmddyy Set real-time clock month, day, year.
    Follow with HHMMSS= or it will not set date.
    DDMMYY=ddmmyy Set real-time clock day, month, year.
    Follow with HHMMSS= or it will not set date.
    HHMMSS=hhmmss Set real-time clock hour, minute, second.
    '''
    INIT_LOGGING = "InitLogging"
    DISPLAY_CALIBRATION = 'DCal'
    SET_BAUD = 'Baud='
    SUPPORTED_BAUDS = (9600, 38400, 600, 19200, 1200, 2400, 4800)

    def __init__(self, port, baud=9600, parent=None, **kywds):
        SeacatComms.__init__(self, port, parent=parent, **kywds)

    def get_num_casts_in_device(self):
        status = self.get_status()
        m = sbe_constants.SeacatHex_SBE19PLUS_NCASTSRE.search(status)
        ncasts = 0
        if m:
            ncasts = int(m.group('NumCasts'))
        return ncasts

    def set_baud(self, rate):
        rate = str(rate)
        if int(rate) in self.SUPPORTED_BAUDS:
            r = self._set_baud(int(rate), self.SET_BAUD + rate)
        else:
            print(rate, 'is an invalid rate, supported:', self.SUPPORTED_BAUDS)
            r = ''
        return r

    def get_voltages(self):
        status = self.get_status()
        r = ''
        for line in status.splitlines():
            m = re.search("vbatt", line, re.IGNORECASE)
            n = re.search("battery", line, re.IGNORECASE)
            if m or n:
                r += line + '\r\n'
        return r

    def get_datetime(self):
        status = self.get_status(True)
        m = re.search(sbe_constants.SEACAT_SBE19PLUS_STATUS_DATETIME, status)
        if m:
            y, mon, d = time.strptime(' '.join([m.group('day'), m.group('month'), m.group('year')]),
                                      sbe_constants.SEACAT_SBE19PLUS_HEX_DATE_TXT_FORMAT)[:3]
            hr, minutes, sec = int(m.group('hour')), int(m.group('minute')), int(m.group('second'))
            dt = datetime.datetime(y, mon, d, hr, minutes, sec)
        else:
            dt = datetime.datetime(1980, 1, 1)
        return dt

    def set_datetime(self, dt):
        _r = self.send_command('MMDDYY=' + dt.strftime('%m%d%y'))  # '031010'
        _r = self.send_command('HHMMSS=' + dt.strftime('%H%M%S'))  # '140828'

    def get_type_string(self):
        return 'SBE19Plus'

    def get_serialnum(self):
        status = self.get_status()
        m = re.search(r'SeacatPlus.*?SERIAL\sNO\.\s+(?P<SN>\d+)', status)
        if m:
            sn = m.group('SN')
        else:
            sn = '0000'
        return sn

    def get_cast_time(self, castnumber=1):
        n = self.get_num_casts_in_device()
        if castnumber > n:
            raise ValueError(
                "castnumber %d is higher than the number of casts in the Seabird device %d" % (castnumber, n))
        header = self.get_headers()[castnumber]
        m = sbe_constants.SEACAT_SBE19PLUS_HEX_DATE_TXTRE.search(header)
        if m:
            yr, mon, day = time.strptime(m.group('full'), sbe_constants.SEACAT_SBE19PLUS_HEX_DATE_TXT_FORMAT)[:3]
        else:
            m = sbe_constants.SEACAT_SBE19PLUS_HEX_DATE_MDYRE.search(header)
            yr = int(m.group('year'))
            mon = int(m.group('month'))
            day = int(m.group('day'))
        m = sbe_constants.SEACAT_SBE19PLUS_HEX_TIMERE.search(header)
        hour, minute, second = int(m.group('hour')), int(m.group('minute')), int(m.group('second'))
        doy = datetime.datetime(yr, mon, day).timetuple().tm_yday
        return (yr, doy, hour, minute, second)

    def get_casts(self, cast_numbers=[1], progbar=None):
        if progbar:
            progbar.start(text='Changing baud and downloading headers', max_value=len(cast_numbers))

        orig_baud = self.comlink.baudrate
        self.set_baud(max(self.SUPPORTED_BAUDS))
        _r = self.send_command(self.HEXFORMAT)
        ret = SeacatComms.get_casts(self, cast_numbers, progbar, cast_command=self.DISPLAY_CASTS)
        self.set_baud(orig_baud)
        return ret


class SBE19PlusV2Comm(SBE19PlusComm):
    '''
    The SBE 19plus V2 receives setup instructions and outputs diagnostic
    information or previously recorded data via a three-wire RS-232C link, and is
    factory-configured for 9600 baud, 8 data bits, 1 stop bit, and no parity.
    19plus V2 RS-232 levels are directly compatible with standard serial interface
    cards (IBM Asynchronous Communications Adapter or equal). The
    communications baud rate can be changed using BaudRate= (see Command
    Descriptions in Section 4: Deploying and Operating SBE 19plus V2).
    '''
    SET_BAUD = 'BaudRate='
    SUPPORTED_BAUDS = (9600, 38400, 600, 57600, 19200, 1200, 2400,
                       4800)  # 115200 is claimed in the manual but it didn't work in testing.  Not certain if its the com port or the Seacat's problem

    def __init__(self, port, baud=9600, parent=None, **kywds):
        SBE19PlusComm.__init__(self, port, parent=parent, prompts=['S>', '<Executed/>'], **kywds)

    def set_baud(self, rate):
        r = SBE19PlusComm.set_baud(self, rate)
        return "baud rate command is confirmed" in r.lower()

    def get_type_string(self):
        return 'SBE19Plus V2+'

    def get_datetime(self):
        status = self.get_status(True)
        m = re.search(sbe_constants.SEACAT_SBE19PLUSV2_STATUS_DATETIME, status)
        if m:
            y, mon, d = time.strptime(' '.join([m.group('day'), m.group('month'), m.group('year')]),
                                      sbe_constants.SEACAT_SBE19PLUS_HEX_DATE_TXT_FORMAT)[:3]
            hr, minute, sec = int(m.group('hour')), int(m.group('minute')), int(m.group('second'))
            dt = datetime.datetime(y, mon, d, hr, minute, sec)
        else:
            dt = datetime.datetime(1980, 1, 1)
        return dt

    def get_serialnum(self):
        status = self.get_status()
        m = re.search(r'SBE 19plus V.*?SERIAL\sNO\.\s+(?P<SN>\d+)', status)
        if m:
            sn = m.group('SN')
        else:
            sn = '0000'
        return sn

    def init_logging(self):
        # somewhere in the V2 series the init logging changed style?  Try old way and new ways and see if they work.
        self.send_command(self.INIT_LOGGING, quiet=True)  # send init logging and get the confirm prompt
        # print('Sending confirmation')
        self.comlink.write('y\r')  # send the yes confirmation
        _r = self.get_response(2.0)

        self.send_command(self.INIT_LOGGING, quiet=True)  # send init logging and get the confirm prompt
        # print('Sending confirmation')
        self.comlink.write(self.INIT_LOGGING + '\r')  # send the yes confirmation
        r = self.get_response(2.0)
        return r


class TestComm19Plus(SBE19PlusComm):
    def get_status(self):
        return 'DS\r\nSBE 19plus V 2.2b  SERIAL NO. 6122    12 Mar 2010 03:03:20\r\nvbatt = 13.4, vlith =  8.6, ioper =  62.6 ma, ipump =  39.1 ma, \r\nstatus = not logging\r\nnumber of scans to average = 1\r\nsamples = 1613, free = 5980036, casts = 9\r\nmode = profile, minimum cond freq = 3023, pump delay = 60 sec\r\nautorun = no, ignore magnetic switch = no\r\nbattery type = alkaline, battery cutoff =  7.5 volts\r\npressure sensor = strain gauge, range = 870.0\r\nSBE 38 = no, OPTODE = no, Gas Tension Device = no\r\nExt Volt 0 = no, Ext Volt 1 = no\r\nExt Volt 2 = no, Ext Volt 3 = no\r\nExt Volt 4 = no, Ext Volt 5 = no\r\necho characters = yes\r\noutput format = raw HEX\r\nS>'


def MakeUniqueFilename(newname):
    bDuplicates = False
    while os.path.exists(newname):
        place = newname.find('.')  # returns -1 if not found
        if place == -1:
            place = len(newname)  # put underscore at end of name
        newname = newname[:place] + '_' + newname[place:]
        bDuplicates = True
    return newname, bDuplicates


def scan_for_comports():
    """scan for available ports. return a list of tuples (num, name)"""
    available = []
    for i in range(1, 256):
        try:
            port = 'COM' + str(i)
            s = serial.Serial(port)
            available.append(port)
            s.close()  # explicit close 'cause of delayed GC in java
        except serial.SerialException as e:
            if 'access is denied' in str(e).lower():
                available.append(port)
    return available


def get_num_casts(strHexFile, strSeacatType):
    ''' Get number of casts retrieved from Seacat of type strSeacatType.
        Inspect a retrieved raw data file strHexFile.
    '''
    print(strHexFile, strSeacatType)
    hexdata = open(strHexFile, 'rb').read()
    if strSeacatType == "SBE19":
        ncasts = sbe_constants.SeacatHex_SBE19_NCASTSRE.search(hexdata).group('NumCasts')
    elif strSeacatType in ("SBE19Plus",):
        ncasts = sbe_constants.SeacatHex_SBE19PLUS_NCASTSRE.search(hexdata).group('NumCasts')
    return int(ncasts)


def view_con_report(path, seabird_utils_dir, parent=None):
    # cmd = GetSeabirdDir()+'ConReport.exe'
    cmd = os.path.join(seabird_utils_dir, 'ConReport.exe')
    p = subprocess.Popen(" ".join(['"' + cmd + '"',
                                   '"' + path + '"',
                                   '"' + os.path.dirname(path) + '"',
                                   ]))  # RUN datcnv to obtain new.cnv
    p.wait()
    try:
        win32api.ShellExecute(0, 'open', path, None, "", win32con.SW_SHOW)
    except:
        subprocess.Popen('Notepad.exe "' + os.path.splitext(path)[0] + '.txt"')


def get_serialnum(hexfile_path):
    hexdata = open(hexfile_path, 'rb').read().decode("utf-8")
    m = sbe_constants.SeacatHex_SNRE.search(hexdata)
    if not m:
        logger.debug('''"Unable to get serial number.

             Check raw data file %s''' % hexfile_path)
        sn = None
    else:
        sn = m.group('SN')
    return sn


def get_confile_name(serial_num, inpath):
    conname = None
    # allow for leading zero on the serial number -- 219 becomes 0219
    for filename in (serial_num + ".con",
                     '0' + serial_num + ".con",
                     serial_num + ".xmlcon",
                     '0' + serial_num + ".xmlcon"):
        if os.path.exists(os.path.join(inpath, filename)):
            conname = os.path.join(inpath, filename)
    return conname


def convert_hexfile(hexfile_path, confile_path, seabird_utils_dir, parent=None):
    '''
    Process raw CTD data using Sea-Bird's software SBEDataProcessing, Version >= 5.31.
    This sub introduced in Velocwin 8.84 to override CatOpt3 which uses Version 5.27a.

    Post-Cast data retrieval for the SBE SEACAT profiler
    produced file YYDDDHHM.Mex in CATFILES directory. This hex file consists of:
        1. Headers - ASCII records containing serial number, software version,
                     upload time, status message, and cast date/time.
        2. Data    - Unmodified raw data in HEX.

    This subprogram, runs Sea-Bird program SBEDataProcessing DatCnvW.exe and Derive.exe, to
    convert the hex data to engineering units. More headers are added including maximum and
    minimum values of each oceanographic parameter and calibration date for each sensor.

    SBEDataProcessing also converts the hexadecimal raw data file (*.hex) or
    binary raw data file (.dat) from an SBE911 CTD to engineering units.

    DatCnvW converts only the primary variables pressure, temperature, conductivity.
    The program setup file (.psa) is used in conjunction with DatCnvW.exe.
    DeriveW computes oceanographic variables salinity, density, sound velocity.
    The program setup file Derive.psa) is used in conjunction with DeriveW.exe

    All conversion program files are in directory SBEDataProcPath
    Resulting output file is YYDDDHHM.Mnv, also saved in CATFILES directory.

    New in Version 8.96 Derive.psa specifies Chen-Millero rather than Wilson
            Dim SerialNum As String                   ' Serial number of SeaBird CTD
            Dim RawDataFile As String                 ' User-selected raw data file
            Dim ConvertedFile As String               ' Output CNV file - headers and ascii columns
            Dim SeaBirdType As String                 ' SBE Type: SBE19 or SBE19PLus or SBE 911
            Dim PsaFile As String                     ' Name of psa file
    '''

    hexdata = open(hexfile_path, 'rb').read().decode("utf-8")
    header = hexdata.split('\n')[0]
    # Determine the SeaBird type and serial number from input file.
    if sbe_constants.SeacatHex_SBE19PLUS_TYPERE.search(header):
        seacat_type = 'SBE19Plus'
    elif sbe_constants.SeacatHex_SBE19_TYPERE.search(header):
        seacat_type = 'SBE19'
    elif sbe_constants.SeacatHex_SBE911_TYPERE.search(header):
        seacat_type = 'SBE911'
    elif sbe_constants.SeacatHex_SBE49_TYPERE.search(header):
        seacat_type = 'SBE49'
    else:
        seacat_type = ''
    if not seacat_type:
        Msg = '''Unable to determine SeaBird type (SBE19, SBE19plus, or SBE 911).
              Returning to Main Menu.

              Check first record of raw data file %s
              FirstLine: %s''' % (hexfile_path, header)
        Title = "UNEXPECTED FIRST RECORD IN HEX RAW DATA FILE"
        return False, (Title, Msg)
    else:
        # Switches -- per the seabird docs -- v5.37e, 7.20b
        # /cString    Use String as instrument configuration (.con) file. String must include full path and file name.
        #     Note: If using this parameter, you must also specify input file name (using  /iString).
        # /iString    Use String as input file name. String must include full path and file name.
        #     The /iString parameter supports standard wildcard expansion:
        #     ? matches any single character in the specified position within the file name or extension
        #     * matches any set of characters starting at the specified position within the file name or extension and continuing until the end of the file name or extension or another specified character
        # /oString    Use String as output directory (not including file name).
        # /fString    Use String as output file name (not including directory).
        # /aString    Append String to output file name (before file name extension).
        # /pString    Use String as Program Setup (.psa) file. String must include full path and file name.
        #     NOTE: Previous versions (5.30a and earlier) of SBE Data Processing used program setup files with a .psu extension instead of a .psa extension.
        #     Program setup files with a .psa extension can be opened, viewed, and modified in any text editor or XML editor. SBE Data Processing can still use your existing .psu files.
        #     However, if you make any changes to the setup (for example, change output variables), SBE Data Processing will save the changes to a new .psa file.
        # /xModule:String    Use String to define an additional parameter to pass to Module. Not all modules have x parameters; see module descriptions.
        #     If specifying multiple x parameters, enclose in double quotes and separate with a space.
        #     Example: Run Data Conversion from command line, telling it to skip first 1000 scans:
        #     datcnvw.exe /xdatcnv:skip1000
        # /s    Start processing now.

        # Changed from copying data to sea-bird dir and moving files around to just using command line switches

        # DatCnv.psa depends on instrument (SBE19 or SBE19plus or SBE911 hex or SBE911 dat)
        # Derive.psa is the same for all.
        if seacat_type == 'SBE911' and hexfile_path[-2:].lower() == 'ex':
            psafile = os.path.join(config_directory(), "DatCnv" + seacat_type + "Hex.psa")
        else:
            # if seacat_type=='SBE49':
            psafile = os.path.join(config_directory(), "DatCnv" + seacat_type + ".psa")

        cnv_directory = os.path.dirname(hexfile_path)
        temp_cnv_filename = os.path.join(cnv_directory, os.path.basename(hexfile_path)[:-3] + 'to_derive.cnv')
        temp_cnv_filename, _ = MakeUniqueFilename(temp_cnv_filename)
        cnv_output_filename = os.path.join(cnv_directory, os.path.basename(hexfile_path)[:-3] + 'cnv')
        cnv_output_filename, _ = MakeUniqueFilename(cnv_output_filename)
        # For some reason when using subprocess.call the seabird programs would fail on paths with spaces in the argument list
        #    and not take quoted strings which worked on command line
        # subprocess.Popen with quoted strings works properly
        p = subprocess.Popen(" ".join(['"' + os.path.join(seabird_utils_dir, 'datcnvw.exe') + '"',
                                       '/c"' + confile_path + '"',
                                       '/i"' + hexfile_path + '"',
                                       '/o"' + cnv_directory + os.path.sep + '"',
                                       '/f"' + os.path.basename(temp_cnv_filename) + '"',
                                       '/p"' + psafile + '"',
                                       '/s']))  # RUN datcnv to obtain new.cnv
        p.wait()
        try:
            p = subprocess.Popen(" ".join(['"' + os.path.join(seabird_utils_dir, 'derivew.exe') + '"',
                                           '/c"' + confile_path + '"',
                                           '/i"' + temp_cnv_filename + '"',
                                           '/o"' + cnv_directory + os.path.sep + '"',
                                           '/f"' + os.path.basename(cnv_output_filename) + '"',
                                           '/p"' + os.path.join(config_directory(), 'derive.psa') + '"',
                                           '/s']))  # RUN derivew to obtain additional parameters
            p.wait()
        except:
            pass
        try:
            os.remove(temp_cnv_filename)
        except:
            pass  # conversion failed??
        # Check that output file got there.
        if not os.path.exists(cnv_output_filename):
            Msg = 'Error occurred running Data Processing Programs\n\n' \
                  'If you are processing SEACAT data, please rerun SEACAT PostCast Data Retrieval'
            Title = "ERROR RUNNING SBEDataProcessing-Win32"
            return False, (Title, Msg)
        else:
            return True, cnv_output_filename  # success, on failure returns None


'''
Dim Zi As Single               ' Pressure in decibars
Dim Conductivity As Single     ' Not used here, added for Version 8
Dim Ti As Single               ' Temperature in degrees C
Dim Si As Single               ' Salinity in PSU
Dim Di As Single               ' Sigma-theta = (density-1)*1000
Dim Vi As Single               ' Sound Velocity in m/sec
Dim Volts As Single            ' Not used here
'''
