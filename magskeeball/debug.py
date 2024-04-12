from .state import GameMode
from . import resources as res
import random
import time


class Debug(GameMode):

    intro_text = [
        "DEBUG MODE"
    ]

    def startup(self):
        self.score = 0
        self.score_buffer = 0
        self.advance_score = False

        self.balls = 0
        self.returned_balls = 0
        self.ball_scores = []

        self.debug = self.settings['debug']

        self.ticks = 0

        self.persist['active_game_mode'] = 'DEBUG'

    def handle_event(self,event):
        if event.button == res.B.QUIT:
            self.quit = True
        if event.down and event.button in [res.B.CONFIG,res.B.START,res.B.SELECT]:
            self.done = True
            self.manager.next_state = "GAMEOVER"
        if event.down and event.button in res.POINTS:
            self.add_score(res.POINTS[event.button])
            res.SOUNDS[event.button.name].play()
        if event.down and event.button == res.B.RETURN:
            self.returned_balls+=1
            if self.returned_balls > self.balls:
                self.add_score(0)
                res.SOUNDS['MISS'].play()
        

    def update(self):
        if self.advance_score and self.score == 9100:
            res.SOUNDS['OVER9000'].play()

        if self.advance_score:
            if self.score_buffer > 0:
                self.score += 100
                self.score_buffer -= 100
        if self.score_buffer == 0:
            self.advance_score = False
        self.ticks += 1


    def draw_panel(self,panel):
        panel.clear()

        sc_x = 17 if self.score < 10000 else 4
        panel.draw_text((sc_x, 4), f"{self.score:04d}", 'Digital16', 'PURPLE')
            
        panel.draw_text((47, 31), "BALLS" , 'Medium', 'WHITE')
        panel.draw_text((53, 41), f"{self.balls:03d}", 'Medium', 'WHITE')

        panel.draw_text((7, 31), "TIME", 'Medium', 'WHITE')
        panel.draw_text((7, 41), f"{self.ticks:04d}", 'Medium', 'WHITE')

        for i,num in enumerate(self.ball_scores[-9:]):
            num = str(num)
            t = 4 * len(num)
            panel.draw_text((96 - t, 1 + 6*i), num, 'Tiny', 'RED')
        panel.draw.text((85, 57), f"{self.returned_balls:02}", 'Small', 'ORANGE')

        if self.done:
            panel.draw_text((15, 54), "EXITING...", 'Medium', 'WHITE')



    def cleanup(self):
        print("Pausing for 1 seconds")
        time.sleep(1)
        self.persist['last_score'] = self.score
        return

    def add_score(self,score):
        self.score_buffer += score
        self.ball_scores.append(score)
        self.balls += 1
        self.advance_score = True
