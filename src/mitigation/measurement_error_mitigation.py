import numpy as np  # Matrix math for MEM.

from src.backends.simulator import run_circuit  # Shared simulator runner.
from src.mitigation.calibration import CALIBRATION_STATES, create_bell_calibration_circuits  # Bell calibration circuits.


def build_calibration_matrix(noise_model) -> np.ndarray:
    calibration_circuits = create_bell_calibration_circuits()  # Generate 00/01/10/11 calibration circuits.
    matrix = np.zeros((4, 4), dtype=float)  # Rows = measured states, columns = prepared states.

    for prepared_index, prepared_state in enumerate(CALIBRATION_STATES):  # Fill one column per prepared basis state.
        counts = run_circuit(calibration_circuits[prepared_state], noise_model=noise_model)  # Run the calibration circuit under readout noise.
        total_shots = sum(counts.values())  # Normalise counts into probabilities.

        for measured_index, measured_state in enumerate(CALIBRATION_STATES):  # Map measured outcomes into matrix rows.
            matrix[measured_index, prepared_index] = counts.get(measured_state, 0) / total_shots  # Store P(measured | prepared).

    return matrix


def mitigate_counts(counts: dict, calibration_matrix: np.ndarray) -> dict:
    measured_vector = np.array([counts.get(state, 0) for state in CALIBRATION_STATES], dtype=float)  # Convert counts to a vector.
    inverse_matrix = np.linalg.inv(calibration_matrix)  # Invert the calibration matrix.
    corrected_vector = inverse_matrix @ measured_vector  # Estimate the ideal counts.
    corrected_vector = np.clip(corrected_vector, 0, None)  # Remove tiny negative values from inversion.
    corrected_total = corrected_vector.sum()  # Check whether any probability mass remains.

    if corrected_total == 0:  # Safety fallback for pathological input.
        return {state: int(counts.get(state, 0)) for state in CALIBRATION_STATES}  # Return the noisy counts unchanged.

    corrected_vector *= measured_vector.sum() / corrected_total  # Preserve the number of shots.
    return {state: round(corrected_vector[index]) for index, state in enumerate(CALIBRATION_STATES)}  # Convert vector back to counts.