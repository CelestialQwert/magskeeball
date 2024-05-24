import pygame
from importlib import resources as impres
from PIL import Image, ImageFont
from pathlib import Path

print(__file__)

import sys
minor_ver = sys.version_info.minor

if minor_ver >= 12:
    from . import fonts
    from . import imgs
    from . import sounds
    FONTS_DIR = impres.files(fonts)
    IMGS_DIR = impres.files(imgs)
    SOUNDS_DIR = impres.files(sounds)
else:
    this_file = Path(__file__)
    FONTS_DIR = this_file.parent / 'fonts'
    IMGS_DIR = this_file.parent / 'imgs'
    SOUNDS_DIR = this_file.parent / 'sounds'


def dict_update(d, u):
    for k, v in u.items():
        if isinstance(v, dict):
            d[k] = dict_update(d.get(k, {}), v)
        else:
            d[k] = v
    return d


class ResourceManager:

    __shared_state = {
        "sound_bank": {},
        "sounds": {},
        "fonts": {},
        "images": {},
    }

    def __init__(self):
        self.__dict__ = self.__shared_state

    def load_all(self):
        self.load_sounds()
        self.load_images()

    def load_sounds(self):
        pygame.mixer.init()
        if minor_ver >= 12:
            with impres.as_file(SOUNDS_DIR) as sounds_dir:
                self.load_sounds_in_dir(sounds_dir, sounds_dir)
        else:
            self.load_sounds_in_dir(SOUNDS_DIR, SOUNDS_DIR)

    def load_sounds_in_dir(self, this_dir, root_dir):
        for sound_file in this_dir.iterdir():
            if sound_file.is_dir():
                self.load_sounds_in_dir(sound_file, root_dir)
            elif sound_file.suffix.lower() in [".wav", ".ogg"]:
                rel_name = str(sound_file.relative_to(root_dir)).replace("\\", "/")
                print(f"Loading {rel_name}")
                self.sound_bank[rel_name] = pygame.mixer.Sound(sound_file)

    def set_sounds(self, sfx_pack="model_s", use_colossus=True):
        self.sounds = dict_update({}, SOUND_BANK["universal"])
        self.sounds = dict_update(self.sounds, SOUND_BANK[sfx_pack])
        if use_colossus:
            self.sounds = dict_update(self.sounds, SOUND_BANK["colossus"])
        self.map_sounds(self.sounds)

    def map_sounds(self, dict_sound):
        for k, v in dict_sound.items():
            if isinstance(v, dict):
                self.map_sounds(v)
            else:
                dict_sound[k] = self.sound_bank[v]

    def load_images(self):
        for name, filepath in IMAGES.items():
            print(f"loading image {name}")
            self.images[name] = Image.open(filepath)

    def load_fonts(self):
        for name, fileinfo in FONTS.items():
            if isinstance(fileinfo, tuple):
                filepath, font_size = fileinfo
            else:
                filepath = fileinfo
            print(f"loading font {name}")
            if filepath.suffix.lower() == ".pil":
                self.fonts[name] = ImageFont.load(filepath)
            else:
                self.fonts[name] = ImageFont.truetype(filepath, font_size)

    def load_barebones(self):
        # load the one font needed for the load and error screens
        self.fonts["Medium"] = ImageFont.load(FONTS_DIR / "6x10.pil")


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

SOUND_BANK = {
    "universal": {
        "misc": {
            "OVER9000": "its_over_9000.ogg",
            "PLACE1": "place_1.ogg",
            "PLACE2": "place_2.ogg",
            "PLACE3": "place_3.ogg",
            "PLACE4": "place_4.ogg",
            "PLACE5": "place_5.ogg",
            "READY": "ready.ogg",
            "GO": "go.ogg",
            "COMPLETE": "complete.ogg",
        },
        "target": {
            "TARGET_INTRO": "break_the_targets.ogg",
            "TARGET_BGM": "target_theme.ogg",
            "TARGET_HIT": "target_hit.ogg",
            "TARGET_MISS": "target_miss.ogg",
        },
    },
    "stuff": {
        "score": {
            "MISS": "stuff/mario_death.ogg",
            "B100": "stuff/sonic_ring.ogg",
            "B200": "stuff/mario_coin.ogg",
            "B300": "stuff/pac_man_wakka.ogg",
            "B400": "stuff/mega_man_item_get.ogg",
            "B500": "colossus_roar.ogg",
            "B1000L": "colossus_roar.ogg",
            "B1000R": "colossus_roar.ogg",
        },
        "attract": {
            "SKEEBALL": "skeeball_jingle.ogg",
            "BLACK_KNIGHT_2000": "stuff/black_knight_2000.ogg",
        },
        "start": {
            "FIRE": "stuff/great_balls_of_fire.ogg",
            "WRECKING_BALL": "stuff/wrecking_ball.ogg",
        },
    },
    "model_s": {
        "score": {
            "MISS": "model_s/no_score_gutter_ball.wav",
            "B100": "model_s/10_points.wav",
            "B200": "model_s/20_points.wav",
            "B300": "model_s/30_points.wav",
            "B400": "model_s/40_points.wav",
            "B500": "model_s/50_points.wav",
            "B1000L": "model_s/100_points.wav",
            "B1000R": "model_s/100_points.wav",
        },
        "attract": {
            "SKEEBALL": "skeeball_jingle.ogg",
        },
        "start": {
            "COINUP": "model_s/machine_coin_up.wav",
        },
    },
    "model_h": {
        "score": {
            "MISS": "model_s/no_score_gutter_ball.wav",
            "B100": "model_s/10_points.wav",
            "B200": "model_s/20_points.wav",
            "B300": "model_s/30_points.wav",
            "B400": "model_s/40_points.wav",
            "B500": "model_s/50_points.wav",
            "B1000L": "model_s/100_points.wav",
            "B1000R": "model_s/100_points.wav",
        },
        "attract": {
            "SKEEBALL": "skeeball_jingle.ogg",
        },
        "start": {
            "COINUP": "model_s/machine_coin_up.wav",
        },
    },
    "colossus": {
        "score": {
            "B500": "colossus_roar.ogg",
            "B1000L": "colossus_roar.ogg",
            "B1000R": "colossus_roar.ogg",
        },
    },
}


if __name__ == "__main__":
    pygame.mixer.init()
    res = ResourceManager()
    res.load_sounds()
    res.set_sounds()
