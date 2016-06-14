import serial
import math
import atexit
import os
import os.path

start = bytes((170,))

serial_device = '/dev/ttyAMA0'
test_device = None

if not os.path.isfile(serial_device):
    # must be running on a test machine, give it a pty
    import ctypes
    libc = ctypes.cdll.LoadLibrary('libc.so.6')
    libc.ptsname.restype = ctypes.c_char_p
    serial_device = '/dev/ptmx'
    ser = serial.Serial(serial_device, 9600)
    libc.grantpt(ser.fd)
    libc.unlockpt(ser.fd)
    test_device = libc.ptsname(ser.fd).decode('utf-8')
else:
    ser = serial.Serial(serial_device, 9600)


max_speed = 127

SPEED_FWD_M1= 0
SPEED_BACK_M1 = 1
SPEED_FWD_M2 = 4
SPEED_BACK_M2 = 5


class Sabertooth:
    def __init__(self, addr):
        self.addr = addr
        self._motor1speed = None
        self._motor2speed = None

    @property
    def motor1(self):
        return self._motor1speed

    @motor1.setter
    def motor1(self, speed):
        # no sending in stupid values and crashing
        if speed > max_speed:
            speed = max_speed
        elif speed < -max_speed:
            speed = -max_speed

        self._motor1speed = speed
        if speed >= 0:
            packet = generate_packet(self.addr, SPEED_FWD_M1, int(speed))
        elif speed < 0:
            packet = generate_packet(self.addr, SPEED_BACK_M1, int(abs(speed)))
        send(packet)

    @property
    def motor2(self):
        return self._motor2speed

    @motor2.setter
    def motor2(self, speed):
        # no sending in stupid values and crashing
        if speed > max_speed:
            speed = max_speed
        elif speed < -max_speed:
            speed = -max_speed

        self._motor2speed = speed
        if speed >= 0:
            packet = generate_packet(self.addr, SPEED_FWD_M2, int(speed))
        elif speed < 0:
            packet = generate_packet(self.addr, SPEED_BACK_M2, int(abs(speed)))
        send(packet)

def generate_packet(addr, cmd, data):
    checksum = ((addr + cmd + data) % 256) & 0b01111111
    return bytes((addr, cmd, data, checksum))

def send(data):
    if 'LF_SERIAL_DEBUG' in os.environ:
        print(data.hex())
    ser.write(data)

def setup():
    send(start)

@atexit.register
def onexit():
    # properly close serial port
    ser.close()

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--address', '-a', type=int)
    parser.add_argument('--motornum', '-m', type=int)
    parser.add_argument('--speed', '-s', type=int)
    args = parser.parse_args()
    saber = Sabertooth(args.address)
    if args.motornum == 1:
        saber.motor1 = args.speed
    elif args.motornum == 2:
        saber.motor2 = args.speed

if __name__ == '__main__':
    main()
