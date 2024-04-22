from .state import GameMode
from . import resources as res
import time


class Flash(GameMode):

    has_high_scores = True
    intro_text = [
        "HIT THE TARGET AT",
        "THE RIGHT TIME TO",
        "GET DOUBLE POINTS!",
    ]

    flash_duration_seconds = 0.75

    flash_duration = int(flash_duration_seconds * res.FPS)
    flash_period = flash_duration * 4

    def startup(self):
        self.score = 0
        self.score_buffer = 0
        self.balls = 9
        self.returned_balls = 9
        self.ball_scores = []
        self.advance_score = False

        self.ticks = 0
        self.ticks_last_ball = 0

        self.flash_counter = 0
        self.score_flash_counter = 0

        self.debug = self.settings["debug"]
        self.timeout = self.settings["timeout"] * res.FPS

        self.persist["active_game_mode"] = "FLASH"

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
        if self.score_buffer == 0:
            self.advance_score = False
        self.ticks += 1
        if (self.ticks - self.ticks_last_ball) > self.timeout:
            self.balls = 0
        if self.balls == 0 and not self.advance_score:
            self.manager.next_state = "HIGHSCORE"
            self.done = True
        
        self.flash_counter = (self.ticks % self.flash_period) // self.flash_duration
        self.flash_counter = 3 - self.flash_counter

        if self.score_flash_counter:
            self.score_flash_counter -= 1

    def draw_panel(self, panel):
        panel.clear()
        shared_color = res.BALL_COLORS[self.balls]
        panel.draw_text((42, 41), self.balls, "Digital14", shared_color)
        panel.draw_text((21, 47), "BALL", "Small", shared_color)
        panel.draw_text((56, 47), "LEFT", "Small", shared_color)

        score_x = 17 if self.score < 10000 else 4
        score_color = "WHITE" if (self.score_flash_counter) else "PURPLE"
        # score_color = "WHITE" if (self.score_flash_counter % 2) else "PURPLE"
        panel.draw_text((score_x, 4), f"{self.score:04d}", "Digital16", score_color)

        # panel.draw_text((85, 2), self.flash_counter, "Medium", "RED")

        if self.score_flash_counter:
            panel.draw_text((24, 32), "x2", "Medium", "WHITE")
            panel.draw_text((61, 32), "x2", "Medium", "WHITE")

        p1_fill = p2_fill = p3_fill = p4_fill = res.COLORS["BLACK"]
        p1_outl = p2_outl = p3_outl = p4_outl = res.COLORS["GRAY"]

        if self.flash_counter == 3:
            p1_fill = res.COLORS["RED"]
            p1_outl = res.COLORS["RED"]
        elif self.flash_counter == 2:
            p2_fill = res.COLORS["RED"]
            p2_outl = res.COLORS["RED"]
        elif self.flash_counter == 1:
            p3_fill = res.COLORS["YELLOW"]
            p3_outl = res.COLORS["YELLOW"]
        elif self.flash_counter == 0:
            p4_fill = res.COLORS["WHITE"]
            p4_outl = res.COLORS["WHITE"]

        panel.draw.ellipse((4, 4, 10, 10), fill=p1_fill, outline=p1_outl)
        panel.draw.ellipse((4, 19, 10, 25), fill=p2_fill, outline=p2_outl)
        panel.draw.ellipse((4, 34, 10, 40), fill=p3_fill, outline=p3_outl)
        panel.draw.ellipse((2, 48, 12, 58), fill=p4_fill, outline=p4_outl)

        panel.draw.ellipse((85, 4, 91, 10), fill=p1_fill, outline=p1_outl)
        panel.draw.ellipse((85, 19, 91, 25), fill=p2_fill, outline=p2_outl)
        panel.draw.ellipse((85, 34, 91, 40), fill=p3_fill, outline=p3_outl)
        panel.draw.ellipse((83, 48, 93, 58), fill=p4_fill, outline=p4_outl)

        if self.debug:
            for i, num in enumerate(self.ball_scores):
                panel.draw_text((80, 1 + 6 * i), f"{num: >4}", "Tiny", "RED")
            panel.draw_text((90, 57), self.returned_balls, "Small", "ORANGE")

        

    def cleanup(self):
        print("Pausing for 1 seconds")
        time.sleep(1)
        self.persist["last_score"] = self.score
        return

    def add_score(self, score):
        if self.flash_counter == 0:
            score *= 2
            self.score_flash_counter = int(res.FPS * 1.5)
        self.score_buffer += score
        self.ball_scores.append(score)
        self.balls -= 1
        self.advance_score = True
        self.ticks_last_ball = self.ticks
