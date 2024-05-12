from .state import GameMode
from . import constants as const
import random
import time


class World(GameMode):

    has_high_scores = True
    is_speed_game = True
    intro_text = [
        "AROUND THE WORLD!",
        "HIT EVERY TARGET",
        "INCLUDING 0 IN",
        "UNDER TWO MINUTES!",
    ]

    def startup(self):
        self.done = False
        self.last_sound = None

        self.balls = 0
        self.returned_balls = 0
        self.ball_scores = []
        self.countdown_time = 3
        # The 8 targets are mapped to buttons 2-9
        self.hit_targets = [1] * 2 + [0] * 8

        self.debug = self.settings["debug"]

        self.time_elapsed = -self.countdown_time * const.FPS
        self.timeout = self.settings["timeout"] * const.FPS
        self.time_last_ball = self.time_elapsed

        self.persist["active_game_mode"] = "WORLD"

    def handle_event(self, event):
        if event.button == const.B.QUIT:
            self.quit = True
        if event.button == const.B.CONFIG:
            self.time_elapsed = 600 * const.FPS - 2
        if self.time_elapsed < 0:
            return
        if event.down and event.button in const.POINTS:
            self.hit_targets[event.button.value] += 1
            self.ball_scores.append(const.POINTS[event.button])
            self.balls += 1
            self.time_last_ball = self.time_elapsed
            self.last_sound = self.res.sounds['score'][event.button.name].play()
        if event.down and event.button == const.B.RETURN:
            self.returned_balls += 1
            if self.returned_balls > self.balls:
                self.hit_targets[9] += 1
                self.balls += 1
                self.res.sounds['score']["MISS"].play()

    def update(self):

        if self.time_elapsed == -self.countdown_time * const.FPS:
            self.res.sounds['misc']["READY"].play()
        elif (
            self.time_elapsed == -const.FPS // 4
        ):  # the sound clip has a delay so this syncs it up
            self.res.sounds['misc']["GO"].play()

        if (self.time_elapsed - self.time_last_ball) > self.timeout:
            self.time_elapsed = 600 * const.FPS - 2

        if self.manager.sensor.buttons[11] > 0:
            if self.manager.sensor.buttons[12] > 0:
                self.time_elapsed = 600 * const.FPS - 2

        if min(self.hit_targets) > 0:
            self.manager.next_state = "HIGHSCORE"
            self.done = True
        else:
            self.time_elapsed += 1

        if self.time_elapsed >= 599 * const.FPS:
            print("that")

            self.manager.next_state = "HIGHSCORE"
            self.done = True

    def draw_panel(self, panel):
        panel.clear()
        if self.time_elapsed < 0:
            display_time = 0
        else:
            display_time = self.time_elapsed
        panel.draw_time((7, 6), display_time, "PURPLE")

        panel.draw_text((78, 31), "B", "Medium", "WHITE")
        panel.draw_text((75, 41), f"{self.balls:02d}", "Medium", "WHITE")

        for button in reversed(range(2, 10)):
            if self.hit_targets[button] > 0:
                score_color = const.COLORS["GREEN"]
            else:
                score_color = const.COLORS["RED"]
            if button == 9:
                text = "0"
            else:
                text = const.BUTTON(button).name[1:]
            x = 7 + 19 * ((9 - button) // 3)
            y = 30 + 8 * ((9 - button) % 3)
            panel.draw_text((x, y), text, "Small", score_color)

        if self.time_elapsed < 0:
            display_time = self.time_elapsed
            secs = (-display_time // const.FPS) % 60 + 1
            panel.draw_text((15, 54), f"READY... {secs}", "Medium", "WHITE")
        elif self.time_elapsed < 2 * const.FPS:
            panel.draw_text((39, 54), "GO!", "Medium", "WHITE")

        if self.debug:
            for i, num in enumerate(self.ball_scores[-9:]):
                num = str(num)
                t = 4 * len(num)
                panel.draw_text((96 - t, 1 + 6 * i), num, "Tiny", "RED")
            panel.draw_text((85, 57), f"{self.returned_balls:02d}", "Small", "ORANGE")

    def cleanup(self):
        if self.last_sound:
            self.last_sound.stop()
        self.res.sounds['misc']["COMPLETE"].play()
        print("Pausing for 2.5 seconds")
        time.sleep(2.5)
        self.persist["last_score"] = self.time_elapsed
        return

    def add_score(self, score):
        self.score_buffer += score
        self.ball_scores.append(score)
        self.balls += 1
        self.time_last_ball = self.time_elapsed
