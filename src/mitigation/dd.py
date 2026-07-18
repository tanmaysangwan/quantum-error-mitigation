from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from src.backends.simulator import run_circuit
from src.circuits.bell_state import create_bell_state
from src.noise_models.depolarizing_noise import create_depolarizing_noise_model
from src.plotting.circuit_plotter import save_circuit
from src.plotting.histogram_plotter import save_histogram
from src.mitigation.probabilistic_error_cancellation import zz_expectation
from src.mitigation.dynamical_decoupling import run_dynamical_decoupling


def _save_comparison_plot(
    ideal_ev: float,
    noisy_ev: float,
    mitigated_xx: float,
    mitigated_xyxy: float,
    error_probability: float,
    filename: str,
) -> None:
    """Save a bar chart comparing ideal, noisy, DD-XX, and DD-XYXY <ZZ> values."""
    output_dir = Path("results/figures/mitigated")
    output_dir.mkdir(parents=True, exist_ok=True)

    labels = ["Ideal", "Noisy", "DD (XX)", "DD (XYXY)"]
    values = [ideal_ev, noisy_ev, mitigated_xx, mitigated_xyxy]
    colors = ["#2196F3", "#F44336", "#FF9800", "#4CAF50"]

    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.bar(labels, values, color=colors, edgecolor="white", width=0.4)

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                f"{val:.4f}", ha="center", va="bottom", fontsize=10, fontweight="bold")

    ax.set_title("Dynamical Decoupling (DD) — Bell State ⟨ZZ⟩",
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
    fig.savefig(output_dir / f"{filename}_dd_comparison.png", dpi=150)


def main():
    circuit = create_bell_state()
    save_circuit(circuit, "bell_state_dd", category="ideal")

    ideal_counts = run_circuit(circuit)
    save_histogram(ideal_counts, "bell_state_dd", category="ideal")
    ideal_ev = zz_expectation(ideal_counts)

    error_probability = 0.05
    noise_model  = create_depolarizing_noise_model(error_probability)
    noisy_counts = run_circuit(circuit, noise_model=noise_model)
    save_histogram(noisy_counts, "bell_state_dd", category="noisy")
    noisy_ev = zz_expectation(noisy_counts)

    mitigated_xx   = run_dynamical_decoupling(circuit, noise_model, rule="xx",   num_trials=10, shots=2048)
    mitigated_xyxy = run_dynamical_decoupling(circuit, noise_model, rule="xyxy", num_trials=10, shots=2048)

    _save_comparison_plot(ideal_ev, noisy_ev, mitigated_xx, mitigated_xyxy,
                          error_probability, "bell_state")

    print("=" * 55)
    print("Dynamical Decoupling (DD) — Bell State")
    print("=" * 55)
    print(f"\nNoise model     : Depolarizing, p = {error_probability:.1%}")
    print(f"Trials          : 10  (averaged over multiple DD insertions)")
    print()
    print(f"{'Metric':<30} {'Value':>10}")
    print("-" * 42)
    print(f"{'Ideal <ZZ>':<30} {ideal_ev:>10.4f}")
    print(f"{'Noisy <ZZ>':<30} {noisy_ev:>10.4f}")
    print(f"{'DD XX Mitigated <ZZ>':<30} {mitigated_xx:>10.4f}")
    print(f"{'DD XYXY Mitigated <ZZ>':<30} {mitigated_xyxy:>10.4f}")
    print(f"{'Error before mitigation':<30} {abs(noisy_ev - ideal_ev):>10.4f}")
    print(f"{'Error after (XX)':<30} {abs(mitigated_xx - ideal_ev):>10.4f}")
    print(f"{'Error after (XYXY)':<30} {abs(mitigated_xyxy - ideal_ev):>10.4f}")

    plt.show()


if __name__ == "__main__":
    main()
