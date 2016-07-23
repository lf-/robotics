from .. import servo
import os
import atexit
import pytest


test_fd = os.fdopen(os.open(servo.test_port,
                            os.O_RDONLY | os.O_NONBLOCK), 'rb')


def test_write_sb():
    servo.write_sb('test')
    assert test_fd.read() == b'test\n'

def test_servo_class():
    serv = servo.Servo(18)
    serv.angle = 90
    assert test_fd.read() == b'P1-18=1500us\n'
    assert serv.angle == 90
    with pytest.raises(ValueError):
        serv.angle = 181

@atexit.register
def on_exit():
    test_fd.close()  # pragma: no cover
