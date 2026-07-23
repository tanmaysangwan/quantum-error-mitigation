"""Unit tests for src/circuits/ — circuit structure and measurement checks."""

import pytest
from qiskit import QuantumCircuit

from src.circuits.bell_state import create_bell_state
from src.circuits.ghz import create_ghz_state
from src.circuits.qft import create_qft
from src.circuits.qaoa import create_qaoa, qaoa_cut_value
from src.circuits.vqe import create_vqe_ansatz, build_vqe_circuit
import numpy as np


class TestBellState:
    def test_is_circuit(self):
        assert isinstance(create_bell_state(), QuantumCircuit)

    def test_qubit_count(self):
        assert create_bell_state().num_qubits == 2

    def test_has_measurements(self):
        gates = [i.operation.name for i in create_bell_state().data]
        assert "measure" in gates


class TestGHZ:
    @pytest.mark.parametrize("n", [2, 3, 5, 8])
    def test_qubit_count(self, n):
        assert create_ghz_state(n).num_qubits == n

    def test_has_measurements(self):
        gates = [i.operation.name for i in create_ghz_state(3).data]
        assert "measure" in gates

    def test_too_few_qubits(self):
        with pytest.raises(ValueError):
            create_ghz_state(1)


class TestQFT:
    @pytest.mark.parametrize("n", [2, 3, 5])
    def test_qubit_count(self, n):
        assert create_qft(n).num_qubits == n

    def test_has_measurements(self):
        gates = [i.operation.name for i in create_qft(3).data]
        assert "measure" in gates

    def test_too_few_qubits(self):
        with pytest.raises(ValueError):
            create_qft(0)


class TestQAOA:
    def test_default_qubit_count(self):
        assert create_qaoa().num_qubits == 4

    def test_has_measurements(self):
        gates = [i.operation.name for i in create_qaoa().data]
        assert "measure" in gates

    def test_too_few_qubits(self):
        with pytest.raises(ValueError):
            create_qaoa(num_qubits=1)

    def test_edge_weight_mismatch(self):
        with pytest.raises(ValueError):
            create_qaoa(edges=[(0, 1)], weights=[1.0, 2.0])

    def test_cut_value_range(self):
        counts = {"0101": 500, "1010": 500}
        val = qaoa_cut_value(counts)
        assert 0.0 <= val <= 4.0

    def test_cut_value_max_cut(self):
        # |0101> and |1010> are max-cut bitstrings for C4 → cut = 4
        assert qaoa_cut_value({"0101": 1}) == pytest.approx(4.0)
        assert qaoa_cut_value({"1010": 1}) == pytest.approx(4.0)

    def test_cut_value_zero_cut(self):
        # |0000> → all same partition → cut = 0
        assert qaoa_cut_value({"0000": 1}) == pytest.approx(0.0)

    def test_cut_value_empty_counts(self):
        assert qaoa_cut_value({}) == pytest.approx(0.0)


class TestVQE:
    def test_ansatz_is_circuit(self):
        assert isinstance(create_vqe_ansatz(), QuantumCircuit)

    def test_ansatz_qubit_count(self):
        assert create_vqe_ansatz().num_qubits == 2

    def test_ansatz_has_parameters(self):
        assert create_vqe_ansatz().num_parameters > 0

    def test_build_vqe_circuit_has_measurements(self):
        params = np.zeros(create_vqe_ansatz().num_parameters)
        circuit = build_vqe_circuit(params)
        gates = [i.operation.name for i in circuit.data]
        assert "measure" in gates

    def test_build_vqe_circuit_no_free_parameters(self):
        params = np.zeros(create_vqe_ansatz().num_parameters)
        circuit = build_vqe_circuit(params)
        assert circuit.num_parameters == 0
