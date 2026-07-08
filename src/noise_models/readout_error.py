from qiskit_aer.noise import NoiseModel, ReadoutError


def create_readout_error_model(error_probability: float) -> NoiseModel:
    """
    Create a readout error model.

    Args:
        error_probability: Probability of measuring the wrong value.

    Returns:
        A configured Qiskit NoiseModel.
    """

    noise_model = NoiseModel()

    readout_error = ReadoutError(
        [
            [1 - error_probability, error_probability],
            [error_probability, 1 - error_probability],
        ]
    )

    noise_model.add_all_qubit_readout_error(readout_error)

    return noise_model