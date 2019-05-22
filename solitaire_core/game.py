import functools
import logging
import random
from typing import List

import numpy as np

from .game_state_pb2 import *

logger = logging.getLogger(__name__)

RED_SUITS = {DIAMONDS, HEARTS}
BLACK_SUITS = {CLUBS, SPADES}


def bit_count(int_type: int) -> int:
    """
    From https://wiki.python.org/moin/BitManipulation
    """
    count = 0
    while int_type:
        int_type &= int_type - 1
        count += 1
    return count


def get_card_idx(suit: Suit, rank: CardRank) -> int:
    assert UNKNOWN_SUIT < suit <= SPADES
    assert UNKNOWN_RANK < rank <= KING
    return (suit - 1) + (rank - 1) * 4


def get_bitmask(suit: Suit, rank: CardRank) -> int:
    return 1 << get_card_idx(suit, rank)


def card_to_bitmask(card: Card) -> int:
    assert card is not None
    return get_bitmask(card.suit, card.rank)


# Inclusive
MAX_CARD_IDX = get_card_idx(SPADES, KING)


# Mask for all ranks of a particular suit
SUIT_MASK = {
    s: functools.reduce(lambda a, r: a | get_bitmask(s, r), CardRank.values()[1:], 0)
    for s in Suit.values()[1:]
}

# Mask for all suits of a particular rank
RANK_MASK = {
    r: functools.reduce(lambda a, s: a | get_bitmask(s, r), Suit.values()[1:], 0)
    for r in CardRank.values()[1:]
}


def card_idx_to_bitmask(card_idx: int) -> int:
    assert 0 <= card_idx <= MAX_CARD_IDX, card_idx
    return 1 << card_idx


def card_idx_to_suit(card_idx: int) -> Suit:
    assert 0 <= card_idx <= MAX_CARD_IDX, card_idx
    return card_idx % 4 + 1


def card_idx_to_rank(card_idx: int) -> CardRank:
    assert 0 <= card_idx <= MAX_CARD_IDX, card_idx
    return card_idx // 4 + 1


def card_idx_to_card(card_idx: int) -> Card:
    assert 0 <= card_idx <= MAX_CARD_IDX, card_idx

    card = Card(suit=card_idx_to_suit(card_idx), rank=card_idx_to_rank(card_idx))
    assert UNKNOWN_SUIT < card.suit <= SPADES, card
    assert UNKNOWN_RANK < card.rank <= KING, card
    return card


def bitmask_to_card_idx(bitmask: int) -> int:
    assert isinstance(bitmask, int)
    assert bit_count(bitmask) == 1, bin(bitmask)
    idx = bitmask.bit_length() - 1
    assert 0 <= idx <= MAX_CARD_IDX, idx
    return idx


def lowest_card_idx(bitmask: int) -> int:
    assert bitmask >= 0, bitmask
    return (bitmask & ~(bitmask - 1)).bit_length() - 1


def highest_card_idx(bitmask: int) -> int:
    assert bitmask >= 0, bitmask
    return bitmask.bit_length() - 1


def bitmask_to_card_idxs(bitmask: int) -> List[int]:
    assert isinstance(bitmask, int)

    num_bits = bit_count(bitmask)

    # Note that the returned list is sorted inherently by the process we are using here
    card_idxs = []
    while bitmask:
        card_idxs.append(lowest_card_idx(bitmask))

        # Similar to the clever bit_count logic above (see link)
        bitmask &= bitmask - 1

    assert len(card_idxs) == num_bits

    return card_idxs


def bitmask_to_cards(bitmask: int) -> List[Card]:
    return [card_idx_to_card(idx) for idx in bitmask_to_card_idxs(bitmask)]


def is_valid_game_state(gs: VisibleGameState) -> bool:
    if len(gs.build_stacks) != 7:
        logger.info(f"Bad num build_stacks for {gs}")
        return False

    if len(gs.build_stacks_num_hidden) != 7:
        logger.info(f"Bad num build_stacks_num_hidden for {gs}")
        return False

    # Check that there are no duplicate cards anywhere
    seen_cards = 0
    for visible_stack in [gs.talon, gs.suit_stack, *gs.build_stacks]:
        if seen_cards & visible_stack != 0:
            # There is a repeated card
            logger.info(
                f"Repeated card for {gs}, {bitmask_to_cards(seen_cards)} "
                f"and {bitmask_to_cards(visible_stack)}"
            )
            return False
        seen_cards |= visible_stack

    # Check the number of hidden cards
    num_hidden = 0
    for i, build_hidden_num in enumerate(gs.build_stacks_num_hidden):
        if build_hidden_num < 0:
            logger.info(f"Negative num hidden for {gs}")
            return False

        if build_hidden_num > i:
            logger.info(f"Num hidden too great for {gs}")
            return False

        if build_hidden_num > 0 and gs.build_stacks[i] == 0:
            logger.info(f"Empty visible build stack but hidden cards for {gs}")
            return False

        num_hidden += build_hidden_num

    # Check the total number of cards
    if bit_count(seen_cards) + num_hidden != 13 * 4:
        logger.info(f"Bad total card count for {gs}")
        return False

    # Check suit stacks for strictly increasing
    for s in Suit.values()[1:]:
        stack = gs.suit_stack & SUIT_MASK[s]
        if stack == 0:
            continue

        highest_idx = highest_card_idx(stack)
        assert card_idx_to_suit(highest_idx) == s

        # Fancy way to check all lower cards are present:
        if stack != ((1 << (highest_idx + 1)) - 1) & SUIT_MASK[s]:
            logger.info(f"Out of order suit stack for {gs}")
            return False

    # Check for the proper structure of the build stacks:
    for stack in gs.build_stacks:
        if stack == 0:
            continue

        # Could optimize this to not use card objects but... meh, seems premature
        previous_card = None
        for card in bitmask_to_cards(stack):
            if previous_card is None:
                previous_card = card
                continue

            # Sequential ranks
            if card.rank != previous_card.rank + 1:
                logger.info(f"Non sequential card rank in build stack for {bitmask_to_cards(stack)}")
                return False

            # Alternating colors:
            if previous_card.suit in BLACK_SUITS and card.suit not in RED_SUITS:
                logger.info(f"Non alternating suits for {bitmask_to_cards(stack)}")
                return False
            if previous_card.suit in RED_SUITS and card.suit not in BLACK_SUITS:
                logger.info(f"Non alternating suits for {bitmask_to_cards(stack)}")
                return False

            previous_card = card

    return True


def state_to_vec(game_state: VisibleGameState) -> np.array:
    pass


class Game:
    gs: VisibleGameState
    hgs: HiddenGameState

    previous_states_and_actions = []

    def __init__(self, current_state: VisibleGameState, current_hidden_state: HiddenGameState):
        self.gs = current_state
        self.hgs = current_hidden_state

    def try_apply_action(self, action: Action, check_only: bool = False) -> bool:

        if action.type == TO_SUIT_STACK:
            assert CLUBS <= action.suit <= SPADES, action.suit
            assert 0 == action.build_stack_src
            assert 0 == action.build_stack_dest

            # Determine the card rank we are going to be looking to move:
            highest_idx = highest_card_idx(self.gs.suit_stack & SUIT_MASK[action.suit])
            rank = card_idx_to_rank(highest_idx) + 1 if highest_idx >= 0 else ACE
            if rank > KING:
                return False

            # Turn the card to find into a bitmaks
            card_bitmask_to_find = get_bitmask(action.suit, rank)
            assert card_bitmask_to_find > 0

            # Find the card to move
            found = False
            if card_bitmask_to_find & self.gs.talon:
                if not check_only:
                    # Remove from talon stack:
                    self.gs.talon &= ~card_bitmask_to_find
                found = True
            else:
                # Look through the build stacks:
                for bidx in range(7):
                    if not (card_bitmask_to_find & self.gs.build_stacks[bidx]):
                        continue

                    if not check_only:
                        # Remove from build stack:
                        self.gs.build_stacks[bidx] &= ~card_bitmask_to_find

                        # Uncover hidden card if necessary:
                        assert self.gs.build_stacks_num_hidden[bidx] == len(self.hgs.stack[bidx].cards)
                        if self.gs.build_stacks_num_hidden[bidx] > 0:
                            self.gs.build_stacks_num_hidden[bidx] -= 1
                            self.gs.build_stacks[bidx] |= card_to_bitmask(self.hgs.stack[bidx].cards.pop())
                    found = True
                    break

            if not found:
                return False

            # Mark it as moved to the suit stack
            if not check_only:
                self.gs.suit_stack |= card_bitmask_to_find

        elif action.type == TALON_TO_BUILD_STACK_NUM:
            assert CLUBS <= action.suit <= SPADES, action.suit
            assert 0 == action.build_stack_src
            assert 0 <= action.build_stack_dest <= 6
            
        else:
            raise Exception(f"Unkown action {action}")


        return True
            # card_idx_to_rank()
        pass


def deal_game(seed: int = None, is_random: bool = True):
    card_idxs = list(range(52))

    if is_random:
        random.Random(seed).shuffle(card_idxs)
    else:
        # Reverse to make the resulting game trivial (useful for testing)
        card_idxs.reverse()

    gs = VisibleGameState(build_stacks=[0] * 7, build_stacks_num_hidden=[0] * 7)
    hgs = HiddenGameState(stack=[HiddenGameState.HiddenStack() for _ in range(7)])

    # This is the index in the list of indexes... not confusing at all...
    current_card_idx = 0

    # Hidden cards on the build stacks
    for fill_pass in range(0, 7):
        for buid_stack_idx in range(fill_pass, 7):
            if fill_pass == buid_stack_idx:
                # Visible
                gs.build_stacks[buid_stack_idx] |= card_idx_to_bitmask(card_idxs[current_card_idx])
            else:
                # Hidden
                hgs.stack[buid_stack_idx].cards.extend([card_idx_to_card(card_idxs[current_card_idx])])
                gs.build_stacks_num_hidden[buid_stack_idx] += 1

            current_card_idx += 1

    # Remaining cards into the talon pile
    while current_card_idx < len(card_idxs):
        gs.talon |= card_idx_to_bitmask(card_idxs[current_card_idx])
        current_card_idx += 1

    logger.debug(
        f"Game state: talon: {bitmask_to_cards(gs.talon)}\n"
        f"Suit stacks: {bitmask_to_cards(gs.suit_stack)}\n"
        f"bs0: {bitmask_to_cards(gs.build_stacks[0])}\n"
        f"bs1: {bitmask_to_cards(gs.build_stacks[1])}\n"
        f"bs2: {bitmask_to_cards(gs.build_stacks[2])}\n"
        f"bs3: {bitmask_to_cards(gs.build_stacks[3])}\n"
        f"bs4: {bitmask_to_cards(gs.build_stacks[4])}\n"
        f"bs5: {bitmask_to_cards(gs.build_stacks[5])}\n"
        f"bs6: {bitmask_to_cards(gs.build_stacks[6])}"
    )

    assert is_valid_game_state(gs)

    return Game(gs, hgs)
