from .state import GameMode
from . import resources as res
import time

COLOR_MATRIX = ['BLUE','RED']
COLOR_PLAYER = ['GREEN', 'MAGENTA']
NAME_PLAYER = ['P1','P2']

class Player():
    def __init__(self,num=0):
        self.num = num
        self.hits = [0]*5
        self.target_scores = [0]*5
        self.ball_scores = []
        self.score = 0
        self.score_buffer = 0
        self.target_buffers = [0]*5

class Cricket(GameMode):

    has_high_scores = True
    intro_text = [
        "THE POPULAR DART",
        "GAME, BUT WITH",
        "SKEE-BALLS!"
    ]

    def startup(self):
        print("Starting cricket")

        self.p1 = Player(1)
        self.p2 = Player(2)

        self.balls = 0
        self.returned_balls = 0

        self.ticks = 0
        self.ticks_last_ball = 0

        self.debug = self.settings['debug']
        self.timeout = self.settings['timeout']*res.FPS

        self.persist['active_game_mode'] = 'CRICKET'

        #self.sensor.release_balls()

    def handle_event(self,event):
        if event.button == res.B.QUIT:
            self.quit = True
        if event.button == res.B.CONFIG:
            self.done = True

        if event.down and event.button in res.POINTS:
            res.SOUNDS[event.button.name].play()
        if event.down and event.button == res.B.RETURN:
            self.returned_balls+=1
            if self.returned_balls < self.balls:
                self.balls = self.returned_balls


    def update(self):
        
        self.ticks += 1
        if (self.ticks - self.ticks_last_ball) > self.timeout:
            self.done = True


    def draw_panel(self,panel):
        # a = active_player - 1
        a = 1
        panel.clear()

        panel.draw_text((3,2), "P1", font='Medium', color='GREEN')
        p1_score = '{: >4}'.format(str(self.p1.score//10))
        panel.draw_text((18,2), p1_score, font='Medium', color='GREEN')

        panel.draw_text((55,2), "P2", font='Medium', color='MAGENTA')
        p2_score = '{: >4}'.format(str(self.p2.score//10))
        panel.draw_text((70,2), p1_score, font='Medium', color='MAGENTA')

        for x,p in enumerate([self.p1,self.p2]):
            for y in range(5):
                posx = 32+26*x
                posy = 13+8*y
                if p.hits[y-5] > 0:
                    pos = (posx,posy,posx+6,posy+6)
                    panel.draw.ellipse(pos, outline=res.COLORS['WHITE'])
                if p.hits[y-5] > 1:
                    pos = (posx+5,posy+1,posx+1,posy+5)
                    panel.draw.line(pos, fill=res.COLORS['WHITE'])
                if p.hits[y-5] > 2:
                    pos = (posx+1,posy+1,posx+5,posy+5)
                    panel.draw.line(pos, fill=res.COLORS['WHITE'])

                num = p.target_scores[y-5]//10
                if True:
                    txt = str(num)
                    l = len(txt)
                    panel.draw_text(
                        (11+6*(3-l)+58*x,12+8*y), 
                        str(txt), 
                        font='Medium', 
                        color=COLOR_MATRIX[x]
                    )

        for i,txt in enumerate([50,40,30,20,10]):
            panel.draw_text((43,12+8*i), str(txt), font='Medium', color='YELLOW')

        if not self.done:
            panel.draw_text(
                (3,54), 
                f"{NAME_PLAYER[a]} BALL LEFT: {self.balls}",
                font='Medium',
                color=COLOR_PLAYER[a]
            )
        else:
            panel.draw_text((40,2), "ENDING GAME", font='Medium', color='WHITE')



    def cleanup(self):
        print("Pausing for 1 seconds")
        time.sleep(1)
        # self.persist['last_score'] = self.score
        return

