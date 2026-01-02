from .state import State, GameMode
from . import constants as const
import random


class GameMenu(GameMode):

    def startup(self):
        if self.settings["extra_games"] == "show":
            self.game_modes = self.manager.all_game_modes
        else:
            self.game_modes = self.manager.game_modes
        self.num_std_game_modes = len(self.game_modes)
        self.refresh_game_modes(self.game_modes)
        self.ticks = 0
        self.locked = False
        self.lock_time = 9999999
        self.hidden_game_state = "locked"
        self.select_hold_time = -1
        self.start_secret_presses = 0

        try:
            self.bg_music = random.choice(
                    list(self.res.sounds["menu"].values())
                )
            self.bg_music.set_volume(0.50)
            self.bg_music.play()
        except IndexError:
            print('No BG music found')
            self.bg_music = None

    def refresh_game_modes(self, modes):
        self.game_modes = modes
        self.game_position = self.num_std_game_modes - 1
        self.next_game()

    def unlock_hidden_games(self):
        print("Modes unlocked!")
        self.refresh_game_modes(self.manager.all_game_modes)

    def handle_event(self, event):
        if event.button == const.B.QUIT:
            self.quit = True
        if not self.locked:
            if event.button == const.B.SELECT and event.down:
                self.next_game()
                if self.settings["extra_games"] == "hide":
                    self.select_hold_time = 0

            if event.button == const.B.SELECT and event.up:
                self.select_hold_time = -1
                self.start_secret_presses = 0
                if self.hidden_game_state != "unlocked":
                    self.hidden_game_state = "locked"

            if event.button == const.B.START and event.down:
                if self.hidden_game_state == "held":
                    self.start_secret_presses -= 1
                    print(f"presses is {self.start_secret_presses}")
                    if self.start_secret_presses == 0:
                        self.hidden_game_state = "unlocked"
                        self.unlock_hidden_games()
                else:
                    self.manager.next_state = self.mode_name
                    self.persist["active_game_mode"] = self.mode_name
                    self.locked = True
                    self.lock_time = self.ticks
                    if self.bg_music:
                        self.bg_music.stop()
                    if self.mode_name == "TARGET":
                        self.start_song = self.res.sounds["target"]["TARGET_INTRO"]
                    else:
                        self.start_song = random.choice(
                            list(self.res.sounds["start"].values())
                        )
                    self.start_song.play()
            if event.button == const.B.CONFIG and event.down:
                self.manager.next_state = "ATTRACT"
                self.done = True
        else:
            if event.button in [const.B.START, const.B.SELECT] and event.down:
                self.done = True

    def update(self):
        self.ticks += 1
        if self.ticks > self.lock_time + 3 * const.FPS:
            self.done = True
        if self.hidden_game_state == "locked" and self.select_hold_time >= 0:
            self.select_hold_time += 1
            if self.select_hold_time == 2 * const.FPS:
                print("changing to held")
                self.hidden_game_state = "held"
                self.start_secret_presses = 3

    def draw_panel(self, panel):
        panel.clear()
        title = "{} MODE".format(self.mode_name)
        x = 48 - 3 * len(title)
        panel.draw_text((x, 1), title, "Medium", "PURPLE")
        for i, line in enumerate(self.intro_text):
            panel.draw_text((1, 13 + 8 * i), line, "Small", "YELLOW")
        if not self.locked:
            panel.draw_text((20, 49), "SELECT MODE", "Small", "WHITE")
            if self.ticks % (3 * const.FPS) < 1.5 * const.FPS:
                panel.draw_text((10, 56), "YELLOW = CHANGE", "Small", "WHITE")
            else:
                panel.draw_text((20, 56), "RED = START", "Small", "WHITE")
        if self.hidden_game_state == "held":
            panel.draw_text((1, 58), self.start_secret_presses, "Tiny", "MAGENTA")
        elif self.hidden_game_state == "unlocked":
            panel.draw_text((1, 58), "X", "Tiny", "MAGENTA")

    def next_game(self):
        self.game_position = (self.game_position + 1) % len(self.game_modes)
        self.mode_name = self.game_modes[self.game_position]
        self.mode = self.manager.states[self.mode_name]
        self.intro_text = self.mode.intro_text
        print("Switching to mode {} {}".format(self.game_position, self.mode_name))
