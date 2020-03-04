This project is based on radionerd's Data logging software USB driver for the Hyelec/Peakmeter MS8236 multimeter:
https://github.com/radionerd/ms8236usb

HYELEC/PEAKMETER MS8236 USB DRIVER FOR LINUX
--------------------------------------------

The Hyelec/PeakMeter MS8236 is a low cost true RMS multimeter with USB interface.
This software helps users to connect the meter to a computer running Linux for logging or display purposes.
The ms8236 USB interface appears to the computer as a serial port running at 2400 baud.
The ms8236 sends 22 bytes of information that reflect icons and LCD segments that are active.
The program ms8236usb receives the active LCD information and translates this to log text on stdout.

Usage
-----
python3 pyms8236usb.py /dev/tty.usbserial
