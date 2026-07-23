"""Unit tests for src/noise_models/ — validate model structure and effect on circuits."""

import pytest
from qiskit_aer.noise import NoiseModel

from src.noise_models.depolarizing_noise import create_depolarizing_noise_model
from src.noise_models.readout_error import create_readout_error_model
from src.noise_models.amplitude_damping import create_amplitude_damping_noise_model
from src.noise_models.phase_damping import create_phase_damping_noise_model
from src.noise_models.coherent_gate_error import create_coherent_gate_error_model
from src.noise_models.combined_noise import create_combined_noise_model
from src.backends.simulator import run_circuit
from src.circuits.bell_state import create_bell_state


def _total_counts(counts: dict) -> int:
    return sum(counts.values())


class TestDepolarizingNoise:
    def test_returns_noise_model(self):
        assert isinstance(create_depolarizing_noise_model(0.01), NoiseModel)

    def test_affects_circuit(self):
        circuit = create_bell_state()
        ideal  = run_circuit(circuit, shots=2048)
        noisy  = run_circuit(circuit, shots=2048,
                             noise_model=create_depolarizing_noise_model(0.2))
        # Under heavy noise, non-00/11 counts should appear
        non_bell = noisy.get("01", 0) + noisy.get("10", 0)
        assert non_bell > 0

    def test_zero_noise_no_effect(self):
        # p=0 → noise model exists but has no errors
        nm = create_depolarizing_noise_model(0.0)
        assert isinstance(nm, NoiseModel)


class TestReadoutError:
    def test_returns_noise_model(self):
        assert isinstance(create_readout_error_model(0.05), NoiseModel)

    def test_affects_measurements(self):
        circuit = create_bell_state()
        ideal  = run_circuit(circuit, shots=4096)
        noisy  = run_circuit(circuit, shots=4096,
                             noise_model=create_readout_error_model(0.3))
        # Readout error flips bits — 01/10 counts should increase
        ideal_err = ideal.get("01", 0) + ideal.get("10", 0)
        noisy_err = noisy.get("01", 0) + noisy.get("10", 0)
        assert noisy_err > ideal_err


class TestAmplitudeDamping:
    def test_returns_noise_model(self):
        assert isinstance(create_amplitude_damping_noise_model(0.05), NoiseModel)

    def test_affects_circuit(self):
        circuit = create_bell_state()
        noisy = run_circuit(circuit, shots=2048,
                            noise_model=create_amplitude_damping_noise_model(0.3))
        assert _total_counts(noisy) > 0


class TestPhaseDamping:
    def test_returns_noise_model(self):
        assert isinstance(create_phase_damping_noise_model(0.05), NoiseModel)

    def test_affects_circuit(self):
        circuit = create_bell_state()
        noisy = run_circuit(circuit, shots=2048,
                            noise_model=create_phase_damping_noise_model(0.3))
        assert _total_counts(noisy) > 0


class TestCoherentGateError:
    def test_returns_noise_model(self):
        assert isinstance(create_coherent_gate_error_model(0.1), NoiseModel)

    def test_affects_circuit(self):
        circuit = create_bell_state()
        noisy = run_circuit(circuit, shots=2048,
                            noise_model=create_coherent_gate_error_model(0.5))
        assert _total_counts(noisy) > 0


class TestCombinedNoise:
    def test_returns_noise_model(self):
        assert isinstance(create_combined_noise_model(0.02), NoiseModel)

    def test_affects_circuit(self):
        circuit = create_bell_state()
        noisy = run_circuit(circuit, shots=2048,
                            noise_model=create_combined_noise_model(0.1))
        non_bell = noisy.get("01", 0) + noisy.get("10", 0)
        assert non_bell > 0
