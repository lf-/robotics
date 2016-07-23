from .. import sabertooth
import serial
import time


ser = serial.Serial(sabertooth.test_device, timeout=0)


def clear_serial_buffer():
    ser.reset_input_buffer()
    ser.reset_output_buffer()


def test_packet_generation():
    assert sabertooth.generate_packet(130, 0, 64) == bytes((130, 0, 64, 66))

def test_class():
    clear_serial_buffer()
    st = sabertooth.Sabertooth(128)
    # test forwards motor 1
    st.motor1 = 127
    time.sleep(0.1)
    assert ser.read(4) == bytes((128, 0, 127, 127))
    # test correct behaviour with out of range values
    st.motor1 = 255
    time.sleep(0.1)
    assert ser.read(4) == bytes((128, 0, 127, 127))
    # back
    st.motor1 = -127
    assert ser.read(4) == bytes((128, 1, 127, 0))
    # motor 2 forward
    st.motor2 = 127
    assert ser.read(4) == bytes((128, 4, 127, 3))
    # back
    st.motor2 = -127
    assert ser.read(4) == bytes((128, 5, 127, 4))

