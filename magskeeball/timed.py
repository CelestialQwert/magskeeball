from .state import GameMode
from . import resources as res
import random
import time


class Timed(GameMode):

    has_high_scores = True
    intro_text = [
        "SCORE AS MANY",
        "POINTS AS POSSIBLE",
        "IN 30 SECONDS!",
    ]

    def startup(self):
        self.score = 0
        self.score_buffer = 0
        self.advance_score = False

        self.balls = 0
        self.returned_balls = 0
        self.ball_scores = []
        self.countdown_time = 3

        self.debug = self.settings["debug"]

        self.time_remain = (30 + self.countdown_time) * res.FPS

        self.persist["active_game_mode"] = "TIMED"

    def handle_event(self, event):
        if event.button == res.B.QUIT:
            self.quit = True
        if event.button == res.B.CONFIG:
            self.time_remain = 0
        if self.time_remain > 30 * res.FPS:
            return
        if event.down and event.button in res.POINTS:
            self.add_score(res.POINTS[event.button])
            res.SOUNDS[event.button.name].play()
        if event.down and event.button == res.B.RETURN:
            self.returned_balls += 1
            if self.returned_balls > self.balls:
                self.add_score(0)
                res.SOUNDS["MISS"].play()

    def update(self):
        if self.time_remain == (30 + self.countdown_time) * res.FPS:
            res.SOUNDS["READY"].play()
        elif self.time_remain == int(
            30.25 * res.FPS
        ):  # the sound clip has a delay so this syncs it up
            res.SOUNDS["GO"].play()

        if self.advance_score and self.score == 9100:
            res.SOUNDS["OVER9000"].play()

        if self.advance_score:
            if self.score_buffer > 0:
                self.score += 100
                self.score_buffer -= 100
        if self.score_buffer == 0:
            self.advance_score = False
        self.time_remain -= 1
        if self.time_remain <= 0 and not self.advance_score:
            self.manager.next_state = "HIGHSCORE"
            self.done = True

    def draw_panel(self, panel):
        panel.clear()
        if self.time_remain > 30 * res.FPS:
            display_time = 30 * res.FPS
        elif self.time_remain < 0:
            display_time = 0
        else:
            display_time = self.time_remain

        seconds = (display_time // res.FPS) % 60
        fraction = round(100.0 / res.FPS * (display_time % res.FPS))

        score_x = 17 if self.score < 10000 else 4
        panel.draw_text((score_x, 4), f"{self.score:04d}", "Digital16", "PURPLE")
        panel.draw_text((57, 31), "BALLS", "Medium", "WHITE")
        panel.draw_text((66, 41), f"{self.balls:02d}", "Medium", "WHITE")

        if self.time_remain < 3 * res.FPS:
            time_color = "RED"
        elif self.time_remain < 10 * res.FPS:
            time_color = "YELLOW"
        else:
            time_color = "GREEN"

        panel.draw_text((12, 31), "TIME", "Medium", time_color)
        panel.draw_text((9, 41), f"{seconds:02d}.{fraction:02d}", "Medium", time_color)

        if self.time_remain > 30 * res.FPS:
            display_time = self.time_remain - 30 * res.FPS
            seconds = (display_time // res.FPS) % 60 + 1
            panel.draw_text((15, 54), f"READY... {seconds}", "Medium", "WHITE")
        elif self.time_remain > 28 * res.FPS:
            panel.draw_text((39, 54), "GO!", "Medium", "WHITE")

        if self.debug:
            for i, num in enumerate(self.ball_scores[-9:]):
                num = str(num)
                t = 4 * len(num)
                panel.draw_text((96 - t, 1 + 6 * i), num, "Tiny", "RED")
            panel.draw_text((85, 57), f"{self.returned_balls:02d}", "Small", "ORANGE")

    def cleanup(self):
        print("Pausing for 1 seconds")
        time.sleep(1)
        self.persist["last_score"] = self.score
        return

    def add_score(self, score):
        self.score_buffer += score
        self.ball_scores.append(score)
        self.balls += 1
        self.advance_score = True
