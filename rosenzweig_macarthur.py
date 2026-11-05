from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Callable, Iterable


@dataclass(frozen=True)
class Parameters:
    """Parameters of the modified Lotka-Volterra model."""

    alpha: float = 1.0
    gamma: float = 0.4
    delta: float = 0.5
    carrying_capacity: float = 10.0
    maximum_consumption: float = 1.0
    handling_constant: float = 1.0

    def __post_init__(self) -> None:
        values = (
            self.alpha,
            self.gamma,
            self.delta,
            self.carrying_capacity,
            self.maximum_consumption,
            self.handling_constant,
        )
        if not all(isfinite(value) for value in values):
            raise ValueError("All model parameters must be finite.")
        if any(value < 0 for value in values):
            raise ValueError("Model parameters must be non-negative.")
        if self.carrying_capacity == 0:
            raise ValueError("Carrying capacity must be greater than zero.")
        if self.handling_constant == 0:
            raise ValueError("Handling constant must be greater than zero.")


@dataclass(frozen=True)
class State:
    """Population state at one point in time."""

    time: float
    prey: float
    predator: float


class RosenzweigMacArthurModel:
    """Right-hand side of the Rosenzweig-MacArthur differential equations."""

    def __init__(self, parameters: Parameters | None = None) -> None:
        self.parameters = parameters or Parameters()

    def derivatives(self, prey: float, predator: float) -> tuple[float, float]:
        """Return dx/dt and dy/dt for the current population values."""
        p = self.parameters
        functional_response = (
            p.maximum_consumption * prey / (p.handling_constant + prey)
        )
        prey_growth = p.alpha * prey * (1 - prey / p.carrying_capacity)
        consumption = functional_response * predator
        predator_growth = p.delta * consumption
        predator_death = p.gamma * predator
        return prey_growth - consumption, predator_growth - predator_death


class RungeKutta4Solver:
    """Fixed-step fourth-order Runge-Kutta solver for a two-dimensional system."""

    def __init__(self, derivative: Callable[[float, float], tuple[float, float]]) -> None:
        self._derivative = derivative

    def solve(
        self,
        initial_prey: float,
        initial_predator: float,
        duration: float,
        step: float,
    ) -> list[State]:
        if not all(
            isfinite(value)
            for value in (initial_prey, initial_predator, duration, step)
        ):
            raise ValueError("Initial values, duration, and step must be finite.")
        if initial_prey < 0 or initial_predator < 0:
            raise ValueError("Initial populations must be non-negative.")
        if duration < 0 or step <= 0:
            raise ValueError("Duration must be non-negative and step must be positive.")

        result = [State(0.0, initial_prey, initial_predator)]
        time = 0.0
        prey, predator = initial_prey, initial_predator
        while time < duration:
            current_step = min(step, duration - time)
            prey, predator = self._advance(prey, predator, current_step)
            time += current_step
            result.append(State(time, prey, predator))
        return result

    def _advance(self, prey: float, predator: float, step: float) -> tuple[float, float]:
        k1_prey, k1_predator = self._derivative(prey, predator)
        k2_prey, k2_predator = self._derivative(
            prey + step * k1_prey / 2,
            predator + step * k1_predator / 2,
        )
        k3_prey, k3_predator = self._derivative(
            prey + step * k2_prey / 2,
            predator + step * k2_predator / 2,
        )
        k4_prey, k4_predator = self._derivative(
            prey + step * k3_prey,
            predator + step * k3_predator,
        )
        return (
            prey + step * (k1_prey + 2 * k2_prey + 2 * k3_prey + k4_prey) / 6,
            predator
            + step * (k1_predator + 2 * k2_predator + 2 * k3_predator + k4_predator) / 6,
        )


def simulate(
    parameters: Parameters,
    initial_prey: float,
    initial_predator: float,
    duration: float,
    step: float,
) -> Iterable[State]:
    """Simulate both differential equations and return sampled states."""
    model = RosenzweigMacArthurModel(parameters)
    return RungeKutta4Solver(model.derivatives).solve(
        initial_prey, initial_predator, duration, step
    )
