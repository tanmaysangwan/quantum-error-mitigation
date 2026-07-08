from qiskit.circuit.library import RZGate
from qiskit_aer.noise import NoiseModel, coherent_unitary_error


def create_coherent_gate_error_model(rotation_angle: float) -> NoiseModel:

    noise_model = NoiseModel()

    coherent_error = coherent_unitary_error(
        RZGate(rotation_angle)
    )

    noise_model.add_all_qubit_quantum_error(
        coherent_error,
        ["h"]
    )

    return noise_model