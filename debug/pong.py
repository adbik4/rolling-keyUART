#!/usr/bin/python3
import serial
import os

DEV = "/dev/ttyS0"

if os.geteuid() != 0:
    print("Run this program as root")
    quit()

try:
    uart = serial.Serial(port=DEV, baudrate=9600, timeout=1)
except serial.SerialException as e:
    print("[WARNING] Failed to open UART port", DEV)
    quit()

print("Listening...")
try:
    while True:
        read_buf = uart.readline()
        if read_buf == b"ping\n":
            print("Recieved ping from", DEV)

except KeyboardInterrupt:
    quit()
