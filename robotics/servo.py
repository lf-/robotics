import os
import os.path
import atexit


ANGLE_MIN = 0
ANGLE_MAX = 180
# µs min/max
US_MIN = 500
US_MAX = 2500


if os.path.exists('/dev/servoblaster'):
    # running on pi
    servoblaster_fd = open('/dev/servoblaster', 'wb+', buffering=0)
    test_port = None
else:
    # test mode
    # TODO: don't abuse ptys
    # Note: FIFOs don't work because of requiring the reading end to open it
    #       first
    import pty
    pty_pair = pty.openpty()
    servoblaster_fd = os.fdopen(pty_pair[0], 'wb', buffering=0)
    test_port = os.ttyname(pty_pair[1])


class ServoPresets:
    # (min_angle, max_angle, min_pulsewidth, max_pulsewidth)
    # bog-standard servo
    standard = (0, 180, 500, 2500)
    # SBRS-5314-HTG continuous (allegedly) servo
    sbrs5314 = (0, 280, 900, 2100)


class Servo:
    def __init__(self, pin, header=1, angle_uS_coupling=(0, 180, 500, 2500)):
        """
        Abstract object for controlling a servo using the ServoBlaster daemon

        Parameters:
        pin -- pin on the header, NOT GPIO number

        Optional Parameters:
        header -- 1 or 5, 1 is the main, big, header
        angle_uS_coupling -- ratio from angle to microseconds for a given
                             servo. Tuple in the format
                             (angle_min, angle_max, uS_min, uS_max)
        """
        self.pin = pin
        self.header = header
        self._angle = None
        self.angle_uS_coupling = angle_uS_coupling

    @property
    def angle(self):
        """
        Angle of a servo, between angle_uS_coupling[0] and angle_uS_coupling[1]
        """
        return self._angle

    @angle.setter
    def angle(self, new_angle):
        if (new_angle < self.angle_uS_coupling[0] or
                new_angle > self.angle_uS_coupling[1]):
            raise ValueError('New angle outside of range '
                             '{0[0]}-{0[1]}'.format(self.angle_uS_coupling))
        uS = int(round(translate(new_angle, *self.angle_uS_coupling), -1))
        cmd = 'P{}-{}={}us'.format(self.header, self.pin, uS)
        write_sb(cmd)
        self._angle = new_angle


def write_sb(cmd: str):
    """
    Write a command to the servoblaster port

    Parameters:
    cmd -- command to send to servoblaster port
    """
    servoblaster_fd.write((cmd + '\n').encode())


def translate(value, leftMin, leftMax, rightMin, rightMax):
    """
    Map one range of values to another.

    Parameters:
    value -- the number, between leftMin and leftMax to map into
             rightMin to rightMax
    leftMin -- bottom of range of value parameter
    leftMax -- top of range of value parameter
    rightMin -- bottom of range of output
    rightMax -- top of range of output
    """
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)


@atexit.register
def close_fd():
    servoblaster_fd.close()
