from unittest import mock
import sdl2
import pytest
from .. import controller


@mock.patch('sdl2.SDL_Init')
def test_init(sdl_init):
    controller.init()
    final_mode = 0
    for call in sdl_init.call_args_list:
        final_mode |= call[0][0]
    assert final_mode & (sdl2.SDL_INIT_JOYSTICK | sdl2.SDL_INIT_HAPTIC)


@mock.patch('sdl2.SDL_NumJoysticks')
def test_check_controller(numjoysticks):
    numjoysticks.return_value = 0
    with pytest.raises(RuntimeError):
        controller.check_controller()

    numjoysticks.return_value = 1
    controller.check_controller()
