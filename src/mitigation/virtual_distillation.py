from typing import Callable

from qiskit import QuantumCircuit
from qiskit_aer.noise import NoiseModel

from src.backends.simulator import run_circuit
from src.mitigation.probabilistic_error_cancellation import zz_expectation


def _zz_weight(bitstring: str) -> float:
    """Return +1 for |00>/|11> and -1 for |01>/|10>. Used as the default ZZ observable."""
    return 1.0 if bitstring in ("00", "11") else -1.0


def run_virtual_distillation(
    circuit: QuantumCircuit,
    noise_model: NoiseModel,
    shots: int = 8192,
    observable: Callable[[str], float] | None = None,
) -> float:
    """Estimate the distilled expectation value using Virtual Distillation.

    VD uses the squared density matrix estimator Tr(rho^2 * O) / Tr(rho^2).
    For a pure ideal state rho^2 = rho, so this returns the true expectation value.
    For a mixed noisy state, squaring suppresses off-diagonal noise terms,
    pushing the estimate closer to the ideal pure-state value.

    Requires high shot counts (>=8192) for stable probability estimates.
    No circuit overhead — runs the original circuit once under noise.

    Args:
        circuit:     The quantum circuit to run.
        noise_model: Qiskit Aer noise model.
        shots:       Number of measurement shots (high count recommended).
        observable:  Function (bitstring -> float) assigning a scalar weight to each
                     measurement outcome. Defaults to ZZ observable (+1 for 00/11,
                     -1 for 01/10). For QAOA pass a cut-value function; for GHZ pass
                     a function that returns +1 for 000/111 and -1 otherwise.
    """
    if observable is None:
        observable = _zz_weight

    counts = run_circuit(circuit, shots=shots, noise_model=noise_model)
    total  = sum(counts.values())
    probs  = {s: c / total for s, c in counts.items()}

    denominator = sum(p ** 2 for p in probs.values())
    if denominator < 1e-10:
        return 0.0

    numerator = sum(observable(s) * p ** 2 for s, p in probs.items())
    return numerator / denominator
