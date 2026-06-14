#!/usr/bin/python3
import serial

DEV = "/dev/ttyUSB0"

try:
    uart = serial.Serial(port=DEV, baudrate=9600, timeout=1)
except serial.SerialException as e:
    print(f"[WARNING] Failed to open UART port {DEV}: {e}")
    quit()

uart.write(b"ping\n")
uart.flush()
uart.close()
