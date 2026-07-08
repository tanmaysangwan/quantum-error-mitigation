import numpy as np  # Numerical operations.


def calculate_error_probability(
    ideal_counts: dict,
    noisy_counts: dict,
) -> float:
    # Estimate the probability that an error occurred.

    ideal_total = sum(ideal_counts.values())

    if ideal_total == 0:
        return 0.0

    correct_states = ["00", "11"]  # Bell-state outcomes.

    ideal_correct = sum(
        ideal_counts.get(state, 0)
        for state in correct_states
    )

    noisy_correct = sum(
        noisy_counts.get(state, 0)
        for state in correct_states
    )

    success_probability = noisy_correct / ideal_total

    return max(0.0, 1.0 - success_probability)


def probabilistic_error_cancellation(
    noisy_counts: dict,
    error_probability: float,
) -> dict:
    # Return the noisy result if no correction is needed.

    if error_probability == 0:
        return noisy_counts.copy()

    corrected_counts = {}

    correction_factor = 1 / (1 - error_probability)  # Cancel the estimated error.

    for state, count in noisy_counts.items():
        corrected_counts[state] = round(
            count * correction_factor
        )  # Apply the correction.

    total_original = sum(noisy_counts.values())
    total_corrected = sum(corrected_counts.values())

    scale = total_original / total_corrected  # Preserve the shot count.

    for state in corrected_counts:
        corrected_counts[state] = round(
            corrected_counts[state] * scale
        )

    return corrected_counts