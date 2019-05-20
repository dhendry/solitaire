from unittest import TestCase

from solitaire_core import game


class GameTes(TestCase):

    def test_get_card_idx(self):
        current_idx = 0
        for r in game.CardRank.values()[1:]:
            for s in game.Suit.values()[1:]:
                self.assertEqual(current_idx, game.get_card_idx(s,r))
                current_idx += 1

