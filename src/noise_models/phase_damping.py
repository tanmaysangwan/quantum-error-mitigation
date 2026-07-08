from qiskit_aer.noise import NoiseModel, phase_damping_error


def create_phase_damping_noise_model(error_probability: float) -> NoiseModel:
    """
    Create a phase damping noise model.

    Args:
        error_probability: Probability of phase damping.

    Returns:
        A configured Qiskit NoiseModel.
    """

    noise_model = NoiseModel()

    single_qubit_error = phase_damping_error(error_probability)

    noise_model.add_all_qubit_quantum_error(
        single_qubit_error,
        ["h"]
    )

    return noise_model