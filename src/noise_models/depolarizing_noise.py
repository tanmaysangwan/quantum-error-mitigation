from qiskit_aer.noise import NoiseModel, depolarizing_error


def create_depolarizing_noise_model(error_probability: float) -> NoiseModel:

    noise_model = NoiseModel()

    single_qubit_error = depolarizing_error(error_probability, 1)
    two_qubit_error = depolarizing_error(error_probability, 2)

    noise_model.add_all_qubit_quantum_error(single_qubit_error, ["h"])
    noise_model.add_all_qubit_quantum_error(two_qubit_error, ["cx"])

    return noise_model