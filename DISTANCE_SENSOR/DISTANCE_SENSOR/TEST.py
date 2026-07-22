import serial
import time

# Initialize serial port (replace '/dev/ttyACM0' with your actual port name)
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
time.sleep(2) # Give the connection time to settle

try:
    while True:
        if ser.in_waiting > 0:
            # Read a line of data, decode it, and strip whitespace
            line = ser.readline().decode('utf-8').rstrip()
            print(line)
except KeyboardInterrupt:
    print("Communication stopped.")
finally:
    ser.close()
