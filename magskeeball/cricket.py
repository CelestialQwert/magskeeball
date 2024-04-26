import time
from enum import Enum

from .state import GameMode
from . import constants as const

COLOR_MATRIX = ["BLUE", "RED"]

SCORING_BUTTONS = {
    const.B.B100: 0,
    const.B.B200: 1,
    const.B.B300: 2,
    const.B.B400: 3,
    const.B.B500: 4,
}


class CricketState(Enum):
    PLAY = 0
    PLAYER_DONE = 1
    PLAYER_CHANGE = 2
    GAME_END = 3


class Player:
    def __init__(self, num=0, color="WHITE"):
        self.num = num
        self.hits = [0] * 5
        self.target_scores = [0] * 5
        self.ball_scores = []
        self.score = 0
        self.score_buffer = 0
        self.target_buffers = [0] * 5
        self.name = f"PLAYER {num}"
        self.short_name = f"P{num}"
        self.color = color


class Cricket(GameMode):

    intro_text = [
        "THE POPULAR DART",
        "GAME, BUT WITH",
        "SKEE-BALLS!",
    ]

    def startup(self):
        print("Starting cricket")

        self.p1 = Player(1, "GREEN")
        self.p2 = Player(2, "MAGENTA")

        self.active_player = self.p1
        self.inactive_player = self.p2

        self.balls = 3
        self.returned_balls = 3

        self.advance_score = False

        self.ticks = 0
        self.ticks_last_ball = 0
        self.ticks_player_change = 0

        self.game_state = CricketState.PLAY

        self.debug = self.settings["debug"]
        self.timeout = self.settings["timeout"] * const.FPS

        self.persist["active_game_mode"] = "CRICKET"

    def handle_event(self, event):
        if event.button == const.B.QUIT:
            self.quit = True
        if event.button == const.B.CONFIG:
            self.game_state = CricketState.GAME_END
            self.ticks_last_ball = self.ticks

        if self.game_state == CricketState.GAME_END:
            if event.button in [const.B.START, const.B.SELECT] and event.down:
                self.done = True

        if self.game_state != CricketState.PLAY:
            return

        if self.balls == 0:
            return

        if event.down and event.button in SCORING_BUTTONS:
            btn = event.button
            btn_idx = SCORING_BUTTONS[btn]
            const.SOUNDS[btn.name].play()
            self.active_player.hits[btn_idx] += 1
            self.balls -= 1
            self.advance_score = True
            print(f"Active player: {self.active_player.hits}")
            if (
                self.active_player.hits[btn_idx] > 3
                and self.inactive_player.hits[btn_idx] < 3
            ):
                points = const.POINTS[btn]
                self.active_player.score_buffer += points
                self.active_player.target_buffers[btn_idx] += points
                self.active_player.ball_scoconst.append(points)

        if event.down and event.button == const.B.RETURN:
            self.returned_balls -= 1
            if self.returned_balls < self.balls:
                self.balls = self.returned_balls

    def update(self):
        # print(f'{self.game_state} {self.ticks_last_ball} {self.ticks}')

        self.ticks += 1

        match self.game_state:
            case CricketState.PLAYER_DONE:
                if self.ticks - self.ticks_last_ball > 2 * const.FPS:
                    self.game_state = CricketState.PLAYER_CHANGE
                    self.ticks_last_ball = self.ticks
                if min(self.active_player.hits) >= 3 and (
                    min(self.inactive_player.hits) >= 3
                    or self.active_player.score > self.inactive_player.score
                ):
                    self.game_state = CricketState.GAME_END
                    self.ticks_last_ball = self.ticks
                return
            case CricketState.PLAYER_CHANGE:
                if self.ticks - self.ticks_last_ball > 3 * const.FPS:
                    self.game_state = CricketState.PLAY
                    self.ticks_last_ball = self.ticks
                    self.balls = 3
                    self.returned_balls = 3
                    self.active_player, self.inactive_player = (
                        self.inactive_player,
                        self.active_player,
                    )
                return
            case CricketState.GAME_END:
                if self.ticks - self.ticks_last_ball > 20 * const.FPS:
                    self.done = True

        if self.balls == 0 and not self.advance_score:
            self.game_state = CricketState.PLAYER_DONE
            self.ticks_last_ball = self.ticks

        if self.advance_score:
            if self.active_player.score_buffer > 0:
                self.active_player.score += 100
                self.active_player.score_buffer -= 100
            for i in range(5):
                if self.active_player.target_buffers[i] > 0:
                    self.active_player.target_scores[i] += 100
                    self.active_player.target_buffers[i] -= 100
        if self.active_player.score_buffer == 0:
            self.advance_score = False

        # if (self.ticks - self.ticks_last_ball) > self.timeout:
        #     self.done = True

    def draw_panel(self, panel):
        panel.clear()

        for x, p in enumerate([self.p1, self.p2]):
            panel.draw_text((3 + 52 * x, 2), p.short_name, "Medium", p.color)
            score = f"{p.score//10: >4}"
            panel.draw_text((18 + 52 * x, 2), score, "Medium", p.color)

            for y in range(5):
                posx = 32 + 26 * x
                posy = 13 + 8 * y
                if p.hits[4 - y] > 0:
                    pos = (posx, posy, posx + 6, posy + 6)
                    panel.draw.ellipse(pos, outline=const.COLORS["WHITE"])
                if p.hits[4 - y] > 1:
                    pos = (posx + 5, posy + 1, posx + 1, posy + 5)
                    panel.draw.line(pos, fill=const.COLORS["WHITE"])
                if p.hits[4 - y] > 2:
                    pos = (posx + 1, posy + 1, posx + 5, posy + 5)
                    panel.draw.line(pos, fill=const.COLORS["WHITE"])

                num = p.target_scores[4 - y] // 10
                if p.hits[4 - y] > 3:
                    txt = f"{num: >3}" if num < 1000 else "XXX"
                    l = len(txt)
                    panel.draw_text(
                        (11 + 58 * x, 12 + 8 * y), txt, "Medium", COLOR_MATRIX[x]
                    )

        for i, txt in enumerate([50, 40, 30, 20, 10]):
            panel.draw_text((43, 12 + 8 * i), txt, "Medium", "YELLOW")

        match self.game_state:
            case CricketState.PLAY | CricketState.PLAYER_DONE:
                panel.draw_text(
                    (3, 54),
                    f"{self.active_player.short_name} BALL LEFT: {self.balls}",
                    "Medium",
                    self.active_player.color,
                )
            case CricketState.PLAYER_CHANGE:
                panel.draw_text((9, 54), f"CHANGE PLAYER", "Medium", "WHITE")
            case CricketState.GAME_END:
                if self.p1.score > self.p2.score:
                    panel.draw_text((9, 54), "PLAYER 1 WIN!", "Medium", "GREEN")
                if self.p1.score < self.p2.score:
                    panel.draw_text((9, 54), "PLAYER 2 WIN!", "Medium", "MAGENTA")
                if self.p1.score == self.p2.score:
                    panel.draw_text((18, 54), "TIED GAME!", "Medium", "WHITE")

    def cleanup(self):
        self.manager.next_state = "ATTRACT"
