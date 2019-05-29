import random
from unittest import TestCase

from solitaire_ai import vectorization
from solitaire_core import game


class VectorizationTest(TestCase):
    def test_stack_to_array(self):
        self.assertEqual([0 for _ in range(52)], vectorization._stack_to_array(0))
        self.assertEqual([1 for _ in range(52)], vectorization._stack_to_array(game.ALL_CARDS_MASK))

        for r in game.CardRank.values()[1:]:
            for s in game.Suit.values()[1:]:
                expected_array = [0 for _ in range(52)]
                expected_array[game.get_card_idx(s, r)] = 1
                self.assertEqual(expected_array, vectorization._stack_to_array(game.get_bitmask(s, r)))

    def test_game_state_to_array(self):
        g = game.deal_game(is_random=False)

        # Super basic test - just make sure we get different things each time as we solve the game:
        seen_state_vectors = set()

        # We expect the non-randomized deal to be directly solveable:
        for r in game.CardRank.values()[1:]:
            for s in game.Suit.values()[1:]:
                g.apply_action(game.Action(type=game.TO_SS_S, suit=s))

                # Note lists are unhashable so convert it to a tuple
                state_vector = tuple(vectorization.game_state_to_array(g.gs))
                self.assertNotIn(state_vector, seen_state_vectors)

                seen_state_vectors.add(state_vector)

        self.assertTrue(g.won)
        self.assertTrue(g.won_effectively)

        self.assertEqual(len(g.visited_game_states), len(seen_state_vectors))
