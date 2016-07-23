from . import sabertooth
from . import servo
from . import util
from . import config


class Robot:
    def __init__(self, drive_sabertooth_id, reverse_drive=False):
        """
        Make a robot.

        Params:
        drive_sabertooth_id -- packetized serial ID for sabertooth connected
                               to drive wheels
        reverse_drive -- reverse the drive wheels/turn direction
        """
        self.drive_sabertooth = sabertooth.Sabertooth(drive_sabertooth_id)
        self.reverse_drive = reverse_drive

    def move(self, throttle, turn, **args):
        """
        Run the main wheels.

        Parameters:
        throttle -- throttle value from -1 to 1
        turn -- turn value from -1 (full left) to 1 (full right)
        """
        if turn >= 0:
            throttleL = throttle
            throttleR = throttle * (1 - turn)
        elif turn < 0:
            throttleL = throttle * (1 - turn)
            throttleR = throttle
        if self.reverse_drive:
            throttleL, throttleR = throttleR, throttleL
        self.drive_sabertooth.motor1 = throttleL
        self.drive_sabertooth.motor2 = throttleR


robot = Robot(config.DRIVE_SABERTOOTH_ID, config.REVERSE_DRIVE)
