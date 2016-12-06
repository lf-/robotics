import sdl2


def on_joystick_axis(joy, axis, value):
    print(axis, value)


def init():
    sdl2.SDL_Init(sdl2.SDL_INIT_JOYSTICK | sdl2.SDL_INIT_HAPTIC)


def check_controller():
    if not sdl2.SDL_NumJoysticks() > 0:
        raise RuntimeError('No controllers available')

def main():
    init()
    check_controller()
    run()


def run():
    evt = sdl2.SDL_Event()
    running = True
    while running:
        while sdl2.SDL_PollEvent(ctypes.byref(evt)) != 0:
            if evt.type == sdl2.SDL_QUIT:
                running = False
                break
            elif evt.type == sdl2.SDL_JOYAXISMOTION:
                jaxis = evt.jaxis
                on_joystick_axis(jaxis.which, jaxis.axis, jaxis.value)
    sdl2.SDL_Quit()
