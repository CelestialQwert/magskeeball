import json
import pygame
import sys
import time
import traceback

from . import constants as const
from . import panel
from . import resources
from . import sensor
from . import settings_manager

from .attract import Attract
from .intro import Intro
from .high_scores import HighScore
from .gameover import GameOver
from .service_menu import ServiceMenu

from .classic import Classic
from .target import Target
from .combo import Combo
from .timed import Timed
from .flash import Flash
from .speedrun import Speedrun
from .threek import ThreeK
from .world import World
from .cricket import Cricket

from .dummy import Dummy
from .debug import Debug
from .game_menu import GameMenu

STATE_CLASSES = {
    "ATTRACT": Attract,
    "SERVICEMENU": ServiceMenu,
    "INTRO": Intro,
    "HIGHSCORE": HighScore,
    "GAMEOVER": GameOver,
    "CLASSIC": Classic,
    "TARGET": Target,
    "COMBO": Combo,
    "TIMED": Timed,
    "FLASH": Flash,
    "SPEEDRUN": Speedrun,
    "THREE-K": ThreeK,
    "WORLD": World,
    "CRICKET": Cricket,
    "DUMMY": Dummy,
    "DEBUG": Debug,
    "GAMEMENU": GameMenu,
}

GAME_MODES = [
    "CLASSIC",
    "TARGET",
    "COMBO",
    "TIMED",
    "FLASH",
    "SPEEDRUN",
    "THREE-K",
    "WORLD",
]

HIDDEN_MODES = [
    "CRICKET",
]

EXTRA_MODES = [
    "DUMMY",
    "DEBUG",
    "GAMEMENU",
]

SELECTABLE_MODES = GAME_MODES + HIDDEN_MODES + EXTRA_MODES


class Manager:

    def __init__(self, state_classes=STATE_CLASSES, starting_state="ATTRACT"):
        self.panel = None
        try:
            self.init(state_classes, starting_state)
        except Exception as e:
            if self.panel:
                self.crash(e)
            else:
                raise e

    def init(self, state_classes=None, starting_state=None):

        print("init pygame")
        pygame.init()
        print("done init pygame")

        self.res = resources.ResourceManager()

        self.panel = panel.Panel()
        self.panel.draw_message_screen("LOADING...")

        try:
            self.sensor = sensor.Sensor()
            self.sensor.set_repeat(0, 0)
        except RuntimeError:
            self.panel.draw_message_screen("SENSOR ERROR", color="RED")
            while True:
                pass

        self.settings = settings_manager.SettingsManager(SELECTABLE_MODES)
        self.settings.load_settings()
        self.persist = {}

        self.res.load_all()
        self.res.set_sounds(self.settings["general_sfx"], self.settings["colossus"])

        self.states = {}
        for name, StateClass in state_classes.items():
            self.states[name] = StateClass(manager=self)
        self.game_modes = GAME_MODES
        self.all_game_modes = GAME_MODES + HIDDEN_MODES

        self.has_high_scores = {}
        for game_mode in SELECTABLE_MODES:
            self.has_high_scores[game_mode] = self.states[game_mode].has_high_scores
        self.has_high_scores["SERVICEMENU"] = False

        self.state_name = starting_state

        self.done = False
        self.clock = pygame.time.Clock()
        self.state = self.states[self.state_name]

        self.persist["hs_game_hist"] = ["CLASSIC"]
        self.persist["active_game_mode"] = "DUMMY"

        self.last_state = ""
        self.next_state = ""

        self.game_log = self.states["HIGHSCORE"].load_game_log()
        print(self.game_log)

        self.high_scores = self.states["HIGHSCORE"].load_all_high_scores()

        self.global_ticks = 0

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
        time.sleep(1 / const.FPS)
        self.sensor.get_events()
        time.sleep(1 / const.FPS)
        # switch to new state
        self.last_state = self.state_name
        self.state_name = self.next_state
        if self.state_name in self.all_game_modes:
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
        try:
            self.state.startup()
            while not self.done:
                self.global_ticks += 1
                self.clock.tick(const.FPS)
                self.handle_events()
                self.update()
                self.draw_panel()
                if self.state.quit:
                    self.done = True
                elif self.state.done:
                    self.flip_state()
            self.state.cleanup()
            pygame.quit()
        except Exception as e:
            self.crash(e)

    def crash(self, exc):
        self.panel.draw_message_screen(exc.__repr__(), color="RED")
        traceback.print_exception(exc)
        input("Press enter to exit")
        sys.exit()


def test():
    from . import test_states

    states = {"INTRO": test_states.Intro, "DUMMYGAME": test_states.DummyGame}
    starting_state = "INTRO"

    game = Manager(states, starting_state)
    game.main_loop()


if __name__ == "__main__":
    test()
