import serial
import math
import atexit

start = bytes((170,))
ser = serial.Serial('/dev/ttyAMA0', 9600)

SPEED_FWD_M1= 0
SPEED_BACK_M1 = 1
SPEED_FWD_M2 = 4
SPEED_BACK_M2 = 5

class Sabertooth:
    def __init__(self, addr):
        self.addr = addr

    @property
    def motor1(self):
        return self._motor1speed

    @motor1.setter
    def motor1(self, speed):
        # no sending in stupid values and crashing
        if speed > 255:
            speed = 255
        elif speed < -255:
            speed = -255

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
        if speed > 255:
            speed = 255
        elif speed < -255:
            speed = -255

        self._motor2speed = speed
        if speed >= 0:
            packet = generate_packet(self.addr, SPEED_FWD_M2, int(speed))
        elif speed < 0:
            packet = generate_packet(self.addr, SPEED_BACK_M2, int(abs(speed)))
        send(packet)

def generate_packet(addr, cmd, data):
    checksum = (addr + cmd + data) & 0b01111111
    return bytes((addr, cmd, data, checksum))

def send(data):
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
