import numpy as np

from src.backends.simulator import run_circuit
from src.mitigation.calibration import create_calibration_circuits


def build_calibration_matrix(noise_model, num_qubits: int = 2) -> tuple[np.ndarray, list[str]]:
    """Generate the calibration matrix for N qubits by running basis state circuits under readout noise.

    Returns:
        (matrix, states) where matrix[measured, prepared] = P(measured | prepared).
    """
    states, calibration_circuits = create_calibration_circuits(num_qubits)
    dim = len(states)
    matrix = np.zeros((dim, dim), dtype=float)

    for prepared_index, prepared_state in enumerate(states):
        counts = run_circuit(calibration_circuits[prepared_state], noise_model=noise_model)
        total_shots = sum(counts.values())

        for measured_index, measured_state in enumerate(states):
            matrix[measured_index, prepared_index] = counts.get(measured_state, 0) / total_shots

    return matrix, states


def mitigate_counts(counts: dict, calibration_matrix: np.ndarray, states: list[str] | None = None) -> dict:
    """Correct noisy measurement counts using the inverse of the calibration matrix."""
    if states is None:
        num_qubits = len(next(iter(counts.keys()))) if counts else 2
        states = [format(i, f"0{num_qubits}b") for i in range(2**num_qubits)]

    measured_vector = np.array([counts.get(state, 0) for state in states], dtype=float)
    try:
        inverse_matrix = np.linalg.inv(calibration_matrix)
        corrected_vector = inverse_matrix @ measured_vector
    except np.linalg.LinAlgError:
        return counts

    corrected_vector = np.clip(corrected_vector, 0, None)
    corrected_total = corrected_vector.sum()

    if corrected_total == 0:
        return {state: int(counts.get(state, 0)) for state in states}

    corrected_vector *= measured_vector.sum() / corrected_total
    return {state: round(corrected_vector[index]) for index, state in enumerate(states) if round(corrected_vector[index]) > 0}