from __future__ import print_function, with_statement

import serial
import time
import traceback

try:
    from hyo36.soundspeed.listener.seacat.sbe_serialcomms import SeacatComms, UTF8Serial
except:
    try:
        from HSTB.soundspeed import SeacatComms, UTF8Serial
    except:
        print("Seacat serial communications module not found or failed to load")
        print("Emulator will still work but the capture function will raise an exception")

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
                    print("bad message received", data)
                # print("decoded data", str(data))
                return str(data)  # converts to ascii for python 2.7, leaves as unicode for 3.x


class captureUTF8(UTF8Serial):
    def __init__(self, fname, *args, **args2):
        UTF8Serial.__init__(self, *args, **args2)
        self.outfile = open(fname, "wb+")

    def write(self, data):
        self.outfile.write("<write>")
        self.outfile.write(data)
        self.outfile.write("</write>\r\n")
        UTF8Serial.write(self, data)

    def read(self, cnt):
        data = UTF8Serial.read(self, cnt)
        self.outfile.write("<read>")
        self.outfile.write(data)
        self.outfile.write("</read>\r\n")


def respond(maxt=5.0, sleeptime=.04, port='COM1', baud=9600, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE, timeout=.1):
    '''listen to a COM port and respond like a Seacat for a certain amount of time'''
    comlink = UTF8Serial(port, baud, bytesize=bytesize, parity=parity, stopbits=stopbits, timeout=timeout)
    try:
        t = time.time()
        while time.time() - t < maxt:
            d = comlink.read(1000)
            if str(d):
                # print type(d), d
                try:
                    # d=str(d.decode("utf-8"))
                    print("str:", repr(d))
                except:
                    print("failed decode")
            if "DS" in d:
                print("writing status")
                comlink.write("SeacatPlus V 1.6b  SERIAL NO. 4677    05 Mar 2010  16:01:56\r\nvbatt = 13.4, vlith =  8.2, ioper =  60.7 ma, ipump =  45.4 ma, \r\nstatus = not logging\r\nnumber of scans to average = 1\r\nsamples = 1374, free = 761226, casts = 2\r\nmode = profile, minimum cond freq = 3258, pump delay = 40 sec\r\nautorun = no, ignore magnetic switch = no\r\nbattery type = alkaline, battery cutoff =  7.3 volts\r\npressure sensor = strain gauge, range = 508.0\r\nSBE 38 = no, Gas Tension Device = no\r\nExt Volt 0 = no, Ext Volt 1 = no, Ext Volt 2 = no, Ext Volt 3 = no\r\necho commands = yes\r\noutput format = raw HEX\r\nS>")
            elif "SB" in d or "Baud=" in d:
                if "SB" in d:
                    if d[2] == "1":
                        newbaud = 600
                    elif d[2] == "2":
                        newbaud = 1200
                    elif d[3] == "3":
                        newbaud = 9600
                    else:
                        print("unrecognized baud rate -- ignoring ", d)
                        continue
                else:
                    newbaud = int(d[5:10])
                comlink.close()
                comlink = UTF8Serial(port, newbaud, bytesize=bytesize, parity=parity, stopbits=stopbits, timeout=timeout)
            elif "DH" in d:
                comlink.write("Headers!!!\r\nS>")
            elif "\r" in d:
                print("writing prompt")
                comlink.write("S>\r\n")
            else:
                time.sleep(sleeptime)
    except:
        traceback.print_exc()
    finally:
        comlink.close()


def rawcapture(fname, port='COM1', baud=9600, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE):
    sbe = SeacatComms.open_seacat(port, baud, bytesize, parity)
    sbe.comlink.close()
    # replace the serial comms with one that will push the data to a file
    sbe.comlink = captureUTF8(fname, sbe.comlink.port, sbe.comlink.baudrate, bytesize=sbe.comlink.bytesize,
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


if __name__ == "__main__":
    from os import path
    p = path.join(path.split(path.abspath(__file__))[0], "seacat_capture.txt")
    rawcapture(p)
