from pathlib import Path

from qiskit.visualization import plot_histogram


def save_histogram(counts: dict, filename: str) -> None:
    output_dir = Path("results/figures")
    output_dir.mkdir(parents=True, exist_ok=True)

    figure = plot_histogram(counts)
    figure.savefig(output_dir / f"{filename}_histogram.png")