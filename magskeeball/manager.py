import sys
import pygame
import time
import json

from . import resources as res
from . import panel
from . import sensor

from .attract import Attract
from .settings import Settings
from .intro import Intro
from .high_scores import HighScore
from .gameover import GameOver

from .classic import Classic
from .target import Target
from .combo import Combo
from .timed import Timed
from .flash import Flash
from .speedrun import Speedrun
from .world import World
from .cricket import Cricket

from .dummy import Dummy
from .debug import Debug
from .game_menu import GameMenu

print("init pygame")
pygame.init()
pygame.mixer.stop()
print("done init pygame")


class Manager:

    def __init__(self, states=None, starting_state=None):

        self.settings = {}
        self.persist = {}

        self.sounds = res.load_sounds()
        
        self.panel = panel.Panel()


        if states == None:
            self.states = {
                "ATTRACT": Attract(manager=self),
                "SETTINGS": Settings(manager=self),
                "INTRO": Intro(manager=self),
                "HIGHSCORE": HighScore(manager=self),
                "GAMEOVER": GameOver(manager=self),
                "CLASSIC": Classic(manager=self),
                "TARGET": Target(manager=self),
                "COMBO": Combo(manager=self),
                "TIMED": Timed(manager=self),
                "FLASH": Flash(manager=self),
                "SPEEDRUN": Speedrun(manager=self),
                "WORLD": World(manager=self),
                "CRICKET": Cricket(manager=self),
                "DUMMY": Dummy(manager=self),
                "DEBUG": Debug(manager=self),
                "GAMEMENU": GameMenu(manager=self),
            }
            self.game_modes = [
                "CLASSIC",
                "TARGET",
                "COMBO",
                "TIMED",
                "FLASH",
                "SPEEDRUN",
                "WORLD",
            ]
            self.selectable_modes = self.game_modes + [
                "CRICKET",
                "DUMMY",
                "DEBUG",
                "GAMEMENU",
            ]

            self.has_high_scores = {}
            for game_mode in self.selectable_modes:
                self.has_high_scores[game_mode] = self.states[game_mode].has_high_scores
            self.has_high_scores["SETTINGS"] = False

        else:
            self.states = {}
            for state in states:
                self.states[state] = states[state](manager=self)
        self.state_name = starting_state
        if self.state_name is None:
            self.state_name = "ATTRACT"

        self.done = False
        self.sensor = sensor.Sensor()
        self.clock = pygame.time.Clock()
        self.state = self.states[self.state_name]

        self.settings["red_game"] = "CLASSIC"
        self.settings["yellow_game"] = "DUMMY"
        self.settings["timeout"] = 60
        self.settings["save_high_scores"] = True
        self.settings["debug"] = False

        self.persist["hs_game_hist"] = ["CLASSIC"]
        self.persist["active_game_mode"] = "DUMMY"

        self.last_state = ""
        self.next_state = ""

        self.game_log = self.states["HIGHSCORE"].load_game_log()
        print(self.game_log)

        self.high_scores = self.states["HIGHSCORE"].load_all_high_scores()
        # lol mutable
        temp_settings = self.states["SETTINGS"].load_settings()
        for key, value in temp_settings.items():
            self.settings[key] = value

        self.global_ticks = 0
        self.sensor.set_repeat(0, 0)

    def handle_events(self):
        for event in self.sensor.get_events():
            if isinstance(event, sensor.InputEvent):
                print(
                    f"Tick {self.global_ticks}, Handling InputEvent, "
                    f"button = {event.button}, down = {event.down}"
                )
            else:
                print(f"Tick {self.global_ticks}, Handling event", type(event))
            self.state.handle_event(event)

    def update(self):
        self.state.update()

    def draw_panel(self):
        self.state.draw_panel(self.panel)
        self.panel.update()

    def flip_state(self):
        # shutdown old state
        self.state.cleanup()
        print("Ending old state", self.state_name)
        # clear events to prevent buffering
        # sleep prevents weird bug where an extra
        # buttonup and buttondown event are generated
        time.sleep(1 / res.FPS)
        self.sensor.get_events()
        time.sleep(1 / res.FPS)
        # switch to new state
        self.last_state = self.state_name
        self.state_name = self.next_state
        if self.state_name in self.game_modes:
            try:
                temp_plays = self.game_log[self.state_name]
            except:
                temp_plays = 0
            self.game_log[self.state_name] = temp_plays + 1
            self.states["HIGHSCORE"].save_game_log()

        self.next_state = ""
        self.state = self.states[self.state_name]
        # startup new state
        print("Starting new state", self.state_name)
        self.state.done = False
        self.state.startup()

    def main_loop(self):
        self.state.startup()
        while not self.done:
            self.global_ticks += 1
            self.clock.tick(res.FPS)
            self.handle_events()
            self.update()
            self.draw_panel()
            if self.state.quit:
                self.done = True
            elif self.state.done:
                self.flip_state()
        self.state.cleanup()
        pygame.quit()


def test():
    from . import test_states

    states = {"INTRO": test_states.Intro, "DUMMYGAME": test_states.DummyGame}
    starting_state = "INTRO"

    game = Manager(states, starting_state)
    game.main_loop()


if __name__ == "__main__":
    test()
