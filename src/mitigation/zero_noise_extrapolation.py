import numpy as np  # Numerical calculations.


def linear_extrapolation(noise_factors: list, expectation_values: list) -> float:
    # Fit a straight line through the noisy data.

    coefficients = np.polyfit(noise_factors, expectation_values, 1)  # slope, intercept

    slope = coefficients[0]  # Change in expectation value with noise.
    intercept = coefficients[1]  # Estimated value at zero noise.

    return intercept


def calculate_expectation_value(counts: dict) -> float:
    # Calculate the expectation value of the Bell state.

    total_shots = sum(counts.values())  # Total measurements.

    if total_shots == 0:
        return 0.0

    expectation = (
        counts.get("00", 0)
        + counts.get("11", 0)
        - counts.get("01", 0)
        - counts.get("10", 0)
    ) / total_shots  # <ZZ> expectation.

    return expectation