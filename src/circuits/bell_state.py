"""
bell_state.py

Reusable Bell State circuit builder.

This module provides a function to create a Bell State quantum circuit
that can be reused across experiments, benchmarks, and error mitigation
techniques.
"""

from qiskit import QuantumCircuit


def create_bell_state() -> QuantumCircuit:
    circuit = QuantumCircuit(2, 2)

    circuit.h(0)

    circuit.cx(0, 1)

    circuit.measure([0, 1], [0, 1])

    return circuit