import itertools

from typing import List

import numpy as np
from solitaire_core import game


def _stack_to_array(stack: int) -> List[float]:
    assert 0 <= stack <= game.ALL_CARDS_MASK
    return [
        float(min(1, stack & game.get_bitmask(s, r)))
        for r in game.CardRank.values()[1:]
        for s in game.Suit.values()[1:]
    ]


def game_state_to_array(gs: game.VisibleGameState) -> List[float]:
    state_vector = list(
        itertools.chain(
            _stack_to_array(gs.talon),
            _stack_to_array(gs.suit_stack),
            *[_stack_to_array(s) for s in gs.build_stacks],
            [h / 6.0 for h in gs.build_stacks_num_hidden]
        )
    )

    assert all(0 <= elem <= 1 for elem in state_vector)

    return state_vector


# def action_to_onehot(action: game.Action) -> List[float]:

# game._ALL_ACTIONS_BYTES_TO_IDX[]
