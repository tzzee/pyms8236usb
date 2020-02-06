import serial
import datetime
import threading
from collections import deque
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
from argparse import ArgumentParser

# This code was pasted together from the following sources
# Protocol reference: https://sigrok.org/wiki/HYELEC_MS8236
# Additions by Richard Jones
# Additions by Kenji Takahashi

def decode_digit(raw_digit):
    digit_pattern = [0x00,0x5f,0x06,0x6b,0x2f,0x36,0x3d,0x7d,0x07,0x7f,0x3f,0x58]
    digit_string  = ["" , "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "L"]
    for i in range(12):
        if digit_pattern[i] == (raw_digit & 0x7f):
            if raw_digit & 0x80:
                return  "." + digit_string[i]
            return digit_string[i]

def decode_bits(bits, icon):
    for i in range(8):
        if bits & 1:
            return icon[i]
        bits = bits >> 1
    return ""

class Data:
    def __init__(self):
        self.degit = 0.0
        self.C = ''
        self.u = ''
        self.diode_icon = ''
        self.progress = ''
        self.usb_icon = ''
        self.time = datetime.datetime.now()

def decode_msg(raw_msg):
    d = Data()
    degit_str = ""
    if raw_msg[10]&0x18:
        degit_str += "-"
    degit_str += decode_digit(raw_msg[9])
    degit_str += decode_digit(raw_msg[8])
    degit_str += decode_digit(raw_msg[7])
    degit_str += decode_digit(raw_msg[6])
    d.degit = float(degit_str)
    icons20 = ["DegC","DegF","?","?","m","u","n","F"]
    d.C = decode_bits(raw_msg[20], icons20)
    icons21 = ["u","m","A","V","M","k","Ohms","Hz"]
    d.u = decode_bits(raw_msg[21], icons21)
    icons10 = ["Diode","AC","DC ","-","-","","Continuity","LowBattery"]
    d.diode_icon = decode_bits(raw_msg[10]&0xE7, icons10)
    icons18 = ["","","","","Wait","Auto","Hold","REL"]
    d.progress = decode_bits(raw_msg[18], icons18)
    icons19 = ["","MAX","-","MIN","N/A","%","hFE","N/A"]
    d.usb_icon = decode_bits(raw_msg[19], icons19)
    return d

def _redraw(_, arg):
    if 0 < len(arg):
        x = [m.time for m in arg]
        y = [m.degit for m in arg]
        msg = arg[0]
        plt.cla()
        plt.title('PeakMeter')
        plt.xlabel("time")
        plt.ylabel(msg.diode_icon+"["+msg.C+msg.u+"]")
        plt.xlim(min(x), max(x))
        plt.ylim(0, 0.3)
        plt.plot(x, y)
        ave = np.average(y)
        plt.axhline(ave, ls = "-.", color = "magenta")
        
def main():
    parser = ArgumentParser()
    parser.add_argument('portname', type=str, help='debug server')
    args = parser.parse_args()

    portname = args.portname

    print("Data Logging interface for PeakMeter MS8236 USB Multimeter.\n")
    print("If logging does not start make sure USB lead is connected,\n")
    print("then press and hold USB button on meter for two seconds.\n")

    plot_length = 4*60*5
    arg = deque(maxlen=plot_length)
    fig = plt.figure(figsize=(10, 6))

    #baudrate 2400, 8 bits, no parity, 1 stop bit
    with serial.Serial(portname, 2400, timeout=0.1) as ser:
        def _update():
            # simple noncanonical input
            raw_msg = []
            while True:
                buf = ser.read()
                rdlen = len(buf)
                r = int.from_bytes(buf, byteorder='big')
                if rdlen > 0:
                    sync_char = [0xAA, 0x55, 0x52, 0x24, 0x01, 0x10]
                    if len(sync_char) <= len(raw_msg) or sync_char[len(raw_msg)] == r:
                        raw_msg.append(r)
                        if len(raw_msg) == 22:
                            msg = decode_msg(raw_msg)
                            arg.append(msg)
                            print(str(msg.degit) +" "+ msg.C + msg.u +" "+ msg.diode_icon +" "+ msg.progress +" "+ msg.usb_icon +" "+ msg.time.strftime("%Y/%m/%d %H:%M:%S.%f"))
                            raw_msg.clear()
                            # time.sleep(0.180)
                    else:
                        raw_msg.clear()
                        # time.sleep(0.180)
                #repeat read to get full message

        def _init():
            t = threading.Thread(target=_update)
            t.daemon = True
            t.start()

        params = {
            'fig': fig,
            'func': _redraw,
            'init_func': _init,
            'fargs': (arg, ),
            'interval': 200,  # msec
        }
        anime = animation.FuncAnimation(**params)
        plt.show()

#==============
# Execution
#==============
if __name__ == '__main__': main()
