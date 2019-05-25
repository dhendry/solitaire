from unittest import TestCase

from solitaire_core.game import *

import random


def _new_gs():
    return deal_game(is_random=False).gs


class GameTest(TestCase):
    def test_bit_operators(self):
        all_cards_bitmask = 0

        current_idx = 0
        # Ranks first
        for r in CardRank.values()[1:]:
            # Then suits
            for s in Suit.values()[1:]:
                # Check the idx mapping
                self.assertEqual(current_idx, get_card_idx(s, r))

                bitmask = get_bitmask(s, r)
                self.assertEqual(bitmask, card_idx_to_bitmask(current_idx))

                # Bitmask back to idx check
                self.assertEqual(current_idx, bitmask_to_card_idx(bitmask))
                self.assertEqual([current_idx], bitmask_to_card_idxs(bitmask))

                # Idx to card check
                card = card_idx_to_card(current_idx)
                self.assertEqual(s, card.suit)
                self.assertEqual(r, card.rank)

                # Check the overall suit masks
                for s2 in Suit.values()[1:]:
                    if s == s2:
                        self.assertEqual(bitmask, bitmask & SUIT_MASK[s2])
                    else:
                        self.assertEqual(0, bitmask & SUIT_MASK[s2])

                # Check the overall rank mask
                for r2 in CardRank.values()[1:]:
                    if r == r2:
                        self.assertEqual(bitmask, bitmask & RANK_MASK[r2])
                    else:
                        self.assertEqual(0, bitmask & RANK_MASK[r2])

                all_cards_bitmask |= bitmask
                current_idx += 1

        self.assertEqual(list(range(52)), bitmask_to_card_idxs(all_cards_bitmask))

    def test_lowest_higest(self):
        self.assertEqual(-1, lowest_card_idx(0))
        self.assertEqual(-1, highest_card_idx(0))

    def test_mask_maps(self):
        # Check the suit masks are complete
        self.assertEqual(
            SUIT_MASK[CLUBS]
            | SUIT_MASK[DIAMONDS]
            | SUIT_MASK[HEARTS]
            | SUIT_MASK[SPADES],
            ALL_CARDS_MASK,
        )

        # Check the rank masks are complete
        rank_mask = 0
        for r in CardRank.values()[1:]:
            rank_mask |= RANK_MASK[r]
        self.assertEqual(rank_mask, ALL_CARDS_MASK)

    def test_bitmask_to_card_idxs(self):
        card_idxs_chosen = set()
        bitmask = 0

        for i in range(5):
            idx = -1
            while idx < 0 or idx in card_idxs_chosen:
                idx = random.randint(0, MAX_CARD_IDX)  # note randint is inclusive
            card_idxs_chosen.add(idx)

            bitmask |= 1 << idx

        self.assertEqual(5, len(card_idxs_chosen))
        self.assertEqual(5, bit_count(bitmask))

        returned_idxs = bitmask_to_card_idxs(bitmask)
        self.assertEqual(5, len(returned_idxs))

        self.assertEqual(card_idxs_chosen, set(returned_idxs))
        self.assertEqual(list(sorted(card_idxs_chosen)), returned_idxs)

    def test_is_valid_game_state(self):
        gs = _new_gs()
        self.assertTrue(is_valid_game_state(gs))

        gs.suit_stack |= 1
        self.assertFalse(is_valid_game_state(gs))

        # Move ace from talon to suit stack
        gs = _new_gs()
        gs.talon &= ~get_bitmask(CLUBS, ACE)
        self.assertFalse(is_valid_game_state(gs))
        gs.suit_stack |= get_bitmask(CLUBS, ACE)
        self.assertTrue(is_valid_game_state(gs))

        # Move another from talon to suit stack
        gs = _new_gs()
        gs.talon &= ~get_bitmask(CLUBS, FIVE)
        self.assertFalse(is_valid_game_state(gs))
        gs.suit_stack |= get_bitmask(CLUBS, FIVE)
        self.assertFalse(is_valid_game_state(gs))  # Should not pass

    def test_try_apply_action_TO_SUIT_STACK(self):
        g = deal_game(is_random=False)

        # Make sure the game state is valid:
        self.assertTrue(g.gs.talon & get_bitmask(CLUBS, ACE))

        res = g.try_apply_action(Action(type=TO_SUIT_STACK, suit=CLUBS))
        self.assertTrue(res)

        # Make sure its been moved:
        self.assertFalse(g.gs.talon & get_bitmask(CLUBS, ACE))
        self.assertTrue(g.gs.suit_stack & get_bitmask(CLUBS, ACE))

        # Make sure nothing else has been moved to the suit stack:
        self.assertFalse(g.gs.suit_stack & ~get_bitmask(CLUBS, ACE))
        self.assertTrue(is_valid_game_state(g.gs))

        # Note upper parameter is exclusive - we expect the seven to be in one of the build stacks based on
        # the non-randomized deal
        for rank_to_move in range(TWO, SEVEN):
            res = g.try_apply_action(Action(type=TO_SUIT_STACK, suit=CLUBS))
            self.assertTrue(res)
            self.assertTrue(is_valid_game_state(g.gs))

        # Seven of clubs should be on the last build stack:
        self.assertEqual(get_bitmask(CLUBS, SEVEN), g.gs.build_stacks[6])
        self.assertEqual(6, g.gs.build_stacks_num_hidden[6])

        # Next action should move from the last build stack:
        res = g.try_apply_action(Action(type=TO_SUIT_STACK, suit=CLUBS))
        self.assertTrue(res)
        self.assertTrue(is_valid_game_state(g.gs))

        # Make sure the next card in the build stack has been uncovered:
        self.assertEqual(get_bitmask(DIAMONDS, SEVEN), g.gs.build_stacks[6])
        self.assertEqual(5, g.gs.build_stacks_num_hidden[6])

        # Cant move another club
        res = g.try_apply_action(Action(type=TO_SUIT_STACK, suit=CLUBS))
        self.assertFalse(res)
        self.assertTrue(is_valid_game_state(g.gs))

        # Finally move another card type:
        res = g.try_apply_action(Action(type=TO_SUIT_STACK, suit=HEARTS))
        self.assertTrue(res)
        self.assertFalse(g.gs.talon & get_bitmask(HEARTS, ACE))
        self.assertTrue(g.gs.suit_stack & get_bitmask(HEARTS, ACE))

    def test_try_apply_action_TO_SUIT_STACK_all_cards(self):
        g = deal_game(is_random=False)

        # We expect the non-randomized deal to be directly solveable:
        for r in CardRank.values()[1:]:
            for s in Suit.values()[1:]:
                res = g.try_apply_action(Action(type=TO_SUIT_STACK, suit=s))
                self.assertTrue(res)
                self.assertTrue(is_valid_game_state(g.gs))

        self.assertTrue(g.won)
        self.assertTrue(g.won_effectively)

        # Cant apply any more:
        for s in Suit.values()[1:]:
            res = g.try_apply_action(Action(type=TO_SUIT_STACK, suit=s))
            self.assertFalse(res)
            self.assertTrue(is_valid_game_state(g.gs))

        self.assertEqual(0, g.gs.talon)
        for bidx in range(7):
            self.assertEqual(0, g.gs.build_stacks[bidx])
            self.assertEqual(0, g.gs.build_stacks_num_hidden[bidx])
            self.assertEqual([], list(g.hgs.stack[bidx].cards))

        # All cards in the suit stack:
        for r in CardRank.values()[1:]:
            for s in Suit.values()[1:]:
                self.assertTrue(g.gs.suit_stack & get_bitmask(s, r))

    def test_try_apply_action_TALON_TO_BUILD_STACK_NUM(self):
        g = deal_game(is_random=False)

        # Expect the 7 of clubs on the last build stack:
        self.assertTrue(g.gs.build_stacks[6] == get_bitmask(CLUBS, SEVEN))

        # A couple which should not work :
        self.assertFalse(
            g.try_apply_action(
                Action(type=TALON_TO_BUILD_STACK_NUM, suit=SPADES, build_stack_dest=1)
            )
        )
        self.assertFalse(
            g.try_apply_action(
                Action(type=TALON_TO_BUILD_STACK_NUM, suit=HEARTS, build_stack_dest=3)
            )
        )
        self.assertFalse(
            g.try_apply_action(
                Action(type=TALON_TO_BUILD_STACK_NUM, suit=CLUBS, build_stack_dest=6)
            )
        )

        # Setup build stack 6 (root card being the 7 of clubs)
        for _ in range(3):
            self.assertTrue(
                g.try_apply_action(
                    Action(type=TALON_TO_BUILD_STACK_NUM, suit=HEARTS, build_stack_dest=6)
                )
            )
            self.assertTrue(is_valid_game_state(g.gs))
            self.assertFalse(
                g.try_apply_action(
                    Action(type=TALON_TO_BUILD_STACK_NUM, suit=HEARTS, build_stack_dest=6)
                )
            )
            self.assertFalse(
                g.try_apply_action(
                    Action(type=TALON_TO_BUILD_STACK_NUM, suit=DIAMONDS, build_stack_dest=6)
                )
            )

            self.assertTrue(
                g.try_apply_action(
                    Action(type=TALON_TO_BUILD_STACK_NUM, suit=CLUBS, build_stack_dest=6)
                )
            )
            self.assertTrue(is_valid_game_state(g.gs))
            self.assertFalse(
                g.try_apply_action(
                    Action(type=TALON_TO_BUILD_STACK_NUM, suit=CLUBS, build_stack_dest=6)
                )
            )
            self.assertFalse(
                g.try_apply_action(
                    Action(type=TALON_TO_BUILD_STACK_NUM, suit=SPADES, build_stack_dest=6)
                )
            )

        self.assertFalse(
            g.try_apply_action(
                Action(type=TALON_TO_BUILD_STACK_NUM, suit=HEARTS, build_stack_dest=6)
            )
        )
        self.assertTrue(is_valid_game_state(g.gs))

    def test_try_apply_action_SUIT_STACK_TO_BUILD_STACK_NUM(self):
        g = deal_game(is_random=False)

        # Check the expected layout of the last two build stacks
        self.assertEqual(get_bitmask(HEARTS, SEVEN), g.gs.build_stacks[5])
        self.assertEqual(get_bitmask(CLUBS, SEVEN), g.gs.build_stacks[6])

        # Move all the clubs from the talon stack to the suit stack
        for _ in range(6):
            self.assertTrue(g.try_apply_action(Action(type=TO_SUIT_STACK, suit=CLUBS)))
            self.assertTrue(is_valid_game_state(g.gs))

        # Check the expected layout of the last two build stacks
        self.assertEqual(get_bitmask(HEARTS, SEVEN), g.gs.build_stacks[5])
        self.assertEqual(get_bitmask(CLUBS, SEVEN), g.gs.build_stacks[6])

        # Check that we cant move th 6 of clubs to the 7 of clubs
        self.assertFalse(
            g.try_apply_action(
                Action(type=SUIT_STACK_TO_BUILD_STACK_NUM, suit=CLUBS, build_stack_dest=6)
            )
        )

        # Now move the 6 of clubs from the suit stack to the 7 of hearts on build stack idx 5
        self.assertTrue(g.gs.suit_stack & get_bitmask(CLUBS, SIX))
        self.assertTrue(
            g.try_apply_action(
                Action(type=SUIT_STACK_TO_BUILD_STACK_NUM, suit=CLUBS, build_stack_dest=5)
            )
        )
        self.assertFalse(g.gs.talon & get_bitmask(CLUBS, SIX))
        self.assertTrue(g.gs.build_stacks[5] & get_bitmask(CLUBS, SIX))

        # Other final state checks
        self.assertTrue(is_valid_game_state(g.gs))
        self.assertTrue(g.gs.build_stacks[5] & get_bitmask(HEARTS, SEVEN))
        self.assertFalse(g.gs.build_stacks[6] & get_bitmask(CLUBS, SIX))

    def test_try_apply_action_SUIT_STACK_TO_BUILD_STACK_NUM_all_cards(self):
        g = deal_game(is_random=False)

        # We expect the non-randomized deal to be directly solveable:
        for r in CardRank.values()[1:]:
            for s in Suit.values()[1:]:
                res = g.try_apply_action(Action(type=TO_SUIT_STACK, suit=s))
                self.assertTrue(res)
                self.assertTrue(is_valid_game_state(g.gs))

        # Everything is in the suit stack
        self.assertEqual(0, g.gs.talon)
        for bidx in range(7):
            self.assertEqual(0, g.gs.build_stacks[bidx])
            self.assertEqual(0, g.gs.build_stacks_num_hidden[bidx])
            self.assertEqual([], list(g.hgs.stack[bidx].cards))

        # Move from the suit stack back to build stacks
        for r in CardRank.values()[1:]:
            if r % 2 == 0:
                for s, dest in [(CLUBS, 1), (DIAMONDS, 2), (HEARTS, 3), (SPADES, 4)]:
                    res = g.try_apply_action(
                        Action(type=SUIT_STACK_TO_BUILD_STACK_NUM, suit=s, build_stack_dest=dest)
                    )
                    self.assertTrue(res)
                    self.assertTrue(is_valid_game_state(g.gs))

            else:
                for s, dest in [(CLUBS, 2), (DIAMONDS, 1), (HEARTS, 4), (SPADES, 3)]:
                    res = g.try_apply_action(
                        Action(type=SUIT_STACK_TO_BUILD_STACK_NUM, suit=s, build_stack_dest=dest)
                    )
                    self.assertTrue(res)
                    self.assertTrue(is_valid_game_state(g.gs))

        self.assertEqual(0, g.gs.talon)
        self.assertEqual(0, g.gs.suit_stack)
        self.assertEqual(0, g.gs.build_stacks[0])
        self.assertEqual(0, g.gs.build_stacks[5])
        self.assertEqual(0, g.gs.build_stacks[6])

        self.assertEqual(0, g.gs.build_stacks[1] & SUIT_MASK[HEARTS])
        self.assertEqual(0, g.gs.build_stacks[2] & SUIT_MASK[HEARTS])
        self.assertEqual(0, g.gs.build_stacks[1] & SUIT_MASK[SPADES])
        self.assertEqual(0, g.gs.build_stacks[2] & SUIT_MASK[SPADES])

        self.assertEqual(0, g.gs.build_stacks[3] & SUIT_MASK[CLUBS])
        self.assertEqual(0, g.gs.build_stacks[4] & SUIT_MASK[CLUBS])
        self.assertEqual(0, g.gs.build_stacks[3] & SUIT_MASK[DIAMONDS])
        self.assertEqual(0, g.gs.build_stacks[4] & SUIT_MASK[DIAMONDS])

    def test_try_apply_action_BUILD_STACK_NUM_TO_BUILD_STACK_NUM(self):
        g = deal_game(is_random=False)

        # Check the desired initial state
        self.assertEqual(get_bitmask(CLUBS, SEVEN), g.gs.build_stacks[6])
        self.assertEqual(get_bitmask(HEARTS, SEVEN), g.gs.build_stacks[5])
        self.assertEqual(get_bitmask(DIAMONDS, EIGHT), g.gs.build_stacks[4])

        # Seven of clubs to seven of hearts - should not work:
        self.assertFalse(
            g.try_apply_action(
                Action(
                    type=BUILD_STACK_NUM_TO_BUILD_STACK_NUM, build_stack_src=6, build_stack_dest=5
                )
            )
        )
        self.assertTrue(is_valid_game_state(g.gs))

        # Seven of hearts to eight of diamonds - should not work
        self.assertFalse(
            g.try_apply_action(
                Action(
                    type=BUILD_STACK_NUM_TO_BUILD_STACK_NUM, build_stack_src=5, build_stack_dest=4
                )
            )
        )
        self.assertTrue(is_valid_game_state(g.gs))

        # Seven of clubs to eight of diamonds - should not
        self.assertTrue(
            g.try_apply_action(
                Action(
                    type=BUILD_STACK_NUM_TO_BUILD_STACK_NUM, build_stack_src=6, build_stack_dest=4
                )
            )
        )
        self.assertTrue(is_valid_game_state(g.gs))

        # Unstack a few from the talon on to one of the red sevens
        self.assertTrue(
            g.try_apply_action(
                # The six
                Action(type=TALON_TO_BUILD_STACK_NUM, suit=SPADES, build_stack_dest=5)
            )
        )
        self.assertTrue(
            g.try_apply_action(
                # The five
                Action(type=TALON_TO_BUILD_STACK_NUM, suit=HEARTS, build_stack_dest=5)
            )
        )
        self.assertTrue(
            g.try_apply_action(
                # The four
                Action(type=TALON_TO_BUILD_STACK_NUM, suit=CLUBS, build_stack_dest=5)
            )
        )
        self.assertTrue(is_valid_game_state(g.gs))

        # Now try moving between the build stacks
        self.assertEqual(4, bit_count(g.gs.build_stacks[5]))
        self.assertEqual(1, bit_count(g.gs.build_stacks[6]))
        self.assertTrue(
            g.try_apply_action(
                Action(
                    type=BUILD_STACK_NUM_TO_BUILD_STACK_NUM, build_stack_src=5, build_stack_dest=6
                )
            )
        )
        self.assertTrue(is_valid_game_state(g.gs))
        self.assertEqual(1, bit_count(g.gs.build_stacks[5]))
        self.assertEqual(4, bit_count(g.gs.build_stacks[6]))

    def test_actions__kings_and_queens(self):
        g = deal_game(is_random=False)
        for r in CardRank.values()[1:-2]:
            for s in Suit.values()[1:]:
                g.apply_action(Action(type=TO_SUIT_STACK, suit=s))

        # Now in this state:
        # +------------------------------------------------------------------------+
        # |                                                                        |
        # |                                                                        |
        # |                                                                        |
        # |                                                                        |
        # |                                                                        |
        # |                                                                        |
        # | +-----+  +-----+  +-----+  +-----+  +-----+  +-----+  +-----+  +-----+ |
        # | | J ♣ |  | K ♠ |  +-----+  | K ♦ |  | K ♣ |  | Q ♠ |  | Q ♥ |  | Q ♦ | |
        # | |     |  |     |  | Q ♣ |  |     |  |     |  |     |  |     |  |     | |
        # | |     |  |     |  |     |  |     |  |     |  |     |  |     |  |     | |
        # | +-----+  +-----+  |     |  +-----+  +-----+  +-----+  +-----+  +-----+ |
        # |                   +-----+                                              |
        # | +-----+                                                                |
        # | | J ♦ |                                                                |
        # | |     |                                                                |
        # | |     |                                                                |
        # | +-----+                                                                |
        # |                                                                        |
        # | +-----+                                                                |
        # | | J ♥ |                                                                |
        # | |     |                                                                |
        # | |     |                                                                |
        # | +-----+                                                                |
        # |                                                                        |
        # | +-----+                                                                |
        # | | J ♠ |                                                                |
        # | |     |                                                                |
        # | |     |                                                                |
        # | +-----+                                                                |
        # +------------------------------------------------------------------------+

        self.assertEqual(
            [
                Action(type=TO_SUIT_STACK, suit=CLUBS),
                Action(type=TO_SUIT_STACK, suit=SPADES),
                Action(type=TO_SUIT_STACK, suit=HEARTS),
                Action(type=TO_SUIT_STACK, suit=DIAMONDS),
                Action(type=SUIT_STACK_TO_BUILD_STACK_NUM, suit=DIAMONDS, build_stack_dest=1),
                Action(type=SUIT_STACK_TO_BUILD_STACK_NUM, suit=HEARTS, build_stack_dest=1),
                Action(type=SUIT_STACK_TO_BUILD_STACK_NUM, suit=DIAMONDS, build_stack_dest=4),
                Action(type=SUIT_STACK_TO_BUILD_STACK_NUM, suit=HEARTS, build_stack_dest=4),
                Action(type=SUIT_STACK_TO_BUILD_STACK_NUM, suit=CLUBS, build_stack_dest=5),
                Action(type=SUIT_STACK_TO_BUILD_STACK_NUM, suit=SPADES, build_stack_dest=5),
                Action(type=SUIT_STACK_TO_BUILD_STACK_NUM, suit=CLUBS, build_stack_dest=6),
                Action(type=SUIT_STACK_TO_BUILD_STACK_NUM, suit=SPADES, build_stack_dest=6),
                Action(type=BUILD_STACK_NUM_TO_BUILD_STACK_NUM, build_stack_src=1, build_stack_dest=2),
                Action(type=BUILD_STACK_NUM_TO_BUILD_STACK_NUM, build_stack_src=4, build_stack_dest=2),
                Action(type=BUILD_STACK_NUM_TO_BUILD_STACK_NUM, build_stack_src=5, build_stack_dest=0),
                Action(type=BUILD_STACK_NUM_TO_BUILD_STACK_NUM, build_stack_src=5, build_stack_dest=3),
                Action(type=BUILD_STACK_NUM_TO_BUILD_STACK_NUM, build_stack_src=6, build_stack_dest=0),
                Action(type=BUILD_STACK_NUM_TO_BUILD_STACK_NUM, build_stack_src=6, build_stack_dest=3),
            ],
            g.get_valid_actions(),
        )

    def test_get_valid_actions__simple_state(self):
        g = deal_game(is_random=False)
        # +------------------------------------------------------------------------+
        # |+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--|
        # ||  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
        # ||A |A |A |A |2 |2 |2 |2 |3 |3 |3 |3 |4 |4 |4 |4 |5 |5 |5 |5 |6 |6 |6 |6 |
        # ||♣ |♦ |♥ |♠ |♣ |♦ |♥ |♠ |♣ |♦ |♥ |♠ |♣ |♦ |♥ |♠ |♣ |♦ |♥ |♠ |♣ |♦ |♥ |♠ |
        # ||  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
        # |+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--|
        # | +-----+  +-----+  +-----+  +-----+  +-----+  +-----+  +-----+  +-----+ |
        # | |   ♣ |  | K ♠ |  +-----+  +-----+  +-----+  +-----+  +-----+  +-----+ |
        # | |     |  |     |  | Q ♣ |  +-----+  +-----+  +-----+  +-----+  +-----+ |
        # | |     |  |     |  |     |  | 10♥ |  +-----+  +-----+  +-----+  +-----+ |
        # | +-----+  +-----+  |     |  |     |  | 9 ♦ |  +-----+  +-----+  +-----+ |
        # |                   +-----+  |     |  |     |  | 8 ♦ |  +-----+  +-----+ |
        # | +-----+                    +-----+  |     |  |     |  | 7 ♥ |  +-----+ |
        # | |   ♦ |                             +-----+  |     |  |     |  | 7 ♣ | |
        # | |     |                                      +-----+  |     |  |     | |
        # | |     |                                               +-----+  |     | |
        # | +-----+                                                        +-----+ |
        # |                                                                        |
        # | +-----+                                                                |
        # | |   ♥ |                                                                |
        # | |     |                                                                |
        # | |     |                                                                |
        # | +-----+                                                                |
        # |                                                                        |
        # | +-----+                                                                |
        # | |   ♠ |                                                                |
        # | |     |                                                                |
        # | |     |                                                                |
        # | +-----+                                                                |
        # +------------------------------------------------------------------------+

        self.assertEqual(
            [
                Action(type=TO_SUIT_STACK, suit=CLUBS),
                Action(type=TO_SUIT_STACK, suit=DIAMONDS),
                Action(type=TO_SUIT_STACK, suit=HEARTS),
                Action(type=TO_SUIT_STACK, suit=SPADES),
                Action(type=TALON_TO_BUILD_STACK_NUM, suit=CLUBS, build_stack_dest=5),
                Action(type=TALON_TO_BUILD_STACK_NUM, suit=SPADES, build_stack_dest=5),
                Action(type=TALON_TO_BUILD_STACK_NUM, suit=DIAMONDS, build_stack_dest=6),
                Action(type=TALON_TO_BUILD_STACK_NUM, suit=HEARTS, build_stack_dest=6),
                Action(
                    type=BUILD_STACK_NUM_TO_BUILD_STACK_NUM, build_stack_src=6, build_stack_dest=4
                ),
            ],
            g.get_valid_actions(),
        )

        # Move the ace through 6 of clubs to the suit stack
        for _ in range(6):
            g.apply_action(Action(type=TO_SUIT_STACK, suit=CLUBS))
        actions = g.get_valid_actions()
        self.assertIn(
            Action(type=SUIT_STACK_TO_BUILD_STACK_NUM, suit=CLUBS, build_stack_dest=5), actions
        )

        # Move the seven fof clubs to the eight of diamonds, this uncovers two red sevens on the last stacks
        g.apply_action(
            Action(type=BUILD_STACK_NUM_TO_BUILD_STACK_NUM, build_stack_src=6, build_stack_dest=4)
        )
        self.assertEqual(get_bitmask(HEARTS, SEVEN), g.gs.build_stacks[5])
        self.assertEqual(get_bitmask(DIAMONDS, SEVEN), g.gs.build_stacks[6])

        # Now move the six of spades from the talon to the 5th build stack:
        g.apply_action(Action(type=TALON_TO_BUILD_STACK_NUM, suit=SPADES, build_stack_dest=5))

        actions = g.get_valid_actions()
        self.assertEqual(
            [
                Action(
                    type=BUILD_STACK_NUM_TO_BUILD_STACK_NUM, build_stack_src=5, build_stack_dest=6
                )
            ],
            [a for a in actions if a.type == BUILD_STACK_NUM_TO_BUILD_STACK_NUM],
        )

    def test_is_won(self):
        g = deal_game(is_random=False)

        self.assertFalse(g.won)
        self.assertFalse(g.won_effectively)

        # Move everything except the last set of kings
        for r in CardRank.values()[1:-1]:
            for s in Suit.values()[1:]:
                g.apply_action(Action(type=TO_SUIT_STACK, suit=s))

        # Game is not entirely one (4 kings still on the build stacks) but its effectively won
        self.assertFalse(g.won)
        self.assertTrue(g.won_effectively)

        # Move the last set of kings
        for s in Suit.values()[1:]:
            g.apply_action(Action(type=TO_SUIT_STACK, suit=s))

        self.assertTrue(g.won)
        self.assertTrue(g.won_effectively)
