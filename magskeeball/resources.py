import pygame
from importlib import resources as impres
from PIL import Image, ImageFont

from . import fonts
from . import imgs
from . import sounds

FONTS_DIR = impres.files(fonts)
IMGS_DIR = impres.files(imgs)
SOUNDS_DIR = impres.files(sounds)

class ResourceManager:

    __shared_state = {
        'sounds': {},
        'fonts': {},
        'images': {},
    }

    def __init__(self):
        self.__dict__ = self.__shared_state

    def load_all(self):
        self.load_sounds()
        self.load_images()

    def load_sounds(self):
        pygame.mixer.init()
        for n1, v1 in SOUNDS.items():
            loaded_sound_group = {}
            print(f'loading sound group {n1}')
            for n2, v2 in v1.items():
                print(f'loading sound {n2}')
                loaded_sound_group[n2] = pygame.mixer.Sound(v2)
            self.sounds[n1] = loaded_sound_group
    
    def load_images(self):
        for name, filepath in IMAGES.items():
            print(f'loading image {name}')
            self.images[name] = Image.open(filepath)

    def load_fonts(self):
        for name, fileinfo in FONTS.items():
            if isinstance(fileinfo, tuple):
                filepath, font_size = fileinfo
            else:
                filepath = fileinfo    
            print(f'loading font {name}')
            if filepath.suffix.lower() == '.pil':
                self.fonts[name] = ImageFont.load(filepath)
            else:
                self.fonts[name] = ImageFont.truetype(filepath, font_size)
    
    def load_barebones(self):
        # load the one font needed for the load and error screens
        self.fonts['Medium'] = ImageFont.load(FONTS_DIR / "6x10.pil")

FONTS = {
    "GameOver": (FONTS_DIR / "GameCube.ttf", 14),
    "MAGFest": (FONTS_DIR / "radio_stars.otf", 15),
    "MAGMini": (FONTS_DIR / "radio_stars.otf", 12),
    "Tiny": FONTS_DIR / "4x6.pil",
    "Small": FONTS_DIR / "5x7.pil",
    "Medium": FONTS_DIR / "6x10.pil",
    "Digital14": FONTS_DIR / "digital-14.pil",
    "Digital16": FONTS_DIR / "digital-16.pil",
}

IMAGES = {"MainLogo": IMGS_DIR / "combined-logo.png"}

SOUNDS = {
    'misc': {
        "OVER9000": SOUNDS_DIR / "its_over_9000.ogg",
        "PLACE1": SOUNDS_DIR / "place_1.ogg",
        "PLACE2": SOUNDS_DIR / "place_2.ogg",
        "PLACE3": SOUNDS_DIR / "place_3.ogg",
        "PLACE4": SOUNDS_DIR / "place_4.ogg",
        "PLACE5": SOUNDS_DIR / "place_5.ogg",
        "READY": SOUNDS_DIR / "ready.ogg",
        "GO": SOUNDS_DIR / "go.ogg",
    },
    'score': {
        "MISS": SOUNDS_DIR / "mario_death.ogg",
        "B100": SOUNDS_DIR / "sonic_ring.ogg",
        "B200": SOUNDS_DIR / "mario_coin.ogg",
        "B300": SOUNDS_DIR / "pac_man_wakka.ogg",
        "B400": SOUNDS_DIR / "mega_man_item_get.ogg",
        "B500": SOUNDS_DIR / "colossus_roar.ogg",
        "B1000L": SOUNDS_DIR / "colossus_roar.ogg",
        "B1000R": SOUNDS_DIR / "colossus_roar.ogg",
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
