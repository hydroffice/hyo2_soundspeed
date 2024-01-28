import serial
import time
import traceback

try:
    from hyo2.ssm2.lib.listener.seacat.sbe_serialcomms import SeacatComms, UTF8Serial

except Exception:
    print("Seacat serial communications module not found or failed to load")
    print("Emulator will still work but the capture function will raise an pkg_exception")


    class UTF8Serial(serial.Serial):
        def write(self, data):
            serial.Serial.write(self, data.encode('utf-8'))

        def read(self, size=1):
            data = serial.Serial.read(self, size)
            # print("raw read:", data, self.port, self.baudrate, self.stopbits, self.parity)
            try:
                data = data.decode("utf-8")  # converts from bytes in python 3.x
            except AttributeError:
                pass
            except UnicodeDecodeError:
                data = ""
                print("bad message received", data)
            # print("decoded data", str(data))
            return str(data)  # converts to ascii for python 2.7, leaves as unicode for 3.x


class UTF8Capture(UTF8Serial):
    def __init__(self, filename, *args, **args2):
        super().__init__(*args, **args2)
        self.outfile = open(filename, "wb+")

    def write(self, data):
        self.outfile.write(b"<write>")
        if isinstance(data, str):
            self.outfile.write(data.encode())
        else:
            self.outfile.write(data)
        self.outfile.write(b"</write>\r\n")
        UTF8Serial.write(self, data)

    def read(self, size=1):
        data = UTF8Serial.read(self, size)
        self.outfile.write(b"<read>")
        if isinstance(data, str):
            self.outfile.write(data.encode())
        else:
            self.outfile.write(data)
        self.outfile.write(b"</read>\r\n")


def respond(max_time=5.0, sleep_time=.04, port='COM1', baud=9600, byte_size=serial.EIGHTBITS, parity=serial.PARITY_NONE,
            stop_bits=serial.STOPBITS_ONE, timeout=.1):
    """listen to a COM port and respond like a SeaCat for a certain amount of time"""
    com_link = UTF8Serial(port, baud, bytesize=byte_size, parity=parity, stopbits=stop_bits, timeout=timeout)

    print("start responding to %s for %.1f sec" % (port, max_time))
    try:
        t = time.time()
        while time.time() - t < max_time:

            d = com_link.read(1000)
            if str(d):
                # print type(d), d
                try:
                    # d=str(d.decode("utf-8"))
                    print("str:", repr(d))
                except:
                    print("failed decode")

            if "DS" in d:
                print("writing status")
                com_link.write(
                    "SeacatPlus V 1.6b  SERIAL NO. 4677    05 Mar 2010  16:01:56\r\nvbatt = 13.4, vlith =  8.2, "
                    "ioper =  60.7 ma, ipump =  45.4 ma, \r\nstatus = not logging\r\nnumber of scans to average = 1\r\n"
                    "samples = 1374, free = 761226, casts = 2\r\nmode = profile, minimum cond freq = 3258, "
                    "pump delay = 40 sec\r\nautorun = no, ignore magnetic switch = no\r\nbattery type = alkaline, "
                    "battery cutoff =  7.3 volts\r\npressure sensor = strain gauge, range = 508.0\r\nSBE 38 = no, "
                    "Gas Tension Device = no\r\nExt Volt 0 = no, Ext Volt 1 = no, Ext Volt 2 = no, Ext Volt 3 = no\r\n"
                    "echo commands = yes\r\noutput format = raw HEX\r\nS>")

            elif "SB" in d or "Baud=" in d:
                if "SB" in d:
                    if d[2] == "1":
                        new_baud = 600
                    elif d[2] == "2":
                        new_baud = 1200
                    elif d[3] == "3":
                        new_baud = 9600
                    else:
                        print("unrecognized baud rate -- ignoring ", d)
                        continue
                else:
                    new_baud = int(d[5:10])
                com_link.close()
                com_link = UTF8Serial(port, new_baud, bytesize=byte_size, parity=parity, stopbits=stop_bits,
                                      timeout=timeout)

            elif "DH" in d:
                com_link.write("Headers!!!\r\nS>")

            elif "\r" in d:
                print("writing prompt")
                com_link.write("S>\r\n")

            else:
                time.sleep(sleep_time)

    except Exception:
        traceback.print_exc()

    finally:
        com_link.close()
        print("end responding to %s" % port)


def raw_capture(filename, port='COM1', baud=9600, byte_size=serial.EIGHTBITS, parity=serial.PARITY_NONE):
    sbe = SeacatComms.open_seacat(port, baud, byte_size, parity)
    sbe.comlink.close()
    # replace the serial COMs with one that will push the data to a file
    sbe.comlink = UTF8Capture(filename, sbe.comlink.port, sbe.comlink.baudrate, bytesize=sbe.comlink.bytesize,
                              parity=sbe.comlink.parity, stopbits=sbe.comlink.stopbits, timeout=sbe.comlink.timeout)
    try:
        sbe.wake()

    except AttributeError:  # HSTB version
        sbe.Wake()
        sbe.GetStatus()
        sbe.GetDateTime()
        sbe.GetVoltages()
        sbe.GetHeaders()
        sbe.GetScans()
        sbe.GetCasts()
        sbe.GetCalibration()

    else:  # hydroffice version
        sbe.get_status()
        sbe.get_datetime()
        sbe.get_voltages()
        sbe.get_headers()
        sbe.get_scans()
        sbe.get_casts()
        sbe.get_calibration()
