from . import resources as res
from .state import GameMode
import random
import colorsys
import time

COMBO_COLORS = ["WHITE", "BLUE", "GREEN", "ORANGE", "MAGENTA"]


class Combo(GameMode):

    has_high_scores = True
    # fmt: off
    intro_text = [
        "HIT THE SAME TARGET", 
        "TO BUILD A COMBO", 
        "AND GET BONUS", 
        "POINTS!",
    ]

    def startup(self):

        self.score = 0
        self.score_buffer = 0
        self.balls = 9
        self.returned_balls = 9
        self.advance_score = False

        self.ticks = 0
        self.ticks_last_ball = 0

        self.debug = self.settings["debug"]
        self.timeout = self.settings["timeout"] * res.FPS

        self.persist["active_game_mode"] = "COMBO"
        self.combo = 0
        self.ball_scores = ["0"]
        self.just_scored = False
    
    def handle_event(self, event):
        if event.button == res.B.QUIT:
            self.quit = True
        if self.balls == 0:
            return
        if event.down and event.button in res.POINTS:
            self.add_score(res.POINTS[event.button])
            res.SOUNDS[event.button.name].play()
        if event.down and event.button == res.B.RETURN:
            self.returned_balls -= 1
            if self.returned_balls < self.balls:
                self.add_score(0)
                res.SOUNDS["MISS"].play()
        if event.button == res.B.CONFIG:
            self.balls = 0
            self.returned_balls = 0

    def update(self):
        if self.advance_score:
            if self.score_buffer > 0:
                self.score += 100
                self.score_buffer -= 100
            if self.score == 9100:
                res.SOUNDS["OVER9000"].play()
        if self.score_buffer == 0:
            self.advance_score = False
        self.ticks += 1
        if (self.ticks - self.ticks_last_ball) > self.timeout:
            self.balls = 0
        if self.balls == 0 and not self.advance_score:
            self.manager.next_state = "HIGHSCORE"
            self.done = True
        if self.just_scored and (self.ticks - self.ticks_last_ball) >= 2 * res.FPS:
            self.just_scored = False

    def add_score(self, score):
        self.ball_scores.append(score)
        self.balls -= 1
        self.just_scored = True
        if self.ball_scores[-1] == self.ball_scores[-2]:
            self.combo += 1
        else:
            self.combo = 1
        if self.ball_scores[-1] == 0:
            self.combo = 0
            self.just_scored = False
        self.score_buffer += self.combo * self.ball_scores[-1]
        self.advance_score = True
        self.ticks_last_ball = self.ticks

    def draw_panel(self, panel):
        panel.clear()
        score_x = 17 if self.score < 10000 else 4
        shared_color = res.BALL_COLORS[self.balls]
        panel.draw_text((score_x, 4), f"{self.score:04d}", "Digital16", "PURPLE")
        panel.draw_text((31, 31), self.balls, "Digital14", shared_color)
        panel.draw_text((5, 31), "BALL", "Medium", shared_color)
        panel.draw_text((5, 41), "LEFT", "Medium", shared_color)

        if self.combo >= 5:
            hue = (self.ticks * 18) % 360
            colour = tuple(int(255 * i) for i in colorsys.hsv_to_rgb(hue / 360, 1, 1))
        else:
            colour = COMBO_COLORS[self.combo]
        ballscore_x = 63 - 3 * len(str(self.ball_scores[-1]))
        panel.draw_text((80, 31), self.combo, "Digital14", colour)
        panel.draw_text((ballscore_x, 41), self.ball_scores[-1], "Medium", colour)
        panel.draw_text((48, 31), "CHAIN", "Medium", colour)

        if self.just_scored:
            text = f"{self.ball_scores[-1]} x {self.combo}"
            panel.draw_text((27, 53), text, "Medium", "WHITE")

        if self.debug:
            for i, num in enumerate(self.ball_scores[1:]):
                panel.draw_text((80, 1 + 6 * i), f"{num: >4}", "Tiny", "RED")
            panel.draw_text((90, 57), self.returned_balls, "Small", "ORANGE")

    def cleanup(self):
        print("Pausing for 1 seconds")
        time.sleep(1)
        self.persist["last_score"] = self.score
        return