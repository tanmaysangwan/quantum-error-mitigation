from qiskit_aer.noise import NoiseModel
from qiskit_aer.noise import amplitude_damping_error


def create_amplitude_damping_noise_model(error_probability: float) -> NoiseModel:

    noise_model = NoiseModel()

    single_qubit_error = amplitude_damping_error(error_probability)

    two_qubit_error = single_qubit_error.tensor(single_qubit_error)

    noise_model.add_all_qubit_quantum_error(
        single_qubit_error,
        ["h"],
    )

    noise_model.add_all_qubit_quantum_error(
        two_qubit_error,
        ["cx"],
    )

    return noise_model