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

    def test_action_to_onehot(self):
        seen_vectors = set()
        for i, a in enumerate(game._ALL_ACTIONS):
            # Convert to tuple to make it hashable
            action_onehot = tuple(vectorization.action_to_onehot(a))

            # Convert it back to an action
            self.assertEqual(a, vectorization.onehot_to_action(action_onehot))

            self.assertNotIn(action_onehot, seen_vectors)
            seen_vectors.add(action_onehot)

            for j, elem in enumerate(action_onehot):
                if i == j:
                    self.assertEqual(1, elem)
                else:
                    self.assertEqual(0, elem)

        self.assertEqual(len(seen_vectors), len(game._ALL_ACTIONS))

    def test_action_to_onehot_chooses_greatest(self):
        vec = [0.1 for _ in range(len(game._ALL_ACTIONS))]
        vec[0] = 0.5
        vec[1] = 0.8
        vec[2] = 0.8  # Choose the first
        vec[3] = 0.7

        self.assertEqual(game._ALL_ACTIONS[1], vectorization.onehot_to_action(vec))
