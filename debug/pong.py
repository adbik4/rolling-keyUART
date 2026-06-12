#/usr/bin/python3
import serial

DEV = "/dev/ttyS0"

try:
    uart = serial.Serial(port=DEV, baudrate=9600, timeout=1)
except serial.SerialException as e:
    print("[WARNING] Failed to open UART port", DEV)
    quit()

print("Listening...")
while True:
    read_buf = uart.readline()
    if read_buf == "ping\n":
        print("Recieved ping from", DEV)