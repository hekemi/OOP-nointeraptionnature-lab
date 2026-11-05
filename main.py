from __future__ import annotations

import argparse
import csv
import random
import sys
from pathlib import Path

from plot_results import make_figure
from rosenzweig_macarthur import Parameters, simulate


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Simulate the modified Lotka-Volterra predator-prey model."
    )
    parser.add_argument(
        "--prey",
        type=float,
        default=None,
        help="Initial prey population (random if omitted).",
    )
    parser.add_argument(
        "--predator",
        type=float,
        default=None,
        help="Initial predator population (random if omitted).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducible initial populations.",
    )
    parser.add_argument("--duration", type=float, default=50.0, help="Simulation duration.")
    parser.add_argument("--step", type=float, default=0.05, help="Integration step.")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/simulation.csv"),
        help="CSV file for simulation results.",
    )
    parser.add_argument(
        "--plot-output",
        type=Path,
        default=Path("results/simulation.png"),
        help="PNG file for the generated plots.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    generator = random.Random(args.seed)
    prey = args.prey if args.prey is not None else generator.uniform(2.0, 8.0)
    predator = (
        args.predator if args.predator is not None else generator.uniform(0.8, 3.5)
    )
    try:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        states = simulate(
            Parameters(),
            prey,
            predator,
            args.duration,
            args.step,
        )
        with args.output.open("w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(("time", "prey", "predator"))
            writer.writerows((state.time, state.prey, state.predator) for state in states)
        make_figure(args.output, args.plot_output)
    except (OSError, ValueError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 1
    print(f"Результаты сохранены в {args.output}")
    print(f"Графики сохранены в {args.plot_output}")
    print(f"Начальные условия: x(0)={prey:.3f}, y(0)={predator:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
