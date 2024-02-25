from datetime import datetime, timedelta
import logging
import struct
import numpy as np

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

        b'#SSM': 'Sound Speed Manager (SSM) datagram',

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

        self.is_valid = False

        self._parse_header()

    def _parse_header(self):
        """Parse header"""
        hdr_data = struct.unpack("<I4cBBHII", self.data[:20])
        self.length = hdr_data[0]
        # logger.debug('length: %s' % self.length)
        self.id = b''.join(hdr_data[1:5])
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
    def kmall_datetime(cls, dgm_time_sec: int, dgm_time_nanosec: int = 0):
        return datetime.utcfromtimestamp(dgm_time_sec) + \
               timedelta(microseconds=(dgm_time_nanosec / 1000.0))

    def __str__(self):
        return 'ID: %s, Date: %s, Model: %d\n' \
               % (self.id, self.dg_time, self.sounder_id)


class KmallSSM(Kmall):
    def __init__(self, data, debug: bool = False):
        super().__init__(data)

        common = struct.unpack("<4H", self.data[20:28])
        # common_length = common[0]
        # logger.debug("common part -> length: %d/%d" % (common_length, self.length))
        # common_sensor_system = common[1]
        # logger.debug("common part -> sensor system: %d" % common_sensor_system)
        common_sensor_status = common[2]
        self.inactive_navigation = (common_sensor_status & 1) != 1
        self.inactive_pinging = (common_sensor_status & 2) != 2
        self.invalid_data = (common_sensor_status & 16) == 16
        if debug:
            if self.invalid_data:
                logger.debug("common part -> sensor status: %s (invalid data: %s)"
                             % (common_sensor_status, self.invalid_data))

        data_blk = struct.unpack("<2fIfI2d", self.data[28:64])
        if self.inactive_pinging:

            if debug:
                logger.debug("common part -> sensor status: %s (inactive pinging: %s)"
                             % (common_sensor_status, self.inactive_pinging))

            self.tss = None
            self.transducer_depth = None
            self.mean_depth = None

        else:

            self.tss = data_blk[0]
            if debug:
                logger.debug('TSS: %s m/s' % self.tss)
            self.transducer_depth = data_blk[1]
            if debug:
                logger.debug('transducer depth re WL: %s m' % self.transducer_depth)
            # ping_time_sec = data_blk[2]
            # logger.debug('ping time sec: %s' % ping_time_sec)
            # ping_datetime = Kmall.kmall_datetime(ping_time_sec, 0)
            # logger.debug('ping datetime: %s' % ping_datetime.strftime('%Y-%m-%d %H:%M:%S.%f'))
            self.mean_depth = data_blk[3]
            if debug:
                logger.debug('ping avg depth: %s' % self.mean_depth)

        if self.inactive_navigation:

            if debug:
                logger.debug("common part -> sensor status: %s (inactive navigation: %s)"
                             % (common_sensor_status, self.inactive_navigation))

            self.latitude = None
            self.longitude = None

        else:

            # nav_time_sec = data_blk[4]
            # logger.debug('nav time sec: %s' % nav_time_sec)
            # nav_datetime = Kmall.kmall_datetime(nav_time_sec, 0)
            # logger.debug('nav datetime: %s' % nav_datetime.strftime('%Y-%m-%d %H:%M:%S.%f'))
            self.latitude = data_blk[5]
            self.longitude = data_blk[6]
            if debug:
                logger.debug('SSM -> pos: %.7f, %.7f' % (self.latitude, self.longitude))

        final_length = struct.unpack("<I", self.data[-4:])
        self.is_valid = final_length != self.length
        # logger.debug('#SPO is valid: %s' % self.is_valid)
        if not self.is_valid:
            logger.warning('SSM -> Invalid length: %s != %s' % (final_length, self.length))

    def __str__(self):
        output = Kmall.__str__(self)
        output += '\tTSS: %.2f m/s\n\tTransducer depth: %.2f m.\n' % (self.tss, self.transducer_depth)
        output += '\tLat/Lon: %lf %lf\n' % (self.latitude, self.longitude)
        output += '\tMean depth: %.2f m\n' % self.mean_depth

        return output


class KmallMRZ(Kmall):
    def __init__(self, data, debug: bool = False):
        super().__init__(data)

        # partition
        # partition = struct.unpack("<2H", self.data[20:24])
        # nr_of_datagrams = partition[0]
        # datagram_nr = partition[1]
        # logger.debug('datagram: %s/%s' % (datagram_nr, nr_of_datagrams))

        # common
        # common = struct.unpack("<2H8B", self.data[24:36])
        # common_length = common[0]
        # logger.debug("common part -> length: %d/%d" % (common_length, self.length))
        # ping_count = common[1]
        # logger.debug("common part -> ping #%d" % (ping_count, ))
        # rx_fans_per_ping = common[2]
        # rx_fan_index = common[3]
        # logger.debug("common part -> rx fan %d/%d" % (rx_fan_index, rx_fans_per_ping))
        # swaths_per_ping = common[4]
        # logger.debug("common part -> swaths per ping: %d" % (swaths_per_ping, ))
        # swath_along_position = common[5]
        # logger.debug("common part -> swath along position: %d" % (swath_along_position, ))
        # tx_transducer_index = common[6]
        # rx_transducer_index = common[7]
        # nr_of_rx_transducers = common[8]
        # logger.debug("common part -> transducer indices -> tx: %d, rx: %d/%d"
        #              % (tx_transducer_index, rx_transducer_index, nr_of_rx_transducers))
        # algorithm_type = common[9]
        # logger.debug("common part -> algorithm type: %d" % (algorithm_type,))

        # ping info                  12 89 20  24   30  34  44 47
        ping_info = struct.unpack("<2Hf6BH11f2h2BHI3f2Hf2H6f4B2df", self.data[36:180])  # 144 bytes
        ping_info_length = ping_info[0]
        # logger.debug("ping info part -> length: %d/%d" % (ping_info_length, self.length))
        nr_or_tx_sectors = ping_info[33]
        bytes_per_tx_sector = ping_info[34]
        # logger.debug('nr or tx sectors: %s (%d B)' % (nr_or_tx_sectors, bytes_per_tx_sector))
        self.tss = ping_info[36]
        # logger.debug('TSS: %s m/s' % (self.tss, ))
        transducer_depth_m = ping_info[37]
        # z_water_level_re_ref_point_m = ping_info[38]
        # logger.debug('WL re RP: %.3f m, transducer depth re WL: %.3f m'
        #              % (z_water_level_re_ref_point_m, transducer_depth_m))
        self.transducer_depth = transducer_depth_m
        # vrp_latitude = ping_info[45]
        # vrp_longitude = ping_info[46]
        # logger.debug('VRP pos: %s, %s' % (vrp_latitude, vrp_longitude))
        start_of_tx_sectors = 36 + ping_info_length
        end_of_tx_sectors = start_of_tx_sectors + nr_or_tx_sectors * bytes_per_tx_sector

        # rx info
        rx_info = struct.unpack("<4H4f4H", self.data[end_of_tx_sectors:end_of_tx_sectors+32])
        rx_info_length = rx_info[0]
        # logger.debug("rx info part -> length: %d/%d" % (rx_info_length, self.length))
        nr_of_soundings = rx_info[1]
        # logger.debug("rx info part -> nr of soundings: %d" % (nr_of_soundings, ))
        sounding_length = rx_info[3]
        # logger.debug("rx info part -> sounding length: %d" % (sounding_length, ))
        nr_extra_detection_classes = rx_info[10]
        nr_bytes_per_class = rx_info[11]
        # logger.debug("rx info part -> extra det. classes: %d [%d B]"
        #              % (nr_extra_detection_classes, nr_bytes_per_class))
        end_of_rx_info = end_of_tx_sectors + rx_info_length
        end_of_extra_det_class_info = end_of_rx_info + nr_extra_detection_classes * nr_bytes_per_class

        # each sounding       8 15   35 39
        sounding_struct = '<H8BH6f2H18f4H'

        depths_valid = 0
        depths_sum = 0.0
        for i in range(nr_of_soundings):
            start_sounding = end_of_extra_det_class_info + i * sounding_length
            end_sounding = end_of_extra_det_class_info + (i + 1) * sounding_length
            if len(self.data[start_sounding:end_sounding]) != sounding_length:
                # logger.debug("sounding #%d: data length: %d -> break"
                #              % (i, len(self.data[start_sounding:end_sounding])))
                break
            sounding = struct.unpack(sounding_struct, self.data[start_sounding:end_sounding])
            # sounding_idx = sounding[0]
            # logger.debug("sounding -> #%d" % (sounding_idx, ))
            sounding_detection_type = sounding[2]
            # logger.debug("sounding -> detection type: %s" % (sounding_detection_type, ))
            sounding_detection_method = sounding[3]
            # logger.debug("sounding -> detection method: %s" % (sounding_detection_method, ))
            sounding_z = sounding[32]
            # sounding_y = sounding[33]
            # sounding_x = sounding[34]
            # logger.debug("sounding -> z: %s, y: %s, x: %s" % (sounding_z, sounding_y, sounding_x))

            if (sounding_detection_type == 0) and (sounding_detection_method != 0):
                depths_valid += 1
                depths_sum += sounding_z

        self.mean_depth = None
        if depths_valid > 0:
            self.mean_depth = (depths_sum / depths_valid) + self.transducer_depth
            if debug:
                logger.debug("MRZ -> mean depth: %.4f" % (self.mean_depth, ))

        # footer
        final_length = struct.unpack("<I", self.data[-4:])
        # logger.debug('final length: %s' % final_length)
        self.is_valid = final_length != self.length
        # logger.debug('#MRZ is valid: %s' % self.is_valid)
        if not self.is_valid:
            logger.warning('MRZ -> Invalid length: %s != %s' % (final_length, self.length))

    def __str__(self):
        output = Kmall.__str__(self)
        output += '\ttss: %s\n\tmean depth: %s m\n' % \
                  (self.tss, self.mean_depth)
        return output


class KmallSPO(Kmall):
    def __init__(self, data, debug: bool = False):
        super().__init__(data)

        common = struct.unpack("<4H", self.data[20:28])
        # common_length = common[0]
        # logger.debug("common part -> length: %d/%d" % (common_length, self.length))
        # common_sensor_system = common[1]
        # logger.debug("common part -> sensor system: %d" % common_sensor_system)
        common_sensor_status = common[2]
        self.inactive_sensor = (common_sensor_status & 1) != 1
        self.invalid_data = (common_sensor_status & 16) == 16
        # if self.inactive_sensor or self.invalid_data:
        #     logger.debug("common part -> sensor status: %s (inactive: %s, invalid: %s)"
        #                  % (common_sensor_status, self.inactive_sensor, self.invalid_data))

        data_blk = struct.unpack("<2If2d3f", self.data[28:68])
        # time_sec = data_blk[0]
        # logger.debug('sensor time sec: %s' % time_sec)
        # time_nanosec = data_blk[1]
        # logger.debug('sensor time nanosec: %s' % time_nanosec)
        # sensor_datetime = Kmall.kmall_datetime(time_sec, time_nanosec)
        # logger.debug('sensor datetime: %s' % sensor_datetime.strftime('%Y-%m-%d %H:%M:%S.%f'))
        # fix_quality = data_blk[2]
        # logger.debug('pos fix quality: %s' % fix_quality)
        self.latitude = data_blk[3]
        self.longitude = data_blk[4]
        if debug:
            logger.debug('SPO -> pos: %.7f, %.7f' % (self.latitude, self.longitude))
        self.sog = data_blk[5]
        self.cog = data_blk[6]
        # logger.debug('sog: %s, cog: %s' % (self.sog, self.cog))
        self.ell_height = data_blk[7]
        # logger.debug('ellipsoid height: %s' % (self.ell_height, ))
        # the remainder are the raw data
        self.raw_input = self.data[68:-5]
        # logger.debug('raw: %s' % (self.raw_input,))

        final_length = struct.unpack("<I", self.data[-4:])
        self.is_valid = final_length != self.length
        # logger.debug('#SPO is valid: %s' % self.is_valid)
        if not self.is_valid:
            logger.warning('SPO -> Invalid length: %s != %s' % (final_length, self.length))

    def __str__(self):
        output = Kmall.__str__(self)
        output += '\tLat/Lon: %lf %lf\n\tSOG: %.2f m/s\n\tCOG: %.2f deg.\n' % \
                  (self.latitude, self.longitude, self.sog, self.cog)
        output += '\tRaw Input (%d bytes): %s\n' % (self.length - 68, self.raw_input)

        return output


class KmallSVP(Kmall):
    def __init__(self, data, debug: bool = False):
        super().__init__(data)

        header_struct = '<2H4BIdd'
        svp_header = struct.unpack(header_struct, self.data[20:48])
        self.num_entries = svp_header[1]
        if debug:
            logger.debug("SVP -> samples: %s" % (self.num_entries,))
        self.acquisition_time = Kmall.kmall_datetime(svp_header[6])
        if debug:
            logger.debug("SVP -> acquisition time: %s" % self.acquisition_time.strftime('%Y-%m-%d %H:%M:%S.%f'))

        fields_struct = '<2fI2f'  # 20B
        self.depth = np.zeros(self.num_entries)
        self.speed = np.zeros(self.num_entries)
        self.temp = np.zeros(self.num_entries)
        self.sal = np.zeros(self.num_entries)
        for i in range(self.num_entries):
            start_field = 48 + i * 20
            end_field = 48 + (i + 1) * 20
            svp_field = struct.unpack(fields_struct, self.data[start_field:end_field])
            self.depth[i] = svp_field[0]
            self.speed[i] = svp_field[1]
            self.temp[i] = svp_field[3]
            self.sal[i] = svp_field[4]
        if debug:
            logger.debug("depths: %s" % (self.depth, ))
            logger.debug("speeds: %s" % (self.speed, ))

        final_length = struct.unpack("<I", self.data[-4:])
        self.is_valid = final_length != self.length
        # logger.debug('#SVP is valid: %s' % self.is_valid)
        if not self.is_valid:
            logger.warning('SVP -> Invalid length: %s != %s' % (final_length, self.length))
