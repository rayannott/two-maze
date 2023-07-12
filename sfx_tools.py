import pathlib

from pygame import mixer


mixer.init()


DEFAULT_SFX_VOLUME = 0.3


SFX_DIR = pathlib.Path('assets', 'sfx')
SFX = {file.stem: mixer.Sound(file) for file in SFX_DIR.iterdir()}


def set_sfx_volume(vol):
    global SFX
    for s_effect in SFX.values():
        s_effect.set_volume(vol)

set_sfx_volume(DEFAULT_SFX_VOLUME)

def play_sfx(name: str):
    SFX[name].play()

import random
def play_sfx_warning():
    if random.random() < 0.96:
        play_sfx('warning')
    else:
        play_sfx('fart')
