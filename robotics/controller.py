import sdl2
import ctypes
import time

from . import util
from . import robot
from . import servo
from . import config


serv = servo.Servo(config.SERVO_PIN)
serv.angle = 85


def on_joystick_axis(axis_state, axis, value):
    throttle_combined = axis_state[5] - axis_state[2]
    throttle = util.translate(throttle_combined, -65535, 65535, -1, 1)
    turn = util.translate(axis_state[0], -32768, 32767, -1, 1)
    servo_pos = util.translate(axis_state[3], -32768, 32767, 55, 115)
    robot.robot.move(throttle ** 3, turn)
    serv.angle = servo_pos


def init():
    sdl2.SDL_Init(sdl2.SDL_INIT_JOYSTICK | sdl2.SDL_INIT_HAPTIC | sdl2.SDL_INIT_EVENTS)


def check_controller():
    if not sdl2.SDL_NumJoysticks() > 0:
        raise RuntimeError('No controllers available')

def main():
    init()
    check_controller()
    run()


def run():
    while sdl2.SDL_NumJoysticks() < 1:
        print('Waiting for controller...')
        time.sleep(0.1)
    print('Got controller')
    axis_state = [0, 0, 0, 0, 0, 0]
    # open the joystick so we get events for it
    js = sdl2.SDL_JoystickOpen(0)
    haptic = sdl2.SDL_HapticOpenFromJoystick(js)
    if sdl2.SDL_HapticRumbleSupported(haptic):
        sdl2.SDL_HapticRumbleInit(haptic)
        sdl2.SDL_HapticRumblePlay(haptic, 1.0, 1500)

    evt = sdl2.SDL_Event()
    running = True
    while running:
        while sdl2.SDL_PollEvent(ctypes.byref(evt)) != 0:
            if evt.type == sdl2.SDL_QUIT:
                running = False
                break
            elif evt.type == sdl2.SDL_JOYAXISMOTION:
                jaxis = evt.jaxis
                axis_state[jaxis.axis] = jaxis.value
                on_joystick_axis(axis_state, jaxis.axis, jaxis.value)
        time.sleep(0.01)
    sdl2.SDL_Quit()
