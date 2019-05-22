from unittest import TestCase

from solitaire_core import game

import random


def _new_gs():
    return game.deal_game(is_random=False).gs


class GameTes(TestCase):
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
        self.assertFalse(g.try_apply_action(
            game.Action(type=game.TALON_TO_BUILD_STACK_NUM, suit=game.SPADES, build_stack_dest=1)
        ))
        self.assertFalse(g.try_apply_action(
            game.Action(type=game.TALON_TO_BUILD_STACK_NUM, suit=game.HEARTS, build_stack_dest=3)
        ))
        self.assertFalse(g.try_apply_action(
            game.Action(type=game.TALON_TO_BUILD_STACK_NUM, suit=game.CLUBS, build_stack_dest=6)
        ))

        # Setup build stack 6 (root card being the 7 of clubs)
        for _ in range(3):
            self.assertTrue(g.try_apply_action(
                game.Action(type=game.TALON_TO_BUILD_STACK_NUM, suit=game.HEARTS, build_stack_dest=6)
            ))
            self.assertTrue(game.is_valid_game_state(g.gs))
            self.assertFalse(g.try_apply_action(
                game.Action(type=game.TALON_TO_BUILD_STACK_NUM, suit=game.HEARTS, build_stack_dest=6)
            ))
            self.assertFalse(g.try_apply_action(
                game.Action(type=game.TALON_TO_BUILD_STACK_NUM, suit=game.DIAMONDS, build_stack_dest=6)
            ))

            self.assertTrue(g.try_apply_action(
                game.Action(type=game.TALON_TO_BUILD_STACK_NUM, suit=game.CLUBS, build_stack_dest=6)
            ))
            self.assertTrue(game.is_valid_game_state(g.gs))
            self.assertFalse(g.try_apply_action(
                game.Action(type=game.TALON_TO_BUILD_STACK_NUM, suit=game.CLUBS, build_stack_dest=6)
            ))
            self.assertFalse(g.try_apply_action(
                game.Action(type=game.TALON_TO_BUILD_STACK_NUM, suit=game.SPADES, build_stack_dest=6)
            ))

        self.assertFalse(g.try_apply_action(
            game.Action(type=game.TALON_TO_BUILD_STACK_NUM, suit=game.HEARTS, build_stack_dest=6)
        ))
        self.assertTrue(game.is_valid_game_state(g.gs))
