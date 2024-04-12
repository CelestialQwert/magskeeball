from .state import GameMode
from . import resources as res
import random
import time

class Target(GameMode):

    has_high_scores = True
    intro_text = [
        "HIT THE TARGET TO",
        "SCORE 1000 POINTS!"
    ]

    def startup(self):
        self.bg_music = res.TARGET_SFX['TARGET_BG']
        self.bg_music.set_volume(0.25)
        self.bg_music.play()

        self.score = 0
        self.score_buffer = 0
        self.balls = 9
        self.returned_balls = 9
        self.ball_scores = []
        self.advance_score = False

        self.ticks = 0
        self.ticks_last_ball = 0

        self.debug = self.settings['debug']
        self.timeout = self.settings['timeout'] * res.FPS

        self.persist['active_game_mode'] = 'TARGET'
        self.ball_bonuses = []
        self.got_bonus = 'idle'
        self.bonus = [100, 200, 200, 300, 300, 300, 400, 400, 500]
        random.shuffle(self.bonus)
        self.playing_outro = False


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
        if self.got_bonus != 'idle':
            if (self.ticks - self.ticks_last_ball) >= 2*res.FPS:
                self.got_bonus = 'idle'
        if self.balls == 0 and not self.playing_outro:
            self.bg_music.stop()
            res.TARGET_SFX['COMPLETE'].play()
            self.playing_outro = True

    def handle_event(self,event):
        if event.button == res.B.QUIT:
            self.quit = True
        if self.balls == 0:
            return 
        if event.down and event.button in res.POINTS:
            self.add_score(res.POINTS[event.button])
        if event.down and event.button == res.B.RETURN:
            self.returned_balls-=1
            if self.returned_balls < self.balls:
                self.add_score(0)
        if event.button == res.B.CONFIG:
            self.balls = 0
            self.returned_balls = 0

    def add_score(self,score):
        self.ball_scores.append(score)
        if self.ball_scores[-1] == self.bonus[9-self.balls]:
            self.score_buffer += 1000
            self.got_bonus = 'yes'
            self.ball_bonuses.append(True)
            res.TARGET_SFX['TARGET_HIT'].play()
        else:
            self.score_buffer += score
            self.got_bonus = 'no'
            self.ball_bonuses.append(False)
            res.TARGET_SFX['TARGET_MISS'].play()
        self.advance_score = True
        self.balls-=1
        self.ticks_last_ball = self.ticks

    def draw_panel(self,panel):
        panel.clear() 
        shared_color = res.BALL_COLORS[self.balls]
        panel.draw_text((34, 31), self.balls, 'Digital14',shared_color)
        panel.draw_text((17, 4), f"{self.score:04d}", 'Digital16', 'PURPLE')
        panel.draw_text((8, 31), "BALL" , 'Medium', shared_color)
        panel.draw_text((8, 41), "LEFT" , 'Medium', shared_color)
        panel.draw_text((52, 31), "TARGET", 'Medium', 'YELLOW')
        if self.balls > 0:
            panel.draw_text((61,41), self.bonus[9-self.balls], 'Medium', 'YELLOW')
        if self.got_bonus == 'yes':
            panel.draw_text((16,53), "BONUS! 1000", 'Medium', 'WHITE')
        if self.got_bonus == 'no':
            panel.draw_text((27,53), "MISSED!", 'Medium', 'WHITE')
        if self.debug:
            for i,(num,b) in enumerate(zip(self.ball_scores,self.ball_bonuses)):
                color = 'WHITE' if b else 'RED'
                panel.draw_text((80, 1+6*i), f"{num: >4}", 'Tiny', color)
            panel.draw_text((90,57), self.returned_balls, 'Small', 'ORANGE')

    def cleanup(self):
        print("Pausing for 2.5 seconds")
        time.sleep(2.5)
        self.persist['last_score'] = self.score
        return