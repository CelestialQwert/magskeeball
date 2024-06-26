from .state import State
from . import constants as const
import random


HISCORE_COLORS = ["BLUE", "RED", "YELLOW", "GREEN", "PINK"]


class Attract(State):

    def startup(self):
        self.ticks = 0
        self.red_game = self.settings["red_game"]
        self.yellow_game = self.settings["yellow_game"]
        self.high_scores = self.manager.high_scores
        self.all_game_modes = self.manager.all_game_modes
        self.has_high_scores = self.manager.has_high_scores
        if not self.settings["save_high_scores"]:
            self.display_queue = [self.draw_factory("LOGO")]
        else:
            self.display_queue = self.get_display_queue()
        self.current_display_ticks = 0
        self.current_display_func, self.current_display_time = self.display_queue[0]
        self.current_display = 0
        self.attract_song = None
        self.attract_song_name = None

    def get_display_queue(self):
        if len(self.persist["hs_game_hist"]) == 2:
            game1, game2 = self.persist["hs_game_hist"]
        else:
            game1 = game2 = self.persist["hs_game_hist"][0]
        queue = []
        if not self.has_high_scores[self.persist["active_game_mode"]]:
            queue.append((self.draw_factory("LOGO"), 10))
        queue.append((self.draw_factory(game1), 10))
        queue.append((self.draw_factory("LOGO"), 10))
        queue.append((self.draw_factory(game2), 10))
        if self.has_high_scores[self.persist["active_game_mode"]]:
            queue.append((self.draw_factory("LOGO"), 10))
        return queue

    def draw_factory(self, mode):
        if mode == "LOGO":

            def draw_func(panel):
                panel.paste(self.res.images["MainLogo"], (0, 5))

        else:

            def draw_func(panel):
                self.draw_high_scores(panel, mode)

        return draw_func

    def handle_event(self, event):
        if event.button == const.B.START and event.down:
            self.activate_new_mode(self.red_game)
        elif event.button == const.B.SELECT and event.down:
            self.activate_new_mode(self.yellow_game)

        elif event.button == const.B.CONFIG and event.down:
            self.activate_new_mode("SERVICEMENU")

    def activate_new_mode(self, mode):
        if mode in self.all_game_modes:
            self.manager.next_state = "INTRO"
            self.persist["active_game_mode"] = mode
        else:
            self.manager.next_state = mode
        self.done = True

    def update(self):
        self.ticks += 1
        self.current_display_ticks += 1
        if self.ticks % (90 * const.FPS) == const.FPS * 30:
            if self.settings["attract_music"]:
                # play jingle once every 90 seconds if idle, starting 30 seconds in
                songs = list(self.res.sounds["attract"].items())
                self.attract_song_name, self.attract_song = random.choice(songs)
                self.attract_song.play()
                print(f"playing attract song {self.attract_song_name}")
            else:
                print("Not playing a song right now")
        if self.current_display_ticks >= (self.current_display_time * const.FPS):
            self.current_display_ticks = 0
            self.current_display = (self.current_display + 1) % len(self.display_queue)
            self.current_display_func, self.current_display_time = self.display_queue[
                self.current_display
            ]
            print(
                "Switching to next display {}/{}".format(
                    self.current_display, len(self.display_queue)
                )
            )

    def draw_panel(self, panel):
        panel.clear()

        self.current_display_func(panel)

        if self.ticks % (2 * const.FPS) < (1.5 * const.FPS):
            panel.draw_text((15, 54), "PRESS START", "Medium", "WHITE")

    def draw_high_scores(self, panel, game):
        if self.manager.states[game].score_type == "time":
            title_text = f"{game} TOP TIMES"
        else:
            title_text = f"{game} HI SCORES"
        x = int(48 - len(title_text) * 2.5) + 1
        panel.draw_text((x, 2), title_text, "Small", "WHITE")

        for i, (name, score) in enumerate(self.high_scores[game]):
            if self.manager.states[game].score_type == "time":
                s = (score // const.FPS) % 60
                f = 5 * (score % const.FPS)
                panel.draw_text(
                    (5 + 8 * i, (i + 1) * 9),
                    f"{name} {s:2d}.{f:02d}",
                    "Medium",
                    HISCORE_COLORS[i],
                )
            else:
                if self.high_scores[game][0][1] > 9999:
                    panel.draw_text(
                        (5 + 8 * i, (i + 1) * 9),
                        f"{name} {score:5d}",
                        "Medium",
                        HISCORE_COLORS[i],
                    )
                else:
                    panel.draw_text(
                        (8 + 8 * i, (i + 1) * 9),
                        f"{name} {score:4d}",
                        "Medium",
                        HISCORE_COLORS[i],
                    )

    def cleanup(self):
        try:
            self.attract_song.stop()
        except AttributeError:
            pass
