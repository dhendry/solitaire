import os
import re

from solitaire_core import text_renderer
from solitaire_core.game import *

NUMBER_RE = re.compile("^\d+$")

if __name__ == "__main__":
    g = deal_game(is_random=False)

    while True:
        actions = g.get_valid_actions()

        os.system("clear")
        print(text_renderer.render(g.gs, actions))
        print("game_state_id", game_state_id(g.gs))
        print("len(g.visited_game_states)", len(g.visited_game_states))
        print("len(g.game_record.actions)", len(g.game_record.actions))
        print("Won:", g.won)
        print("Won effectively:", g.won_effectively)

        choice = input("Choice: ").lower()

        if choice == "q":
            break
        elif choice == "n":
            g = deal_game()
        elif NUMBER_RE.match(choice):
            action_idx = int(choice)

            if action_idx >= len(actions):
                continue

            g.apply_action(actions[action_idx])

            assert is_valid_game_state(g.gs)
