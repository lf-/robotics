from .. import sabertooth
import serial
import time
import unittest.mock as mock


ser = serial.Serial(sabertooth.test_device, timeout=0)


def clear_serial_buffer():
    ser.reset_input_buffer()
    ser.reset_output_buffer()


def test_packet_generation():
    assert sabertooth.generate_packet(130, 0, 64) == bytes((130, 0, 64, 66))


@mock.patch.object(sabertooth, 'send')
def test_motorN(send_mock):
    """
    Test the behaviour of the Sabertooth.motor{1,2} properties
    """
    st = sabertooth.Sabertooth(128)
    # test forwards motor 1
    st.motor1 = 127
    send_mock.assert_called_with(bytes((128, 0, 127, 127)))
    # test correct behaviour with out of range values
    st.motor1 = 255
    send_mock.assert_called_with(bytes((128, 0, 127, 127)))
    # back
    st.motor1 = -127
    send_mock.assert_called_with(bytes((128, 1, 127, 0)))
    # motor 2 forward
    st.motor2 = 127
    send_mock.assert_called_with(bytes((128, 4, 127, 3)))
    # back
    st.motor2 = -127
    send_mock.assert_called_with(bytes((128, 5, 127, 4)))

    # ensure correct storage
    st.motor1 = 127
    assert st.motor1 == 127
    st.motor2 = 127
    assert st.motor2 == 127


def test_limit_speed():
    """
    Ensure that _limit_speed() has correct behaviour with out of range speeds
    """
    assert sabertooth._limit_speed(128) == 127
    assert sabertooth._limit_speed(64) == 64
    assert sabertooth._limit_speed(-128) == -127
    assert sabertooth._limit_speed(-64) == -64


@mock.patch.object(sabertooth, 'send')
def test_init_bus(send_mock):
    """
    Ensure init_bus() sends the correct start byte
    """
    sabertooth.init_bus()
    send_mock.assert_called_with(bytes((0xaa,)))


def test_onexit():
    """
    Ensure that onexit() works properly
    """
    with mock.patch.object(sabertooth.ser, 'close'):
        sabertooth.onexit()
        assert sabertooth.ser.close.called


def test_parse_args():
    """
    Test argument parsing
    """
    ns = sabertooth.parse_args(['-a', '128', '-m', '1', '-s', '-127'])
    assert ns.address == 128
    assert ns.motornum == 1
    assert ns.speed == -127


def test_main():
    """
    Test main()
    """
    def pm_side_effect(val):
        assert val == 127

    with mock.patch.object(sabertooth.Sabertooth, 'motor1',
                           new_callable=mock.PropertyMock) as pm1:
        with mock.patch.object(sabertooth.Sabertooth, 'motor2',
                               new_callable=mock.PropertyMock) as pm2:
            pm1.side_effect = pm_side_effect
            pm2.side_effect = pm_side_effect
            sabertooth.main(argv=['-a', '128', '-m', '1', '-s', '127'])
            sabertooth.main(argv=['-a', '128', '-m', '2', '-s', '127'])
