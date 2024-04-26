from .state import GameMode
from . import constants as const

class Dummy(GameMode):

    intro_text = [
        "STUB GAME MODE",
        "FOR TESTING",
    ]

    def handle_event(self, event):
        if event.button == const.B.QUIT:
            self.quit = True
        if event.button == const.B.START and event.down:
            self.manager.next_state = "ATTRACT"
            self.done = True

    def draw_panel(self, panel):
        panel.clear()
        panel.draw_text((1, 0), "DUMMY MODE", "Medium", "WHITE")
        panel.draw_text((1, 9), "RED TO QUIT", "Medium", "WHITE")
        panel.draw_text((1, 20), "DUMMY GAME", "MAGFest", "WHITE")
        panel.draw_text((1, 40), "RED TO QUIT", "MAGFest", "WHITE")
