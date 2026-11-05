import math
import unittest

from rosenzweig_macarthur import Parameters, RosenzweigMacArthurModel, simulate


class RosenzweigMacArthurTests(unittest.TestCase):
    def test_derivatives_match_the_two_differential_equations(self):
        parameters = Parameters(
            alpha=2,
            gamma=0.5,
            delta=0.25,
            carrying_capacity=10,
            maximum_consumption=3,
            handling_constant=2,
        )
        prey, predator = 4, 1.5
        expected_consumption = 3 * prey * predator / (2 + prey)
        expected_prey = 2 * prey * (1 - prey / 10) - expected_consumption
        expected_predator = 0.25 * expected_consumption - 0.5 * predator

        actual = RosenzweigMacArthurModel(parameters).derivatives(prey, predator)

        self.assertAlmostEqual(actual[0], expected_prey)
        self.assertAlmostEqual(actual[1], expected_predator)

    def test_zero_populations_remain_zero(self):
        states = list(simulate(Parameters(), 0, 0, duration=2, step=0.1))
        self.assertTrue(all(state.prey == 0 and state.predator == 0 for state in states))

    def test_solver_reaches_requested_duration(self):
        states = list(simulate(Parameters(), 4, 1.5, duration=1, step=0.3))
        self.assertEqual(len(states), 5)
        self.assertTrue(math.isclose(states[-1].time, 1))

    def test_invalid_initial_population_is_rejected(self):
        with self.assertRaises(ValueError):
            simulate(Parameters(), -1, 1, duration=1, step=0.1)


if __name__ == "__main__":
    unittest.main()
