from . import sabertooth
from . import util
from . import config


class Robot:
    """
    A class representing and controlling a real life robot.
    """
    SAFE_STATE = {
        'throttle': 0,
        'turn': 0
    }
    STATE_PROPS = SAFE_STATE.keys()

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
        self._throttle = 0
        self._turn = 0

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
            throttleL = throttle * (1 - abs(turn))
            throttleR = throttle
        if self.reverse_drive:
            throttleL, throttleR = throttleR, throttleL
        self.throttleL = throttleL
        self.throttleR = throttleR

        self._throttle = throttle
        self._turn = turn

        self.drive_sabertooth.motor1 = util.translate(throttleL, -1, 1,
                                                      -127, 127)
        self.drive_sabertooth.motor2 = util.translate(throttleR, -1, 1,
                                                      -127, 127)

    @property
    def state(self):
        """
        The current state of a robot
        """
        return {prop: getattr(self, prop) for prop in self.STATE_PROPS}

    def update_state(self, update: dict):
        for prop, value in update.items():
            if prop in self.STATE_PROPS:
                setattr(self, prop, value)

    def safe(self):
        """
        Halts main wheel movement, returns servos to zero, etc
        """
        self.update_state(self.SAFE_STATE)

    @property
    def throttle(self):
        return self._throttle

    @throttle.setter
    def throttle(self, new: float):
        self.move(new, self._turn)

    @property
    def turn(self):
        return self._turn

    @turn.setter
    def turn(self, new: float):
        self.move(self._throttle, new)


robot = Robot(config.DRIVE_SABERTOOTH_ID, config.REVERSE_DRIVE)
