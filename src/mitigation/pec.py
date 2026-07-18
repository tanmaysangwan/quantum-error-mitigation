from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from src.backends.simulator import run_circuit
from src.circuits.bell_state import create_bell_state
from src.noise_models.depolarizing_noise import create_depolarizing_noise_model
from src.plotting.circuit_plotter import save_circuit
from src.plotting.histogram_plotter import save_histogram
from src.mitigation.probabilistic_error_cancellation import (
    build_quasi_probability_representation,
    run_pec,
    zz_expectation,
)


def _save_comparison_plot(
    ideal_counts: dict,
    noisy_counts: dict,
    mitigated_counts: dict,
    error_probability: float,
    gamma: float,
    filename: str,
) -> None:
    """Save a three-bar comparison chart: ideal vs noisy vs PEC-mitigated probabilities."""
    output_dir = Path("results/figures/mitigated")
    output_dir.mkdir(parents=True, exist_ok=True)

    states = ["00", "01", "10", "11"]

    def to_probs(counts):
        total = sum(counts.values())
        return [counts.get(s, 0) / total for s in states] if total > 0 else [0] * 4

    x     = np.arange(len(states))
    width = 0.25
    fig, ax = plt.subplots(figsize=(10, 6))

    for offset, probs, label, color in [
        (-width, to_probs(ideal_counts),     "Ideal", "#2196F3"),
        (0,      to_probs(noisy_counts),     "Noisy", "#F44336"),
        (+width, to_probs(mitigated_counts), "PEC",   "#4CAF50"),
    ]:
        bars = ax.bar(x + offset, probs, width, label=label, color=color, edgecolor="white")
        for bar, prob in zip(bars, probs):
            if prob > 0.01:
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                        f"{prob:.3f}", ha="center", va="bottom", fontsize=8, fontweight="bold")

    ax.set_title("Probabilistic Error Cancellation (PEC) — Bell State", fontsize=14, fontweight="bold", pad=14)
    ax.set_xlabel("Measured Bitstring", fontsize=11)
    ax.set_ylabel("Probability", fontsize=11)
    ax.set_xticks(x)
    ax.set_xticklabels(["|00⟩", "|01⟩", "|10⟩", "|11⟩"], fontsize=10)
    ax.set_ylim(0, 1.15)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.0%}"))
    ax.grid(axis="y", linestyle="--", alpha=0.4, zorder=0)
    ax.set_axisbelow(True)
    ax.legend(fontsize=10)
    ax.annotate(
        f"Depolarizing p = {error_probability:.1%}   |   γ = {gamma:.3f}",
        xy=(0.98, 0.97), xycoords="axes fraction", ha="right", va="top", fontsize=9,
        bbox=dict(boxstyle="round,pad=0.4", facecolor="#FFF9C4", edgecolor="#CCCC00"),
    )

    fig.tight_layout()
    fig.savefig(output_dir / f"{filename}_pec_comparison.png", dpi=150)


def main():
    circuit = create_bell_state()
    save_circuit(circuit, "bell_state_pec", category="ideal")

    ideal_counts = run_circuit(circuit)
    save_histogram(ideal_counts, "bell_state_pec", category="ideal")
    ideal_ev = zz_expectation(ideal_counts)

    error_probability = 0.05
    noise_model  = create_depolarizing_noise_model(error_probability)
    noisy_counts = run_circuit(circuit, noise_model=noise_model)
    save_histogram(noisy_counts, "bell_state_pec", category="noisy")
    noisy_ev = zz_expectation(noisy_counts)

    qpr   = build_quasi_probability_representation(error_probability)
    gamma = qpr["gamma"]

    mitigated_counts = run_pec(
        circuit,
        noise_model=noise_model,
        error_probability=error_probability,
        num_samples=200,
        shots_per_sample=1024,
        seed=42,
    )
    save_histogram(mitigated_counts, "bell_state_pec", category="mitigated")
    mitigated_ev = zz_expectation(mitigated_counts)

    _save_comparison_plot(ideal_counts, noisy_counts, mitigated_counts,
                          error_probability, gamma, "bell_state")

    print("=" * 55)
    print("Probabilistic Error Cancellation (PEC) — Bell State")
    print("=" * 55)
    print(f"\nNoise model        : Depolarizing, p = {error_probability:.1%}")
    print(f"Sampling overhead  : γ = {gamma:.4f}  (×{gamma**3:.2f} samples vs unmitigated)")
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
        print(f"  {op}: {q:+.4f}  (sampling prob: {qpr['probabilities'][op]:.4f})")

    plt.show()


if __name__ == "__main__":
    main()
