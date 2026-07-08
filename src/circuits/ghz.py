"""GHZ state circuit builder."""

from __future__ import annotations

from qiskit import QuantumCircuit


def build_ghz_state(num_qubits: int = 3, measure: bool = False) -> QuantumCircuit:
    """
    Build a GHZ state circuit for the given number of qubits.

    The circuit prepares:
        (|000...0> + |111...1>) / sqrt(2)

    Args:
        num_qubits: Number of qubits in the GHZ state. Must be at least 2.
        measure: If True, add measurements to all qubits.

    Returns:
        A Qiskit QuantumCircuit representing the GHZ state.

    Raises:
        ValueError: If num_qubits is less than 2.
    """
    if num_qubits < 2:
        raise ValueError("GHZ state requires at least 2 qubits.")

    if measure:
        circuit = QuantumCircuit(num_qubits, num_qubits, name=f"ghz_{num_qubits}")
    else:
        circuit = QuantumCircuit(num_qubits, name=f"ghz_{num_qubits}")

    circuit.h(0)
    for qubit in range(num_qubits - 1):
        circuit.cx(qubit, qubit + 1)

    if measure:
        circuit.measure(range(num_qubits), range(num_qubits))

    return circuit