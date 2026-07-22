"""
qaoa_demo.py

QAOA demo: Max-Cut on a 3-node triangle graph.
Compares ideal vs noisy vs ZNE-mitigated cut values.

Run with:
    python run.py qaoa
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from src.backends.simulator import run_circuit
from src.circuits.qaoa import (
    create_qaoa,
    qaoa_cut_value,
    OPTIMAL_GAMMA,
    OPTIMAL_BETA,
    _DEFAULT_EDGES,
    _DEFAULT_WEIGHTS,
)
from src.noise_models.depolarizing_noise import create_depolarizing_noise_model
from src.plotting.circuit_plotter import save_circuit
from src.plotting.histogram_plotter import save_histogram
from src.mitigation.zero_noise_extrapolation import fold_gates, richardson_extrapolation


def _evaluator(counts: dict) -> float:
    """Cut-value evaluator for ZNE — wraps qaoa_cut_value for the default graph."""
    return qaoa_cut_value(counts, _DEFAULT_EDGES, _DEFAULT_WEIGHTS)


def _zne_mitigate(circuit, noise_model, noise_factors=(1, 3, 5)) -> float:
    """ZNE via circuit folding + Richardson extrapolation on the QAOA cut value."""
    evs = [_evaluator(run_circuit(fold_gates(circuit, sf), noise_model=noise_model))
           for sf in noise_factors]
    return richardson_extrapolation(list(noise_factors), evs)


def _save_comparison_plot(ideal_cut, noisy_cut, zne_cut, error_probability, max_cut=2.0):
    """Bar chart comparing ideal, noisy, and ZNE-mitigated QAOA cut values."""
    output_dir = Path("results/figures/mitigated")
    output_dir.mkdir(parents=True, exist_ok=True)

    labels = ["Ideal", "Noisy", "ZNE Mitigated"]
    values = [ideal_cut, noisy_cut, zne_cut]
    colors = ["#2196F3", "#F44336", "#4CAF50"]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(labels, values, color=colors, edgecolor="white", width=0.4)

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                f"{val:.4f}", ha="center", va="bottom", fontsize=10, fontweight="bold")

    ax.axhline(y=max_cut, color="#9C27B0", linestyle="--", linewidth=1.2, alpha=0.6,
               label=f"Optimal Max-Cut = {max_cut:.0f}")
    ax.set_title("QAOA — Max-Cut on 3-Node Triangle Graph (p=1)",
                 fontsize=13, fontweight="bold", pad=14)
    ax.set_ylabel("Expected Cut Value", fontsize=11)
    ax.set_ylim(0, max_cut * 1.35)
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
                 title="QAOA p=1 — 3-Node Max-Cut Circuit (Ideal)")

    # --- Ideal run ---
    ideal_counts = run_circuit(circuit, shots=4096)
    save_histogram(ideal_counts, "qaoa", category="ideal",
                   title="QAOA — Ideal Measurement Distribution")
    ideal_cut = _evaluator(ideal_counts)

    # --- Noisy run ---
    error_probability = 0.05
    noise_model  = create_depolarizing_noise_model(error_probability)
    noisy_counts = run_circuit(circuit, shots=4096, noise_model=noise_model)
    save_histogram(noisy_counts, "qaoa", category="noisy",
                   title="QAOA — Noisy Measurement Distribution")
    noisy_cut = _evaluator(noisy_counts)

    # --- ZNE mitigation ---
    zne_cut = _zne_mitigate(circuit, noise_model)

    # --- Plot ---
    _save_comparison_plot(ideal_cut, noisy_cut, zne_cut, error_probability)

    # --- Print results ---
    print("\n" + "=" * 55)
    print("QAOA — Max-Cut (3-Node Triangle Graph, p=1)")
    print("=" * 55)
    print(f"\nGraph            : 3 nodes, edges (0-1), (1-2), (0-2)")
    print(f"Optimal Max-Cut  : 2  (any 1-vs-2 node partition)")
    print(f"QAOA angles      : γ = {OPTIMAL_GAMMA:.4f},  β = {OPTIMAL_BETA:.4f}")
    print(f"Noise model      : Depolarizing, p = {error_probability:.1%}")
    print()
    print(f"{'Metric':<32} {'Value':>10}")
    print("-" * 44)
    print(f"{'Ideal cut value':<32} {ideal_cut:>10.4f}")
    print(f"{'Noisy cut value':<32} {noisy_cut:>10.4f}")
    print(f"{'ZNE mitigated cut value':<32} {zne_cut:>10.4f}")
    print(f"{'Error before mitigation':<32} {abs(noisy_cut - ideal_cut):>10.4f}")
    print(f"{'Error after ZNE':<32} {abs(zne_cut - ideal_cut):>10.4f}")
    reduction = (1 - abs(zne_cut - ideal_cut) / max(abs(noisy_cut - ideal_cut), 1e-9)) * 100
    print(f"{'Error reduction':<32} {reduction:>9.1f}%")
    print()
    print("Top 5 bitstring outcomes (ideal):")
    for bs, cnt in sorted(ideal_counts.items(), key=lambda x: -x[1])[:5]:
        print(f"  |{bs}⟩  p = {cnt/sum(ideal_counts.values()):.3f}")

    plt.show()


if __name__ == "__main__":
    main()
