from .. import servo
import os
import atexit
import pytest
import unittest.mock as mock


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


def test_fd_close():
    """
    Ensures that close_fd() works
    """
    with mock.patch.object(servo.servoblaster_fd, 'close') as fd_mock:
        servo.close_fd()
        assert fd_mock.called


def test_module_init():
    # TODO: less ugly test that has fewer side effects
    with mock.patch('os.path.exists', return_value=True):
        with mock.patch('builtins.open') as open_mock:
            servo.module_init()
            assert open_mock.called
    servo.module_init()
    assert servo.servoblaster_fd
    assert servo.test_port

@atexit.register
def on_exit():
    test_fd.close()  # pragma: no cover
