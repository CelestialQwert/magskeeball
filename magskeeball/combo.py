from .basic_skeeball import BasicSkeeball
from . import resources as res
import random
import colorsys

COMBO_COLORS = ['WHITE', 'BLUE', 'GREEN', 'ORANGE', 'MAGENTA']

class Combo(BasicSkeeball):

    intro_text = [
        "HIT THE SAME TARGET",
        "TO BUILD A COMBO",
        "AND GET MASSIVE",
        "POINTS!"
    ]

    def startup(self):
        super(Combo,self).startup()
        print("Special Mode: Combo")
        self.persist['active_game_mode'] = 'COMBO'
        self.combo = 0
        self.ball_scores = ['0']
        self.just_scored = False


    def update(self):
        super(Combo,self).update()
        if self.advance_score and self.score == 9100:
            res.SOUNDS['OVER9000'].play()
        if self.just_scored and (self.ticks - self.ticks_last_ball) >= 2*res.FPS:
                self.just_scored = False
            

    def add_score(self,score):
        self.ball_scores.append(score)
        self.balls-=1
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
        #if self.balls in [3,6]:
        #    self.sensor.release_balls()
        self.ticks_last_ball = self.ticks

    def draw_panel(self,panel):  
        panel.clear()
        score_x = 17 if self.score < 10000 else 4
        shared_color = res.BALL_COLORS[self.balls]
        panel.draw_text((score_x, 4), f"{self.score:04d}", 'Digital16', 'PURPLE')
        panel.draw_text((31, 31), self.balls, 'Digital14', shared_color)
        panel.draw_text((5,31), "BALL", 'Medium', shared_color)
        panel.draw_text((5,41), "LEFT", 'Medium', shared_color)

        if self.combo >= 5:
            hue = (self.ticks*18)%360
            colour = tuple(int(255*i) for i in colorsys.hsv_to_rgb(hue/360,1,1))
        else:
            colour = COMBO_COLORS[self.combo]
        ballscore_x = 63-3*len(str(self.ball_scores[-1]))
        panel.draw_text((80,31), self.combo, 'Digital14', colour)
        panel.draw_text((ballscore_x,41), self.ball_scores[-1] ,'Medium', colour)
        panel.draw_text((48,31), "CHAIN", 'Medium', colour)

        if self.just_scored:
            text = f'{self.ball_scores[-1]} x {self.combo}'
            panel.draw_text((27,53), text, 'Medium', 'WHITE')

        if self.debug:
            for i,num in enumerate(self.ball_scores[1:]):
                panel.draw_text((80, 1+6*i), f"{num: >4}", 'Tiny', 'RED')
            panel.draw_text((90,57), self.returned_balls, 'Small', 'ORANGE')


