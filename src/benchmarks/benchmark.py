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


def get_ev(counts: dict, circuit_name: str) -> float:
    """Return the appropriate expectation value metric for each circuit type."""
    total = sum(counts.values())
    if total == 0:
        return 0.0
    if circuit_name == "Bell":
        return zz_expectation(counts)
    if circuit_name == "GHZ-3":
        return (counts.get("000", 0) + counts.get("111", 0)) / total
    if circuit_name == "QFT-3":
        return counts.get("000", 0) / total  # QFT on |+>^3 concentrates at |000>
    return 0.0


def clip_ev(ev: float, circuit_name: str) -> float:
    """Clip expectation value to its valid range for the circuit type."""
    if circuit_name == "Bell":
        return float(np.clip(ev, -1.0, 1.0))
    return float(np.clip(ev, 0.0, 1.0))


def run_mem(circuit, noise_model, circuit_name) -> float:
    """MEM: build readout calibration matrix and correct noisy counts."""
    readout_nm   = create_readout_error_model(0.05)
    noisy_counts = run_circuit(circuit, noise_model=readout_nm)
    cal_matrix, states = build_calibration_matrix(readout_nm, num_qubits=circuit.num_qubits)
    mitigated    = mitigate_counts(noisy_counts, cal_matrix, states=states)
    return get_ev(mitigated, circuit_name)


def run_zne(circuit, noise_model, circuit_name) -> float:
    """ZNE: fold gates at 1x/3x/5x and Richardson-extrapolate to zero noise."""
    evs = [get_ev(run_circuit(fold_gates(circuit, sf), noise_model=noise_model), circuit_name)
           for sf in [1, 3, 5]]
    return richardson_extrapolation([1, 3, 5], evs)


def run_pec_bench(circuit, noise_model, error_probability, circuit_name) -> float:
    """PEC: Mitiq quasi-probability sampling. Falls back to ZNE for non-Bell circuits."""
    if circuit.num_qubits == 2:
        return run_pec(circuit, noise_model, error_probability, num_samples=100, shots=1024)
    # PEC with Mitiq for multi-qubit circuits using local depolarizing representations.
    from qiskit import transpile
    from qiskit_aer import AerSimulator
    from mitiq.pec import execute_with_pec, represent_operations_in_circuit_with_local_depolarizing_noise
    import warnings

    native = transpile(circuit, basis_gates=["rz", "sx", "cx"], optimization_level=0)

    def executor(circ):
        sim = AerSimulator(noise_model=noise_model)
        return get_ev(sim.run(circ, shots=1024).result().get_counts(), circuit_name)

    reps = represent_operations_in_circuit_with_local_depolarizing_noise(
        native, noise_level=error_probability
    )
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        result = execute_with_pec(native, executor, representations=reps, num_samples=50)
    return float(result)


def run_cdr_bench(circuit, noise_model, circuit_name) -> float:
    """CDR: Mitiq training circuit regression."""
    evaluator = lambda counts: get_ev(counts, circuit_name)
    return run_cdr(circuit, noise_model, num_training_circuits=10, shots=1024, evaluator=evaluator)


def run_vd_bench(circuit, noise_model, circuit_name) -> float:
    """VD: squared density matrix estimator Tr(rho^2 * O) / Tr(rho^2)."""
    counts = run_circuit(circuit, shots=8192, noise_model=noise_model)
    total  = sum(counts.values())
    probs  = {s: c / total for s, c in counts.items()}
    denom  = sum(p ** 2 for p in probs.values())
    if denom < 1e-10:
        return 0.0
    if circuit_name == "Bell":
        num = sum((1 if s in ("00", "11") else -1) * p ** 2 for s, p in probs.items())
        return num / denom
    # GHZ-3 and QFT-3: normalise to [0, 1]
    correct = ("000", "111") if circuit_name == "GHZ-3" else ("000",)
    num = sum((1 if s in correct else -1) * p ** 2 for s, p in probs.items())
    return (num / denom + 1.0) / 2.0


def run_dd_bench(circuit, noise_model, circuit_name) -> float:
    """DD: Mitiq XYXY pulse sequences inserted into idle windows."""
    evaluator = lambda counts: get_ev(counts, circuit_name)
    return run_dynamical_decoupling(circuit, noise_model, rule="xyxy",
                                    num_trials=5, shots=2048, evaluator=evaluator)


CIRCUITS    = {"Bell": create_bell_state(), "GHZ-3": create_ghz_state(3), "QFT-3": create_qft(3)}
NOISE_LEVELS = [0.01, 0.05, 0.10, 0.15, 0.20]
TECHNIQUES  = ["MEM", "ZNE", "PEC", "CDR", "VD", "DD"]


def run_benchmark() -> list[dict]:
    """Run all 6 techniques × 3 circuits × 5 noise levels. Returns list of result dicts."""
    results = []

    for circuit_name, circuit in CIRCUITS.items():
        print(f"\nCircuit: {circuit_name}")

        for noise_level in NOISE_LEVELS:
            print(f"  Noise: {noise_level:.0%}")
            noise_model  = create_depolarizing_noise_model(noise_level)
            ideal_ev     = get_ev(run_circuit(circuit, shots=4096), circuit_name)
            noisy_ev     = get_ev(run_circuit(circuit, shots=4096, noise_model=noise_model), circuit_name)

            for technique in TECHNIQUES:
                t_start = time.perf_counter()
                try:
                    if technique == "MEM":
                        mitigated_ev = run_mem(circuit, noise_model, circuit_name)
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

                    mitigated_ev = clip_ev(mitigated_ev, circuit_name)
                except Exception as e:
                    print(f"    {technique}: FAILED — {e}")
                    continue

                runtime = round(time.perf_counter() - t_start, 2)
                row     = summarise(technique, ideal_ev, noisy_ev, mitigated_ev, overhead)
                row["circuit"]     = circuit_name
                row["noise_level"] = noise_level
                row["runtime_s"]   = runtime
                results.append(row)

                print(f"    {technique:<4}  fidelity={row['fidelity']:.4f}  "
                      f"reduction={row['error_reduction_%']:.1f}%  "
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
