"""Build publication-style plots for the Rosenzweig-MacArthur simulation."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from rosenzweig_macarthur import Parameters


def read_results(path: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    with path.open(newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))
    if not rows:
        raise ValueError(f"Файл {path} не содержит результатов симуляции.")
    try:
        time = np.asarray([float(row["time"]) for row in rows])
        prey = np.asarray([float(row["prey"]) for row in rows])
        predator = np.asarray([float(row["predator"]) for row in rows])
        return time, prey, predator
    except (KeyError, ValueError) as error:
        raise ValueError("CSV должен содержать колонки time, prey, predator.") from error


def make_figure(
    results_path: Path,
    output_path: Path,
    parameters: Parameters | None = None,
) -> None:
    time, prey, predator = read_results(results_path)
    parameters = parameters or Parameters()
    response_x = np.linspace(0, parameters.carrying_capacity * 1.15, 400)
    response_y = (
        parameters.maximum_consumption
        * response_x
        / (parameters.handling_constant + response_x)
    )

    plt.style.use("seaborn-v0_8-whitegrid")
    figure, axes = plt.subplots(2, 2, figsize=(14, 9), constrained_layout=True)
    figure.patch.set_facecolor("#f8fafc")
    for axis in axes.flat:
        axis.set_facecolor("#ffffff")
        axis.grid(True, color="#dbe4ee", linewidth=0.8)
        axis.spines[["top", "right"]].set_visible(False)

    axes[0, 0].plot(time, prey, color="#1976d2", linewidth=2.4, label="Жертвы x(t)")
    axes[0, 0].plot(
        time, predator, color="#d32f2f", linewidth=2.4, label="Хищники y(t)"
    )
    axes[0, 0].set_title("Динамика численности", fontweight="bold")
    axes[0, 0].set_xlabel("Время t")
    axes[0, 0].set_ylabel("Численность")
    axes[0, 0].legend(frameon=True, facecolor="white")

    axes[0, 1].plot(
        prey,
        predator,
        color="#7b1fa2",
        linewidth=2.2,
        label="Траектория системы",
    )
    axes[0, 1].scatter(
        prey[0], predator[0], color="#2e7d32", s=70, zorder=3, label="Начало"
    )
    axes[0, 1].scatter(
        prey[-1], predator[-1], color="#f57c00", s=70, zorder=3, label="Конец"
    )
    axes[0, 1].set_title("Фазовый портрет", fontweight="bold")
    axes[0, 1].set_xlabel("Жертвы x")
    axes[0, 1].set_ylabel("Хищники y")
    axes[0, 1].legend(frameon=True, facecolor="white")

    axes[1, 0].plot(response_x, response_y, color="#00897b", linewidth=2.5)
    axes[1, 0].fill_between(response_x, response_y, alpha=0.12, color="#00897b")
    axes[1, 0].axhline(
        parameters.maximum_consumption,
        color="#607d8b",
        linestyle="--",
        linewidth=1.2,
        label="Насыщение m",
    )
    axes[1, 0].set_title("Функция отклика Холлинга II", fontweight="bold")
    axes[1, 0].set_xlabel("Плотность жертв x")
    axes[1, 0].set_ylabel("Скорость потребления")
    axes[1, 0].legend(frameon=True, facecolor="white")

    axes[1, 1].axis("off")
    axes[1, 1].text(
        0.05,
        0.9,
        "Модель Розенцвейга–Макартура",
        fontsize=15,
        fontweight="bold",
        color="#263238",
    )
    axes[1, 1].text(
        0.05,
        0.72,
        "dx/dt = αx(1 − x/K) − mxy/(a + x)\n"
        "dy/dt = δmxy/(a + x) − γy",
        fontsize=13,
        linespacing=1.8,
        color="#37474f",
    )
    axes[1, 1].text(
        0.05,
        0.35,
        "Синим показаны жертвы,\nкрасным — хищники.\n"
        "Фиолетовая линия — движение\nсистемы в фазовом пространстве.",
        fontsize=12,
        linespacing=1.6,
        color="#546e7a",
    )

    figure.suptitle(
        "Модифицированная модель хищник–жертва",
        fontsize=20,
        fontweight="bold",
        color="#102a43",
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path, dpi=180, facecolor=figure.get_facecolor())
    plt.close(figure)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("simulation.csv"))
    parser.add_argument("--output", type=Path, default=Path("simulation.png"))
    args = parser.parse_args()
    make_figure(args.input, args.output)
    print(f"Графики сохранены в {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
