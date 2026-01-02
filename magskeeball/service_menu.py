from .state import State
from . import constants as const
import socket
import time

LINES_PER_PAGE = 6

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]


class ServiceMenu(State):

    def startup(self):
        self.cur_loc = 0
        self.manager.next_state = "ATTRACT"
        self.persist["active_game_mode"] = "SERVICEMENU"
        self.settings["erase_high_scores"] = False
        self.sub_state = 0
        self.setting_names = list(self.settings.get_all_keys())
        ip = get_ip_address()
        if ip == "127.0.0.1":
            self.my_ip = "NO NETWORK"
        else:
            self.my_ip = ip

    def handle_event(self, event):
        if self.sub_state == 0:
            if event.button == const.B.START and event.down:
                self.settings.set_next_option(self.setting_names[self.cur_loc])
            if event.button == const.B.SELECT and event.down:
                self.cur_loc = (self.cur_loc + 1) % len(self.setting_names)
        if event.button == const.B.CONFIG and event.down:
            self.sub_state += 1

    def update(self):
        if self.sub_state > 1:
            self.done = True

    def draw_panel(self, panel):
        if self.done:
            self.draw_end(panel)
        elif self.sub_state == 0:
            self.draw_settings(panel)
        else:
            self.draw_stats(panel)

    def draw_settings(self, panel):
        panel.clear()
        panel.draw_text((8, 1), "SKEE-BALL CONFIG", "Small", "WHITE")
        page = self.cur_loc // 6
        max_pages = (LINES_PER_PAGE // 6) + 1
        for i, setting in enumerate(self.setting_names[page * 6 : (page + 1) * 6]):
            lbl = self.settings.get_label(setting)
            match self.settings[setting]:
                case True:
                    val = "YES"
                case False:
                    val = "NO"
                case 9999:
                    val = "NONE"
                case _:
                    val = str(self.settings[setting]).upper().replace("_", " ")
            panel.draw_text((6, 12 + 7 * i), f"{lbl}: {val}", "Tiny", "WHITE")
        panel.draw_text((1, 12 + 7 * (self.cur_loc % 6)), ">", "Tiny", "WHITE")
        panel.draw_text((2, 56), f"{page+1}/{max_pages}", "Tiny", "WHITE")
        align = 96 - len(self.my_ip) * 4
        panel.draw_text((align, 58), self.my_ip, "Tiny", "BLUE")

    def draw_stats(self, panel):
        panel.clear()
        panel.draw_text((23, 1), "GAME STATS", "Small", "WHITE")
        for i, key in enumerate(self.manager.all_game_modes):
            alltext = f"{key:8}{self.manager.game_log[key]:4d}"
            colour = "GREEN" if i % 2 else "BLUE"
            panel.draw_text((18, 10 + 7 * i), alltext, "Small", colour)

    def draw_end(self, panel):
        panel.clear()
        panel.draw_text((2, 2), "SETTINGS SAVED!", "Medium", "WHITE")
        if self.settings["erase_high_scores"]:
            panel.draw_text((2, 10), "HI SCORES ERASED", "Medium", "RED")

    def cleanup(self):
        if self.settings["erase_high_scores"]:
            self.erase_high_scores()
            self.settings["erase_high_scores"] = False

        self.settings.save_settings()
        self.res.set_sounds(self.settings["general_sfx"], self.settings["colossus"])
        time.sleep(1.5)

    def erase_high_scores(self):
        self.manager.high_scores = self.manager.states[
            "HIGHSCORE"
        ].init_all_high_scores()
        self.manager.game_log = self.manager.states["HIGHSCORE"].init_game_log()
