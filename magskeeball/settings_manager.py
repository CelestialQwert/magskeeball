from . import constants as const
import json

SETTINGS_INFO = {
    "red_game": {
        "label": "RED GAME",
        "options": ["CLASSIC", "TARGET"],
        "default_value": "CLASSIC",
    },
    "yellow_game": {
        "label": "YLW GAME",
        "options": ["CLASSIC", "TARGET"],
        "default_value": "TARGET",
    },
    "extra_games": {
        "label": "EXTRA GAMES",
        "options": ["show", "hide", "disable"],
        "default_value": "hide",
    },
    "flash_speed": {
        "label": "FLASH SPEED",
        "options": [0.5, 0.75, 1, 1.25, 1.5, 2, 2.5, 3, 4, 5],
        "default_value": 2,
    },
    "sfx": {
        "label": "SFX",
        "options": ["model_h", "model_s", "stuff"],
        "default_value": "model_s",
    },
    "colossus": {
        "label": "COLOSSUS",
        "options": [True, False],
        "default_value": True,
    },
    "timeout": {
        "label": "TIMEOUT",
        "options": [30, 45, 60, 75, 90, 9999],
        "default_value": 60,
    },
    "save_high_scores": {
        "label": "HI SCORES",
        "options": [True, False],
        "default_value": True,
    },
    "debug": {
        "label": "SHOW DEBUG",
        "options": [True, False],
        "default_value": False,
    },
    "erase_high_scores": {
        "label": "ERASE SCORES",
        "options": [True, False],
        "default_value": False,
    },
    "dummy1": {
        "label": "DUMMY1",
        "options": [True, False],
        "default_value": False,
    },
}


class SettingsManager:

    def __init__(self, game_modes=None):
        self.settings_info = SETTINGS_INFO.copy()
        if game_modes:
            self.settings_info["red_game"]["options"] = game_modes
            self.settings_info["red_game"]["default_value"] = game_modes[0]
            self.settings_info["yellow_game"]["options"] = game_modes
            self.settings_info["yellow_game"]["default_value"] = game_modes[0]
        self.init_settings()

    def init_settings(self):
        for thing in self.settings_info.values():
            thing["current_value"] = thing["default_value"]

    def __getitem__(self, key):
        if key not in self.settings_info:
            raise ValueError(f"Key {key} is not in settings!")
        return self.settings_info[key]["current_value"]

    def __setitem__(self, key, value):
        if key not in self.settings_info:
            raise ValueError(f"Key {key} is not in settings!")
        if value not in self.settings_info[key]["options"]:
            raise ValueError(f"Value {value} is invalid for {key}!")
        self.settings_info[key]["current_value"] = value
        return key

    def get_label(self, key):
        if key not in self.settings_info:
            raise ValueError(f"Key {key} is not in settings!")
        return self.settings_info[key]["label"]

    def get_all_keys(self):
        return self.settings_info.keys()

    def set_next_option(self, key):
        if key not in self.settings_info:
            raise ValueError(f"Key {key} is not in settings!")

        spot = self.settings_info[key]["options"].index(
            self.settings_info[key]["current_value"]
        )
        spot = (spot + 1) % len(self.settings_info[key]["options"])
        new_val = self.settings_info[key]["options"][spot]
        spot = self.settings_info[key]["current_value"] = new_val

        return new_val

    def load_settings(self, settings_file="config.json"):
        self.init_settings()
        try:
            with open(settings_file) as f:
                config_json = json.load(f)
        except FileNotFoundError:
            print("Can't open config file, using default values")
            return
        for file_key, file_val in config_json.items():
            try:
                self.__setitem__(file_key, file_val)
            except ValueError:
                print(f"Bad value for {file_key} in config, using default")
        self.save_settings(settings_file)

    def save_settings(self, settings_file="config.json"):
        settings_to_save = {x: self.__getitem__(x) for x in self.settings_info}
        with open(settings_file, "w") as f:
            json.dump(settings_to_save, f)
