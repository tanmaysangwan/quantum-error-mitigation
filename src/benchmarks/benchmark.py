import csv
import time
from pathlib import Path

import numpy as np

from src.backends.simulator import run_circuit
from src.circuits.bell_state import create_bell_state
from src.circuits.ghz import create_ghz_state
from src.circuits.qft import create_qft
from src.circuits.qaoa import create_qaoa, qaoa_cut_value
from src.circuits.vqe import H2_EXACT_ENERGY, run_vqe, evaluate_energy, build_vqe_circuit
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

# VQE energy range for normalised fidelity: [noisy_floor, ideal_energy].
# Energies are negative (hartree), so we normalise to [0,1] for consistent metrics.
_VQE_ENERGY_RANGE = abs(H2_EXACT_ENERGY)  # ~1.857 — used to scale errors


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
    if circuit_name == "QAOA-C4":
        return qaoa_cut_value(counts)        # expected cut value in [0, 4]
    return 0.0


def clip_ev(ev: float, circuit_name: str) -> float:
    """Clip expectation value to its valid range for the circuit type."""
    if circuit_name == "Bell":
        return float(np.clip(ev, -1.0, 1.0))
    if circuit_name == "QAOA-C4":
        return float(np.clip(ev, 0.0, 4.0))
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
    """PEC: Mitiq quasi-probability sampling with the correct observable per circuit type."""
    evaluator   = lambda counts: get_ev(counts, circuit_name)
    ev_range    = (-1.0, 1.0) if circuit_name == "Bell" else (0.0, 4.0) if circuit_name == "QAOA-C4" else (0.0, 1.0)
    return run_pec(
        circuit, noise_model, error_probability,
        num_samples=100, shots=1024,
        evaluator=evaluator,
        result_range=ev_range,
    )


def run_cdr_bench(circuit, noise_model, circuit_name) -> float:
    """CDR: Mitiq training circuit regression with the correct observable per circuit type.

    Note: CDR performs poorly on QAOA because the circuit uses heavily non-Clifford
    angles (optimal gamma/beta). Near-Clifford training circuits do not approximate
    the QAOA cost landscape well. We use more training circuits (20) to compensate,
    and clip the output to the valid observable range.
    """
    evaluator = lambda counts: get_ev(counts, circuit_name)
    n_training = 20 if circuit_name == "QAOA-C4" else 10
    result = run_cdr(
        circuit, noise_model,
        num_training_circuits=n_training,
        shots=1024,
        evaluator=evaluator,
    )
    # Clip to valid observable range to prevent wild extrapolation.
    if circuit_name == "QAOA-C4":
        return float(np.clip(result, 0.0, 4.0))
    if circuit_name == "Bell":
        return float(np.clip(result, -1.0, 1.0))
    return float(np.clip(result, 0.0, 1.0))


def run_vd_bench(circuit, noise_model, circuit_name) -> float:
    """VD: squared density matrix estimator Tr(rho^2 * O) / Tr(rho^2) with a circuit-aware observable."""
    if circuit_name == "Bell":
        observable = lambda s: 1.0 if s in ("00", "11") else -1.0
    elif circuit_name == "GHZ-3":
        observable = lambda s: 1.0 if s in ("000", "111") else -1.0
        # GHZ VD returns a value in [-1, 1]; rescale to [0, 1] (probability of correct state)
        raw = run_virtual_distillation(circuit, noise_model=noise_model, shots=8192, observable=observable)
        return (raw + 1.0) / 2.0
    elif circuit_name == "QFT-3":
        observable = lambda s: 1.0 if s == "000" else -1.0
        raw = run_virtual_distillation(circuit, noise_model=noise_model, shots=8192, observable=observable)
        return (raw + 1.0) / 2.0
    elif circuit_name == "QAOA-C4":
        # Observable is the direct cut value per bitstring — range [0, 4].
        observable = lambda s: qaoa_cut_value({s: 1})
    else:
        observable = None

    return run_virtual_distillation(circuit, noise_model=noise_model, shots=8192, observable=observable)


def run_dd_bench(circuit, noise_model, circuit_name) -> float:
    """DD: Mitiq XYXY pulse sequences inserted into idle windows."""
    evaluator = lambda counts: get_ev(counts, circuit_name)
    return run_dynamical_decoupling(circuit, noise_model, rule="xyxy",
                                    num_trials=5, shots=2048, evaluator=evaluator)



def _vqe_fidelity(energy: float) -> float:
    """Normalised fidelity for VQE: 1 - |energy - exact| / |exact|. Clipped to [0,1]."""
    return float(np.clip(1.0 - abs(energy - H2_EXACT_ENERGY) / _VQE_ENERGY_RANGE, 0.0, 1.0))


def _vqe_zz(counts: dict) -> float:
    """<ZZ> observable for the VQE ansatz counts — proxy for the dominant Hamiltonian term."""
    return zz_expectation(counts)


def run_vqe_benchmark(noise_level: float) -> list[dict]:
    """Run VQE benchmark across all applicable techniques.

    Technique applicability:
      ZNE  — Estimator + circuit folding (exact energy estimate)
      MEM  — counts-based via bound ansatz circuit
      CDR  — counts-based via bound ansatz circuit
      VD   — counts-based via bound ansatz circuit
      DD   — counts-based via bound ansatz circuit
      PEC  — NOT applicable: requires per-gate noise representations for
             arbitrary rotation angles, which are not available for the
             COBYLA-optimised VQE ansatz parameters.
    """
    from qiskit_aer.noise import NoiseModel, depolarizing_error
    from qiskit.circuit.library import n_local

    nm = NoiseModel()
    nm.add_all_qubit_quantum_error(depolarizing_error(noise_level, 1), ["ry", "rz"])
    nm.add_all_qubit_quantum_error(depolarizing_error(noise_level, 2), ["cx"])

    ideal_energy, optimal_params = run_vqe(noise_model=None, maxiter=200)
    noisy_energy = evaluate_energy(optimal_params, noise_model=nm)

    # Counts circuit: bound ansatz with measurements for MEM/CDR/VD/DD.
    counts_circuit = build_vqe_circuit(optimal_params)
    ideal_zz   = _vqe_zz(run_circuit(counts_circuit, shots=4096))
    noisy_zz   = _vqe_zz(run_circuit(counts_circuit, shots=4096, noise_model=nm))

    results = []

    # --- ZNE via Estimator (energy-based) ---
    t0 = time.perf_counter()
    try:
        ansatz = n_local(2, ["ry", "rz"], "cx", reps=1)
        bound  = ansatz.assign_parameters(optimal_params)
        from qiskit_aer.primitives import Estimator as AerEstimator
        from src.circuits.vqe import H2_HAMILTONIAN
        evs = []
        for sf in [1, 3, 5]:
            folded    = fold_gates(bound, sf)
            estimator = AerEstimator(backend_options={"noise_model": nm})
            evs.append(estimator.run([folded], [H2_HAMILTONIAN], [[]]).result().values[0])
        mitigated_energy = richardson_extrapolation([1, 3, 5], evs)
        runtime = round(time.perf_counter() - t0, 2)
        row = {
            "circuit": "VQE", "noise_level": noise_level, "technique": "ZNE",
            "ideal_ev":          round(ideal_energy, 4),
            "noisy_ev":          round(noisy_energy, 4),
            "mitigated_ev":      round(mitigated_energy, 4),
            "error_before":      round(abs(noisy_energy - ideal_energy), 4),
            "error_after":       round(abs(mitigated_energy - ideal_energy), 4),
            "error_reduction_%": round((1 - abs(mitigated_energy - ideal_energy) /
                                        max(abs(noisy_energy - ideal_energy), 1e-9)) * 100, 1),
            "fidelity":          round(_vqe_fidelity(mitigated_energy), 4),
            "sampling_overhead": round(sampling_overhead("ZNE", num_scale_factors=3), 3),
            "runtime_s":         runtime,
        }
        results.append(row)
        print(f"    ZNE   ideal={ideal_energy:.4f}  noisy={noisy_energy:.4f}  "
              f"mitigated={mitigated_energy:.4f}  reduction={row['error_reduction_%']:.1f}%")
    except Exception as e:
        print(f"    ZNE: FAILED — {e}")

    # --- Counts-based techniques: MEM, CDR, VD, DD ---
    readout_nm = create_readout_error_model(0.05)
    cal_matrix, cal_states = build_calibration_matrix(readout_nm, num_qubits=counts_circuit.num_qubits)

    counts_techniques = {
        "MEM": (lambda: _vqe_zz(mitigate_counts(
                    run_circuit(counts_circuit, noise_model=readout_nm),
                    cal_matrix, states=cal_states)),
                sampling_overhead("MEM")),
        "CDR": (lambda: float(np.clip(run_cdr(
                    counts_circuit, nm, num_training_circuits=10, shots=1024,
                    evaluator=_vqe_zz), -1.0, 1.0)),
                sampling_overhead("CDR", num_training_circuits=10)),
        "VD":  (lambda: run_virtual_distillation(
                    counts_circuit, noise_model=nm, shots=8192,
                    observable=lambda s: 1.0 if s in ("00", "11") else -1.0),
                sampling_overhead("VD")),
        "DD":  (lambda: run_dynamical_decoupling(
                    counts_circuit, nm, rule="xyxy", num_trials=5, shots=2048,
                    evaluator=_vqe_zz),
                sampling_overhead("DD", num_trials=5)),
    }

    for technique, (fn, overhead) in counts_techniques.items():
        t0 = time.perf_counter()
        try:
            mitigated_zz = fn()
            runtime = round(time.perf_counter() - t0, 2)
            row = summarise(technique, ideal_zz, noisy_zz, mitigated_zz, overhead)
            row["circuit"]     = "VQE"
            row["noise_level"] = noise_level
            row["runtime_s"]   = runtime
            results.append(row)
            print(f"    {technique:<4}  fidelity={row['fidelity']:.4f}  "
                  f"reduction={row['error_reduction_%']:.1f}%")
        except Exception as e:
            print(f"    {technique}: FAILED — {e}")

    return results


CIRCUITS     = {"Bell": create_bell_state(), "GHZ-3": create_ghz_state(3),
                "QFT-3": create_qft(3), "QAOA-C4": create_qaoa()}
NOISE_LEVELS = [0.01, 0.05, 0.10, 0.15, 0.20]
TECHNIQUES   = ["MEM", "ZNE", "PEC", "CDR", "VD", "DD"]


def run_benchmark() -> list[dict]:
    """Run all 6 techniques × 4 circuits × 5 noise levels, plus VQE-ZNE × 5 noise levels."""
    results = []

    # --- Counts-based circuits: Bell, GHZ-3, QFT-3, QAOA-C4 ---
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
                        n_training   = 20 if circuit_name == "QAOA-C4" else 10
                        overhead     = sampling_overhead("CDR", num_training_circuits=n_training)
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

    # --- VQE: ZNE (Estimator) + MEM/CDR/VD/DD (counts-based) ---
    print("\nCircuit: VQE (H2 ground state)")
    for noise_level in NOISE_LEVELS:
        print(f"  Noise: {noise_level:.0%}")
        results.extend(run_vqe_benchmark(noise_level))

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
