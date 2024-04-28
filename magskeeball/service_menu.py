from .state import State
from . import constants as const
import json
import os
import time

class ServiceMenu(State):

    def startup(self):
        self.cur_loc = 0
        self.manager.next_state = "ATTRACT"
        self.persist["active_game_mode"] = "SERVICEMENU"
        self.settings["erase_high_scores"] = False
        self.page = 0
        self.setting_names = list(self.settings.get_all_keys())

    def handle_event(self, event):
        if self.page == 0:
            if event.button == const.B.START and event.down:
                self.settings.set_next_option(self.setting_names[self.cur_loc])
            if event.button == const.B.SELECT and event.down:
                self.cur_loc = (self.cur_loc + 1) % len(self.setting_names)
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
            alltext = f"{key:9}{self.manager.game_log[key]:4d}"
            panel.draw_text((15, 12 + 8 * i), alltext, "Small", "WHITE")

    def draw_settings(self, panel):
        panel.clear()
        panel.draw_text((8, 1), "SKEE-BALL CONFIG", "Small", "WHITE")
        for i, setting in enumerate(self.setting_names):
            lbl = self.settings.get_label(setting)
            match self.settings[setting]:
                case True:
                    val = "YES"
                case False:
                    val = "NO"
                case _:
                    val = self.settings[setting]
            panel.draw_text((6, 12 + 8 * i), f"{lbl}: {val}", "Small", "WHITE")
        panel.draw_text((0, 12 + 8 * self.cur_loc), ">", "Small", "WHITE")

    def draw_end(self, panel):
        panel.clear()
        panel.draw_text((8, 20), "SETTINGS SAVED!", "Small", "WHITE")
        if self.settings["erase_high_scores"]:
            panel.draw_text((8, 28), "HI SCORES ERASED", "Small", "RED")

    def cleanup(self):
        if self.settings["erase_high_scores"]:
            self.erase_high_scores()
            self.settings["erase_high_scores"] = False

        self.settings.save_settings()
        time.sleep(1.5)

    def erase_high_scores(self):
        self.manager.high_scores = self.manager.states[
            "HIGHSCORE"
        ].init_all_high_scores()
        self.manager.game_log = self.manager.states["HIGHSCORE"].init_game_log()
