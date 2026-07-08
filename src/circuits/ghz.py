from qiskit import QuantumCircuit


def create_ghz_state(num_qubits: int) -> QuantumCircuit:
    if num_qubits < 2:
        raise ValueError("GHZ state requires at least 2 qubits.")

    circuit = QuantumCircuit(num_qubits, num_qubits)

    circuit.h(0)

    for qubit in range(num_qubits - 1):
        circuit.cx(qubit, qubit + 1)

    circuit.measure(range(num_qubits), range(num_qubits))

    return circuit