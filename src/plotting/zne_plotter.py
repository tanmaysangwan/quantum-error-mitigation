from pathlib import Path

import matplotlib.pyplot as plt


def save_zne_plot(
    noise_factors: list,
    expectation_values: list,
    mitigated_value: float,
    filename: str,
) -> None:

    output_dir = Path("results/figures/mitigated")  # Save inside mitigated figures.
    output_dir.mkdir(parents=True, exist_ok=True)  # Create folder if missing.

    plt.figure(figsize=(6, 4))  # Create a new figure.

    plt.plot(
        noise_factors,
        expectation_values,
        marker="o",
        linewidth=2,
        label="Measured",
    )  # Plot measured expectation values.

    plt.scatter(
        0,
        mitigated_value,
        s=100,
        marker="*",
        label="Extrapolated",
    )  # Plot estimated zero-noise value.

    plt.plot(
        [0] + noise_factors,
        [mitigated_value] + expectation_values,
        linestyle="--",
    )  # Draw extrapolation line.

    plt.xlabel("Noise Scaling Factor")  # X-axis label.
    plt.ylabel("Expectation Value")  # Y-axis label.
    plt.title("Zero Noise Extrapolation")  # Figure title.
    plt.grid(True)  # Show grid.
    plt.legend()  # Show legend.

    plt.savefig(output_dir / f"{filename}_zne_plot.png")  # Save the graph.