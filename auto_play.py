import base64
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
    games_played = 0
    games_won = 0
    games_lost = 0
    total_moves_made = 0

    last_stat_update = time.time()
    last_total_moves_made = 0

    def mark_won(self, gr: GameRecord):
        self.games_won += 1
        self.games_played += 1

    def mark_lost(self, gr: GameRecord):
        self.games_lost += 1
        self.games_played += 1

    def mark_move(self):
        self.total_moves_made += 1

        self._try_print_stats()

    def _try_print_stats(self):
        if time.time() < self.last_stat_update + 1:
            return

        since_last = time.time() - self.last_stat_update
        print(
            f"Played:{str(self.games_played).rjust(6)}  \t"
            f"Won:{str(self.games_won).rjust(5)}  \t"
            f"Lost:{str(self.games_lost).rjust(5)}  \t"
            f"Total moves:{str(self.total_moves_made).rjust(7)}  \t"
            f"moves/s:{str(round((self.total_moves_made - self.last_total_moves_made)/since_last, 2)).rjust(7)}  \t",
            f"Win rate:{str(round(self.games_won/max(self.games_played, 1), 2)).rjust(6)}  \t",
        )
        self.last_total_moves_made = self.total_moves_made
        self.last_stat_update = time.time()


if __name__ == "__main__":
    stats = StatTracker()

    g = deal_game()

    date = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

    with open(f"{date}-win-game-records.b64", "w") as f:
        f.read()
        while True:
            if TO_EFFECTIVE_WIN and g.won_effectively or g.won:
                stats.mark_won(g.game_record)
                f.write(base64.b64encode(g.game_record.SerializeToString()).decode("utf-8") + "\n")
                g = deal_game()
                continue

            if not play_move(g):
                stats.mark_lost(g.game_record)
                g = deal_game()
                continue

            assert is_valid_game_state(g.gs), g.get_game_state_id()

            stats.mark_move()
