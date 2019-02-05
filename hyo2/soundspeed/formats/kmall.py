from datetime import datetime, timedelta
import logging
import struct

logger = logging.getLogger(__name__)


class Kmall:
    datagrams = {
        b'#IIP': 'Installation parameters and sensor setup',
        b'#IOP': 'Runtime parameters as chosen by operator',
        b'#IBE': 'Built in test (BIST) error report',
        b'#IBR': 'Built in test (BIST) reply',
        b'#IBS': 'Built in test (BIST) short reply',

        b'#MRZ': 'Multibeam (M) raw range (R) and depth(Z) datagram',
        b'#MWC': 'Multibeam (M) water (W) column (C) datagram',

        b'#SPO': 'Sensor (S) data for position (PO)',
        b'#SKM': 'Sensor (S) KM binary sensor format',
        b'#SVP': 'Sensor (S) data from sound velocity (V) profile (P) or CTD',
        b'#SVT': 'Sensor (S) data for sound velocity (V) at transducer (T)',
        b'#SCL': 'Sensor (S) data from clock (CL)',
        b'#SDE': 'Sensor (S) data from depth (DE) sensor',
        b'#SHI': 'Sensor (S) data for height (HI)',

        b'#CPO': 'Compatibility (C) data for position (PO)',
        b'#CHE': 'Compatibility (C) data for heave (HE)',
    }

    def __init__(self, data):

        self.data = data

        self.length = None
        self.id = None
        self.version = None
        self.system_id = None
        self.sounder_id = None
        self.time_sec = None
        self.time_nanosec = None
        self.dg_time = None

        self._parse_header()

    def _parse_header(self):
        """Parse header"""
        hdr_data = struct.unpack("<I4cBBHII", self.data[:20])
        self.length = hdr_data[0]
        # logger.debug('length: %s' % self.length)
        self.type = b''.join(hdr_data[1:5])
        # logger.debug('type: %s -> %s' % (self.type, self.kmall_datagrams[self.type]))
        self.version = hdr_data[5]
        # logger.debug('version: %s' % self.version)
        self.system_id = hdr_data[6]
        # logger.debug('system id: %s' % self.system_id)
        self.sounder_id = hdr_data[7]
        # logger.debug('sounder id: %s' % self.sounder_id)
        self.time_sec = hdr_data[8]
        # logger.debug('time sec: %s' % self.time_sec)
        self.time_nanosec = hdr_data[9]
        # logger.debug('time nanosec: %s' % self.time_nanosec)
        self.dg_time = Kmall.kmall_datetime(self.time_sec, self.time_nanosec)
        # logger.debug('datetime: %s' % self.dg_time.strftime('%Y-%m-%d %H:%M:%S.%f'))

    @classmethod
    def kmall_datetime(cls, dgm_time_sec, dgm_time_nanosec):
        return datetime.utcfromtimestamp(dgm_time_sec) + \
               timedelta(microseconds=(dgm_time_nanosec / 1000.0))

    def __str__(self):
        return 'ID: %d, Date: %s, Model: %d\n' \
               % (self.id, self.dg_time, self.sounder_id)


class KmallSPO(Kmall):
    def __init__(self, data):
        super().__init__(data)

        common = struct.unpack("<4H", self.data[20:28])
        common_length = common[0]
        # logger.debug("common part -> length: %d/%d" % (common_length, self.length))
        common_sensor_system = common[1]
        # logger.debug("common part -> sensor system: %d" % common_sensor_system)
        common_sensor_status = common[2]
        # logger.debug("common part -> sensor status: %d" % common_sensor_status)

        data_blk = struct.unpack("<2If2d3f", self.data[28:68])
        time_sec = data_blk[0]
        # logger.debug('sensor time sec: %s' % time_sec)
        time_nanosec = data_blk[1]
        # logger.debug('sensor time nanosec: %s' % time_nanosec)
        sensor_datetime = Kmall.kmall_datetime(time_sec, time_nanosec)
        # logger.debug('sensor datetime: %s' % sensor_datetime.strftime('%Y-%m-%d %H:%M:%S.%f'))
        fix_quality = data_blk[2]
        # logger.debug('pos fix quality: %s' % fix_quality)
        self.latitude = data_blk[3]
        self.longitude = data_blk[4]
        # logger.debug('pos: %s, %s' % (self.latitude, self.longitude))
        self.sog = data_blk[5]
        self.cog = data_blk[6]
        # logger.debug('sog: %s, cog: %s' % (self.sog, self.cog))
        self.ell_height = data_blk[7]
        # logger.debug('ellipsoid height: %s' % (self.ell_height, ))
        # the remainder are the raw data
        self.raw_input = self.data[68:]
        # logger.debug('raw: %s' % (self.raw_input,))

    def __str__(self):
        output = Kmall.__str__(self)
        output += '\tLat/Lon: %lf %lf\n\tSOG: %.2f m/s\n\tCOG: %.2f deg.\n' % \
                  (self.latitude, self.longitude, self.sog, self.cog)
        output += '\tRaw Input (%d bytes): %s\n' % (self.length - 68, self.raw_input)

        return output
