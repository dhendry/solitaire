import base64
import functools
import logging
import random

from typing import Generator, List, Set

from .game_state_pb2 import *

logger = logging.getLogger(__name__)

RED_SUITS = {DIAMONDS, HEARTS}
BLACK_SUITS = {CLUBS, SPADES}

SUITS_OF_ALT_COLOR = {DIAMONDS: BLACK_SUITS, HEARTS: BLACK_SUITS, CLUBS: RED_SUITS, SPADES: RED_SUITS}


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

ALL_CARDS_MASK = (1 << (MAX_CARD_IDX + 1)) - 1

# Mask for all ranks of a particular suit
SUIT_MASK = {
    s: functools.reduce(lambda a, r: a | get_bitmask(s, r), CardRank.values()[1:], 0)
    for s in Suit.values()[1:]
}

ALT_SUIT_MASK = {
    DIAMONDS: SUIT_MASK[CLUBS] | SUIT_MASK[SPADES],
    HEARTS: SUIT_MASK[CLUBS] | SUIT_MASK[SPADES],
    CLUBS: SUIT_MASK[DIAMONDS] | SUIT_MASK[HEARTS],
    SPADES: SUIT_MASK[DIAMONDS] | SUIT_MASK[HEARTS],
}

# Mask for all suits of a particular rank
RANK_MASK = {
    r: functools.reduce(lambda a, s: a | get_bitmask(s, r), Suit.values()[1:], 0)
    for r in CardRank.values()[1:]
}

# Contains the set of all possible actions. This is really needed for the one hot encoding but putting it in
# this file so we can do asserts they are all valid
_ALL_ACTIONS = [
    *[Action(type=TO_SS_S, suit=s) for s in Suit.values()[1:]],
    *[
        Action(type=BS_N_TO_BS_N, build_stack_src=src, build_stack_dest=dest)
        for src in range(7)
        for dest in range(7)
        if src != dest
    ],
    *[
        Action(type=TALON_S_TO_BS_N, suit=s, build_stack_dest=dest)
        for s in Suit.values()[1:]
        for dest in range(7)
    ],
    *[
        Action(type=SS_S_TO_BS_N, suit=s, build_stack_dest=dest)
        for s in Suit.values()[1:]
        for dest in range(7)
    ],
]

_ALL_ACTIONS_BYTES_TO_IDX = {a.SerializeToString(): i for i, a in enumerate(_ALL_ACTIONS)}
assert len(_ALL_ACTIONS) == len(_ALL_ACTIONS_BYTES_TO_IDX)


def card_idx_to_bitmask(card_idx: int) -> int:
    assert 0 <= card_idx <= MAX_CARD_IDX, card_idx
    return 1 << card_idx


def card_idx_to_suit(card_idx: int) -> Suit:
    assert 0 <= card_idx <= MAX_CARD_IDX, card_idx
    return card_idx % 4 + 1


def card_idx_to_rank(card_idx: int) -> CardRank:
    if card_idx == -1:
        # Special case to deal with an empty mask passed into the lowest/highest functions
        return UNKNOWN_RANK

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


def bitmask_to_suit(bitmask: int) -> Suit:
    return card_idx_to_suit(bitmask_to_card_idx(bitmask))


def lowest_bitmask(bitmask: int) -> int:
    assert bitmask >= 0, bitmask
    return bitmask & ~(bitmask - 1)


def lowest_card_idx(bitmask: int) -> int:
    assert bitmask >= 0, bitmask
    return (bitmask & ~(bitmask - 1)).bit_length() - 1


def highest_card_idx(bitmask: int) -> int:
    assert bitmask >= 0, bitmask
    return bitmask.bit_length() - 1


def highest_bitmask(bitmask: int) -> int:
    idx = highest_card_idx(bitmask)
    if idx == -1:
        return 0
    return card_idx_to_bitmask(idx)


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


def game_state_id(gs: VisibleGameState) -> str:
    # return base58.b58encode_check(gs.SerializeToString(deterministic=True)).decode("utf-8")
    return base64.b64encode(gs.SerializeToString(deterministic=True)).decode("utf-8")


def is_valid_game_state(gs: VisibleGameState) -> bool:
    if len(gs.build_stacks) != 7:
        logger.info(f"Bad num build_stacks for {gs}")
        return False

    if len(gs.build_stacks_num_hidden) != 7:
        logger.info(f"Bad num build_stacks_num_hidden for {gs}")
        return False

    # TODO: check max number of cards in the talon stack

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

        # Could optimize this to not use card objects but... meh
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


def _try_apply_action(gs: VisibleGameState, hgs: HiddenGameState, action: Action) -> bool:
    assert action.SerializeToString() in _ALL_ACTIONS_BYTES_TO_IDX, action

    if action.type == TO_SS_S:
        assert CLUBS <= action.suit <= SPADES, action.suit
        assert 0 == action.build_stack_src
        assert 0 == action.build_stack_dest

        # Determine the card rank we are going to be looking to move:
        rank = card_idx_to_rank(highest_card_idx(gs.suit_stack & SUIT_MASK[action.suit])) + 1
        if rank > KING:
            return False

        # Turn the card to find into a bitmaks
        card_bitmask_to_find = get_bitmask(action.suit, rank)
        assert card_bitmask_to_find > 0

        # Find the card to move
        found = False
        if card_bitmask_to_find & gs.talon:
            # Remove from talon stack:
            gs.talon &= ~card_bitmask_to_find
            found = True
        else:
            # Look through the build stacks:
            for bidx in range(7):
                if not (card_bitmask_to_find & gs.build_stacks[bidx]):
                    continue

                if lowest_bitmask(gs.build_stacks[bidx]) != card_bitmask_to_find:
                    continue

                # Remove from build stack:
                gs.build_stacks[bidx] &= ~card_bitmask_to_find

                # Uncover hidden card if necessary:
                assert gs.build_stacks_num_hidden[bidx] == len(hgs.stack[bidx].cards)
                if gs.build_stacks[bidx] == 0 and gs.build_stacks_num_hidden[bidx] > 0:
                    gs.build_stacks_num_hidden[bidx] -= 1
                    gs.build_stacks[bidx] |= card_to_bitmask(hgs.stack[bidx].cards.pop())
                found = True
                break

        if not found:
            return False

        # Mark it as moved to the suit stack
        gs.suit_stack |= card_bitmask_to_find

    elif action.type == TALON_S_TO_BS_N:
        assert CLUBS <= action.suit <= SPADES, action.suit
        assert 0 == action.build_stack_src
        assert 0 <= action.build_stack_dest <= 6

        # Determine the card rank we are going to be looking to move:
        lowest_idx = lowest_card_idx(gs.build_stacks[action.build_stack_dest])
        rank = card_idx_to_rank(lowest_idx) - 1 if lowest_idx >= 0 else KING

        if rank < ACE:
            return False

        # This is the bitmask:
        card_to_move = get_bitmask(action.suit, rank)

        # Check the card to move is actually in the talon pile
        if gs.talon & card_to_move == 0:
            # Appropriate rank in requested suit is not in the talon pile
            return False

        # Check the colors
        if lowest_idx >= 0 and card_idx_to_suit(lowest_idx) not in SUITS_OF_ALT_COLOR[action.suit]:
            # Bottom of the build stack is not the appropriate color
            return False

        gs.talon &= ~card_to_move
        gs.build_stacks[action.build_stack_dest] |= card_to_move
    elif action.type == SS_S_TO_BS_N:
        assert CLUBS <= action.suit <= SPADES, action.suit
        assert 0 == action.build_stack_src
        assert 0 <= action.build_stack_dest <= 6

        # Determine the card rank we are going to be looking to move:
        lowest_idx = lowest_card_idx(gs.build_stacks[action.build_stack_dest])
        rank = card_idx_to_rank(lowest_idx) - 1 if lowest_idx >= 0 else KING

        if rank < ACE:
            return False

        # This is the bitmask:
        card_to_move = get_bitmask(action.suit, rank)

        # Check the card to move is actually in the suit stack
        if highest_bitmask(gs.suit_stack & SUIT_MASK[action.suit]) & card_to_move == 0:
            # Appropriate rank in requested suit is not in the pile
            return False

        # Check the colors
        if lowest_idx >= 0 and card_idx_to_suit(lowest_idx) not in SUITS_OF_ALT_COLOR[action.suit]:
            # Bottom of the build stack is not the appropriate color
            return False

        gs.suit_stack &= ~card_to_move
        gs.build_stacks[action.build_stack_dest] |= card_to_move
    elif action.type == BS_N_TO_BS_N:
        assert action.suit == UNKNOWN_SUIT, action.suit
        assert 0 <= action.build_stack_src <= 6
        assert 0 <= action.build_stack_dest <= 6

        if action.build_stack_src == action.build_stack_dest:
            return False

        # Lowest rank in the destination:
        lowest_idx = lowest_card_idx(gs.build_stacks[action.build_stack_dest])

        # Determine the max card rank we are going to be looking to move:
        max_rank = card_idx_to_rank(lowest_idx) - 1 if lowest_idx >= 0 else KING

        if max_rank < ACE:
            return False

        base_card_to_move = gs.build_stacks[action.build_stack_src] & RANK_MASK[max_rank]

        # Check the card is in the source
        if gs.build_stacks[action.build_stack_src] & base_card_to_move == 0:
            return False

        assert bit_count(base_card_to_move) == 1, bin(base_card_to_move)

        # Check the colors
        if lowest_idx >= 0 and card_idx_to_suit(lowest_idx) not in (
            SUITS_OF_ALT_COLOR[bitmask_to_suit(base_card_to_move)]
        ):
            return False

        # Note that we are not just moving one card but all cards under the base
        to_move = gs.build_stacks[action.build_stack_src] & ((base_card_to_move << 1) - 1)
        assert to_move > 0, bin(to_move)

        gs.build_stacks[action.build_stack_src] &= ~to_move
        gs.build_stacks[action.build_stack_dest] |= to_move

        # If necessary, uncover from hidden
        if (
            gs.build_stacks[action.build_stack_src] == 0
            and gs.build_stacks_num_hidden[action.build_stack_src] > 0
        ):
            gs.build_stacks_num_hidden[action.build_stack_src] -= 1
            gs.build_stacks[action.build_stack_src] |= card_to_bitmask(
                hgs.stack[action.build_stack_src].cards.pop()
            )
    else:
        raise Exception(f"Unkown action {action}")

    return True


def _get_TO_SS_S_actions(gs: VisibleGameState) -> Generator[Action, None, None]:
    to_suit_valid_mask = 0
    for s in Suit.values()[1:]:
        next_rank = card_idx_to_rank(highest_card_idx(gs.suit_stack & SUIT_MASK[s])) + 1
        if next_rank > KING:
            continue

        to_suit_valid_mask |= get_bitmask(s, next_rank)

    # Look for cards suitable for to suit stack actions
    if to_suit_valid_mask:
        for i, stack in enumerate([gs.talon, *gs.build_stacks]):
            if i > 0:
                # Unless we are looking at the talon stack, only the last card is eligible
                stack = lowest_bitmask(stack)

            found_in_stack = stack & to_suit_valid_mask
            if found_in_stack == 0:
                continue

            for card in bitmask_to_cards(found_in_stack):
                yield Action(type=TO_SS_S, suit=card.suit)

            to_suit_valid_mask &= ~found_in_stack
            if to_suit_valid_mask == 0:
                break


def _get_TALON_S_TO_BS_N_actions(gs: VisibleGameState) -> Generator[Action, None, None]:
    for bidx in range(7):
        suitability_mask = 0  # Get it?
        if gs.build_stacks[bidx] == 0:
            suitability_mask = RANK_MASK[KING]
        else:
            lowest_idx = lowest_card_idx(gs.build_stacks[bidx])

            next_rank = card_idx_to_rank(lowest_idx) - 1
            if next_rank < ACE:
                continue

            suitability_mask = RANK_MASK[next_rank] & ALT_SUIT_MASK[card_idx_to_suit(lowest_idx)]

        for card in bitmask_to_cards(gs.talon & suitability_mask):
            yield Action(type=TALON_S_TO_BS_N, suit=card.suit, build_stack_dest=bidx)


def _get_SS_S_TO_BS_N_actions(gs: VisibleGameState) -> Generator[Action, None, None]:
    suit_stack_highest = 0
    for s in Suit.values()[1:]:
        suit_stack_highest |= highest_bitmask(gs.suit_stack & SUIT_MASK[s])

    for bidx in range(7):
        suitability_mask = 0  # Get it?
        if gs.build_stacks[bidx] == 0:
            suitability_mask = RANK_MASK[KING]
        else:
            lowest_idx = lowest_card_idx(gs.build_stacks[bidx])

            next_rank = card_idx_to_rank(lowest_idx) - 1
            if next_rank < ACE:
                continue

            suitability_mask = RANK_MASK[next_rank] & ALT_SUIT_MASK[card_idx_to_suit(lowest_idx)]

        for card in bitmask_to_cards(suit_stack_highest & suitability_mask):
            yield Action(type=SS_S_TO_BS_N, suit=card.suit, build_stack_dest=bidx)


def _get_BS_N_TO_BS_N_actions(gs: VisibleGameState) -> Generator[Action, None, None]:
    for src in range(7):
        # Is there anything to move?
        if gs.build_stacks[src] == 0:
            assert gs.build_stacks_num_hidden[src] == 0
            continue

        # Look through each of the dest piles
        for dest in range(7):
            if src == dest:
                continue

            # Lowest card idx in the dest piple
            dest_lowest = lowest_card_idx(gs.build_stacks[dest])

            # Rank to find in the src pile
            max_rank = card_idx_to_rank(dest_lowest) - 1 if dest_lowest >= 0 else KING
            if max_rank < ACE:
                continue

            if max_rank == KING and gs.build_stacks_num_hidden[src] == 0:
                # Dont suggest moving kings between empty build stacks - even if its valid
                continue

            # Check the appropriate rank and color is in the src stack at - least somewhere
            src_card_mask = (
                gs.build_stacks[src]
                & (ALT_SUIT_MASK[card_idx_to_suit(dest_lowest)] if dest_lowest >= 0 else ALL_CARDS_MASK)
                & RANK_MASK[max_rank]
            )
            if src_card_mask == 0:
                continue
            assert bit_count(src_card_mask) == 1

            yield Action(type=BS_N_TO_BS_N, build_stack_src=src, build_stack_dest=dest)


class Game:
    gs: VisibleGameState
    hgs: HiddenGameState

    game_record: GameRecord

    # Note that after some benchmarking, it looks like just keeping the entire game state byte array around
    # is significantly faster than any kind of hashing
    visited_game_states: Set[bytes]

    def __init__(self, current_state: VisibleGameState, current_hidden_state: HiddenGameState):
        self.gs = current_state
        self.hgs = current_hidden_state

        self.game_record = GameRecord()
        self.game_record.initial_state.MergeFrom(self.gs)
        self.game_record.initial_hidden_state.MergeFrom(self.hgs)

        self.visited_game_states = set()

    def apply_action(self, action: Action):
        result = self.try_apply_action(action)
        if not result:
            raise Exception(f"Could not apply action {action}")

        assert is_valid_game_state(self.gs)

    def try_apply_action(
        self, action: Action, check_only: bool = False, exclude_actions_to_previous_states: bool = True
    ):
        tmp_gs = VisibleGameState()
        tmp_gs.MergeFrom(self.gs)
        tmp_hgs = HiddenGameState()
        tmp_hgs.MergeFrom(self.hgs)

        # Try apply the action
        if not _try_apply_action(gs=tmp_gs, hgs=tmp_hgs, action=action):
            assert game_state_id(self.gs) == game_state_id(tmp_gs)
            return False

        new_gs_serialized = tmp_gs.SerializeToString()
        assert game_state_id(self.gs) != game_state_id(tmp_gs)

        # Check for previous states
        if exclude_actions_to_previous_states and new_gs_serialized in self.visited_game_states:
            return False

        # If not actually applying, done
        if check_only:
            return True

        # Apply it:
        self.gs = tmp_gs
        self.hgs = tmp_hgs

        # Keep a record of what has happened
        self.game_record.actions.add().MergeFrom(action)
        self.game_record.won = self.won
        self.game_record.won_effectively = self.won_effectively
        self.visited_game_states.add(new_gs_serialized)

        return True

    def get_valid_actions(self, exclude_actions_to_previous_states: bool = True) -> List[Action]:
        actions = [
            *_get_TO_SS_S_actions(self.gs),
            *_get_BS_N_TO_BS_N_actions(self.gs),
            *_get_TALON_S_TO_BS_N_actions(self.gs),
            *_get_SS_S_TO_BS_N_actions(self.gs),
        ]

        assert all(
            self.try_apply_action(a, check_only=True, exclude_actions_to_previous_states=False)
            for a in actions
        )

        if exclude_actions_to_previous_states:
            actions = [a for a in actions if self.try_apply_action(a, True, True)]

        return actions

    @property
    def won(self) -> bool:
        if self.gs.suit_stack != ALL_CARDS_MASK:
            return False

        assert is_valid_game_state(self.gs)
        assert self.gs.talon == 0
        assert all(bs == 0 for bs in self.gs.build_stacks)
        assert all(bs_nh == 0 for bs_nh in self.gs.build_stacks_num_hidden)
        assert all(len(s.cards) == 0 for s in self.hgs.stack)

        return True

    @property
    def won_effectively(self) -> bool:
        """
        "Effectively won" means all hidden cards have been uncovered (but possibly not moved to the suit
        stack). Once all cards are uncovered its always possible to fully win the game.
        """
        # Is the game outright won?
        if self.gs.suit_stack == ALL_CARDS_MASK:
            assert self.won
            return True

        # If there are any hidden cards, the game has not been effectively one (note I believe the REAL
        # 'always winnable' condition occurs when sum(num_hidden) <= 1
        for nh in self.gs.build_stacks_num_hidden:
            if nh > 0:
                return False

        # No hidden cards, game has been effectively won
        assert is_valid_game_state(self.gs)
        assert all(len(s.cards) == 0 for s in self.hgs.stack)
        return True

    def get_game_state_id(self):
        return game_state_id(self.gs)


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

    # logger.debug(
    #     f"Game state: talon: {bitmask_to_cards(gs.talon)}\n"
    #     f"Suit stacks: {bitmask_to_cards(gs.suit_stack)}\n"
    #     f"bs0: {bitmask_to_cards(gs.build_stacks[0])}\n"
    #     f"bs1: {bitmask_to_cards(gs.build_stacks[1])}\n"
    #     f"bs2: {bitmask_to_cards(gs.build_stacks[2])}\n"
    #     f"bs3: {bitmask_to_cards(gs.build_stacks[3])}\n"
    #     f"bs4: {bitmask_to_cards(gs.build_stacks[4])}\n"
    #     f"bs5: {bitmask_to_cards(gs.build_stacks[5])}\n"
    #     f"bs6: {bitmask_to_cards(gs.build_stacks[6])}"
    # )

    assert is_valid_game_state(gs)

    return Game(gs, hgs)
