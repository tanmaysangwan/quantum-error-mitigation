from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel


def run_circuit(
    circuit: QuantumCircuit,
    shots: int = 1024,
    noise_model: NoiseModel | None = None,
) -> dict:
    simulator = AerSimulator(noise_model=noise_model)

    result = simulator.run(circuit, shots=shots).result()

    return result.get_counts()