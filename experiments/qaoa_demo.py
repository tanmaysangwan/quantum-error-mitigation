"""
qaoa_demo.py

QAOA demo: Max-Cut on a 4-node cycle graph (C4).
Compares ideal vs noisy vs ZNE-mitigated cut values.

Graph: C4 cycle  0-1-2-3-0
  - Max-Cut = 4   (alternating partition: {0,2} vs {1,3})
  - Random baseline = 2.0
  - p=1 QAOA achieves ~3.0 at optimal angles (75% of max)

Run with:
    python run.py qaoa
"""

from pathlib import Path

import matplotlib.pyplot as plt

from src.backends.simulator import run_circuit
from src.circuits.qaoa import (
    create_qaoa,
    qaoa_cut_value,
    OPTIMAL_GAMMA,
    OPTIMAL_BETA,
)
from src.noise_models.depolarizing_noise import create_depolarizing_noise_model
from src.plotting.circuit_plotter import save_circuit
from src.plotting.histogram_plotter import save_histogram
from src.mitigation.zero_noise_extrapolation import fold_gates, richardson_extrapolation

# Max-Cut for the C4 cycle graph.
MAX_CUT        = 4.0
RANDOM_BASELINE = 2.0   # expected cut for a uniformly random bitstring on C4


def _zne_mitigate(circuit, noise_model, noise_factors=(1, 3, 5)) -> float:
    """ZNE via circuit folding + Richardson extrapolation on the QAOA cut value."""
    evs = [qaoa_cut_value(run_circuit(fold_gates(circuit, sf), noise_model=noise_model))
           for sf in noise_factors]
    return richardson_extrapolation(list(noise_factors), evs)


def _save_comparison_plot(ideal_cut, noisy_cut, zne_cut, error_probability):
    """Bar chart comparing ideal, noisy, and ZNE-mitigated QAOA cut values."""
    output_dir = Path("results/figures/mitigated")
    output_dir.mkdir(parents=True, exist_ok=True)

    labels = ["Ideal", "Noisy", "ZNE Mitigated"]
    values = [ideal_cut, noisy_cut, zne_cut]
    colors = ["#2196F3", "#F44336", "#4CAF50"]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(labels, values, color=colors, edgecolor="white", width=0.4)

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02,
                f"{val:.4f}", ha="center", va="bottom", fontsize=10, fontweight="bold")

    # Reference lines.
    ax.axhline(y=MAX_CUT, color="#9C27B0", linestyle="--", linewidth=1.2, alpha=0.7,
               label=f"Optimal Max-Cut = {MAX_CUT:.0f}")
    ax.axhline(y=RANDOM_BASELINE, color="#FF9800", linestyle=":", linewidth=1.2, alpha=0.7,
               label=f"Random baseline = {RANDOM_BASELINE:.0f}")

    ax.set_title("QAOA — Max-Cut on 4-Node Cycle Graph C4 (p=1)",
                 fontsize=13, fontweight="bold", pad=14)
    ax.set_ylabel("Expected Cut Value", fontsize=11)
    ax.set_ylim(0, MAX_CUT * 1.3)
    ax.grid(axis="y", linestyle="--", alpha=0.4, zorder=0)
    ax.set_axisbelow(True)
    ax.legend(fontsize=10)
    ax.annotate(
        f"Depolarizing p = {error_probability:.1%}  |  γ = {OPTIMAL_GAMMA:.4f}  |  β = {OPTIMAL_BETA:.4f}",
        xy=(0.98, 0.97), xycoords="axes fraction", ha="right", va="top", fontsize=9,
        bbox=dict(boxstyle="round,pad=0.4", facecolor="#FFF9C4", edgecolor="#CCCC00"),
    )

    fig.tight_layout()
    fig.savefig(output_dir / "qaoa_cut_comparison.png", dpi=150)
    print("  Saved: results/figures/mitigated/qaoa_cut_comparison.png")


def main():
    circuit = create_qaoa()

    save_circuit(circuit, "qaoa", category="ideal",
                 title="QAOA p=1 — C4 Max-Cut Circuit (Ideal)")

    # --- Ideal run ---
    ideal_counts = run_circuit(circuit, shots=8192)
    save_histogram(ideal_counts, "qaoa", category="ideal",
                   title="QAOA — Ideal Measurement Distribution (C4)")
    ideal_cut = qaoa_cut_value(ideal_counts)

    # --- Noisy run ---
    error_probability = 0.05
    noise_model  = create_depolarizing_noise_model(error_probability)
    noisy_counts = run_circuit(circuit, shots=8192, noise_model=noise_model)
    save_histogram(noisy_counts, "qaoa", category="noisy",
                   title="QAOA — Noisy Measurement Distribution (C4)")
    noisy_cut = qaoa_cut_value(noisy_counts)

    # --- ZNE mitigation ---
    zne_cut = _zne_mitigate(circuit, noise_model)

    # --- Plot ---
    _save_comparison_plot(ideal_cut, noisy_cut, zne_cut, error_probability)

    # --- Print results ---
    print("\n" + "=" * 58)
    print("QAOA — Max-Cut (4-Node Cycle C4, p=1)")
    print("=" * 58)
    print(f"\nGraph             : 4 nodes, cycle 0-1-2-3-0")
    print(f"Optimal Max-Cut   : {MAX_CUT:.0f}  (partition {{0,2}} vs {{1,3}})")
    print(f"Random baseline   : {RANDOM_BASELINE:.1f}  (uniform random bitstring)")
    print(f"QAOA p=1 achieves : ~3.0  (75% of optimal at best angles)")
    print(f"QAOA angles       : γ = {OPTIMAL_GAMMA:.4f},  β = {OPTIMAL_BETA:.4f}")
    print(f"Noise model       : Depolarizing, p = {error_probability:.1%}")
    print()
    print(f"{'Metric':<36} {'Value':>10}")
    print("-" * 48)
    print(f"{'Ideal cut value':<36} {ideal_cut:>10.4f}")
    print(f"{'Noisy cut value':<36} {noisy_cut:>10.4f}")
    print(f"{'ZNE mitigated cut value':<36} {zne_cut:>10.4f}")
    print(f"{'Error before mitigation':<36} {abs(noisy_cut - ideal_cut):>10.4f}")
    print(f"{'Error after ZNE':<36} {abs(zne_cut - ideal_cut):>10.4f}")
    reduction = (1 - abs(zne_cut - ideal_cut) / max(abs(noisy_cut - ideal_cut), 1e-9)) * 100
    print(f"{'Error reduction':<36} {reduction:>9.1f}%")
    print()
    print("Top 5 bitstring outcomes (ideal):")
    for bs, cnt in sorted(ideal_counts.items(), key=lambda x: -x[1])[:5]:
        print(f"  |{bs}⟩  p = {cnt/sum(ideal_counts.values()):.3f}")
    print("\nNote: |0101⟩ and |1010⟩ are the Max-Cut solutions for C4.")

    plt.show()


if __name__ == "__main__":
    main()
