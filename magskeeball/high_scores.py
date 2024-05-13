from .state import State
from . import constants as const
import time
import shutil
import json
from pathlib import Path

LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ._<%"


class HighScore(State):

    def __init__(self, manager):
        super(HighScore, self).__init__(manager)
        self.high_scores = {}
        self.high_score_dir = Path("high_scores")

    def startup(self):
        self.manager.next_state = "GAMEOVER"
        self.last_mode = self.persist["active_game_mode"]

        print("old list", self.persist["hs_game_hist"])
        self.persist["hs_game_hist"] = [self.last_mode] + self.persist["hs_game_hist"]
        temp_hist = []
        for game in self.persist["hs_game_hist"]:
            if game not in temp_hist:
                temp_hist.append(game)
        self.persist["hs_game_hist"] = temp_hist[:2]
        print("new list", self.persist["hs_game_hist"])

        self.score = self.persist["last_score"]
        self.game_high_scores = self.high_scores[self.last_mode]

        place = 0

        self.name = ""
        self.cursor = 0
        self.ticks = 0
        self.new_score = False

        for their_name, their_score in self.game_high_scores:
            place += 1
            their_score = int(their_score)
            if (
                self.score > their_score
                and self.manager.states[self.last_mode].score_type == "score"
            ) or (
                self.score < their_score
                and self.manager.states[self.last_mode].score_type == "time"
            ):
                self.new_score = True
                self.place = place
                self.res.sounds["misc"][f"PLACE{self.place}"].play()
                return

    def handle_event(self, event):
        if event.button == const.B.QUIT:
            self.quit = True
        if not self.new_score:
            return
        if event.down and event.button == const.B.SELECT:
            self.cursor = (self.cursor + 1) % len(LETTERS)
        if event.down and event.button == const.B.START:
            if self.curr_letter == "<":
                # keep cursor at same location in LETTERS
                self.name = self.name[:-1]
                if len(self.name) == 0:
                    self.cursor = 0
            elif self.curr_letter == "%":
                # name is done so pad with spaces
                while len(self.name) < 4:
                    self.name = self.name + " "
            else:
                self.name = self.name + self.curr_letter
                if len(self.name) == 3:
                    self.cursor = len(LETTERS) - 1
                else:
                    self.cursor = 0
                # underscores are there so spaces can be seen
                self.name = self.name.replace("_", " ")
        # if name is 3 letters, lock out everything but OK and <
        # (last 2 chars)
        if len(self.name) == 3 and self.cursor < len(LETTERS) - 2:
            self.cursor = len(LETTERS) - 2

    def update(self):
        if not self.new_score:
            self.done = True
            return
        if len(self.name) == 4:
            self.done = True
        self.ticks += 1
        self.curr_letter = LETTERS[self.cursor]

    def draw_panel(self, panel):
        if not self.new_score:
            return
        panel.clear()

        if self.manager.states[self.last_mode].score_type == "time":
            display_time = self.persist["last_score"]
            panel.draw_time((7, 6), display_time, "PURPLE")
            panel.draw_text((16, 30), "GREAT TIME!", "Medium", "YELLOW")
        else:
            score_x = 17 if self.score < 10000 else 4
            panel.draw_text((score_x, 4), f"{self.score:04d}", "Digital16", "PURPLE")
            panel.draw_text((16, 30), "HIGH SCORE!", "Medium", "YELLOW")

        # each line is shown for 3/2 (1.5) seconds
        if self.ticks % 90 < 30:
            panel.draw_text((7, 40), "ENTER INITIALS", "Medium", "YELLOW")
        elif self.ticks % 90 < 60:
            panel.draw_text((3, 40), "YELLOW = CHANGE", "Medium", "YELLOW")
        else:
            panel.draw_text((18, 40), "RED = PICK", "Medium", "YELLOW")
        panel.draw_text((39, 50), self.name, "Medium", "WHITE")
        if self.ticks % 4 < 3 and len(self.name) < 4:
            # blink current letter
            panel.draw_text(
                (39 + 6 * len(self.name), 50), self.curr_letter, "Medium", "WHITE"
            )
        panel.draw_text((19, 50), f"#{self.place}", "Medium", "WHITE")

    def cleanup(self):
        if self.new_score:
            print("Pausing for 2 seconds")
            time.sleep(2)
            self.name = self.name[:3]
            new_high_scores = (
                self.game_high_scores[: self.place - 1]
                + [(self.name, self.score)]
                + self.game_high_scores[self.place - 1 : 4]
            )
            self.save_high_scores(self.last_mode, new_high_scores)

    def load_all_high_scores(self):
        for game_mode in self.manager.all_game_modes:
            if self.manager.states[game_mode].has_high_scores:
                self.high_scores[game_mode] = self.load_high_scores(game_mode)
        return self.high_scores

    def init_all_high_scores(self):
        for game_mode in self.manager.all_game_modes:
            if self.manager.states[game_mode].has_high_scores:
                self.high_scores[game_mode] = self.init_high_scores(game_mode)
        return self.high_scores

    def init_game_log(self):
        self.high_score_dir.mkdir(mode=0o777, parents=True, exist_ok=True)

        game_plays_log = self.high_score_dir / "game_plays.txt"
        if game_plays_log.exists():
            ts = time.strftime("%Y-%m-%d_%H-%M-%S")
            dest = self.high_score_dir / f"game_plays_{ts}.txt"
            shutil.move(game_plays_log, dest)

        game_log = {}
        for game in self.manager.all_game_modes:
            game_log[game] = 0

        with open(game_plays_log, "w") as f:
            f.write(json.dumps(game_log))
        game_plays_log.chmod(0o777)

        return game_log

    def load_game_log(self):
        game_plays_log = self.high_score_dir / "game_plays.txt"
        try:
            with open(game_plays_log, "r") as f:
                return json.loads(f.read())
        except:
            print("loading game log failed, remaking")
            return self.init_game_log()

    def save_game_log(self):
        with open(self.high_score_dir / "game_plays.txt", "w") as f:
            f.write(json.dumps(self.manager.game_log))

    def init_high_scores(self, game_mode):
        self.high_score_dir.mkdir(mode=0o777, parents=True, exist_ok=True)

        mode_scores_file = self.high_score_dir / f"{game_mode}.txt"
        if mode_scores_file.exists():
            ts = time.strftime("%Y-%m-%d_%H-%M-%S")
            dest = self.high_score_dir / f"{game_mode}_{ts}.txt"
            shutil.move(mode_scores_file, dest)
        with open(mode_scores_file, "w") as sf:
            if self.manager.states[game_mode].score_type == "time":
                sf.write("MAG,1195\nFES,1196\nTIS,1197\nADO,1198\nNUT,1199\n")
            else:
                sf.write("MAG,2000\nFES,1600\nTIS,1200\nADO,800\nNUT,400\n")
        mode_scores_file.chmod(0o777)
        return self.load_high_scores(game_mode)

    def load_high_scores(self, game_mode):
        mode_scores_file = self.high_score_dir / f"{game_mode}.txt"
        high_scores = []
        try:
            with open(mode_scores_file, "r") as f:
                for line in f.readlines():
                    name, score = line.split(",")
                    if len(name) > 3:
                        raise IOError("Name is too long")
                    score = int(score)
                    high_scores.append((name, score))
        except:
            print(f"Error in high score file for mode {game_mode}, creating new...")
            high_scores = self.init_high_scores(game_mode)
        return high_scores

    def save_high_scores(self, game_mode, scores):
        mode_scores_file = self.high_score_dir / f"{game_mode}.txt"
        with open(mode_scores_file, "w") as sf:
            for name, score in scores:
                sf.write(f"{name},{score}\n")
        self.high_scores[game_mode] = scores
