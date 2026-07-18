from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

from src.backends.simulator import run_circuit
from src.circuits.bell_state import create_bell_state
from src.noise_models.depolarizing_noise import create_depolarizing_noise_model
from src.plotting.circuit_plotter import save_circuit
from src.plotting.histogram_plotter import save_histogram
from src.mitigation.probabilistic_error_cancellation import (
    apply_pec_correction,
    build_quasi_probability_representation,
    calculate_pec_expectation_value,
)


def _save_pec_comparison_plot(
    ideal_counts: dict,
    noisy_counts: dict,
    mitigated_counts: dict,
    error_probability: float,
    gamma: float,
    filename: str,
) -> None:
    """
    Save a side-by-side bar chart comparing ideal, noisy, and PEC-mitigated counts.

    Each group of bars represents one bitstring outcome. The three bars in each
    group show the ideal probability (blue), noisy probability (red), and the
    PEC-corrected probability (green), making the correction effect immediately visible.
    """

    output_dir = Path("results/figures/mitigated")
    output_dir.mkdir(parents=True, exist_ok=True)

    states = ["00", "01", "10", "11"]

    def to_probs(counts: dict) -> list:
        total = sum(counts.values())
        return [counts.get(s, 0) / total for s in states] if total > 0 else [0] * 4

    ideal_probs     = to_probs(ideal_counts)
    noisy_probs     = to_probs(noisy_counts)
    mitigated_probs = to_probs(mitigated_counts)

    x      = np.arange(len(states))
    width  = 0.25

    fig, ax = plt.subplots(figsize=(10, 6))

    bars_ideal     = ax.bar(x - width, ideal_probs,     width, label="Ideal (no noise)",      color="#2196F3", edgecolor="white")
    bars_noisy     = ax.bar(x,         noisy_probs,     width, label="Noisy",                 color="#F44336", edgecolor="white")
    bars_mitigated = ax.bar(x + width, mitigated_probs, width, label="PEC Mitigated",         color="#4CAF50", edgecolor="white")

    # Annotate bars with probability values.
    for bars, probs in [(bars_ideal, ideal_probs), (bars_noisy, noisy_probs), (bars_mitigated, mitigated_probs)]:
        for bar, prob in zip(bars, probs):
            if prob > 0.01:
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 0.01,
                    f"{prob:.3f}",
                    ha="center", va="bottom",
                    fontsize=8, fontweight="bold",
                )

    # Titles and axis labels.
    ax.set_title(
        "Probabilistic Error Cancellation (PEC) — Bell State Results",
        fontsize=14, fontweight="bold", pad=14,
    )
    ax.set_xlabel(
        "Measured Bitstring Outcome\n"
        "|00⟩ and |11⟩ are the correct Bell state outcomes — "
        "|01⟩ and |10⟩ are errors",
        fontsize=11,
    )
    ax.set_ylabel("Probability of Outcome", fontsize=11)
    ax.set_xticks(x)
    ax.set_xticklabels(
        ["|00⟩\n(correct)", "|01⟩\n(error)", "|10⟩\n(error)", "|11⟩\n(correct)"],
        fontsize=10,
    )
    ax.set_ylim(0, 1.15)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.0%}"))
    ax.grid(axis="y", linestyle="--", alpha=0.4, zorder=0)
    ax.set_axisbelow(True)
    ax.legend(fontsize=10)

    # Sampling overhead annotation.
    ax.annotate(
        f"Depolarizing error rate: {error_probability:.1%}\n"
        f"PEC sampling overhead (γ): ×{gamma:.3f}",
        xy=(0.98, 0.97),
        xycoords="axes fraction",
        ha="right", va="top",
        fontsize=9,
        bbox=dict(boxstyle="round,pad=0.4", facecolor="#FFF9C4", edgecolor="#CCCC00"),
    )

    # Footer explanation.
    fig.text(
        0.5, 0.01,
        "PEC decomposes the noise channel into quasi-probability operations and applies "
        "an analytical correction that cancels the leading noise contribution.",
        ha="center", fontsize=9, color="#555555", style="italic",
    )

    fig.tight_layout(rect=[0, 0.05, 1, 1])
    fig.savefig(output_dir / f"{filename}_pec_comparison.png", dpi=150)
    # Note: do NOT close here — plt.show() in main() displays all open figures.


def main():
    circuit = create_bell_state()  # Build the Bell-state circuit.

    save_circuit(circuit, "bell_state_pec", category="ideal")  # Save circuit diagram.

    # --- Ideal (noiseless) run ---
    ideal_counts = run_circuit(circuit)
    save_histogram(ideal_counts, "bell_state_pec", category="ideal")
    ideal_ev = calculate_pec_expectation_value(ideal_counts)

    # --- Noisy run ---
    error_probability = 0.05
    noise_model  = create_depolarizing_noise_model(error_probability)
    noisy_counts = run_circuit(circuit, noise_model=noise_model)
    save_histogram(noisy_counts, "bell_state_pec", category="noisy")
    noisy_ev = calculate_pec_expectation_value(noisy_counts)

    # --- PEC correction ---
    qpr = build_quasi_probability_representation(error_probability)
    gamma = qpr["gamma"]

    mitigated_counts = apply_pec_correction(noisy_counts, error_probability)
    save_histogram(mitigated_counts, "bell_state_pec", category="mitigated")
    mitigated_ev = calculate_pec_expectation_value(mitigated_counts)

    # --- Comparison plot ---
    _save_pec_comparison_plot(
        ideal_counts,
        noisy_counts,
        mitigated_counts,
        error_probability,
        gamma,
        "bell_state",
    )

    # --- Terminal output ---
    print("=" * 55)
    print("Probabilistic Error Cancellation (PEC) — Bell State")
    print("=" * 55)
    print(f"\nNoise model        : Depolarizing, p = {error_probability:.1%}")
    print(f"Sampling overhead  : γ = {gamma:.4f}  (×{gamma:.2f} more shots needed)")
    print()
    print(f"{'Metric':<30} {'Value':>10}")
    print("-" * 42)
    print(f"{'Ideal <ZZ>':<30} {ideal_ev:>10.4f}")
    print(f"{'Noisy <ZZ>':<30} {noisy_ev:>10.4f}")
    print(f"{'PEC Mitigated <ZZ>':<30} {mitigated_ev:>10.4f}")
    print(f"{'Error before mitigation':<30} {abs(noisy_ev - ideal_ev):>10.4f}")
    print(f"{'Error after mitigation':<30} {abs(mitigated_ev - ideal_ev):>10.4f}")
    reduction = (1 - abs(mitigated_ev - ideal_ev) / max(abs(noisy_ev - ideal_ev), 1e-9)) * 100
    print(f"{'Error reduction':<30} {reduction:>9.1f}%")
    print()
    print("Quasi-probability representation:")
    for op, q in qpr["quasi_probs"].items():
        sign = "+" if q >= 0 else ""
        print(f"  {op}: {sign}{q:.4f}  (sampling prob: {qpr['probabilities'][op]:.4f})")

    print("\nSaved figures:")
    print("  results/figures/ideal/bell_state_pec_circuit.png")
    print("  results/figures/ideal/bell_state_pec_histogram.png")
    print("  results/figures/noisy/bell_state_pec_histogram.png")
    print("  results/figures/mitigated/bell_state_pec_histogram.png")
    print("  results/figures/mitigated/bell_state_pec_comparison.png")

    plt.show()


if __name__ == "__main__":
    main()
