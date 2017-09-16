import datetime as dt
import logging
import struct

import numpy as np

logger = logging.getLogger(__name__)

from hyo.soundspeed.profile.dicts import Dicts


class Km:

    datagrams = {
        48: 'PU Id output',
        49: 'PU Status',
        65: 'Attitude',
        66: 'BIST Output',
        67: 'Clock',
        68: 'Depth',
        71: 'Surface Sound Speed',
        72: 'Heading',
        73: 'Installation Parameters (start)',
        78: 'Raw Range and Angle (78)',
        80: 'Position',
        82: 'Runtime Parameters',
        83: 'Seabed Image',
        85: 'Sound Speed Profile (new)',
        88: 'XYZ (88)',
        89: 'Seabed Imagery (89)',
        102: 'Raw Beam and Angle (new)',
        105: 'Installation Parameters (stop)',
        107: 'Watercolumn',
        110: 'Network Attitude Velocity'
    }

    def __init__(self, data, remote=True):

        self.data = data

        self.remote = remote

        self.length = None
        if self.remote:
            self.length_i = None
        else:
            self.length_i = 0

        self.stx = None
        if self.remote:
            self.stx_i = 0
        else:
            self.stx_i = 1

        self.id = None
        if self.remote:
            self.id_i = 1
        else:
            self.id_i = 2

        self.model = None
        if self.remote:
            self.model_i = 2
        else:
            self.model_i = 3

        self.dg_time = None
        self.date = None
        self.time = None
        if self.remote:
            self.date_i = 3
            self.time_i = 4
        else:
            self.date_i = 4
            self.time_i = 5

        self.counter = None
        if self.remote:
            self.counter_i = 5
        else:
            self.counter_i = 6

        self.serial_number = None
        if self.remote:
            self.serial_number_i = 6
        else:
            self.serial_number_i = 7

        self.parse_header()

    def parse_header(self):
        """Parse header"""
        if self.remote:
            header = struct.unpack("<BBHIIHH", self.data[0:16])
        else:
            header = struct.unpack("<IBBHIIHH", self.data[0:20])
            self.length = header[self.length_i]

        self.stx = header[self.stx_i]
        self.id = header[self.id_i]
        self.model = header[self.model_i]

        self.date = header[self.date_i]
        # print("date %s" % self.date)
        self.time = header[self.time_i]
        # print("time %s" % self.time)
        if (self.date > 0) and (self.time > 0):
            self.dg_time = self.km_time(self.date, self.time)
        else:
            self.dg_time = None
        # print("dg_time: %s" % self.dg_time)

        self.counter = header[self.counter_i]
        self.serial_number = header[self.serial_number_i]

    def serialize(self):
        """Serialize header"""
        loc_data = bytearray(self.data)

        b_count = 0
        if not self.remote:
            b_data = struct.pack("<I", self.length)
            b_size = len(b_data)
            loc_data[b_count:b_count + b_size] = b_data
            b_count += b_size

        b_data = struct.pack("<B", self.stx)
        b_size = len(b_data)
        loc_data[b_count:b_count + b_size] = b_data
        b_count += b_size

        b_data = struct.pack("<B", self.id)
        b_size = len(b_data)
        loc_data[b_count:b_count + b_size] = b_data
        b_count += b_size

        b_data = struct.pack("<H", self.model)
        b_size = len(b_data)
        loc_data[b_count:b_count + b_size] = b_data
        b_count += b_size

        b_data = struct.pack("<I", self.date)
        b_size = len(b_data)
        loc_data[b_count:b_count + b_size] = b_data
        b_count += b_size

        b_data = struct.pack("<I", self.time)
        b_size = len(b_data)
        loc_data[b_count:b_count + b_size] = b_data
        b_count += b_size

        b_data = struct.pack("<H", self.counter)
        b_size = len(b_data)
        loc_data[b_count:b_count + b_size] = b_data
        b_count += b_size

        b_data = struct.pack("<H", self.serial_number)
        b_size = len(b_data)
        loc_data[b_count:b_count + b_size] = b_data
        b_count += b_size

        print('serialized: %s B' % b_count)

        return loc_data

    @classmethod
    def calc_2bytes_checksum(cls, bytes_data):
        """Calculate the 2-byte Kongsberg checksum"""
        checksum = 0
        for i in range(len(bytes_data)):
            if (i < 5) or (i > len(bytes_data) - 4):
                continue
            checksum += bytes_data[i]
        checksum %= 2 ** 16
        return checksum

    @classmethod
    def km_time(cls, km_date, km_time):
        # log.debug("KM DATE: %s, TIME: %s" % (km_date, km_time))

        date = str(km_date)

        if km_time < 86400000:
            seconds = km_time // 1000
            hours = seconds // 3600
            seconds -= 3600 * hours
            minutes = seconds // 60
            seconds -= 60 * minutes
            micro_secs = (km_time % 1000) * 1000
        else:
            hours = 0
            seconds = 0
            minutes = 0
            micro_secs = 0

        try:
            return dt.datetime(int(date[0:4]), int(date[4:6]), int(date[6:8]),
                               int(hours), int(minutes), int(seconds), micro_secs)
        except ValueError:
            return None

    def __str__(self):
        return 'ID: %d, Date: %s, Model: %d, Counter: %d, S/N: %d\n' \
               % (self.id, self.dg_time, self.model, self.counter, self.serial_number)


class KmNav(Km):
    def __init__(self, data):
        super(KmNav, self).__init__(data)

        # break it into its bits
        nav = struct.unpack("<iiHHHHBB", self.data[16:34])

        # now decode into human readable numbers
        # convert KM integer lat/lon into floats
        self.latitude = 1.0 * nav[0] / 20000000
        self.longitude = 1.0 * nav[1] / 10000000

        # raw fix quality is in cm, sog is cm/s; make both m and m/s
        self.fix_quality = 1.0 * nav[2] / 100.0
        self.sog = 1.0 * nav[3] / 100.0

        # raw cog and heading is in 0.01deg resolution
        self.cog = 1.0 * nav[4] / 100.0
        self.heading = 1.0 * nav[5] / 100.0

        self.descriptor = nav[6]

        self.num_input_bytes = nav[7]

        # the remainder is the input datagram, ETX and checksum
        self.input_datagram = self.data[34:34 + self.num_input_bytes]

        self.etx, self.checksum = struct.unpack("<BH",
                                                self.data[34 + self.num_input_bytes:34 + self.num_input_bytes + 3])

    def __str__(self):
        output = Km.__str__(self)
        output += '\tLat/Lon: %lf %lf\n\tQuality: %.2f m\n\tSOG: %.2f m/s\n\tCOG: %.2f deg.\n\tHdg: %.2f deg.\n' % \
                  (self.latitude, self.longitude, self.fix_quality, self.sog, self.cog, self.heading)
        output += '\tDescriptor: %d\n' % self.descriptor
        output += '\tInput (%d bytes): %s\n' % (self.num_input_bytes, self.input_datagram)

        return output


class KmRuntime(Km):
    def __init__(self, data):
        super(KmRuntime, self).__init__(data)

        # break it into its bits
        bits = struct.unpack("<6B5Hb5BH4BHh2BH", self.data[16:52])

        self.operator_station_status = bits[0]
        self.processing_unit_status = bits[1]
        self.BSP_status = bits[2]
        self.sonar_head_status = bits[3]
        self.mode = bits[4]
        self.filter_identifier = bits[5]
        self.min_depth = bits[6]
        self.max_depth = bits[7]
        self.abs_coefficient = bits[8] / 100.0
        self.pulse_length = bits[9] / 1000000.0
        self.tx_beamwidth = bits[10] / 10.0
        self.tx_power = bits[11]
        self.rx_beamwidth = bits[12] / 10.0
        self.rx_bandwidth = bits[13] * 50.0
        self.rx_fixed_gain = bits[14]
        self.TVG_crossover_angle = bits[15]
        self.tdcr_sound_speed_source = bits[16]
        self.max_port_swath_width = bits[17]
        self.beam_spacing = bits[18]
        self.max_port_coverage = bits[19]
        self.yaw_pitch_stabilize_mode = bits[20]
        self.max_stbd_coverage = bits[21]
        self.max_stbd_swath_width = bits[22]
        self.transmit_along_tilt = bits[23] / 10.0
        self.spare = bits[24]
        self.hi_lo_freq_abs_coeff_ratio = bits[25]

    def __str__(self):
        output = Km.__str__(self)

        output += "- op. stat. status: %s\n" % self.operator_station_status \
                  + "- proc. unit status: %s\n" % self.processing_unit_status \
                  + "- bsp status: %s\n" % self.BSP_status \
                  + "- sonar head status: %s\n" % self.sonar_head_status \
                  + "- mode: %s\n" % self.mode \
                  + "- filter id.: %s\n" % self.filter_identifier \
                  + "- min depth: %s\n" % self.min_depth \
                  + "- max depth: %s\n" % self.max_depth \
                  + "- abs. coeff.: %s\n" % self.abs_coefficient \
                  + "- pulse len.: %s\n" % self.pulse_length \
                  + "- tx beamwidth: %s\n" % self.tx_beamwidth \
                  + "- tx power: %s\n" % self.tx_power \
                  + "- rx beamwidth: %s\n" % self.rx_beamwidth \
                  + "- rx fix.gain: %s\n" % self.rx_fixed_gain \
                  + "- tvg crossover ang.: %s\n" % self.TVG_crossover_angle \
                  + "- tdcr ss source: %s\n" % self.tdcr_sound_speed_source \
                  + "- max port swath width: %s\n" % self.max_port_swath_width \
                  + "- beam spacing: %s\n" % self.beam_spacing \
                  + "- max port cvg: %s\n" % self.max_port_coverage \
                  + "- yaw pith stab. mode: %s\n" % self.yaw_pitch_stabilize_mode \
                  + "- max stbd. cvg.: %s\n" % self.max_stbd_coverage \
                  + "- max stbd. swath width: %s\n" % self.max_stbd_swath_width \
                  + "- tx along tilt: %s\n" % self.transmit_along_tilt \
                  + "- spare: %s\n" % self.spare \
                  + "- hi lo freq. abs. coeff. ratio: %s" % self.hi_lo_freq_abs_coeff_ratio

        return output


class KmInstallation(Km):
    def __init__(self, data):

        super(KmInstallation, self).__init__(data)

        self.values = {}

        # break it into its bits
        self.serial_number_2 = struct.unpack("<H", self.data[16:18])

        line = self.data[18:-3]

        for l in line.split(","):
            if len(l) == 0:
                continue

            num_fields = len(l.split("="))

            if num_fields != 2:
                continue

            [key, value] = l.split("=")

            self.values[key] = value

    def __str__(self):

        output = Km.__str__(self)

        return output


class KmSsp(Km):
    def __init__(self, data):

        super(KmSsp, self).__init__(data)

        # break it into its bits
        self.num_entries = struct.unpack("<H", self.data[16:18])[0]

        self.time_offset = np.zeros(self.num_entries)
        self.speed = np.zeros(self.num_entries)

        offset = 18
        for count in range(self.num_entries):
            self.time_offset[count], self.speed[count] = struct.unpack("<HH", self.data[offset:offset + 4])
            self.speed[count] /= 10.0
            offset += 4

    def __str__(self):

        output = Km.__str__(self)
        output += '\tNum entries: %d\n' % self.num_entries
        for count in range(self.num_entries):
            output += '\t%d %.1f\n' % (self.time_offset[count], self.speed[count])

        return output


class KmSvpInput(Km):
    def __init__(self, data):
        super(KmSvpInput, self).__init__(data)

        self.input_datagram = self.data[16:len(data) - 3]

        year = self.input_datagram.split(",")[6]
        month = self.input_datagram.split(",")[5]
        day = self.input_datagram.split(",")[4]
        cast_time = self.input_datagram.split(",")[3]

        self.acquisition_time = dt.datetime(int(year), int(month), int(day), int(cast_time[0:2]), int(cast_time[2:4]),
                                            int(cast_time[4:6]), 0)

    def __str__(self):
        output = Km.__str__(self)
        output += '\tAcquisition time: %s\n' % self.acquisition_time
        output += '\tInput datagram: %s\n' % self.input_datagram

        return output


class KmBist(Km):
    def __init__(self, data):
        super(KmBist, self).__init__(data)

        bist = struct.unpack("<Hh", self.data[16:20])
        self.test_number = bist[0]
        self.result_status = bist[1]

        self.input_datagram = self.data[18:len(data) - 3]

    def __str__(self):
        output = Km.__str__(self)
        output += '\tTest: %d\n' % self.test_number
        output += '\tResult: %d\n' % self.result_status
        output += '\tDatagram:\n%s\n' % self.input_datagram

        return output


class KmSvp(Km):
    def __init__(self, data):

        super(KmSvp, self).__init__(data)

        self.name = "KMS"

        # break it into its bits
        svp = struct.unpack("<IIHH", self.data[16:28])

        # log.debug("KM SVP: %s %s:" % (svp[0], svp[1]))
        self.acquisition_time = Km.km_time(svp[0], svp[1] * 1000)  # since we reuse the time in milli seconds function

        self.num_entries = svp[2]
        self.depth_resolution_cms = svp[3]

        self.depth = np.zeros(self.num_entries)
        self.speed = np.zeros(self.num_entries)

        offset = 28
        for count in range(self.num_entries):
            self.depth[count], self.speed[count] = struct.unpack("<II", self.data[offset:offset + 8])
            self.depth[count] = 0.01 * self.depth[count] / self.depth_resolution_cms
            self.speed[count] /= 10.0
            offset += 8

    def convert_ssp(self):
        from ..profile.profile import Profile

        ssp = Profile()
        ssp.meta.utc_time = self.acquisition_time
        ssp.meta.sensor_type = Dicts.sensor_types['Synthetic']
        ssp.meta.probe_type = Dicts.probe_types['SIS']
        ssp.meta.proc_info = "SIS"
        ssp.meta.original_path = "SIS_%s" % self.acquisition_time.strftime("%Y%m%d_%H%M%S")
        ssp.init_data(self.depth.size)
        ssp.data.depth = self.depth
        ssp.data.speed = self.speed

        return ssp

    def __str__(self):

        output = Km.__str__(self)
        output += '> acquisition time: %s\n' % self.acquisition_time
        output += '> entries: %d\n' % self.num_entries
        output += '> depth resolution (cms): %d\n' % self.depth_resolution_cms
        if self.num_entries < 9:
            for idx in range(self.num_entries):
                output += '   %.2f %.1f\n' % (self.depth[idx], self.speed[idx])
        else:
            for idx in range(8):
                output += '   %.2f %.1f\n' % (self.depth[idx], self.speed[idx])
            output += '   ... ...\n'

        return output


class KmRangeAngle78(Km):
    def __init__(self, data):

        super(KmRangeAngle78, self).__init__(data)

        range_angle78 = struct.unpack("<HHHHfI", self.data[16:32])

        self.sound_speed = range_angle78[0] / 10.0
        self.number_sectors = range_angle78[1]
        self.number_beams = range_angle78[2]
        self.number_detections = range_angle78[3]
        self.sampling_frequency = range_angle78[4]
        self.d_scale = range_angle78[5]

        self.tilt_angle = np.zeros(self.number_sectors)
        self.focus_range = np.zeros(self.number_sectors)
        self.signal_length = np.zeros(self.number_sectors)
        self.transmit_delay = np.zeros(self.number_sectors)
        self.center_frequency = np.zeros(self.number_sectors)
        self.absorption_coefficient = np.zeros(self.number_sectors)
        self.signal_waveform_id = np.zeros(self.number_sectors)
        self.transmit_sector_number = np.zeros(self.number_sectors)
        self.signal_bandwidth = np.zeros(self.number_sectors)

        offset = 32
        bytes_per_sector = 24
        for count in range(self.number_sectors):
            sector = struct.unpack("<hH3fH2Bf", self.data[offset:offset + bytes_per_sector])
            self.tilt_angle[count] = sector[0] / 100.0
            self.focus_range[count] = sector[1] / 10.0
            self.signal_length[count] = sector[2]
            self.transmit_delay[count] = sector[3]
            self.center_frequency[count] = sector[4]
            self.absorption_coefficient[count] = sector[5] / 100.0
            self.signal_waveform_id[count] = sector[6]
            self.transmit_sector_number[count] = sector[7]
            self.signal_bandwidth[count] = sector[8]
            offset += bytes_per_sector

        self.angle = np.zeros(self.number_beams)
        self.sector_number = np.zeros(self.number_beams)
        self.detection_information = np.zeros(self.number_beams)
        self.detection_window = np.zeros(self.number_beams)
        self.quality_factor = np.zeros(self.number_beams)
        self.d_corr = np.zeros(self.number_beams)
        self.travel_time = np.zeros(self.number_beams)
        self.reflectivity = np.zeros(self.number_beams)
        self.realtime_cleaning_information = np.zeros(self.number_beams)
        self.spare = np.zeros(self.number_beams)

        bytes_per_beam = 16
        for count in range(self.number_beams):
            beam = struct.unpack("<h2BHBbfhbB", self.data[offset:offset + bytes_per_beam])
            self.angle[count] = beam[0] / 100.0
            self.sector_number[count] = int(beam[1])
            self.detection_information[count] = beam[2]
            self.detection_window[count] = beam[3]
            self.quality_factor[count] = beam[4]
            self.d_corr[count] = beam[5]
            self.travel_time[count] = beam[6]
            self.reflectivity[count] = beam[7] / 10.0
            self.realtime_cleaning_information[count] = beam[8]
            self.spare[count] = beam[9]
            offset += bytes_per_beam

    def __str__(self):

        output = Km.__str__(self)

        output += "- sound speed: %s\n" % self.sound_speed \
                  + "- number sectors: %s\n" % self.number_sectors \
                  + "- number beams: %s\n" % self.number_beams \
                  + "- number detections: %s\n" % self.number_detections \
                  + "- sampling frequency: %s\n" % self.sampling_frequency \
                  + "- d scale: %s" % self.d_scale

        return output


class KmXyz88(Km):
    def __init__(self, data):

        super(KmXyz88, self).__init__(data)

        xyz88 = struct.unpack("<HHfHHfi", self.data[16:36])

        self.heading = xyz88[0] / 100.0
        self.sound_speed = xyz88[1] / 10.0
        self.transducer_draft = xyz88[2]
        self.number_beams = xyz88[3]
        self.number_detections = xyz88[4]
        self.sampling_frequency = xyz88[5]
        self.spare = xyz88[6]

        self.depth = np.zeros(self.number_beams)
        self.across = np.zeros(self.number_beams)
        self.along = np.zeros(self.number_beams)
        self.detection_window = np.zeros(self.number_beams)
        self.quality_factor = np.zeros(self.number_beams)
        self.beam_incidence_angle_adjustment = np.zeros(self.number_beams)
        self.detection_information = np.zeros(self.number_beams)
        self.realtime_cleaning_information = np.zeros(self.number_beams)
        self.reflectivity = np.zeros(self.number_beams)

        offset = 36
        bytes_per_beam = 20
        for count in range(self.number_beams):
            beam = struct.unpack("<fffHBbBbh", self.data[offset:offset + bytes_per_beam])
            self.depth[count] = beam[0]
            self.across[count] = beam[1]
            self.along[count] = beam[2]
            self.detection_window[count] = beam[3]
            self.quality_factor[count] = beam[4]
            self.beam_incidence_angle_adjustment[count] = beam[5] / 10.0
            self.detection_information[count] = beam[6]
            self.realtime_cleaning_information[count] = beam[7]
            self.reflectivity[count] = beam[8] / 10.0
            offset += bytes_per_beam

    @property
    def mean_depth(self):
        if (self.number_beams is None) or (self.depth is None) or (self.transducer_draft is None) or \
                (self.detection_information is None):
            return None

        mean_depth = 0.0
        depth_count = 0
        for beam in range(self.number_beams):
            if int(self.detection_information[beam]) & 0x80 != 0:
                # We skip beams without valid detections
                continue
            mean_depth = mean_depth + self.depth[beam]
            depth_count += 1

        if depth_count > 0:
            mean_depth = mean_depth / depth_count + self.transducer_draft
            return mean_depth
        return None

    def __str__(self):

        output = Km.__str__(self)
        output += '- Heading: %.2f\n' % self.heading
        output += '- Sound speed: %.1f\n' % self.sound_speed
        output += '- Transducer draft: %.2f\n' % self.transducer_draft
        output += '- Number of beams: %d\n' % self.number_beams
        output += '- Number of valid detections: %d\n' % self.number_detections
        output += '- Sampling frequency: %.2f Hz\n' % self.sampling_frequency
        output += '- Spare: %d\n' % self.spare

        for count in range(self.number_beams):
            output += '\tBeam: %d\n' % count
            output += '\tXYZ: %.2f %.2f %.2f\n' % (self.along[count], self.across[count], self.depth[count])
            output += '\tDetection window: %d\n' % self.detection_window[count]
            output += '\tQuality factor: %d\n' % self.quality_factor[count]
            output += '\tBeam incidence angle adjustment: %.1f\n' % self.beam_incidence_angle_adjustment[count]
            output += '\tDetection information: %d\n' % self.detection_information[count]
            output += '\tReal time cleaning information: %d\n' % self.realtime_cleaning_information[count]
            output += '\tReflectivity: %.1f\n' % self.reflectivity[count]

        return output


class KmSeabedImage89(Km):
    def __init__(self, data, remote=True):

        super(KmSeabedImage89, self).__init__(data, remote=remote)

        if remote:
            image_head = struct.unpack("<fH2h3H", self.data[16:32])
        else:
            image_head = struct.unpack("<fH2h3H", self.data[20:36])

        self.sampling_frequency = image_head[0]
        self.range_to_normal_incidence = image_head[1]
        self.BSN = float(image_head[2]) / 10.0
        self.BSO = float(image_head[3]) / 10.0
        self.tx_beamwidth = float(image_head[4]) / 10.0
        self.tvg_crossover_angle = float(image_head[5]) / 10.0
        self.number_beams = image_head[6]

        self.sorting_direction = np.zeros(self.number_beams, dtype=np.int)
        self.detection_information = np.zeros(self.number_beams, dtype=np.int)
        self.number_samples = np.zeros(self.number_beams, dtype=np.int)
        self.center_sample = np.zeros(self.number_beams, dtype=np.int)

        if remote:
            offset = 32
        else:
            offset = 36
        bytes_per_beam = 6
        self.snippets_nr = 0
        for b in range(self.number_beams):
            beam = struct.unpack("<bB2H", self.data[offset:offset + bytes_per_beam])
            self.sorting_direction[b] = beam[0]
            self.detection_information[b] = beam[1]
            self.number_samples[b] = beam[2]
            self.center_sample[b] = beam[3]
            self.snippets_nr += self.number_samples[b]
            offset += bytes_per_beam

        self.snippets = []
        for b in range(self.number_beams):
            parse_string = "<%dh" % (self.number_samples[b])
            bytes_to_read = int(2 * self.number_samples[b])
            raw_samples = struct.unpack(parse_string, self.data[offset:offset + bytes_to_read])
            samples = np.zeros(self.number_samples[b])
            for s in range(int(self.number_samples[b])):
                samples[s] = float(raw_samples[s]) / 10.0
            self.snippets.append(samples)
            offset += bytes_to_read

    def serialize(self):
        loc_data = super(KmSeabedImage89, self).serialize()

        if self.remote:
            b_count = 16
        else:
            b_count = 20

        b_data = struct.pack("<f", self.sampling_frequency)
        b_size = len(b_data)
        loc_data[b_count:b_count + b_size] = b_data
        b_count += b_size

        b_data = struct.pack("<H", self.range_to_normal_incidence)
        b_size = len(b_data)
        loc_data[b_count:b_count + b_size] = b_data
        b_count += b_size

        b_data = struct.pack("<h", int(self.BSN * 10))
        b_size = len(b_data)
        loc_data[b_count:b_count + b_size] = b_data
        b_count += b_size

        b_data = struct.pack("<h", int(self.BSO * 10))
        b_size = len(b_data)
        loc_data[b_count:b_count + b_size] = b_data
        b_count += b_size

        b_data = struct.pack("<H", int(self.tx_beamwidth * 10))
        b_size = len(b_data)
        loc_data[b_count:b_count + b_size] = b_data
        b_count += b_size

        b_data = struct.pack("<H", int(self.tvg_crossover_angle * 10))
        b_size = len(b_data)
        loc_data[b_count:b_count + b_size] = b_data
        b_count += b_size

        b_data = struct.pack("<H", self.number_beams)
        b_size = len(b_data)
        loc_data[b_count:b_count + b_size] = b_data
        b_count += b_size

        # beams
        for b in range(self.number_beams):
            b_data = struct.pack("<b", self.sorting_direction[b])
            b_size = len(b_data)
            loc_data[b_count:b_count + b_size] = b_data
            b_count += b_size

            b_data = struct.pack("<B", self.detection_information[b])
            b_size = len(b_data)
            loc_data[b_count:b_count + b_size] = b_data
            b_count += b_size

            b_data = struct.pack("<H", self.number_samples[b])
            b_size = len(b_data)
            loc_data[b_count:b_count + b_size] = b_data
            b_count += b_size

            b_data = struct.pack("<H", self.center_sample[b])
            b_size = len(b_data)
            loc_data[b_count:b_count + b_size] = b_data
            b_count += b_size

        # samples
        for b in range(self.number_beams):
            for s in range(int(self.number_samples[b])):
                b_data = struct.pack("<h", int(self.snippets[b][s] * 10))
                b_size = len(b_data)
                loc_data[b_count:b_count + b_size] = b_data
                b_count += b_size
        # log.debug(self.snippets[0][402], self.snippets[0][403])
        logger.debug("serialized: %s B" % b_count)

        # fix checksum
        b_data = struct.pack("<H", KmSeabedImage89.calc_2bytes_checksum(loc_data))
        b_size = len(b_data)
        loc_data[-b_size:] = b_data

        return loc_data

    def __str__(self):

        output = Km.__str__(self)
        output += '- Sampling frequency (Hz): %f\n' % self.sampling_frequency
        output += '- Range to normal incidence: %d\n' % self.range_to_normal_incidence
        output += '- BS normal incidence: %0.1f\n' % self.BSN
        output += '- BS oblique incidence: %0.1f\n' % self.BSO
        output += '- TX beamwidth along: %0.1f\n' % self.tx_beamwidth
        output += '- TVG crossover angle: %0.1f\n' % self.tvg_crossover_angle
        output += '- Number beams: %d\n' % self.number_beams

        for count in range(self.number_beams):
            output += '\n\tBeam %d\n' % count
            output += '\tSorting direction: %d\n' % self.sorting_direction[count]
            output += '\tDetection information: %d\n' % self.detection_information[count]
            output += '\tNumber samples: %d\n' % self.number_samples[count]
            output += '\tCenter sample: %d\n' % self.center_sample[count]
            output += '\tCenter BS: %d\n' % self.snippets[count][self.center_sample[count] - 1]

        return output


class KmWatercolumn(Km):
    def __init__(self, data):

        super(KmWatercolumn, self).__init__(data)

        wc_header = struct.unpack("<6HIhBbB3B", self.data[16:40])
        self.number_datagrams = wc_header[0]
        self.datagram_number = wc_header[1]
        self.number_tx_sectors = wc_header[2]
        self.total_number_beams = wc_header[3]
        self.number_beams = wc_header[4]
        self.sound_speed = float(wc_header[5]) / 10.0
        self.sampling_frequency = float(wc_header[6]) / 100.0
        self.heave = float(wc_header[7]) / 100.0
        self.tvg_x = wc_header[8]
        self.tvg_c = wc_header[9]
        self.scanning_info = wc_header[10]
        self.spare1 = wc_header[11]
        self.spare2 = wc_header[12]
        self.spare3 = wc_header[13]

        self.sector_tilt_angle = np.zeros(self.number_tx_sectors)
        self.sector_frequency = np.zeros(self.number_tx_sectors)
        self.sector_number = np.zeros(self.number_tx_sectors)
        self.sector_spare = np.zeros(self.number_tx_sectors)

        offset = 40
        for s in range(self.number_tx_sectors):
            sector = struct.unpack("<hHBB", self.data[offset:offset + 6])
            self.sector_tilt_angle[s] = float(sector[0]) / 100.0
            self.sector_frequency[s] = float(sector[1]) * 10
            self.sector_number[s] = sector[2]
            self.sector_spare[s] = sector[3]
            offset += 6

        self.beam_pointing_angle = np.zeros(self.number_beams)
        self.beam_start_range = np.zeros(self.number_beams)
        self.beam_num_samples = np.zeros(self.number_beams)
        self.beam_detected_range = np.zeros(self.number_beams)
        self.beam_sector_number = np.zeros(self.number_beams)
        self.beam_number = np.zeros(self.number_beams)

        self.samples = []

        bytes_per_beam = 10
        for b in range(self.number_beams):
            beam = struct.unpack("<h3H2B", self.data[offset:offset + bytes_per_beam])
            self.beam_pointing_angle[b] = float(beam[0]) / 100.0
            self.beam_start_range[b] = beam[1]
            self.beam_num_samples[b] = beam[2]
            self.beam_detected_range[b] = beam[3]
            self.beam_sector_number[b] = beam[4]
            self.beam_number[b] = beam[5]

            offset += bytes_per_beam
            samples = self.data[offset:offset + int(self.beam_num_samples[b])]
            self.samples.append(samples)
            offset += int(self.beam_num_samples[b])

    def __str__(self):

        output = Km.__str__(self)
        output += '- Datagram %d of %d\n' % (self.datagram_number, self.number_datagrams)
        output += '- Number of TX sectors: %d\n' % self.number_tx_sectors
        output += '- Number of RX beams: %d of %d\n' % (self.number_beams, self.total_number_beams)
        output += '- Sound speed (m/s): %.1f\n' % self.sound_speed
        output += '- Sampling Frequency (Hz): %.2f\n' % self.sampling_frequency
        output += '- Heave at TX (m): %.2f\n' % self.heave
        output += '- TVG "X" offset: %d\n' % self.tvg_x
        output += '- TVG "C": %d\n' % self.tvg_c
        output += '- Scanning info: %d\n' % self.scanning_info
        output += '- Spare: %d %d %d\n' % (self.spare1, self.spare2, self.spare3)

        for s in range(self.number_tx_sectors):
            output += '\n\tSector %d\n' % s
            output += '\tSector ID number: %d\n' % self.sector_number[s]
            output += '\tTilt angle (deg): %.2f\n' % self.sector_tilt_angle[s]
            output += '\tFrequency (Hz): %d\n' % self.sector_frequency[s]
            output += '\tSpare: %d\n' % self.sector_spare[s]

        for count in range(self.number_beams):
            output += '\n\tBeam %d\n' % count
            output += '\tPointing angle (deg): %.2f\n' % self.beam_pointing_angle[count]
            output += '\tStart range: %d\n' % self.beam_start_range[count]
            output += '\tNumber of samples: %d\n' % self.beam_num_samples[count]
            output += '\tDetection range: %d\n' % self.beam_detected_range[count]
            output += '\tSector number: %d\n' % self.beam_sector_number[count]
            output += '\tBeam number: %d\n' % self.beam_number[count]

        return output
