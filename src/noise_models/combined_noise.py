from qiskit_aer.noise import (
    NoiseModel,
    ReadoutError,
    amplitude_damping_error,
    depolarizing_error,
    phase_damping_error,
)


def create_combined_noise_model(error_probability: float) -> NoiseModel:

    noise_model = NoiseModel()

    single_qubit_error = depolarizing_error(error_probability, 1)
    two_qubit_error = depolarizing_error(error_probability, 2)

    amplitude_error = amplitude_damping_error(error_probability)
    phase_error = phase_damping_error(error_probability)

    readout_error = ReadoutError(
        [
            [1 - error_probability, error_probability],
            [error_probability, 1 - error_probability],
        ]
    )

    noise_model.add_all_qubit_quantum_error(single_qubit_error, ["h"])
    noise_model.add_all_qubit_quantum_error(two_qubit_error, ["cx"])

    noise_model.add_all_qubit_quantum_error(amplitude_error, ["h"])
    noise_model.add_all_qubit_quantum_error(phase_error, ["h"])

    noise_model.add_all_qubit_readout_error(readout_error)

    return noise_model