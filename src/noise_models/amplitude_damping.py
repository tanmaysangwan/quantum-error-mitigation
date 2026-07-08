from qiskit_aer.noise import NoiseModel, amplitude_damping_error


def create_amplitude_damping_noise_model(error_probability: float) -> NoiseModel:
    
    noise_model = NoiseModel()

    single_qubit_error = amplitude_damping_error(error_probability)

    noise_model.add_all_qubit_quantum_error(
        single_qubit_error,
        ["h"]
    )

    return noise_model