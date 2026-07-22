from typing import Callable
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel
from mitiq.ddd import execute_with_ddd
from mitiq.ddd.rules import xx, xyxy

from src.mitigation.probabilistic_error_cancellation import zz_expectation


def _make_executor(noise_model: NoiseModel | None, shots: int, evaluator: Callable[[dict], float]):
    """Return an executor that runs a circuit and evaluates the observable."""
    def executor(circuit: QuantumCircuit) -> float:
        sim = AerSimulator(noise_model=noise_model)
        counts = sim.run(circuit, shots=shots).result().get_counts()
        return evaluator(counts)
    return executor


def run_dynamical_decoupling(
    circuit: QuantumCircuit,
    noise_model: NoiseModel,
    rule: str = "xyxy",
    num_trials: int = 10,
    shots: int = 2048,
    evaluator: Callable[[dict], float] | None = None,
) -> float:
    """Run Dynamical Decoupling via Mitiq and return the mitigated value.

    DD inserts pulse sequences (XX or XYXY) into idle windows between gates.
    These sequences average out low-frequency dephasing noise (T2 errors)
    while leaving the circuit logically equivalent.
    """
    if evaluator is None:
        evaluator = zz_expectation

    native   = transpile(circuit, basis_gates=["rz", "sx", "cx"], optimization_level=0)
    dd_rule  = xyxy if rule == "xyxy" else xx
    executor = _make_executor(noise_model, shots, evaluator)

    return float(execute_with_ddd(
        native,
        executor=executor,
        rule=dd_rule,
        num_trials=num_trials,
    ))

