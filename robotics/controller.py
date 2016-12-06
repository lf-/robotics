import sdl2


def init():
    sdl2.SDL_Init(sdl2.SDL_INIT_JOYSTICK | sdl2.SDL_INIT_HAPTIC)


def check_controller():
    if not sdl2.SDL_NumJoysticks() > 0:
        raise RuntimeError('No controllers available')
