from qiskit import QuantumCircuit  # Builds calibration circuits.

CALIBRATION_STATES = ("00", "01", "10", "11")  # Bell-state calibration order.


def create_calibration_circuit(bitstring: str) -> QuantumCircuit:
    if len(bitstring) != 2 or any(bit not in "01" for bit in bitstring):  # Keep the calibration input valid.
        raise ValueError("Calibration bitstring must be one of: 00, 01, 10, 11.")

    circuit = QuantumCircuit(2, 2) 

    for qubit, bit in enumerate(reversed(bitstring)):  # Match Qiskit's bit ordering.
        if bit == "1":
            circuit.x(qubit)  # Applies X gate whenever qubit needs t be |1>

    circuit.measure([0, 1], [0, 1])  # Measure both qubits.
    return circuit


def create_bell_calibration_circuits() -> dict[str, QuantumCircuit]:
    return {state: create_calibration_circuit(state) for state in CALIBRATION_STATES}  # Build all four Bell calibration circuits.