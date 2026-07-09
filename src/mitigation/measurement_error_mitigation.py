import numpy as np  

from src.backends.simulator import run_circuit  
from src.mitigation.calibration import CALIBRATION_STATES, create_bell_calibration_circuits  


def build_calibration_matrix(noise_model) -> np.ndarray:    #function generates the calibration matrix by executing the calibration circuits under the given readout noise model.
    calibration_circuits = create_bell_calibration_circuits()  
    matrix = np.zeros((4, 4), dtype=float)  

    for prepared_index, prepared_state in enumerate(CALIBRATION_STATES):  #Runs each state one by one through the noisy simulator 
        counts = run_circuit(calibration_circuits[prepared_state], noise_model=noise_model)  # Run the calibration circuit under readout noise.
        total_shots = sum(counts.values())  

        for measured_index, measured_state in enumerate(CALIBRATION_STATES):  #Checks how often every possible state was measured.
            matrix[measured_index, prepared_index] = counts.get(measured_state, 0) / total_shots  # Store P(measured | prepared).

    return matrix


def mitigate_counts(counts: dict, calibration_matrix: np.ndarray) -> dict:    #uses the calibration matrix to correct the noisy measurement results.
    measured_vector = np.array([counts.get(state, 0) for state in CALIBRATION_STATES], dtype=float)  # Convert counts to a vector.
    inverse_matrix = np.linalg.inv(calibration_matrix)  # Invert the calibration matrix.
    corrected_vector = inverse_matrix @ measured_vector  # Estimate the ideal counts.
    corrected_vector = np.clip(corrected_vector, 0, None)  # Removes negative values
    corrected_total = corrected_vector.sum()  # Check whether any probability mass remains.

    if corrected_total == 0:  # Safety check in case the correction fails unexpectedly.
        return {state: int(counts.get(state, 0)) for state in CALIBRATION_STATES}  # Return the noisy counts unchanged.

    corrected_vector *= measured_vector.sum() / corrected_total  # Preserve the number of shots.
    return {state: round(corrected_vector[index]) for index, state in enumerate(CALIBRATION_STATES)}  # Convert vector back to counts.

#The first function builds the calibration matrix from calibration circuits, while the second function applies the inverse of that matrix to the noisy measurement counts to estimate the ideal measurement results.