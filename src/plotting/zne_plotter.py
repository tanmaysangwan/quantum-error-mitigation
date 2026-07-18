from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def save_zne_plot(
    noise_factors: list,
    expectation_values: list,
    richardson_estimate: float,
    filename: str,
    linear_estimate: float | None = None,
    ideal_value: float | None = None,
) -> None:
    """
    Save a labelled Zero Noise Extrapolation plot as a PNG.

    The plot shows:
      - Measured <ZZ> expectation values at each noise scaling level
      - The fitted extrapolation line extended back to zero noise
      - The Richardson extrapolated zero-noise estimate (star marker)
      - Optionally the linear estimate and the ideal noiseless reference

    Args:
        noise_factors:        List of noise scaling factors used (e.g. [1, 3, 5]).
        expectation_values:   Measured <ZZ> values at each noise factor.
        richardson_estimate:  Zero-noise estimate from Richardson extrapolation.
        filename:             Base filename (no extension) for the saved PNG.
        linear_estimate:      Optional zero-noise estimate from linear extrapolation.
        ideal_value:          Optional ideal noiseless reference value to plot.
    """

    output_dir = Path("results/figures/mitigated")
    output_dir.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(9, 6))

    # --- Measured data points ---
    ax.plot(
        noise_factors,
        expectation_values,
        marker="o",
        markersize=9,
        linewidth=2,
        color="#F44336",
        label="Measured ⟨ZZ⟩ (noisy circuit)",
        zorder=4,
    )

    # Annotate each measured point.
    for x, y in zip(noise_factors, expectation_values):
        ax.annotate(
            f"{y:.3f}",
            xy=(x, y),
            xytext=(6, 6),
            textcoords="offset points",
            fontsize=9,
            color="#F44336",
        )

    # --- Extrapolation line (extended to x=0) ---
    x_extended = [0] + list(noise_factors)
    y_extended = [richardson_estimate] + list(expectation_values)
    ax.plot(
        x_extended,
        y_extended,
        linestyle="--",
        color="#FF9800",
        linewidth=1.5,
        alpha=0.7,
        label="Extrapolation line",
        zorder=2,
    )

    # --- Richardson zero-noise estimate ---
    ax.scatter(
        0,
        richardson_estimate,
        s=200,
        marker="*",
        color="#4CAF50",
        zorder=5,
        label=f"Richardson estimate at 0× noise: {richardson_estimate:.4f}",
    )

    # --- Optional linear estimate ---
    if linear_estimate is not None:
        ax.scatter(
            0,
            linear_estimate,
            s=120,
            marker="D",
            color="#2196F3",
            zorder=5,
            label=f"Linear estimate at 0× noise: {linear_estimate:.4f}",
        )

    # --- Optional ideal reference line ---
    if ideal_value is not None:
        ax.axhline(
            y=ideal_value,
            color="#9C27B0",
            linestyle=":",
            linewidth=2,
            zorder=1,
            label=f"Ideal noiseless value: {ideal_value:.4f}",
        )

    # --- Vertical line at x=0 (zero noise axis) ---
    ax.axvline(x=0, color="#BBBBBB", linestyle="-", linewidth=1, zorder=1)

    # Titles and labels.
    ax.set_title(
        "Zero Noise Extrapolation (ZNE) — Bell State ⟨ZZ⟩",
        fontsize=14,
        fontweight="bold",
        pad=14,
    )
    ax.set_xlabel(
        "Noise Scaling Factor  (1× = original circuit, 3× and 5× = gate-folded circuits)",
        fontsize=11,
    )
    ax.set_ylabel("⟨ZZ⟩ Expectation Value", fontsize=11)
    ax.set_xticks([0] + list(noise_factors))
    ax.set_xticklabels(["0×\n(target)"] + [f"{f}×" for f in noise_factors])
    ax.grid(linestyle="--", alpha=0.4, zorder=0)
    ax.set_axisbelow(True)
    ax.legend(fontsize=10, loc="lower left")

    # Footer explanation for a lay reader.
    fig.text(
        0.5, 0.01,
        "Each gate in the circuit is repeated to amplify noise deliberately. "
        "The result at zero noise is estimated by extrapolating the trend back to the y-axis.",
        ha="center",
        fontsize=9,
        color="#555555",
        style="italic",
    )

    fig.tight_layout(rect=[0, 0.05, 1, 1])
    fig.savefig(output_dir / f"{filename}_zne_plot.png", dpi=150)
    # Note: do NOT close here — plt.show() in the demo script displays all open figures.
