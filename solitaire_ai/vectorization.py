import itertools

from typing import List, Optional

from solitaire_core import game


def _stack_to_array(stack: int) -> List[float]:
    """
    Card stack (as a bitmask) to partial state vector
    """
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
            [h / 6.0 for h in gs.build_stacks_num_hidden],
        )
    )

    assert all(0 <= elem <= 1 for elem in state_vector)

    return state_vector


def action_to_onehot(action: game.Action) -> List[float]:
    idx = game._ALL_ACTIONS_BYTES_TO_IDX[action.SerializeToString()]

    onehot_vector = [1.0 if i == idx else 0.0 for i in range(len(game._ALL_ACTIONS))]

    assert sum(onehot_vector) == 1.0
    assert sum(elem == 1.0 for elem in onehot_vector) == 1.0

    return onehot_vector


def onehot_to_action(one_hot: List[float], acceptable_actions: Optional[List[game.Action]] = None) -> game.Action:
    assert acceptable_actions is None or len(acceptable_actions) > 0

    acceptable_action_idxs = set()
    if acceptable_actions:
        for a in acceptable_actions:
            acceptable_action_idxs.add(game._ALL_ACTIONS_BYTES_TO_IDX[a.SerializeToString()])
    else:
        acceptable_action_idxs = set(game._ALL_ACTIONS_BYTES_TO_IDX.values())

    # Find the greatest element in the array - not its not exactly a "onehot"
    max_value = 0
    max_value_idx = -1

    for i, v in enumerate(one_hot):
        assert v <= 1
        if v > max_value and i in acceptable_action_idxs:
            max_value = v
            max_value_idx = i

    if max_value_idx == -1:
        raise Exception(f"No element set in list {one_hot}")

    return game._ALL_ACTIONS[max_value_idx]
