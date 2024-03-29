from .state import GameMode
from . import resources as res
import time

class BasicSkeeball(GameMode):

    has_high_scores = True
    intro_text = [
        "GET THE HIGH SCORE",
        "WITH 9 BALLS!",
        "NO SPECIAL BONUSES!"
    ]

    def startup(self):
        print("Starting Skeeball!")

        self.score = 0
        self.score_buffer = 0
        self.balls = 9
        self.returned_balls = 9
        self.ball_scores = []
        self.advance_score = False

        self.ticks = 0
        self.ticks_last_ball = 0

        self.debug = self.settings['debug']
        self.timeout = self.settings['timeout']*res.FPS

        self.persist['active_game_mode'] = 'BASIC'

        #self.sensor.release_balls()

    def handle_event(self,event):
        if event.button == res.B.QUIT:
            self.quit = True
        if self.balls == 0:
            return 
        if event.down and event.button in res.POINTS:
            self.add_score(res.POINTS[event.button])
            res.SOUNDS[event.button.name].play()
        if event.down and event.button == res.B.RETURN:
            self.returned_balls-=1
            if self.returned_balls < self.balls:
                self.add_score(0)
                res.SOUNDS['MISS'].play()
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
        #print(self.ticks)
        if (self.ticks - self.ticks_last_ball) > self.timeout:
            self.balls = 0
        if self.balls == 0 and not self.advance_score:
            self.manager.next_state = "HIGHSCORE"
            self.done = True

    def draw_panel(self,panel):
        panel.clear()
        shared_color = res.BALL_COLORS[self.balls]
        panel.draw_text((42, 39), self.balls , 'Digital14', shared_color)
        panel.draw_text((17, 4), f"{self.score:04d}", 'Digital16', 'PURPLE')
        panel.draw_text((16, 44), "BALL", 'Medium', shared_color)
        panel.draw_text((57, 44), "LEFT", 'Medium', shared_color)
        if self.debug:
            for i,num in enumerate(self.ball_scores):
                panel.draw_text((80, 1+6*i), f"{num: >4}", 'Tiny', 'RED')
            panel.draw_text((90,57), self.returned_balls, 'Small', 'ORANGE')

    def cleanup(self):
        print("Pausing for 1 seconds")
        time.sleep(1)
        self.persist['last_score'] = self.score
        return

    def add_score(self,score):
        self.score_buffer += score
        self.ball_scores.append(score)
        self.balls-=1
        self.advance_score = True
        #if self.balls in [3,6]:
        #    self.sensor.release_balls()
        self.ticks_last_ball = self.ticks
