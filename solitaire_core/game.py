from .game_state_pb2 import *
import numpy as np


def get_card_idx(suit: Suit, rank: CardRank) -> int:
    assert UNKNOWN_SUIT < suit <= SPADES
    assert UNKNOWN_RANK < rank <= KING
    return (suit - 1) + (rank - 1) * 4


def get_bitmask(suit: Suit, rank: CardRank) -> int:
    return 1 << get_card_idx(suit, rank)

def is_valid_game_state(game_state: VisibleGameState) -> bool:


    pass


def state_to_vec(game_state: VisibleGameState) -> np.array:
    pass

class Game:
    current_state: VisibleGameState
    current_hidden_state: HiddenGameState

    previous_states_and_actions = []


    def try_apply_action(self, action: Action, check_only: bool = False) -> bool:

        if action.type == TO_SUIT_STACK_CLUBS:
            pass
        pass
