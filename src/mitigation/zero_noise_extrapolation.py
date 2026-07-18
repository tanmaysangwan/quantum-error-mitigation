import numpy as np
from qiskit import QuantumCircuit


def fold_gates(circuit: QuantumCircuit, scale_factor: int) -> QuantumCircuit:
    """
    Amplify noise in a circuit via gate folding.

    Each gate G is replaced by G (G† G)^k, where k = (scale_factor - 1) / 2.
    This inserts extra gate-inverse pairs that are logically identity operations
    but each contribute additional noise, scaling the total noise by scale_factor.

    Only odd integer scale factors are supported (1, 3, 5, ...) because each
    folding unit adds one G† and one G, keeping the circuit equivalent.

    Args:
        circuit:      The original QuantumCircuit to fold. Must end with measurements.
        scale_factor: Odd integer >= 1. 1 returns an unmodified copy.

    Returns:
        A new QuantumCircuit with gates folded to the requested noise scale.

    Raises:
        ValueError: If scale_factor is even or less than 1.
    """

    if scale_factor < 1 or scale_factor % 2 == 0:
        raise ValueError(
            f"scale_factor must be an odd integer >= 1, got {scale_factor}."
        )

    if scale_factor == 1:
        return circuit.copy()  # No folding needed at 1×.

    # Separate gate instructions from measurement instructions.
    gate_instructions = [
        (instruction, qargs, cargs)
        for instruction, qargs, cargs in circuit.data
        if instruction.name != "measure"
    ]

    measurement_instructions = [
        (instruction, qargs, cargs)
        for instruction, qargs, cargs in circuit.data
        if instruction.name == "measure"
    ]

    # Build a new circuit with the same registers.
    folded = QuantumCircuit(*circuit.qregs, *circuit.cregs)

    # How many extra (G† G) pairs to append after each gate.
    num_pairs = (scale_factor - 1) // 2

    for instruction, qargs, cargs in gate_instructions:
        # Apply the original gate G.
        folded.append(instruction, qargs, cargs)

        # Append (G† G) num_pairs times.
        for _ in range(num_pairs):
            folded.append(instruction.inverse(), qargs, cargs)  # G†
            folded.append(instruction, qargs, cargs)            # G

    # Re-attach measurements at the end.
    for instruction, qargs, cargs in measurement_instructions:
        folded.append(instruction, qargs, cargs)

    return folded


def linear_extrapolation(noise_factors: list, expectation_values: list) -> float:
    """
    Estimate the zero-noise expectation value using linear extrapolation.

    Fits a straight line through (noise_factor, expectation_value) data points
    and returns the y-intercept, which is the estimate at zero noise.

    Args:
        noise_factors:      List of noise scaling factors used (e.g. [1, 3, 5]).
        expectation_values: Measured expectation values at each noise factor.

    Returns:
        Estimated expectation value extrapolated to zero noise.
    """

    coefficients = np.polyfit(noise_factors, expectation_values, 1)  # slope, intercept

    slope = coefficients[0]      # Change in expectation value per unit noise.
    intercept = coefficients[1]  # Estimated value at zero noise.

    return intercept


def richardson_extrapolation(noise_factors: list, expectation_values: list) -> float:
    """
    Estimate the zero-noise expectation value using Richardson extrapolation.

    Richardson extrapolation combines measurements at different noise levels using
    analytically derived weights so that the leading-order noise terms cancel exactly.
    For n data points it cancels the n-1 lowest-order noise contributions, giving a
    more accurate zero-noise estimate than a simple linear fit — especially when the
    noise-vs-expectation relationship is not perfectly linear.

    The weights w_i for scale factors lambda_i are:

        w_i = product_{j != i} [ lambda_j / (lambda_j - lambda_i) ]

    and the estimate is:

        E(0) = sum_i [ w_i * E(lambda_i) ]

    Args:
        noise_factors:      List of noise scaling factors (e.g. [1, 3, 5]).
                            Must have at least 2 entries. All values must be distinct.
        expectation_values: Measured expectation values at each noise factor.
                            Must be the same length as noise_factors.

    Returns:
        Estimated expectation value extrapolated to zero noise.

    Raises:
        ValueError: If fewer than 2 data points are provided.
    """

    if len(noise_factors) < 2:
        raise ValueError("Richardson extrapolation requires at least 2 data points.")

    lambdas = np.array(noise_factors, dtype=float)
    values  = np.array(expectation_values, dtype=float)
    n       = len(lambdas)

    zero_noise_estimate = 0.0

    for i in range(n):
        # Compute the Richardson weight for point i.
        # This is the product of lambda_j / (lambda_j - lambda_i) for all j != i.
        weight = 1.0
        for j in range(n):
            if j != i:
                weight *= lambdas[j] / (lambdas[j] - lambdas[i])

        zero_noise_estimate += weight * values[i]

    return float(zero_noise_estimate)


def calculate_expectation_value(counts: dict) -> float:
    """
    Calculate the <ZZ> expectation value from two-qubit measurement counts.

    Assigns +1 to correlated outcomes (|00>, |11>) and -1 to anti-correlated
    outcomes (|01>, |10>), then normalises by total shots.

    Args:
        counts: Measurement result dictionary mapping bitstring to count.

    Returns:
        <ZZ> expectation value in the range [-1, 1].
    """

    total_shots = sum(counts.values())

    if total_shots == 0:
        return 0.0

    expectation = (
        counts.get("00", 0)
        + counts.get("11", 0)
        - counts.get("01", 0)
        - counts.get("10", 0)
    ) / total_shots  # <ZZ> = P(00) + P(11) - P(01) - P(10)

    return expectation
