import serial
import time

ser = serial.Serial('/dev/ttyUSB0', 115200)  # Open serial port

try:
    while True:
        # ser.write(b'Hello ESP32\n')  # Send a message
        ser.write(b'1\n')  # Send a message
        # print('Sent message to ESP32')
        time.sleep(2)
except KeyboardInterrupt:
    ser.close()  # Close serial port when done
