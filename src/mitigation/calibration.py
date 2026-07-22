from qiskit import QuantumCircuit

CALIBRATION_STATES = ("00", "01", "10", "11")  # Default 2-qubit states for backwards compatibility


def create_calibration_circuit(bitstring: str) -> QuantumCircuit:
    """Create a calibration circuit that prepares the computational basis state defined by bitstring."""
    n_qubits = len(bitstring)
    circuit = QuantumCircuit(n_qubits, n_qubits)

    for qubit, bit in enumerate(reversed(bitstring)):  # Match Qiskit's bit ordering
        if bit == "1":
            circuit.x(qubit)

    circuit.measure(range(n_qubits), range(n_qubits))
    return circuit


def create_calibration_circuits(num_qubits: int = 2) -> tuple[list[str], dict[str, QuantumCircuit]]:
    """Return ordered list of basis bitstrings and dict of calibration circuits for N qubits."""
    states = [format(i, f"0{num_qubits}b") for i in range(2**num_qubits)]
    circuits = {state: create_calibration_circuit(state) for state in states}
    return states, circuits


def create_bell_calibration_circuits() -> dict[str, QuantumCircuit]:
    """Backwards compatible 2-qubit calibration circuits."""
    _, circuits = create_calibration_circuits(2)
    return circuits