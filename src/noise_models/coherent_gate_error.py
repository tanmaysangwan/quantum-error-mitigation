from qiskit.circuit.library import RXGate
from qiskit_aer.noise import NoiseModel, coherent_unitary_error


def create_coherent_gate_error_model(rotation_angle: float) -> NoiseModel:

    noise_model = NoiseModel()

    single_qubit_error = coherent_unitary_error(
        RXGate(rotation_angle)
    )

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