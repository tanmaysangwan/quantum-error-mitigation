"""Unit tests for src/mitigation/ — verify each technique returns values in the correct range
and improves (or at minimum does not wildly worsen) the expectation value under noise."""

import pytest
import numpy as np

from src.backends.simulator import run_circuit
from src.circuits.bell_state import create_bell_state
from src.noise_models.depolarizing_noise import create_depolarizing_noise_model
from src.noise_models.readout_error import create_readout_error_model

from src.mitigation.zero_noise_extrapolation import (
    fold_gates, linear_extrapolation, richardson_extrapolation, calculate_expectation_value,
)
from src.mitigation.measurement_error_mitigation import build_calibration_matrix, mitigate_counts
from src.mitigation.probabilistic_error_cancellation import (
    build_quasi_probability_representation, zz_expectation, run_pec,
)
from src.mitigation.clifford_data_regression import run_cdr
from src.mitigation.virtual_distillation import run_virtual_distillation
from src.mitigation.dynamical_decoupling import run_dynamical_decoupling


NOISE_LEVEL = 0.05
SHOTS       = 1024


@pytest.fixture(scope="module")
def bell():
    return create_bell_state()


@pytest.fixture(scope="module")
def noise_model():
    return create_depolarizing_noise_model(NOISE_LEVEL)


# ---------------------------------------------------------------------------
# ZNE
# ---------------------------------------------------------------------------

class TestZNE:
    def test_fold_gates_scale_1_unchanged(self, bell):
        folded = fold_gates(bell, 1)
        # Same gate count (excluding measures)
        orig_gates   = [i for i in bell.data  if i.operation.name != "measure"]
        folded_gates = [i for i in folded.data if i.operation.name != "measure"]
        assert len(orig_gates) == len(folded_gates)

    def test_fold_gates_scale_3_longer(self, bell):
        folded = fold_gates(bell, 3)
        orig_gates   = [i for i in bell.data  if i.operation.name != "measure"]
        folded_gates = [i for i in folded.data if i.operation.name != "measure"]
        assert len(folded_gates) == 3 * len(orig_gates)

    def test_fold_gates_even_raises(self, bell):
        with pytest.raises(ValueError):
            fold_gates(bell, 2)

    def test_linear_extrapolation(self):
        # Perfectly linear data → intercept should be exact
        noise_factors = [1, 3, 5]
        evs = [0.9, 0.7, 0.5]   # linear: ev = 1.0 - 0.1*noise
        result = linear_extrapolation(noise_factors, evs)
        assert result == pytest.approx(1.0, abs=0.01)

    def test_richardson_extrapolation_two_points(self):
        # With 2 points Richardson cancels leading linear term
        result = richardson_extrapolation([1, 3], [0.9, 0.7])
        assert isinstance(result, float)

    def test_richardson_extrapolation_requires_two_points(self):
        with pytest.raises(ValueError):
            richardson_extrapolation([1], [0.9])

    def test_calculate_expectation_value_bell(self):
        ev = calculate_expectation_value({"00": 500, "11": 500})
        assert ev == pytest.approx(1.0)

    def test_calculate_expectation_value_empty(self):
        assert calculate_expectation_value({}) == pytest.approx(0.0)

    def test_zne_output_in_range(self, bell, noise_model):
        evs = [calculate_expectation_value(
                   run_circuit(fold_gates(bell, sf), noise_model=noise_model, shots=SHOTS))
               for sf in [1, 3, 5]]
        result = richardson_extrapolation([1, 3, 5], evs)
        # Richardson extrapolation can overshoot slightly due to shot noise —
        # allow a 10% tolerance beyond the theoretical [-1, 1] range.
        assert -1.1 <= result <= 1.1


# ---------------------------------------------------------------------------
# MEM
# ---------------------------------------------------------------------------

class TestMEM:
    def test_calibration_matrix_shape(self):
        nm = create_readout_error_model(0.05)
        mat, states = build_calibration_matrix(nm, num_qubits=2)
        assert mat.shape == (4, 4)
        assert len(states) == 4

    def test_calibration_matrix_columns_sum_to_one(self):
        nm = create_readout_error_model(0.05)
        mat, _ = build_calibration_matrix(nm, num_qubits=2)
        col_sums = mat.sum(axis=0)
        np.testing.assert_allclose(col_sums, np.ones(4), atol=0.05)

    def test_mitigate_counts_returns_dict(self, bell):
        nm = create_readout_error_model(0.05)
        noisy_counts = run_circuit(bell, noise_model=nm, shots=SHOTS)
        mat, states = build_calibration_matrix(nm, num_qubits=2)
        result = mitigate_counts(noisy_counts, mat, states=states)
        assert isinstance(result, dict)

    def test_mitigate_counts_nonnegative(self, bell):
        nm = create_readout_error_model(0.05)
        noisy_counts = run_circuit(bell, noise_model=nm, shots=SHOTS)
        mat, states = build_calibration_matrix(nm, num_qubits=2)
        result = mitigate_counts(noisy_counts, mat, states=states)
        assert all(v >= 0 for v in result.values())


# ---------------------------------------------------------------------------
# PEC helpers
# ---------------------------------------------------------------------------

class TestPECHelpers:
    def test_zz_expectation_bell_ideal(self):
        assert zz_expectation({"00": 500, "11": 500}) == pytest.approx(1.0)

    def test_zz_expectation_anti_bell(self):
        assert zz_expectation({"01": 500, "10": 500}) == pytest.approx(-1.0)

    def test_zz_expectation_empty(self):
        assert zz_expectation({}) == pytest.approx(0.0)

    def test_qpr_gamma_positive(self):
        qpr = build_quasi_probability_representation(0.05)
        assert qpr["gamma"] > 0

    def test_qpr_probabilities_sum_to_one(self):
        qpr = build_quasi_probability_representation(0.05)
        total = sum(qpr["probabilities"].values())
        assert total == pytest.approx(1.0, abs=1e-6)

    def test_qpr_zero_noise(self):
        qpr = build_quasi_probability_representation(0.0)
        assert qpr["gamma"] >= 1.0

    def test_pec_output_in_range(self, bell, noise_model):
        result = run_pec(bell, noise_model, NOISE_LEVEL, num_samples=50, shots=512)
        assert -1.0 <= result <= 1.0


# ---------------------------------------------------------------------------
# CDR
# ---------------------------------------------------------------------------

class TestCDR:
    def test_output_in_range(self, bell, noise_model):
        result = run_cdr(bell, noise_model, num_training_circuits=5, shots=512)
        assert -1.5 <= result <= 1.5  # CDR can extrapolate slightly outside [-1,1]

    def test_output_is_float(self, bell, noise_model):
        result = run_cdr(bell, noise_model, num_training_circuits=5, shots=512)
        assert isinstance(result, float)


# ---------------------------------------------------------------------------
# VD
# ---------------------------------------------------------------------------

class TestVD:
    def test_output_in_range_bell(self, bell, noise_model):
        result = run_virtual_distillation(bell, noise_model=noise_model, shots=4096)
        assert -1.0 <= result <= 1.0

    def test_output_closer_to_ideal_than_noisy(self, bell, noise_model):
        ideal_ev  = zz_expectation(run_circuit(bell, shots=4096))
        noisy_ev  = zz_expectation(run_circuit(bell, shots=4096, noise_model=noise_model))
        vd_ev     = run_virtual_distillation(bell, noise_model=noise_model, shots=8192)
        assert abs(vd_ev - ideal_ev) <= abs(noisy_ev - ideal_ev) + 0.1  # tolerance for shot noise

    def test_custom_observable(self, bell, noise_model):
        # observable that always returns 0.5 → VD should return 0.5
        result = run_virtual_distillation(bell, noise_model=noise_model,
                                          shots=2048, observable=lambda s: 0.5)
        assert result == pytest.approx(0.5, abs=1e-6)


# ---------------------------------------------------------------------------
# DD
# ---------------------------------------------------------------------------

class TestDD:
    def test_output_is_float(self, bell, noise_model):
        result = run_dynamical_decoupling(bell, noise_model, rule="xx",
                                          num_trials=3, shots=512)
        assert isinstance(result, float)

    def test_output_in_range(self, bell, noise_model):
        result = run_dynamical_decoupling(bell, noise_model, rule="xyxy",
                                          num_trials=3, shots=512)
        assert -1.0 <= result <= 1.0
