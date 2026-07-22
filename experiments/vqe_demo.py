"""VQE demo: find H2 ground state energy, compare ideal vs noisy vs ZNE-mitigated."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from qiskit_aer.noise import NoiseModel, depolarizing_error

from src.circuits.vqe import H2_EXACT_ENERGY, H2_HAMILTONIAN, run_vqe, evaluate_energy
from src.mitigation.zero_noise_extrapolation import fold_gates, richardson_extrapolation
from qiskit.circuit.library import n_local
from qiskit_aer.primitives import Estimator


def _zne_energy(params, noise_model, noise_factors=(1, 3, 5)):
    """Estimate zero-noise energy using ZNE on the VQE ansatz at fixed params."""
    ansatz = n_local(2, ["ry", "rz"], "cx", reps=1)
    bound  = ansatz.assign_parameters(params)
    evs    = []
    for sf in noise_factors:
        folded    = fold_gates(bound, sf)
        estimator = Estimator(backend_options={"noise_model": noise_model})
        ev        = estimator.run([folded], [H2_HAMILTONIAN], [[]]).result().values[0]
        evs.append(ev)
    return richardson_extrapolation(list(noise_factors), evs)


def main():
    error_probability = 0.05
    noise_model = NoiseModel()
    noise_model.add_all_qubit_quantum_error(depolarizing_error(error_probability, 1), ["ry", "rz"])
    noise_model.add_all_qubit_quantum_error(depolarizing_error(error_probability, 2), ["cx"])

    print("Running ideal VQE (finding optimal parameters)...")
    ideal_energy, optimal_params = run_vqe(noise_model=None, maxiter=200)

    print("Evaluating at optimal params under noise...")
    noisy_energy = evaluate_energy(optimal_params, noise_model=noise_model)

    print("Applying ZNE mitigation...")
    zne_energy = _zne_energy(optimal_params, noise_model)

    print("\n" + "=" * 50)
    print("VQE — H2 Ground State Energy (Hartree)")
    print("=" * 50)
    print(f"{'Exact FCI energy':<28}: {H2_EXACT_ENERGY:.6f}")
    print(f"{'Ideal VQE':<28}: {ideal_energy:.6f}  (error: {abs(ideal_energy-H2_EXACT_ENERGY):.6f})")
    print(f"{'Noisy VQE (p=5%)':<28}: {noisy_energy:.6f}  (error: {abs(noisy_energy-H2_EXACT_ENERGY):.6f})")
    print(f"{'ZNE Mitigated VQE':<28}: {zne_energy:.6f}  (error: {abs(zne_energy-H2_EXACT_ENERGY):.6f})")

    # Bar chart comparison.
    output_dir = Path("results/figures/mitigated")
    output_dir.mkdir(parents=True, exist_ok=True)

    labels = ["Exact", "Ideal VQE", "Noisy VQE", "ZNE Mitigated"]
    values = [H2_EXACT_ENERGY, ideal_energy, noisy_energy, zne_energy]
    colors = ["#9C27B0", "#2196F3", "#F44336", "#4CAF50"]

    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.bar(labels, values, color=colors, edgecolor="white", width=0.45)
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() - 0.03,
                f"{val:.4f}", ha="center", va="top", fontsize=10, fontweight="bold", color="white")

    ax.set_title("VQE — H₂ Ground State Energy Comparison", fontsize=13, fontweight="bold", pad=12)
    ax.set_ylabel("Energy (Hartree)", fontsize=11)
    ax.set_ylim(min(values) - 0.15, max(values) + 0.05)
    ax.axhline(y=H2_EXACT_ENERGY, color="#9C27B0", linestyle="--", linewidth=1.2, alpha=0.6)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    fig.tight_layout()
    fig.savefig(output_dir / "vqe_energy_comparison.png", dpi=150)

    plt.show()


if __name__ == "__main__":
    main()
