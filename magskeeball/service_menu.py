from .state import State
from . import constants as const
import json
import os
import time

class Settings(State):

    def startup(self):
        self.cur_loc = 0
        self.manager.next_state = "ATTRACT"
        self.persist["active_game_mode"] = "SETTINGS"
        self.settings["erase_high_scores"] = False
        self.page = 0

    def handle_event(self, event):
        if self.page == 0:
            if event.button == const.B.START and event.down:
                key = options[self.cur_loc]
                if settings_type[key] == "boolean":
                    self.settings[key] = not (self.settings[key])
                if settings_type[key] == "game":
                    spot = self.game_modes.index(self.settings[key])
                    spot = (spot + 1) % len(self.game_modes)
                    self.settings[key] = self.game_modes[spot]
                if settings_type[key] == "timeout":
                    spot = times.index(self.settings[key])
                    spot = (spot + 1) % len(times)
                    self.settings[key] = times[spot]
            if event.button == const.B.SELECT and event.down:
                self.cur_loc = (self.cur_loc + 1) % len(options)
        if event.button == const.B.CONFIG and event.down:
            self.page += 1

    def update(self):
        if self.page > 1:
            self.done = True

    def draw_panel(self, panel):
        if self.done:
            self.draw_end(panel)
        elif self.page == 0:
            self.draw_settings(panel)
        else:
            self.draw_stats(panel)

    def draw_stats(self, panel):
        panel.clear()
        panel.draw_text((23, 1), "GAME STATS", "Small", "WHITE")
        for i, key in enumerate(self.manager.game_modes):
            alltext = "{:9}{:4d}".format(key, self.manager.game_log[key])
            panel.draw_text((15, 12 + 8 * i), alltext, "Small", "WHITE")

    def draw_settings(self, panel):
        panel.clear()
        panel.draw_text((8, 1), "SKEE-BALL CONFIG", "Small", "WHITE")
        for i, key in enumerate(options):
            if settings_type[key] == "boolean":
                setting_text = "YES" if self.settings[key] else "NO"
            else:
                setting_text = (
                    "NONE" if self.settings[key] == 9999 else str(self.settings[key])
                )
            alltext = "{}: {}".format(settings_desc_text[key], setting_text)
            panel.draw_text((6, 12 + 8 * i), alltext, "Small", "WHITE")
        panel.draw_text((0, 12 + 8 * self.cur_loc), ">", "Small", "WHITE")

    def draw_end(self, panel):
        panel.clear()
        panel.draw_text((8, 20), "SETTINGS SAVED!", "Small", "WHITE")
        if self.settings["erase_high_scores"]:
            panel.draw_text((8, 28), "HI SCORES ERASED", "Small", "RED")

    def cleanup(self):
        if self.settings.pop("erase_high_scores"):
            self.erase_high_scores()
        self.save_settings()
        time.sleep(1.5)

    def erase_high_scores(self):
        self.manager.high_scores = self.manager.states[
            "HIGHSCORE"
        ].init_all_high_scores()
        self.manager.game_log = self.manager.states["HIGHSCORE"].init_game_log()

    def save_settings(self):
        with open("config.json", "w") as config_json_file:
            json.dump(self.settings, config_json_file)

    def load_settings(self):
        self.game_modes = self.manager.selectable_modes
        try:
            settings = {}
            with open("config.json", "r") as config_json_file:
                config_json = json.load(config_json_file)
                for key, value in config_json.items():
                    if key not in options:
                        raise ValueError(
                            "That's not a proper setting! {}: {}".format(key, value)
                        )
                    if settings_type[key] == "boolean" and type(value) != type(bool()):
                        raise ValueError(
                            "That's not a proper value! {}: {}".format(key, value)
                        )
                    if settings_type[key] == "timeout" and value not in times:
                        raise ValueError(
                            "That's not a proper value! {}: {}".format(key, value)
                        )
                    if settings_type[key] == "game" and value not in self.game_modes:
                        raise ValueError(
                            "That's not a proper value! {}: {}".format(key, value)
                        )
                    settings[key] = value
        except Exception as e:
            print(e)
            print("json is busted, using default settings")
            settings = {
                "red_game": "CLASSIC",
                "yellow_game": "TARGET",
                "timeout": 60,
                "save_high_scores": True,
                "debug": False,
            }
            with open("config.json", "w") as config_json_file:
                json.dump(self.settings, config_json_file)
            os.chmod("config.json", 0o777)
        return settings
