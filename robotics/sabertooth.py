import serial
import atexit
import os
import os.path
import threading

from . import config


serial_write_lock = threading.Lock()
serial_device = config.SABERTOOTH_SERIAL_DEVICE
test_device = None

if not os.path.exists(serial_device):
    # must be running on a test machine, give it a pty

    # this is ugly and horrible because:
    # * python has no bindings for grantpt and unlockpt
    # * pyserial is idiotic and doesn't do all this pty crap sensibly or by
    #   itself at all

    # opens a pty without initializing it, then initializes it once it gets
    # the fd out of pyserial
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


START = bytes((170,))
MAX_SPEED = 127

CMD_FWD_M1 = 0
CMD_BACK_M1 = 1
CMD_FWD_M2 = 4
CMD_BACK_M2 = 5


class Sabertooth:
    """
    A class representing a single DimensionEngineering Sabertooth motor driver
    """
    def __init__(self, addr):
        """
        Parameters:
        addr -- packetized serial address set on the DIP switches
        """
        self.addr = addr
        self._motor1speed = None
        self._motor2speed = None

    @property
    def motor1(self):
        return self._motor1speed

    @motor1.setter
    def motor1(self, speed):
        """
        Set motor 1 of the sabertooth to a given speed (0-127)
        """
        # no sending in stupid values and crashing
        if speed > MAX_SPEED:
            speed = MAX_SPEED
        elif speed < -MAX_SPEED:
            speed = -MAX_SPEED

        self._motor1speed = speed
        if speed >= 0:
            packet = generate_packet(self.addr, CMD_FWD_M1, int(speed))
        elif speed < 0:
            packet = generate_packet(self.addr, CMD_BACK_M1, int(abs(speed)))
        send(packet)

    @property
    def motor2(self):
        return self._motor2speed

    @motor2.setter
    def motor2(self, speed):
        """
        Set motor 2 of the sabertooth to a given speed (0-127)
        """
        # no sending in stupid values and crashing
        if speed > MAX_SPEED:
            speed = MAX_SPEED
        elif speed < -MAX_SPEED:
            speed = -MAX_SPEED

        self._motor2speed = speed
        if speed >= 0:
            packet = generate_packet(self.addr, CMD_FWD_M2, int(speed))
        elif speed < 0:
            packet = generate_packet(self.addr, CMD_BACK_M2, int(abs(speed)))
        send(packet)


def generate_packet(addr, cmd, data) -> bytes:
    """
    Generate a 4-byte packet conforming to the packetized serial protocol.
    Generates the checksum for you.

    Parameters:
    addr -- address byte, > 128
    cmd -- command byte, < 128
    data -- data byte, < 128

    Returns:
    A 4-byte bytes object suitable for sending to a sabertooth
    """
    checksum = ((addr + cmd + data) % 256) & 0b01111111
    return bytes((addr, cmd, data, checksum))


def send(data: bytes):
    """
    Sends some serial data to the serial port.
    Handles thread locking.

    Parameters:
    data -- a bytes object
    """
    if 'LF_SERIAL_DEBUG' in os.environ:
        print(data.hex())
    with serial_write_lock:
        ser.write(data)


def setup():
    """
    Sends the initial 0xaa byte to the sabertooth to initialize it.
    Do not call more than once *per boot* nor within 1 second of powering the
    sabertooth!
    """
    send(START)


@atexit.register
def onexit():
    """
    Properly close serial port
    """
    ser.close()


def main():
    """
    A rudimentary CLI for controlling sabertooths
    """
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
