import warnings
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel
from mitiq.pec import (
    execute_with_pec,
    represent_operations_in_circuit_with_global_depolarizing_noise,
)


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
    q_P          = -(1.0 - alpha) / (4.0 * alpha)
    quasi_probs  = {"I": q_I, "X": q_P, "Y": q_P, "Z": q_P}
    gamma        = abs(q_I) + 3.0 * abs(q_P)
    probabilities = {op: abs(q) / gamma for op, q in quasi_probs.items()}
    signs         = {op: int(np.sign(q)) if q != 0 else 1 for op, q in quasi_probs.items()}

    return {"quasi_probs": quasi_probs, "gamma": gamma,
            "probabilities": probabilities, "signs": signs}


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
    shots: int = 1024,
) -> float:
    """Run PEC via Mitiq's quasi-probability sampling and return the mitigated <ZZ> value.

    Transpiles to {Rz, SX, CX}, builds operation representations for the depolarizing channel,
    then calls Mitiq's execute_with_pec which handles all Monte Carlo sampling internally.
    """
    native = transpile(circuit, basis_gates=["rz", "sx", "cx"], optimization_level=0)

    def executor(circ: QuantumCircuit) -> float:
        sim = AerSimulator(noise_model=noise_model)
        return zz_expectation(sim.run(circ, shots=shots).result().get_counts())

    representations = represent_operations_in_circuit_with_global_depolarizing_noise(
        native, noise_level=error_probability
    )

    # Suppress Mitiq's warnings about measurement gates having no representation (expected).
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        result = execute_with_pec(
            native,
            executor=executor,
            representations=representations,
            num_samples=num_samples,
            random_state=42,
        )

    return float(np.clip(result, -1.0, 1.0))
