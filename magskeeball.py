#!/usr/bin/env python3

import time
import sys
import os
from PIL import Image, ImageFont

from basic_skeeball import BasicSkeeball
from combo import Combo
from target import Target
from dummy import Dummy
from config_menu import ConfigMenu
from common import *
import panel
import sensor
import timer


COLORS = [
    (50,50,255),
    (255,0,0),
    (255,255,0),
    (0,255,0),
    (255,150,150)
]


class SkeeballApp():

    def __init__(self):
        self.sensor = sensor.Sensor(sensor.EMULATED)
        self.panel = panel.Panel(panel.EMULATED)
        
        self.basic_skeeball = BasicSkeeball(self.panel,self.sensor)
        self.combo = Combo(self.panel,self.sensor)
        self.target = Target(self.panel,self.sensor)
        self.dummy = Dummy(self.panel,self.sensor)
        self.game_list = [
            self.basic_skeeball,
            self.combo,
            self.target,
            self.dummy,
        ]
        self.game_dict = {g.name: g for g in self.game_list}
        

        self.config_menu = ConfigMenu(self.panel,self.sensor,self.game_list)
        self.settings = self.config_menu.settings
        self.do_red_hiscore = True

    def main_loop(self):
        self.clock = timer.Timer()
        self.clock.ticks = 280
        while True:
            self.clock.tick(20)

            if self.clock.ticks % 200 < 100 or not(self.settings['do_hi_scores']):
                self.draw_attract()
            else:
                if self.clock.ticks % 400 < 200:
                    game = self.game_dict[self.settings['red_game']]
                else:
                    game = self.game_dict[self.settings['yellow_game']]
                self.draw_high_scores(game)
            
            self.sensor.update_buttons()
            if self.sensor.is_pressed(BUTTON['START']):
                self.game_dict[self.settings['red_game']].main_loop(self.settings)
                self.clock.ticks = 100
            elif self.sensor.is_pressed(BUTTON['SELECT']):
                self.game_dict[self.settings['yellow_game']].main_loop(self.settings)
                self.clock.ticks = 300
            elif self.sensor.is_pressed(BUTTON['CONFIG']):
                self.config_menu.main_loop()
                self.clock.ticks = 0

    def draw_attract(self):
        self.panel.clear()
        self.panel.paste(IMAGES['MainLogo'],(0,5))
        if self.clock.ticks % 40 < 30:
            self.panel.draw.text((15,53), "PRESS START",font=FONTS['Medium'],fill=(255,255,255))
        self.panel.update()

    def draw_high_scores(self,game):
        self.panel.clear()
        title_text = 'HI SCORES - {}'.format(game.name)
        x = int(48-len(title_text)*2.5)+1
        self.panel.draw.text((x,2),title_text,font=FONTS['Small'],fill=(255,255,255))
        (name,score) = game.high_scores[0]
        self.panel.draw.text((24,10),'{} {:04d}'.format(name,score),font=FONTS['Medium'],fill=COLORS[0])
        #for i,(name,score) in enumerate(game.high_scores):
        for i in [1,2,3,4]:
            (name,score) = game.high_scores[i]
            self.panel.draw.text((28,i*8+12),'{} {}'.format(name,score),font=FONTS['Small'],fill=COLORS[i])
            #self.panel.draw.text((8+8*i,(i+1)*9),'%s %04d' % (name,score),font=FONTS['Small'],fill=COLORS[i])
        if self.clock.ticks % 40 < 30:
            self.panel.draw.text((15,53), "PRESS START",font=FONTS['Medium'],fill=(255,255,255))
        self.panel.update()
        #self.do_red_hiscore = not(self.do_red_hiscore)
    
    

def main():
    game = SkeeballApp()
    game.main_loop()

if __name__ == '__main__':
    main()