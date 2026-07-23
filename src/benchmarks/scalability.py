"""
Scalability analysis.

Runs ZNE and VD on GHZ and QFT circuits for qubit counts 2–8 at a fixed
noise level (5% depolarizing) and plots fidelity vs number of qubits.

Produces: results/figures/comparison/scalability_fidelity.png
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from src.backends.simulator import run_circuit
from src.circuits.ghz import create_ghz_state
from src.circuits.qft import create_qft
from src.metrics.metrics import fidelity
from src.mitigation.virtual_distillation import run_virtual_distillation
from src.mitigation.zero_noise_extrapolation import fold_gates, richardson_extrapolation
from src.noise_models.depolarizing_noise import create_depolarizing_noise_model

QUBIT_COUNTS = list(range(2, 9))   # 2 → 8 qubits
NOISE_LEVEL  = 0.05                # fixed at moderate noise for scalability sweep
OUTPUT_DIR   = Path("results/figures/comparison")

COLORS = {
    ("GHZ", "ZNE"): "#FF9800",
    ("GHZ", "VD"):  "#4CAF50",
    ("QFT", "ZNE"): "#2196F3",
    ("QFT", "VD"):  "#9C27B0",
}


def _ghz_ev(counts: dict, n: int) -> float:
    """GHZ fidelity proxy: P(|0...0>) + P(|1...1>)."""
    total = sum(counts.values())
    return (counts.get("0" * n, 0) + counts.get("1" * n, 0)) / total if total else 0.0


def _qft_ev(counts: dict) -> float:
    """QFT fidelity proxy: P(|0...0>) — concentrates at |000...> for ideal QFT on |+>^n."""
    total = sum(counts.values())
    n     = len(next(iter(counts))) if counts else 1
    return counts.get("0" * n, 0) / total if total else 0.0


def _run_zne(circuit, noise_model, evaluator) -> float:
    evs = [evaluator(run_circuit(fold_gates(circuit, sf), noise_model=noise_model))
           for sf in [1, 3, 5]]
    return richardson_extrapolation([1, 3, 5], evs)


def _run_vd(circuit, noise_model, observable) -> float:
    return run_virtual_distillation(circuit, noise_model=noise_model,
                                    shots=8192, observable=observable)


def run_scalability() -> dict:
    """Return {(circuit, technique): [fidelity per qubit count]}."""
    noise_model = create_depolarizing_noise_model(NOISE_LEVEL)
    results     = {key: [] for key in COLORS}

    for n in QUBIT_COUNTS:
        print(f"  Qubits: {n}")

        # --- GHZ ---
        ghz = create_ghz_state(n)
        ghz_ev     = lambda counts: _ghz_ev(counts, n)
        ghz_obs    = lambda s: 1.0 if s in ("0" * n, "1" * n) else -1.0
        ideal_ghz  = ghz_ev(run_circuit(ghz, shots=8192))

        zne_ghz = _run_zne(ghz, noise_model, ghz_ev)
        vd_ghz  = _run_vd(ghz, noise_model, ghz_obs)
        # VD returns value in [-1,1]; rescale to [0,1]
        vd_ghz  = np.clip((vd_ghz + 1.0) / 2.0, 0.0, 1.0)

        results[("GHZ", "ZNE")].append(fidelity(ideal_ghz, np.clip(zne_ghz, 0.0, 1.0)))
        results[("GHZ", "VD")].append(fidelity(ideal_ghz, vd_ghz))

        # --- QFT ---
        qft = create_qft(n)
        qft_ev    = lambda counts: _qft_ev(counts)
        qft_obs   = lambda s: 1.0 if s == "0" * len(s) else -1.0
        ideal_qft = qft_ev(run_circuit(qft, shots=8192))

        zne_qft = _run_zne(qft, noise_model, qft_ev)
        vd_qft  = _run_vd(qft, noise_model, qft_obs)
        vd_qft  = np.clip((vd_qft + 1.0) / 2.0, 0.0, 1.0)

        results[("QFT", "ZNE")].append(fidelity(ideal_qft, np.clip(zne_qft, 0.0, 1.0)))
        results[("QFT", "VD")].append(fidelity(ideal_qft, vd_qft))

        print(f"    GHZ  ZNE={results[('GHZ','ZNE')][-1]:.3f}  VD={results[('GHZ','VD')][-1]:.3f}")
        print(f"    QFT  ZNE={results[('QFT','ZNE')][-1]:.3f}  VD={results[('QFT','VD')][-1]:.3f}")

    return results


def plot_scalability(results: dict) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    fig, axes = plt.subplots(1, 2, figsize=(13, 5), sharey=True)
    fig.suptitle(f"Scalability: Fidelity vs Qubit Count  (depolarizing p={NOISE_LEVEL:.0%})",
                 fontsize=14, fontweight="bold")

    for ax, circuit_name in zip(axes, ["GHZ", "QFT"]):
        for technique in ["ZNE", "VD"]:
            key = (circuit_name, technique)
            ax.plot(QUBIT_COUNTS, results[key], marker="o", linewidth=2, markersize=7,
                    color=COLORS[key], label=technique)

        ax.set_title(f"{circuit_name} Circuit", fontsize=12, fontweight="bold")
        ax.set_xlabel("Number of Qubits", fontsize=11)
        ax.set_xticks(QUBIT_COUNTS)
        ax.set_ylim(0.0, 1.05)
        ax.axhline(y=1.0, color="#AAAAAA", linestyle="--", linewidth=1)
        ax.grid(linestyle="--", alpha=0.4)
        ax.legend(fontsize=10)

    axes[0].set_ylabel("Fidelity (1 = perfect recovery)", fontsize=11)
    fig.tight_layout()

    out = OUTPUT_DIR / "scalability_fidelity.png"
    fig.savefig(out, dpi=150)
    print(f"  Saved: {out}")


def main():
    print(f"Running scalability analysis (qubits {QUBIT_COUNTS[0]}–{QUBIT_COUNTS[-1]}, "
          f"noise={NOISE_LEVEL:.0%})...")
    results = run_scalability()
    plot_scalability(results)
    plt.show()


if __name__ == "__main__":
    main()
