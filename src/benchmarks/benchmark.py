"""
Automated benchmarking suite.

Runs all 6 mitigation techniques on Bell, GHZ, and QFT circuits
across 5 noise levels and saves results to results/data/benchmark_results.csv.
"""

import csv
import time
from pathlib import Path

import numpy as np

from src.backends.simulator import run_circuit
from src.circuits.bell_state import create_bell_state
from src.circuits.ghz import create_ghz_state
from src.circuits.qft import create_qft
from src.noise_models.depolarizing_noise import create_depolarizing_noise_model
from src.noise_models.readout_error import create_readout_error_model
from src.metrics.metrics import sampling_overhead, summarise

from src.mitigation.measurement_error_mitigation import build_calibration_matrix, mitigate_counts
from src.mitigation.zero_noise_extrapolation import fold_gates, richardson_extrapolation
from src.mitigation.probabilistic_error_cancellation import (
    build_quasi_probability_representation, run_pec, zz_expectation,
)
from src.mitigation.clifford_data_regression import run_cdr
from src.mitigation.virtual_distillation import run_virtual_distillation
from src.mitigation.dynamical_decoupling import run_dynamical_decoupling


# ── Unified expectation value ──────────────────────────────────────────────────

def population_fidelity(counts_a: dict, counts_b: dict) -> float:
    """Bhattacharyya coefficient between two count distributions. Range [0, 1]."""
    all_states = set(counts_a) | set(counts_b)
    total_a    = sum(counts_a.values())
    total_b    = sum(counts_b.values())
    p_a = {s: counts_a.get(s, 0) / total_a for s in all_states}
    p_b = {s: counts_b.get(s, 0) / total_b for s in all_states}
    return float(sum(np.sqrt(p_a[s] * p_b[s]) for s in all_states))


def get_ev(counts: dict, circuit_name: str) -> float:
    """Return the appropriate expectation value for each circuit type."""
    total = sum(counts.values())
    if circuit_name == "Bell":
        return zz_expectation(counts)
    if circuit_name == "GHZ-3":
        return (counts.get("000", 0) + counts.get("111", 0)) / total
    if circuit_name == "QFT-3":
        # QFT on |+>^3 concentrates output at |000>; use P(000) as the quality metric.
        return counts.get("000", 0) / total
    return 0.0


# ── Per-technique runners returning a single float ─────────────────────────────

def run_mem(circuit, noise_model) -> float | None:
    """MEM: calibration matrix correction. Only valid for 2-qubit Bell circuits."""
    if circuit.num_qubits != 2:
        return None  # MEM calibration is Bell-basis specific
    readout_nm   = create_readout_error_model(0.05)
    noisy_counts = run_circuit(circuit, noise_model=readout_nm)
    cal_matrix   = build_calibration_matrix(readout_nm)
    mitigated    = mitigate_counts(noisy_counts, cal_matrix)
    return zz_expectation(mitigated)


def run_zne(circuit, noise_model, circuit_name) -> float:
    """ZNE: fold gates at 1x/3x/5x and Richardson-extrapolate to zero noise."""
    noise_factors = [1, 3, 5]
    evs = []
    for sf in noise_factors:
        folded = fold_gates(circuit, sf)
        counts = run_circuit(folded, noise_model=noise_model)
        evs.append(get_ev(counts, circuit_name))
    return richardson_extrapolation(noise_factors, evs)


def run_pec_bench(circuit, noise_model, error_probability, circuit_name) -> float:
    """PEC: Monte Carlo quasi-probability sampling (Bell only; others use ZNE fallback)."""
    if circuit.num_qubits > 2:
        return run_zne(circuit, noise_model, circuit_name)  # PEC is 2-qubit specific here
    mitigated_counts = run_pec(circuit, noise_model, error_probability,
                                num_samples=100, shots_per_sample=1024, seed=42)
    return get_ev(mitigated_counts, circuit_name)


def run_cdr_bench(circuit, noise_model, circuit_name) -> float | None:
    """CDR: Mitiq training circuit regression. Only valid for 2-qubit circuits."""
    if circuit.num_qubits != 2:
        return None  # CDR executor returns zz_expectation which is 2-qubit specific
    return run_cdr(circuit, noise_model, num_training_circuits=10, shots=1024)


def run_vd_bench(circuit, noise_model, circuit_name) -> float:
    """VD: squared density matrix estimator, generalised to any circuit type."""
    counts = run_circuit(circuit, shots=8192, noise_model=noise_model)
    total  = sum(counts.values())
    probs  = {s: c / total for s, c in counts.items()}
    denom  = sum(p ** 2 for p in probs.values())
    if denom < 1e-10:
        return 0.0
    if circuit_name == "Bell":
        num = sum((1 if s in ("00", "11") else -1) * p ** 2 for s, p in probs.items())
        return float(np.clip(num / denom, -1.0, 1.0))
    if circuit_name == "GHZ-3":
        num = sum((1 if s in ("000", "111") else -1) * p ** 2 for s, p in probs.items())
        return float(np.clip((num / denom + 1.0) / 2.0, 0.0, 1.0))
    if circuit_name == "QFT-3":
        # Correct state is |000>; boost its squared probability, suppress others.
        num = sum((1 if s == "000" else -1) * p ** 2 for s, p in probs.items())
        return float(np.clip((num / denom + 1.0) / 2.0, 0.0, 1.0))
    return 0.0


def run_dd_bench(circuit, noise_model, circuit_name) -> float | None:
    """DD: Mitiq XYXY pulse sequences. Only valid for 2-qubit circuits."""
    if circuit.num_qubits != 2:
        return None  # DD executor uses zz_expectation which is 2-qubit specific
    return run_dynamical_decoupling(circuit, noise_model, rule="xyxy", num_trials=5, shots=2048)


# ── Main benchmark loop ────────────────────────────────────────────────────────

CIRCUITS = {
    "Bell":  create_bell_state(),
    "GHZ-3": create_ghz_state(3),
    "QFT-3": create_qft(3),
}

NOISE_LEVELS = [0.01, 0.05, 0.10, 0.15, 0.20]

TECHNIQUES = ["MEM", "ZNE", "PEC", "CDR", "VD", "DD"]


def run_benchmark() -> list[dict]:
    """Run all techniques × circuits × noise levels. Returns list of result dicts."""
    results = []

    for circuit_name, circuit in CIRCUITS.items():
        print(f"\n{'='*60}")
        print(f"Circuit: {circuit_name}")
        print(f"{'='*60}")

        for noise_level in NOISE_LEVELS:
            print(f"\n  Noise level: {noise_level:.0%}")
            noise_model = create_depolarizing_noise_model(noise_level)

            ideal_counts = run_circuit(circuit, shots=4096)
            noisy_counts = run_circuit(circuit, shots=4096, noise_model=noise_model)
            ideal_ev     = get_ev(ideal_counts, circuit_name)
            noisy_ev     = get_ev(noisy_counts, circuit_name)

            for technique in TECHNIQUES:
                t_start = time.perf_counter()
                try:
                    if technique == "MEM":
                        mitigated_ev = run_mem(circuit, noise_model)
                        overhead     = sampling_overhead("MEM")
                    elif technique == "ZNE":
                        mitigated_ev = run_zne(circuit, noise_model, circuit_name)
                        overhead     = sampling_overhead("ZNE", num_scale_factors=3)
                    elif technique == "PEC":
                        mitigated_ev = run_pec_bench(circuit, noise_model, noise_level, circuit_name)
                        qpr          = build_quasi_probability_representation(noise_level)
                        overhead     = sampling_overhead("PEC", gamma=qpr["gamma"], n_gates=3)
                    elif technique == "CDR":
                        mitigated_ev = run_cdr_bench(circuit, noise_model, circuit_name)
                        overhead     = sampling_overhead("CDR", num_training_circuits=10)
                    elif technique == "VD":
                        mitigated_ev = run_vd_bench(circuit, noise_model, circuit_name)
                        overhead     = sampling_overhead("VD")
                    elif technique == "DD":
                        mitigated_ev = run_dd_bench(circuit, noise_model, circuit_name)
                        overhead     = sampling_overhead("DD", num_trials=5)
                except Exception as e:
                    print(f"    {technique}: FAILED — {e}")
                    continue

                if mitigated_ev is None:
                    print(f"    {technique:<4}  N/A for {circuit_name}")
                    continue

                runtime = round(time.perf_counter() - t_start, 2)
                row     = summarise(technique, ideal_ev, noisy_ev, mitigated_ev, overhead)
                row["circuit"]      = circuit_name
                row["noise_level"]  = noise_level
                row["runtime_s"]    = runtime
                results.append(row)

                print(f"    {technique:<4}  fidelity={row['fidelity']:.4f}  "
                      f"error_reduction={row['error_reduction_%']:.1f}%  "
                      f"overhead={overhead:.2f}x  time={runtime}s")

    return results


def save_results(results: list[dict]) -> None:
    """Save benchmark results to CSV."""
    output_path = Path("results/data/benchmark_results.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = ["circuit", "noise_level", "technique", "ideal_ev", "noisy_ev",
                  "mitigated_ev", "error_before", "error_after", "error_reduction_%",
                  "fidelity", "sampling_overhead", "runtime_s"]

    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"\nResults saved to {output_path}")


def main():
    results = run_benchmark()
    save_results(results)


if __name__ == "__main__":
    main()
