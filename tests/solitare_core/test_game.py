from unittest import TestCase

from solitaire_core import game

import random


def _new_gs():
    return game.deal_game(is_random=False).gs


class GameTest(TestCase):
    def test_bit_operators(self):
        all_cards_bitmask = 0

        current_idx = 0
        # Ranks first
        for r in game.CardRank.values()[1:]:
            # Then suits
            for s in game.Suit.values()[1:]:
                # Check the idx mapping
                self.assertEqual(current_idx, game.get_card_idx(s, r))

                bitmask = game.get_bitmask(s, r)
                self.assertEqual(bitmask, game.card_idx_to_bitmask(current_idx))

                # Bitmask back to idx check
                self.assertEqual(current_idx, game.bitmask_to_card_idx(bitmask))
                self.assertEqual([current_idx], game.bitmask_to_card_idxs(bitmask))

                # Idx to card check
                card = game.card_idx_to_card(current_idx)
                self.assertEqual(s, card.suit)
                self.assertEqual(r, card.rank)

                # Check the overall suit masks
                for s2 in game.Suit.values()[1:]:
                    if s == s2:
                        self.assertEqual(bitmask, bitmask & game.SUIT_MASK[s2])
                    else:
                        self.assertEqual(0, bitmask & game.SUIT_MASK[s2])

                # Check the overall rank mask
                for r2 in game.CardRank.values()[1:]:
                    if r == r2:
                        self.assertEqual(bitmask, bitmask & game.RANK_MASK[r2])
                    else:
                        self.assertEqual(0, bitmask & game.RANK_MASK[r2])

                all_cards_bitmask |= bitmask
                current_idx += 1

        self.assertEqual(list(range(52)), game.bitmask_to_card_idxs(all_cards_bitmask))

    def test_lowest_higest(self):
        self.assertEqual(-1, game.lowest_card_idx(0))
        self.assertEqual(-1, game.highest_card_idx(0))

    def test_bitmask_to_card_idxs(self):
        card_idxs_chosen = set()
        bitmask = 0

        for i in range(5):
            idx = -1
            while idx < 0 or idx in card_idxs_chosen:
                idx = random.randint(0, game.MAX_CARD_IDX)  # note randint is inclusive
            card_idxs_chosen.add(idx)

            bitmask |= 1 << idx

        self.assertEqual(5, len(card_idxs_chosen))
        self.assertEqual(5, game.bit_count(bitmask))

        returned_idxs = game.bitmask_to_card_idxs(bitmask)
        self.assertEqual(5, len(returned_idxs))

        self.assertEqual(card_idxs_chosen, set(returned_idxs))
        self.assertEqual(list(sorted(card_idxs_chosen)), returned_idxs)

    def test_is_valid_game_state(self):
        gs = _new_gs()
        gs.suit_stack |= 1
        self.assertFalse(game.is_valid_game_state(gs))

        # Move ace from talon to suit stack
        gs = _new_gs()
        gs.talon &= ~game.get_bitmask(game.CLUBS, game.ACE)
        self.assertFalse(game.is_valid_game_state(gs))
        gs.suit_stack |= game.get_bitmask(game.CLUBS, game.ACE)
        self.assertTrue(game.is_valid_game_state(gs))

        # Move another from talon to suit stack
        gs = _new_gs()
        gs.talon &= ~game.get_bitmask(game.CLUBS, game.FIVE)
        self.assertFalse(game.is_valid_game_state(gs))
        gs.suit_stack |= game.get_bitmask(game.CLUBS, game.FIVE)
        self.assertFalse(game.is_valid_game_state(gs))  # Should not pass

    def test_try_apply_action_TO_SUIT_STACK(self):
        g = game.deal_game(is_random=False)

        # Make sure the game state is valid:
        self.assertTrue(g.gs.talon & game.get_bitmask(game.CLUBS, game.ACE))

        res = g.try_apply_action(game.Action(type=game.TO_SUIT_STACK, suit=game.CLUBS))
        self.assertTrue(res)

        # Make sure its been moved:
        self.assertFalse(g.gs.talon & game.get_bitmask(game.CLUBS, game.ACE))
        self.assertTrue(g.gs.suit_stack & game.get_bitmask(game.CLUBS, game.ACE))

        # Make sure nothing else has been moved to the suit stack:
        self.assertFalse(g.gs.suit_stack & ~game.get_bitmask(game.CLUBS, game.ACE))
        self.assertTrue(game.is_valid_game_state(g.gs))

        # Note upper parameter is exclusive - we expect the seven to be in one of the build stacks based on
        # the non-randomized deal
        for rank_to_move in range(game.TWO, game.SEVEN):
            res = g.try_apply_action(game.Action(type=game.TO_SUIT_STACK, suit=game.CLUBS))
            self.assertTrue(res)
            self.assertTrue(game.is_valid_game_state(g.gs))

        # Seven of clubs should be on the last build stack:
        self.assertEqual(game.get_bitmask(game.CLUBS, game.SEVEN), g.gs.build_stacks[6])
        self.assertEqual(6, g.gs.build_stacks_num_hidden[6])

        # Next action should move from the last build stack:
        res = g.try_apply_action(game.Action(type=game.TO_SUIT_STACK, suit=game.CLUBS))
        self.assertTrue(res)
        self.assertTrue(game.is_valid_game_state(g.gs))

        # Make sure the next card in the build stack has been uncovered:
        self.assertEqual(game.get_bitmask(game.DIAMONDS, game.SEVEN), g.gs.build_stacks[6])
        self.assertEqual(5, g.gs.build_stacks_num_hidden[6])

        # Cant move another club
        res = g.try_apply_action(game.Action(type=game.TO_SUIT_STACK, suit=game.CLUBS))
        self.assertFalse(res)
        self.assertTrue(game.is_valid_game_state(g.gs))

        # Finally move another card type:
        res = g.try_apply_action(game.Action(type=game.TO_SUIT_STACK, suit=game.HEARTS))
        self.assertTrue(res)
        self.assertFalse(g.gs.talon & game.get_bitmask(game.HEARTS, game.ACE))
        self.assertTrue(g.gs.suit_stack & game.get_bitmask(game.HEARTS, game.ACE))

    def test_try_apply_action_TO_SUIT_STACK_all_cards(self):
        g = game.deal_game(is_random=False)

        # We expect the non-randomized deal to be directly solveable:
        for r in game.CardRank.values()[1:]:
            for s in game.Suit.values()[1:]:
                res = g.try_apply_action(game.Action(type=game.TO_SUIT_STACK, suit=s))
                self.assertTrue(res)
                self.assertTrue(game.is_valid_game_state(g.gs))

        # Cant apply any more:
        for s in game.Suit.values()[1:]:
            res = g.try_apply_action(game.Action(type=game.TO_SUIT_STACK, suit=s))
            self.assertFalse(res)
            self.assertTrue(game.is_valid_game_state(g.gs))

        self.assertEqual(0, g.gs.talon)
        for bidx in range(7):
            self.assertEqual(0, g.gs.build_stacks[bidx])
            self.assertEqual(0, g.gs.build_stacks_num_hidden[bidx])
            self.assertEqual([], list(g.hgs.stack[bidx].cards))

        # All cards in the suit stack:
        for r in game.CardRank.values()[1:]:
            for s in game.Suit.values()[1:]:
                self.assertTrue(g.gs.suit_stack & game.get_bitmask(s, r))

    def test_try_apply_action_TALON_TO_BUILD_STACK_NUM(self):
        g = game.deal_game(is_random=False)

        # Expect the 7 of clubs on the last build stack:
        self.assertTrue(g.gs.build_stacks[6] == game.get_bitmask(game.CLUBS, game.SEVEN))

        # A couple which should not work :
        self.assertFalse(
            g.try_apply_action(
                game.Action(type=game.TALON_TO_BUILD_STACK_NUM, suit=game.SPADES, build_stack_dest=1)
            )
        )
        self.assertFalse(
            g.try_apply_action(
                game.Action(type=game.TALON_TO_BUILD_STACK_NUM, suit=game.HEARTS, build_stack_dest=3)
            )
        )
        self.assertFalse(
            g.try_apply_action(
                game.Action(type=game.TALON_TO_BUILD_STACK_NUM, suit=game.CLUBS, build_stack_dest=6)
            )
        )

        # Setup build stack 6 (root card being the 7 of clubs)
        for _ in range(3):
            self.assertTrue(
                g.try_apply_action(
                    game.Action(type=game.TALON_TO_BUILD_STACK_NUM, suit=game.HEARTS, build_stack_dest=6)
                )
            )
            self.assertTrue(game.is_valid_game_state(g.gs))
            self.assertFalse(
                g.try_apply_action(
                    game.Action(type=game.TALON_TO_BUILD_STACK_NUM, suit=game.HEARTS, build_stack_dest=6)
                )
            )
            self.assertFalse(
                g.try_apply_action(
                    game.Action(type=game.TALON_TO_BUILD_STACK_NUM, suit=game.DIAMONDS, build_stack_dest=6)
                )
            )

            self.assertTrue(
                g.try_apply_action(
                    game.Action(type=game.TALON_TO_BUILD_STACK_NUM, suit=game.CLUBS, build_stack_dest=6)
                )
            )
            self.assertTrue(game.is_valid_game_state(g.gs))
            self.assertFalse(
                g.try_apply_action(
                    game.Action(type=game.TALON_TO_BUILD_STACK_NUM, suit=game.CLUBS, build_stack_dest=6)
                )
            )
            self.assertFalse(
                g.try_apply_action(
                    game.Action(type=game.TALON_TO_BUILD_STACK_NUM, suit=game.SPADES, build_stack_dest=6)
                )
            )

        self.assertFalse(
            g.try_apply_action(
                game.Action(type=game.TALON_TO_BUILD_STACK_NUM, suit=game.HEARTS, build_stack_dest=6)
            )
        )
        self.assertTrue(game.is_valid_game_state(g.gs))

    def test_try_apply_action_SUIT_STACK_TO_BUILD_STACK_NUM(self):
        g = game.deal_game(is_random=False)

        # Check the expected layout of the last two build stacks
        self.assertEqual(game.get_bitmask(game.HEARTS, game.SEVEN), g.gs.build_stacks[5])
        self.assertEqual(game.get_bitmask(game.CLUBS, game.SEVEN), g.gs.build_stacks[6])

        # Move all the clubs from the talon stack to the suit stack
        for _ in range(6):
            self.assertTrue(g.try_apply_action(game.Action(type=game.TO_SUIT_STACK, suit=game.CLUBS)))
            self.assertTrue(game.is_valid_game_state(g.gs))

        # Check the expected layout of the last two build stacks
        self.assertEqual(game.get_bitmask(game.HEARTS, game.SEVEN), g.gs.build_stacks[5])
        self.assertEqual(game.get_bitmask(game.CLUBS, game.SEVEN), g.gs.build_stacks[6])

        # Check that we cant move th 6 of clubs to the 7 of clubs
        self.assertFalse(
            g.try_apply_action(
                game.Action(type=game.SUIT_STACK_TO_BUILD_STACK_NUM, suit=game.CLUBS, build_stack_dest=6)
            )
        )

        # Now move the 6 of clubs from the suit stack to the 7 of hearts on build stack idx 5
        self.assertTrue(g.gs.suit_stack & game.get_bitmask(game.CLUBS, game.SIX))
        self.assertTrue(
            g.try_apply_action(
                game.Action(type=game.SUIT_STACK_TO_BUILD_STACK_NUM, suit=game.CLUBS, build_stack_dest=5)
            )
        )
        self.assertFalse(g.gs.talon & game.get_bitmask(game.CLUBS, game.SIX))
        self.assertTrue(g.gs.build_stacks[5] & game.get_bitmask(game.CLUBS, game.SIX))

        # Other final state checks
        self.assertTrue(game.is_valid_game_state(g.gs))
        self.assertTrue(g.gs.build_stacks[5] & game.get_bitmask(game.HEARTS, game.SEVEN))
        self.assertFalse(g.gs.build_stacks[6] & game.get_bitmask(game.CLUBS, game.SIX))

    def test_try_apply_action_SUIT_STACK_TO_BUILD_STACK_NUM_all_cards(self):
        g = game.deal_game(is_random=False)

        # We expect the non-randomized deal to be directly solveable:
        for r in game.CardRank.values()[1:]:
            for s in game.Suit.values()[1:]:
                res = g.try_apply_action(game.Action(type=game.TO_SUIT_STACK, suit=s))
                self.assertTrue(res)
                self.assertTrue(game.is_valid_game_state(g.gs))

        # Everything is in the suit stack
        self.assertEqual(0, g.gs.talon)
        for bidx in range(7):
            self.assertEqual(0, g.gs.build_stacks[bidx])
            self.assertEqual(0, g.gs.build_stacks_num_hidden[bidx])
            self.assertEqual([], list(g.hgs.stack[bidx].cards))

        # Move from the suit stack back to build stacks
        for r in game.CardRank.values()[1:]:
            if r % 2 == 0:
                for s, dest in [(game.CLUBS, 1), (game.DIAMONDS, 2), (game.HEARTS, 3), (game.SPADES, 4)]:
                    res = g.try_apply_action(
                        game.Action(type=game.SUIT_STACK_TO_BUILD_STACK_NUM, suit=s, build_stack_dest=dest)
                    )
                    self.assertTrue(res)
                    self.assertTrue(game.is_valid_game_state(g.gs))

            else:
                for s, dest in [(game.CLUBS, 2), (game.DIAMONDS, 1), (game.HEARTS, 4), (game.SPADES, 3)]:
                    res = g.try_apply_action(
                        game.Action(type=game.SUIT_STACK_TO_BUILD_STACK_NUM, suit=s, build_stack_dest=dest)
                    )
                    self.assertTrue(res)
                    self.assertTrue(game.is_valid_game_state(g.gs))

        self.assertEqual(0, g.gs.talon)
        self.assertEqual(0, g.gs.suit_stack)
        self.assertEqual(0, g.gs.build_stacks[0])
        self.assertEqual(0, g.gs.build_stacks[5])
        self.assertEqual(0, g.gs.build_stacks[6])

        self.assertEqual(0, g.gs.build_stacks[1] & game.SUIT_MASK[game.HEARTS])
        self.assertEqual(0, g.gs.build_stacks[2] & game.SUIT_MASK[game.HEARTS])
        self.assertEqual(0, g.gs.build_stacks[1] & game.SUIT_MASK[game.SPADES])
        self.assertEqual(0, g.gs.build_stacks[2] & game.SUIT_MASK[game.SPADES])

        self.assertEqual(0, g.gs.build_stacks[3] & game.SUIT_MASK[game.CLUBS])
        self.assertEqual(0, g.gs.build_stacks[4] & game.SUIT_MASK[game.CLUBS])
        self.assertEqual(0, g.gs.build_stacks[3] & game.SUIT_MASK[game.DIAMONDS])
        self.assertEqual(0, g.gs.build_stacks[4] & game.SUIT_MASK[game.DIAMONDS])

    def test_try_apply_action_BUILD_STACK_NUM_TO_BUILD_STACK_NUM(self):
        g = game.deal_game(is_random=False)

        # Check the desired initial state
        self.assertEqual(game.get_bitmask(game.CLUBS, game.SEVEN), g.gs.build_stacks[6])
        self.assertEqual(game.get_bitmask(game.HEARTS, game.SEVEN), g.gs.build_stacks[5])
        self.assertEqual(game.get_bitmask(game.DIAMONDS, game.EIGHT), g.gs.build_stacks[4])

        # Seven of clubs to seven of hearts - should not work:
        self.assertFalse(
            g.try_apply_action(
                game.Action(
                    type=game.BUILD_STACK_NUM_TO_BUILD_STACK_NUM, build_stack_src=6, build_stack_dest=5
                )
            )
        )
        self.assertTrue(game.is_valid_game_state(g.gs))

        # Seven of hearts to eight of diamonds - should not work
        self.assertFalse(
            g.try_apply_action(
                game.Action(
                    type=game.BUILD_STACK_NUM_TO_BUILD_STACK_NUM, build_stack_src=5, build_stack_dest=4
                )
            )
        )
        self.assertTrue(game.is_valid_game_state(g.gs))

        # Seven of clubs to eight of diamonds - should not
        self.assertTrue(
            g.try_apply_action(
                game.Action(
                    type=game.BUILD_STACK_NUM_TO_BUILD_STACK_NUM, build_stack_src=6, build_stack_dest=4
                )
            )
        )
        self.assertTrue(game.is_valid_game_state(g.gs))

        # Unstack a few from the talon on to one of the red sevens
        self.assertTrue(
            g.try_apply_action(
                # The six
                game.Action(type=game.TALON_TO_BUILD_STACK_NUM, suit=game.SPADES, build_stack_dest=5)
            )
        )
        self.assertTrue(
            g.try_apply_action(
                # The five
                game.Action(type=game.TALON_TO_BUILD_STACK_NUM, suit=game.HEARTS, build_stack_dest=5)
            )
        )
        self.assertTrue(
            g.try_apply_action(
                # The four
                game.Action(type=game.TALON_TO_BUILD_STACK_NUM, suit=game.CLUBS, build_stack_dest=5)
            )
        )
        self.assertTrue(game.is_valid_game_state(g.gs))

        # Now try moving between the build stacks
        self.assertEqual(4, game.bit_count(g.gs.build_stacks[5]))
        self.assertEqual(1, game.bit_count(g.gs.build_stacks[6]))
        self.assertTrue(
            g.try_apply_action(
                game.Action(
                    type=game.BUILD_STACK_NUM_TO_BUILD_STACK_NUM, build_stack_src=5, build_stack_dest=6
                )
            )
        )
        self.assertTrue(game.is_valid_game_state(g.gs))
        self.assertEqual(1, game.bit_count(g.gs.build_stacks[5]))
        self.assertEqual(4, game.bit_count(g.gs.build_stacks[6]))

    def test_get_valid_actions__simple_state(self):
        g = game.deal_game(is_random=False)
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

        self.assertEqual(
            [
                game.Action(game.TO_SUIT_STACK, game.CLUBS),
                game.Action(game.TO_SUIT_STACK, game.DIAMONDS),
                game.Action(game.TO_SUIT_STACK, game.HEARTS),
                game.Action(game.TO_SUIT_STACK, game.SPADES),
                game.Action(game.TALON_TO_BUILD_STACK_NUM, game.CLUBS, build_stack_dest=5),
                game.Action(game.TALON_TO_BUILD_STACK_NUM, game.SPADES, build_stack_dest=5),
                game.Action(game.TALON_TO_BUILD_STACK_NUM, game.DIAMONDS, build_stack_dest=6),
                game.Action(game.TALON_TO_BUILD_STACK_NUM, game.HEARTS, build_stack_dest=6),
            ],
            g.get_valid_actions(),
        )
