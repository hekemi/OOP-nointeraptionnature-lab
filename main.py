from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

from plot_results import make_figure
from rosenzweig_macarthur import Parameters, simulate


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Simulate the modified Lotka-Volterra predator-prey model."
    )
    parser.add_argument("--prey", type=float, default=4.0, help="Initial prey population.")
    parser.add_argument(
        "--predator", type=float, default=1.5, help="Initial predator population."
    )
    parser.add_argument("--duration", type=float, default=50.0, help="Simulation duration.")
    parser.add_argument("--step", type=float, default=0.05, help="Integration step.")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("simulation.csv"),
        help="CSV file for simulation results.",
    )
    parser.add_argument(
        "--plot-output",
        type=Path,
        default=Path("simulation.png"),
        help="PNG file for the generated plots.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        states = simulate(
            Parameters(),
            args.prey,
            args.predator,
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
