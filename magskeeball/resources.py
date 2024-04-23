from PIL import Image, ImageFont

# from pkg_resources import resource_filename
import pygame
from enum import Enum

from importlib import resources as impres
from . import fonts
from . import imgs
from . import sounds

FONTS_DIR = impres.files(fonts)
IMGS_DIR = impres.files(imgs)
SOUNDS_DIR = impres.files(sounds)


FONTS = {
    "GameOver": ImageFont.truetype(FONTS_DIR / "GameCube.ttf", 14),
    "MAGFest": ImageFont.truetype(FONTS_DIR / "radio_stars.otf", 15),
    "MAGMini": ImageFont.truetype(FONTS_DIR / "radio_stars.otf", 12),
    "Tiny": ImageFont.load(FONTS_DIR / "4x6.pil"),
    "Small": ImageFont.load(FONTS_DIR / "5x7.pil"),
    "Medium": ImageFont.load(FONTS_DIR / "6x10.pil"),
    "Digital14": ImageFont.load(FONTS_DIR / "digital-14.pil"),
    "Digital16": ImageFont.load(FONTS_DIR / "digital-16.pil"),
}

IMAGES = {"MainLogo": Image.open(IMGS_DIR / "combined-logo.png")}

SOUNDS = {
    'general': {
        "OVER9000": SOUNDS_DIR / "its_over_9000.ogg",
        "PLACE1": SOUNDS_DIR / "place_1.ogg",
        "PLACE2": SOUNDS_DIR / "place_2.ogg",
        "PLACE3": SOUNDS_DIR / "place_3.ogg",
        "PLACE4": SOUNDS_DIR / "place_4.ogg",
        "PLACE5": SOUNDS_DIR / "place_5.ogg",
        "MISS": SOUNDS_DIR / "mario_death.ogg",
        "B100": SOUNDS_DIR / "sonic_ring.ogg",
        "B200": SOUNDS_DIR / "mario_coin.ogg",
        "B300": SOUNDS_DIR / "pac_man_wakka.ogg",
        "B400": SOUNDS_DIR / "mega_man_item_get.ogg",
        "B500": SOUNDS_DIR / "colossus_roar.ogg",
        "B1000L": SOUNDS_DIR / "colossus_roar.ogg",
        "B1000R": SOUNDS_DIR / "colossus_roar.ogg",
        "READY": SOUNDS_DIR / "ready.ogg",
        "GO": SOUNDS_DIR / "go.ogg",
    },
    'attract':{
        "SKEEBALL": SOUNDS_DIR / "skeeball_jingle.ogg",
    },
    'start': {
       "FIRE": SOUNDS_DIR / "great_balls_of_fire.ogg",
    },
    'target': {
        "TARGET_INTRO": SOUNDS_DIR / "break_the_targets.ogg",
        "TARGET_BG": SOUNDS_DIR / "target_theme.ogg",
        "COMPLETE": SOUNDS_DIR / "complete.ogg",
        "TARGET_HIT": SOUNDS_DIR / "target_hit.ogg",
        "TARGET_MISS": SOUNDS_DIR / "target_miss.ogg",
    }
}

def load_sounds():
    # pygame.mixer.pre_init(buffer=2048)
    pygame.mixer.init()
    sounds = {}
    for n1, v1 in SOUNDS.items():
        loaded_sound_group = {}
        print(f'loading sound group {n1}')
        for n2, v2 in v1.items():
            print(f'loading sound {n2}')
            loaded_sound_group[n2] = pygame.mixer.Sound(v2)
        sounds[n1] = loaded_sound_group
    return sounds

FPS = 20


# these map to the physical pins on the arduino except QUIT
class Button(Enum):
    QUIT = 0
    NULL_01 = 1
    B1000L = 2
    B1000R = 3
    B500 = 4
    B400 = 5
    B300 = 6
    B200 = 7
    B100 = 8
    RETURN = 9
    CONFIG = 10
    START = 11
    SELECT = 12
    NULL_13 = 13
    NULL_14 = 14
    NULL_15 = 15
    NULL_16 = 16
    NULL_17 = 17
    NULL_18 = 18
    NULL_19 = 19


B = Button
BUTTON = Button

POINTS = {
    Button.B1000L: 1000,
    Button.B1000R: 1000,
    Button.B500: 500,
    Button.B400: 400,
    Button.B300: 300,
    Button.B200: 200,
    Button.B100: 100,
}

COLORS = {
    "BLACK": (0, 0, 0),
    "RED": (255, 0, 0),
    "YELLOW": (255, 255, 0),
    "GREEN": (0, 255, 0),
    "CYAN": (0, 255, 255),
    "BLUE": (50, 50, 255),
    "MAGENTA": (255, 0, 255),
    "PINK": (255, 150, 150),
    "WHITE": (255, 255, 255),
    "GRAY": (128, 128, 128),
    "PURPLE": (100, 0, 255),
    "ORANGE": (255, 69, 0),
}

BALL_COLORS = [
    "RED",
    "RED",
    "YELLOW",
    "YELLOW",
    "GREEN",
    "GREEN",
    "GREEN",
    "GREEN",
    "GREEN",
    "GREEN",
]
