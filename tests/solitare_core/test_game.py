from unittest import TestCase

from solitaire_core import game

import random


def _new_gs():
    return game.deal_game(is_random=False).current_state


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
