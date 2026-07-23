"""Unit tests for src/metrics/metrics.py"""

import pytest
from src.metrics.metrics import error_reduction, fidelity, sampling_overhead, summarise


class TestErrorReduction:
    def test_perfect_mitigation(self):
        assert error_reduction(1.0, 0.8, 1.0) == pytest.approx(100.0)

    def test_no_improvement(self):
        assert error_reduction(1.0, 0.8, 0.8) == pytest.approx(0.0)

    def test_partial_improvement(self):
        result = error_reduction(1.0, 0.8, 0.9)
        assert result == pytest.approx(50.0)

    def test_no_noise(self):
        # ideal == noisy → no error to reduce, should return 0
        assert error_reduction(1.0, 1.0, 1.0) == pytest.approx(0.0)

    def test_negative_reduction(self):
        # mitigated is worse than noisy
        result = error_reduction(1.0, 0.9, 0.7)
        assert result < 0.0


class TestFidelity:
    def test_perfect(self):
        assert fidelity(1.0, 1.0) == pytest.approx(1.0)

    def test_zero_fidelity_clipped(self):
        # |mitigated - ideal| > 1 gets clipped to 0
        assert fidelity(1.0, -0.5) == pytest.approx(0.0)

    def test_partial(self):
        assert fidelity(1.0, 0.9) == pytest.approx(0.9)

    def test_symmetry(self):
        assert fidelity(0.8, 1.0) == pytest.approx(fidelity(1.0, 0.8))


class TestSamplingOverhead:
    def test_mem(self):
        assert sampling_overhead("MEM") == pytest.approx(5.0)

    def test_zne_default(self):
        assert sampling_overhead("ZNE") == pytest.approx(3.0)

    def test_zne_custom(self):
        assert sampling_overhead("ZNE", num_scale_factors=5) == pytest.approx(5.0)

    def test_pec(self):
        # gamma=2, n_gates=3 → 2^3 = 8
        assert sampling_overhead("PEC", gamma=2.0, n_gates=3) == pytest.approx(8.0)

    def test_cdr_default(self):
        assert sampling_overhead("CDR") == pytest.approx(11.0)

    def test_cdr_custom(self):
        assert sampling_overhead("CDR", num_training_circuits=20) == pytest.approx(21.0)

    def test_vd(self):
        assert sampling_overhead("VD") == pytest.approx(1.0)

    def test_dd_default(self):
        assert sampling_overhead("DD") == pytest.approx(10.0)

    def test_dd_custom(self):
        assert sampling_overhead("DD", num_trials=5) == pytest.approx(5.0)

    def test_unknown_technique(self):
        assert sampling_overhead("UNKNOWN") == pytest.approx(1.0)

    def test_case_insensitive(self):
        assert sampling_overhead("mem") == sampling_overhead("MEM")


class TestSummarise:
    def test_keys_present(self):
        row = summarise("ZNE", 1.0, 0.9, 0.95, 3.0)
        for key in ["technique", "ideal_ev", "noisy_ev", "mitigated_ev",
                    "error_before", "error_after", "error_reduction_%",
                    "fidelity", "sampling_overhead"]:
            assert key in row

    def test_values_correct(self):
        row = summarise("ZNE", 1.0, 0.8, 0.9, 3.0)
        assert row["error_before"] == pytest.approx(0.2, abs=1e-3)
        assert row["error_after"]  == pytest.approx(0.1, abs=1e-3)
        assert row["fidelity"]     == pytest.approx(0.9, abs=1e-3)
        assert row["sampling_overhead"] == pytest.approx(3.0)
        assert row["technique"] == "ZNE"
