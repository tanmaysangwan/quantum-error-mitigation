from qiskit import QuantumCircuit
from qiskit_aer.noise import NoiseModel

from src.backends.simulator import run_circuit


def run_virtual_distillation(
    circuit: QuantumCircuit,
    noise_model: NoiseModel,
    shots: int = 8192,
) -> float:
    """Estimate the distilled <ZZ> expectation value using Virtual Distillation.

    VD uses the squared density matrix estimator Tr(rho^2 * ZZ) / Tr(rho^2).
    For a pure ideal state rho^2 = rho, so this returns the true expectation value.
    For a mixed noisy state, squaring suppresses off-diagonal noise terms,
    pushing the estimate closer to the ideal pure-state value.

    Requires high shot counts (>=8192) for stable probability estimates.
    No circuit overhead — runs the original circuit once under noise.
    """
    counts = run_circuit(circuit, shots=shots, noise_model=noise_model)
    total  = sum(counts.values())
    probs  = {s: c / total for s, c in counts.items()}

    numerator   = sum((1 if s in ("00", "11") else -1) * p ** 2 for s, p in probs.items())
    denominator = sum(p ** 2 for p in probs.values())

    return numerator / denominator if denominator > 0 else 0.0
