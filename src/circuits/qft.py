import numpy as np
from qiskit import QuantumCircuit


def create_qft(num_qubits: int) -> QuantumCircuit:
    """Build a QFT circuit starting from |+>^n input so noise produces measurable degradation.

    Input |+>^n (H on all qubits) followed by QFT produces a highly structured output
    concentrated near |0>, giving a clear ideal vs noisy contrast for benchmarking.
    """
    if num_qubits < 1:
        raise ValueError("QFT requires at least 1 qubit.")

    circuit = QuantumCircuit(num_qubits, num_qubits)

    # Prepare |+>^n input — without this, QFT on |0> gives uniform output regardless of noise.
    for q in range(num_qubits):
        circuit.h(q)

    # QFT layer.
    for target in range(num_qubits):
        circuit.h(target)
        for ctrl in range(target + 1, num_qubits):
            angle = np.pi / (2 ** (ctrl - target))
            circuit.cp(angle, ctrl, target)

    # Swap to standard QFT output ordering.
    for i in range(num_qubits // 2):
        circuit.swap(i, num_qubits - 1 - i)

    circuit.measure(range(num_qubits), range(num_qubits))
    return circuit
