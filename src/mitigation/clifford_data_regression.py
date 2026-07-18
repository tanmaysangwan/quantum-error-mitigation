import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel
from mitiq.cdr import execute_with_cdr

from src.mitigation.probabilistic_error_cancellation import zz_expectation


def _to_native_basis(circuit: QuantumCircuit) -> QuantumCircuit:
    """Transpile circuit to {Rz, SX, CX} — the basis Mitiq CDR requires."""
    return transpile(circuit, basis_gates=["rz", "sx", "cx"], optimization_level=0)


def _make_executor(noise_model: NoiseModel | None, shots: int):
    """Return an executor function that runs a circuit and returns <ZZ>."""
    def executor(circuit: QuantumCircuit) -> float:
        sim = AerSimulator(noise_model=noise_model)
        return zz_expectation(sim.run(circuit, shots=shots).result().get_counts())
    return executor


def run_cdr(
    circuit: QuantumCircuit,
    noise_model: NoiseModel,
    num_training_circuits: int = 10,
    fraction_non_clifford: float = 0.1,
    shots: int = 1024,
) -> float:
    """Run CDR via Mitiq and return the mitigated <ZZ> expectation value.

    Generates near-Clifford training circuits by replacing a fraction of non-Clifford
    gates with Clifford gates. Runs each training circuit on both the noisy executor and
    the ideal simulator, fits a linear model mapping noisy → ideal, then applies that
    model to the noisy result of the original circuit.
    """
    native = _to_native_basis(circuit)
    noisy_executor = _make_executor(noise_model, shots)
    ideal_executor = _make_executor(None, shots)

    return float(execute_with_cdr(
        native,
        executor=noisy_executor,
        simulator=ideal_executor,
        num_training_circuits=num_training_circuits,
        fraction_non_clifford=fraction_non_clifford,
    ))
