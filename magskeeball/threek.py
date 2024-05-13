from .state import GameMode
from . import constants as const
import time


class ThreeK(GameMode):

    has_high_scores = False
    intro_text = [
        "GET EXACTLY 3000",
        "POINTS, BUT DON'T",
        "GO OVER OR END ON",
        "A 100!"
    ]

    def startup(self):
        self.score = 0
        self.score_buffer = 0
        self.balls = 0
        self.returned_balls = 0
        self.ball_scores = []
        self.advance_score = False

        self.ticks = 0
        self.ticks_last_ball = 0

        self.debug = self.settings["debug"]
        self.timeout = self.settings["timeout"] * const.FPS

        self.persist["active_game_mode"] = "THREE-K"

    def handle_event(self, event):
        if event.button == const.B.QUIT:
            self.quit = True
        if self.score >= 2900:
            return
        if event.down and event.button in const.POINTS:
            self.add_score(const.POINTS[event.button])
            self.res.sounds['score'][event.button.name].play()
        if event.down and event.button == const.B.RETURN:
            self.returned_balls += 1
            if self.returned_balls > self.balls:
                self.add_score(0)
                self.res.sounds['score']["MISS"].play()
        if event.button == const.B.CONFIG:
            self.balls = 0
            self.returned_balls = 0

    def update(self):
        if self.advance_score:
            if self.score_buffer > 0:
                self.score += 100
                self.score_buffer -= 100
        if self.score_buffer == 0:
            self.advance_score = False
        self.ticks += 1
        if (self.ticks - self.ticks_last_ball) > self.timeout:
            self.balls = 0
        if self.score >= 2900 and not self.advance_score:
            self.manager.next_state = "GAMEOVER"
            self.done = True

    def draw_panel(self, panel):
        panel.clear()
        if self.done:
            if self.score == 3000:
                score_color = "WHITE"
                panel.draw_text((25, 53), 'SUCCESS!', "Medium", "WHITE")
            elif self.score == 2900:
                score_color = "RED"
                panel.draw_text((6, 54), "CAN'T END ON 100!", "Small", "RED")
            else:
                score_color = "RED"
                panel.draw_text((28, 53), 'BUSTED!', "Medium", "RED")
        else:
            score_color = "PURPLE"
        panel.draw_text((53, 31), f"{self.balls:02}", "Digital14", "GREEN")
        panel.draw_text((17, 4), f"{self.score:04d}", "Digital16", score_color)
        panel.draw_text((20, 32), "BALLS", "Medium", "GREEN")
        panel.draw_text((14, 41), "PLAYED", "Medium", "GREEN")
        
        if self.debug:
            for i, num in enumerate(self.ball_scores):
                panel.draw_text((80, 1 + 6 * i), f"{num: >4}", "Tiny", "RED")
            panel.draw_text((90, 57), self.returned_balls, "Small", "ORANGE")
    

    def cleanup(self):
        print("Pausing for 3 seconds")
        time.sleep(3)
        self.persist["last_score"] = self.score
        return

    def add_score(self, score):
        self.score_buffer += score
        self.ball_scores.append(score)
        self.balls += 1
        self.advance_score = True
        self.ticks_last_ball = self.ticks
