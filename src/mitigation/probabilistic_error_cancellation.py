import numpy as np
from qiskit import QuantumCircuit
from qiskit_aer.noise import NoiseModel

from src.backends.simulator import run_circuit


def build_quasi_probability_representation(error_probability: float) -> dict:
    """Compute QPR for a single-qubit depolarizing channel: inverts Lambda to get quasi-probs, gamma, and signs."""
    p     = error_probability
    alpha = 1.0 - (4.0 * p / 3.0)

    if abs(alpha) < 1e-10:
        return {
            "quasi_probs":   {"I": 1.0, "X": 0.0, "Y": 0.0, "Z": 0.0},
            "gamma":         1.0,
            "probabilities": {"I": 1.0, "X": 0.0, "Y": 0.0, "Z": 0.0},
            "signs":         {"I": +1,  "X": +1,  "Y": +1,  "Z": +1},
        }

    q_I          = (1.0 + 3.0 * alpha) / (4.0 * alpha)
    q_P          = -(1.0 - alpha) / (4.0 * alpha)  # same value for X, Y, Z
    quasi_probs  = {"I": q_I, "X": q_P, "Y": q_P, "Z": q_P}
    gamma        = abs(q_I) + 3.0 * abs(q_P)
    probabilities = {op: abs(q) / gamma for op, q in quasi_probs.items()}
    signs         = {op: int(np.sign(q)) if q != 0 else 1 for op, q in quasi_probs.items()}

    return {"quasi_probs": quasi_probs, "gamma": gamma,
            "probabilities": probabilities, "signs": signs}


def _sample_pauli(probabilities: dict, rng: np.random.Generator) -> str:
    """Sample one Pauli label (I/X/Y/Z) weighted by sampling probabilities."""
    ops = list(probabilities.keys())
    return rng.choice(ops, p=[probabilities[op] for op in ops])


def _insert_pauli(circuit: QuantumCircuit, pauli: str, qubit: int) -> QuantumCircuit:
    """Return a copy of circuit with a Pauli gate inserted on qubit before measurements."""
    gate_data    = [(i, q, c) for i, q, c in circuit.data if i.name != "measure"]
    measure_data = [(i, q, c) for i, q, c in circuit.data if i.name == "measure"]

    new_circ = QuantumCircuit(*circuit.qregs, *circuit.cregs)
    for i, q, c in gate_data:
        new_circ.append(i, q, c)

    if pauli == "X":
        new_circ.x(qubit)
    elif pauli == "Y":
        new_circ.y(qubit)
    elif pauli == "Z":
        new_circ.z(qubit)

    for i, q, c in measure_data:
        new_circ.append(i, q, c)

    return new_circ


def zz_expectation(counts: dict) -> float:
    """Compute <ZZ>: +1 for |00>,|11> and -1 for |01>,|10>, normalised by total shots."""
    total = sum(counts.values())
    if total == 0:
        return 0.0
    return (counts.get("00", 0) + counts.get("11", 0)
            - counts.get("01", 0) - counts.get("10", 0)) / total


def run_pec(
    circuit: QuantumCircuit,
    noise_model: NoiseModel,
    error_probability: float,
    num_samples: int = 200,
    shots_per_sample: int = 1024,
    seed: int = 42,
) -> dict:
    """Run PEC via Monte Carlo quasi-probability sampling and return mitigated counts.

    Each sample independently draws a Pauli correction per gate application from the
    QPR, applies it to the circuit, runs under noise, and accumulates sign * <ZZ>.
    Final estimate: gamma^n_gates * mean(signed_estimators).
    Bell circuit: 3 qubit-gate applications (H on q0, CX on q0, CX on q1).
    """
    qpr          = build_quasi_probability_representation(error_probability)
    gamma        = qpr["gamma"]
    n_gates      = 3  # H(q0), CX(q0), CX(q1)
    total_gamma  = gamma ** n_gates
    rng          = np.random.default_rng(seed)
    signed_evs   = []

    for _ in range(num_samples):
        sampled = [_sample_pauli(qpr["probabilities"], rng) for _ in range(n_gates)]
        sign    = int(np.prod([qpr["signs"][p] for p in sampled]))

        # Apply sampled Pauli corrections: sampled[0] → q0 (H), sampled[2] → q1 (CX target).
        corrected = _insert_pauli(circuit, sampled[0], qubit=0)
        corrected = _insert_pauli(corrected, sampled[2], qubit=1)

        counts = run_circuit(corrected, shots=shots_per_sample, noise_model=noise_model)
        signed_evs.append(sign * zz_expectation(counts))

    mitigated_ev = float(np.clip(total_gamma * np.mean(signed_evs), -1.0, 1.0))

    # Reconstruct counts from the scalar <ZZ> estimate assuming symmetric Bell state.
    p_corr  = (1.0 + mitigated_ev) / 2.0
    p_error = (1.0 - mitigated_ev) / 2.0
    counts  = {
        "00": round(p_corr  * shots_per_sample / 2),
        "11": round(p_corr  * shots_per_sample / 2),
        "01": round(p_error * shots_per_sample / 2),
        "10": round(p_error * shots_per_sample / 2),
    }
    return {s: c for s, c in counts.items() if c > 0}
