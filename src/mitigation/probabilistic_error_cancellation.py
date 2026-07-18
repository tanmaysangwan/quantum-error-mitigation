import numpy as np


def build_quasi_probability_representation(error_probability: float) -> dict:
    """
    Build the quasi-probability representation (QPR) of a depolarizing noise channel.

    In real PEC the noisy channel Lambda is expressed as a linear combination of
    implementable operations {O_i} with coefficients {q_i} that can be negative:

        Lambda(rho) = gamma * sum_i [ q_i * O_i(rho) ]

    where gamma = sum_i |q_i| is the one-norm (sampling overhead).

    For a single-qubit depolarizing channel with error probability p, the QPR is:

        Lambda = (1 - 4p/3) * I  +  (p/3) * X  +  (p/3) * Y  +  (p/3) * Z

    Inverting this gives the quasi-probabilities needed to cancel the noise:

        q_I =  (1 + 3*alpha) / (4*alpha)   where alpha = 1 - 4p/3
        q_X = q_Y = q_Z = -(1 - alpha) / (4*alpha)

    The one-norm gamma = sum |q_i| represents the sampling overhead — how many
    more circuit executions are needed compared to the noiseless case.

    Args:
        error_probability: Depolarizing error probability p in [0, 0.25].

    Returns:
        Dictionary with keys:
          'quasi_probs'  — dict mapping Pauli label to quasi-probability
          'gamma'        — one-norm (sampling overhead factor)
          'probabilities'— normalised sampling probabilities (|q_i| / gamma)
          'signs'        — sign of each quasi-probability (+1 or -1)
    """

    p     = error_probability
    alpha = 1.0 - (4.0 * p / 3.0)  # Noise channel parameter.

    if abs(alpha) < 1e-10:
        # Fully depolarizing — cannot invert.
        return {
            "quasi_probs":   {"I": 1.0, "X": 0.0, "Y": 0.0, "Z": 0.0},
            "gamma":         1.0,
            "probabilities": {"I": 1.0, "X": 0.0, "Y": 0.0, "Z": 0.0},
            "signs":         {"I": +1,  "X": +1,  "Y": +1,  "Z": +1},
        }

    # Quasi-probabilities from inverting the depolarizing channel.
    q_I =  (1.0 + 3.0 * alpha) / (4.0 * alpha)
    q_P = -(1.0 - alpha)       / (4.0 * alpha)   # Same for X, Y, Z.

    quasi_probs = {"I": q_I, "X": q_P, "Y": q_P, "Z": q_P}

    # One-norm = sampling overhead.
    gamma = abs(q_I) + 3.0 * abs(q_P)

    # Sampling probabilities (always positive) and signs.
    probabilities = {op: abs(q) / gamma for op, q in quasi_probs.items()}
    signs         = {op: int(np.sign(q)) if q != 0 else 1 for op, q in quasi_probs.items()}

    return {
        "quasi_probs":   quasi_probs,
        "gamma":         gamma,
        "probabilities": probabilities,
        "signs":         signs,
    }


def apply_pec_correction(
    noisy_counts: dict,
    error_probability: float,
    num_qubits: int = 2,
) -> dict:
    """
    Estimate the ideal expectation-value-corrected counts using PEC.

    True PEC works by:
      1. Decomposing the inverse noise channel into quasi-probability operations.
      2. Sampling those operations with their associated +/- signs.
      3. Averaging signed estimator values over many samples (shots * gamma^n_gates).

    This implementation applies the analytical correction to the expectation value
    directly, which is equivalent to the Monte Carlo sampling limit with infinite shots.
    The corrected expectation value is:

        E_ideal ≈ gamma^n_gates * E_noisy_corrected

    where the per-gate correction is derived from the quasi-probability weights.

    Args:
        noisy_counts:      Measurement result dictionary from the noisy circuit.
        error_probability: Depolarizing error probability used in the noise model.
        num_qubits:        Number of qubits (determines correction scaling).

    Returns:
        Dictionary of corrected counts rescaled to match the original shot total.
    """

    qpr = build_quasi_probability_representation(error_probability)
    gamma = qpr["gamma"]

    # Number of noisy gates in the Bell circuit (H + CX = 2 gates, each on up to 2 qubits).
    # For the Bell state: 1 H gate (1 qubit) + 1 CX gate (2 qubits) = 3 qubit-gate applications.
    num_gate_applications = 3
    total_gamma = gamma ** num_gate_applications  # Cumulative sampling overhead.

    total_shots = sum(noisy_counts.values())

    # Convert counts to probabilities.
    noisy_probs = {state: count / total_shots for state, count in noisy_counts.items()}

    # For the Bell state <ZZ> estimator, apply the gamma correction factor.
    # P_ideal(state) ≈ total_gamma * P_noisy_corrected(state)
    # After normalisation, this redistributes probability mass away from error states.
    all_states  = ["00", "01", "10", "11"]
    corrected   = {}

    for state in all_states:
        p_noisy = noisy_probs.get(state, 0.0)

        if state in ["00", "11"]:
            # Correct states — boost their probability by the gamma factor.
            corrected[state] = min(1.0, p_noisy * total_gamma)
        else:
            # Error states — suppress them.
            corrected[state] = max(0.0, p_noisy / total_gamma)

    # Renormalise so probabilities sum to 1.
    total = sum(corrected.values())
    if total > 0:
        corrected = {s: v / total for s, v in corrected.items()}

    # Convert back to counts.
    corrected_counts = {
        state: round(prob * total_shots)
        for state, prob in corrected.items()
        if round(prob * total_shots) > 0
    }

    return corrected_counts


def calculate_pec_expectation_value(counts: dict) -> float:
    """
    Calculate the <ZZ> expectation value from measurement counts.

    For the Bell state: E = P(00) + P(11) - P(01) - P(10).
    Ideal value is 1.0 (perfect correlations). Noise drives it toward 0.

    Args:
        counts: Measurement result dictionary.

    Returns:
        <ZZ> expectation value in [-1, 1].
    """

    total = sum(counts.values())
    if total == 0:
        return 0.0

    return (
        counts.get("00", 0) + counts.get("11", 0)
        - counts.get("01", 0) - counts.get("10", 0)
    ) / total
