import base64
from typing import Optional

import time
from datetime import datetime

from solitaire_core.game import *

TO_EFFECTIVE_WIN = True
# Win rate @5 = ~19%
# Win rate @2 = ~22%
# Win rate @1 = ~23%
WEIGHTING_BIAS = 1


def play_move(game: Game) -> bool:
    actions = game.get_valid_actions()
    if len(actions) == 0:
        return False

    # Weighted bias is somewhat arbitrary
    weighted_actions = {(WEIGHTING_BIAS / (i + WEIGHTING_BIAS)): a for i, a in enumerate(actions)}

    selection = random.random() * sum(weighted_actions.keys())
    current_sum = 0
    for w, a in weighted_actions.items():
        current_sum += w
        if current_sum > selection:
            game.apply_action(a)
            return True

    raise Exception()


class StatTracker:
    def __init__(self, *, parent = None, name: str = "", update_interval: float = 1.0):
        self.parent = parent
        self.name = name
        self.games_played = 0
        self.games_won = 0
        self.games_lost = 0
        self.total_moves_made = 0

        self.update_interval = update_interval
        self.last_stat_update = time.time()
        self.last_total_moves_made = 0

    def mark_won(self):
        self.games_won += 1
        self.games_played += 1

        if self.parent is not None:
            self.parent.mark_won()

    def mark_lost(self):
        self.games_lost += 1
        self.games_played += 1

        if self.parent is not None:
            self.parent.mark_lost()

    def mark_move(self):
        self.total_moves_made += 1

        self._try_print_stats()

        if self.parent is not None:
            self.parent.mark_move()

    def _try_print_stats(self):
        if time.time() < self.last_stat_update + self.update_interval:
            return

        self.print_stats()

    def print_stats(self):
        since_last = time.time() - self.last_stat_update
        print(
            f"Name:{str(self.name).ljust(15)} \t"
            f"Played:{str(self.games_played).rjust(6)}  \t"
            f"Won:{str(self.games_won).rjust(5)}  \t"
            f"Lost:{str(self.games_lost).rjust(5)}  \t"
            f"Total moves:{str(self.total_moves_made).rjust(7)}  \t"
            f"moves/s:{str(round((self.total_moves_made - self.last_total_moves_made)/since_last, 2)).rjust(7)}  \t",
            f"Win rate:{str(round(self.games_won/max(self.games_played, 1), 2)).rjust(6)}  \t",
        )
        self.last_total_moves_made = self.total_moves_made
        self.last_stat_update = time.time()


class SingleGamePlayLoop:
    """
    For playing a particular deal multiple times.
    """

    def __init__(self):
        g = deal_game()
        self.initial_gs = g.gs
        self.initial_hgs = g.hgs

        self.win_records: List[GameRecord] = []
        self.loss_records: List[GameRecord] = []

    def play_one_game(self, *, play_move_fn=play_move, stats: Optional[StatTracker] = None):
        # Copy the game states since they are going to be mutated
        gs = VisibleGameState()
        hgs = HiddenGameState()
        gs.MergeFrom(self.initial_gs)
        hgs.MergeFrom(self.initial_hgs)

        g = Game(current_state=gs, current_hidden_state=hgs)

        while True:
            if TO_EFFECTIVE_WIN and g.won_effectively or g.won:
                if stats is not None:
                    stats.mark_won()
                self.win_records.append(g.game_record)
                return True

            if not play_move_fn(g):
                if stats is not None:
                    stats.mark_lost()
                self.loss_records.append(g.game_record)
                return False

            if stats is not None:
                stats.mark_move()

            assert is_valid_game_state(g.gs), g.get_game_state_id()

    def get_best_win_record(self) -> Optional[GameRecord]:
        if len(self.win_records) == 0:
            return None
        elif len(self.win_records) == 1:
            return self.win_records[0]

        return functools.reduce(lambda a, b: b if len(b.actions) < len(a.actions) else a, self.win_records)


if __name__ == "__main__":
    date = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    with open(f"{date}-win-game-records.b64", "w") as f:
        stats = StatTracker(name="All games", update_interval=1)
        first_game_stats = StatTracker(parent=stats, name="First games", update_interval=5)
        winnable_game_stats = StatTracker(parent=stats, name="Winnable games", update_interval=5)

        while True:
            sgpl = SingleGamePlayLoop()

            # Try playing a couple of times to see if the gs seems to be winnable
            for _ in range(5):
                sgpl.play_one_game(stats=first_game_stats)

            if len(sgpl.win_records) == 0:
                # Try a new deal if we have not found a win yet
                continue

            # Play the deal a few more times to try and find the shortest path to a win
            for _ in range(10):
                sgpl.play_one_game(stats=winnable_game_stats)

            # Save the best with to the file
            f.write(base64.b64encode(sgpl.get_best_win_record().SerializeToString()).decode("utf-8") + "\n")
