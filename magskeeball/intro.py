from .state import State
from . import constants as const
import random


class Intro(State):

    # def __init__(self,manager):
    #    super(Dummy,self).__init__(manager)

    def startup(self):
        self.mode_name = self.persist["active_game_mode"]
        self.manager.next_state = self.mode_name
        self.mode = self.manager.states[self.mode_name]
        self.intro_text = self.mode.intro_text
        self.ticks = 0
        if self.mode_name == "TARGET":
            self.start_song = self.res.sounds["target"]["TARGET_INTRO"]
        else:
            self.start_song = random.choice(list(self.res.sounds["start"].values()))
        self.start_song.play()

    def handle_event(self, event):
        if event.button == const.B.QUIT:
            self.quit = True
        if event.button in [const.B.START, const.B.SELECT] and event.down:
            self.done = True

    def update(self):
        self.ticks += 1
        if self.ticks > 10 * const.FPS:
            self.done = True

    def draw_panel(self, panel):
        panel.clear()
        title = "{} MODE".format(self.mode_name)
        x = 48 - 3 * len(title)
        panel.draw_text((x, 1), title, "Medium", "PURPLE")
        for i, line in enumerate(self.intro_text):
            panel.draw_text((1, 15 + 8 * i), line, "Small", "YELLOW")
        panel.draw_text((15, 48), "PRESS START", "Medium", "WHITE")
