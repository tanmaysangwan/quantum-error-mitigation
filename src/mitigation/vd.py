from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from src.backends.simulator import run_circuit
from src.circuits.bell_state import create_bell_state
from src.noise_models.depolarizing_noise import create_depolarizing_noise_model
from src.plotting.circuit_plotter import save_circuit
from src.plotting.histogram_plotter import save_histogram
from src.mitigation.probabilistic_error_cancellation import zz_expectation
from src.mitigation.virtual_distillation import run_virtual_distillation


def _save_comparison_plot(
    ideal_ev: float,
    noisy_ev: float,
    mitigated_ev: float,
    error_probability: float,
    filename: str,
) -> None:
    """Save a bar chart comparing ideal, noisy, and VD-mitigated <ZZ> values."""
    output_dir = Path("results/figures/mitigated")
    output_dir.mkdir(parents=True, exist_ok=True)

    labels = ["Ideal", "Noisy", "VD Mitigated"]
    values = [ideal_ev, noisy_ev, mitigated_ev]
    colors = ["#2196F3", "#F44336", "#4CAF50"]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(labels, values, color=colors, edgecolor="white", width=0.4)

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                f"{val:.4f}", ha="center", va="bottom", fontsize=10, fontweight="bold")

    ax.set_title("Virtual Distillation (VD) — Bell State ⟨ZZ⟩",
                 fontsize=14, fontweight="bold", pad=14)
    ax.set_ylabel("⟨ZZ⟩ Expectation Value", fontsize=11)
    ax.set_ylim(0, 1.2)
    ax.axhline(y=ideal_ev, color="#9C27B0", linestyle="--", linewidth=1.2, alpha=0.6, label="Ideal reference")
    ax.grid(axis="y", linestyle="--", alpha=0.4, zorder=0)
    ax.set_axisbelow(True)
    ax.legend(fontsize=10)
    ax.annotate(
        f"Depolarizing p = {error_probability:.1%}",
        xy=(0.98, 0.97), xycoords="axes fraction", ha="right", va="top", fontsize=9,
        bbox=dict(boxstyle="round,pad=0.4", facecolor="#FFF9C4", edgecolor="#CCCC00"),
    )

    fig.tight_layout()
    fig.savefig(output_dir / f"{filename}_vd_comparison.png", dpi=150)


def main():
    circuit = create_bell_state()
    save_circuit(circuit, "bell_state_vd", category="ideal")

    ideal_counts = run_circuit(circuit)
    save_histogram(ideal_counts, "bell_state_vd", category="ideal")
    ideal_ev = zz_expectation(ideal_counts)

    error_probability = 0.05
    noise_model  = create_depolarizing_noise_model(error_probability)
    noisy_counts = run_circuit(circuit, noise_model=noise_model)
    save_histogram(noisy_counts, "bell_state_vd", category="noisy")
    noisy_ev = zz_expectation(noisy_counts)

    # VD uses high shot count for stable probability estimates.
    mitigated_ev = run_virtual_distillation(circuit, noise_model=noise_model, shots=8192)

    _save_comparison_plot(ideal_ev, noisy_ev, mitigated_ev, error_probability, "bell_state")

    print("=" * 55)
    print("Virtual Distillation (VD) — Bell State")
    print("=" * 55)
    print(f"\nNoise model     : Depolarizing, p = {error_probability:.1%}")
    print(f"Shots           : 8192  (high count needed for stable P(s)^2 estimates)")
    print()
    print(f"{'Metric':<30} {'Value':>10}")
    print("-" * 42)
    print(f"{'Ideal <ZZ>':<30} {ideal_ev:>10.4f}")
    print(f"{'Noisy <ZZ>':<30} {noisy_ev:>10.4f}")
    print(f"{'VD Mitigated <ZZ>':<30} {mitigated_ev:>10.4f}")
    print(f"{'Error before mitigation':<30} {abs(noisy_ev - ideal_ev):>10.4f}")
    print(f"{'Error after mitigation':<30} {abs(mitigated_ev - ideal_ev):>10.4f}")
    reduction = (1 - abs(mitigated_ev - ideal_ev) / max(abs(noisy_ev - ideal_ev), 1e-9)) * 100
    print(f"{'Error reduction':<30} {reduction:>9.1f}%")

    plt.show()


if __name__ == "__main__":
    main()
