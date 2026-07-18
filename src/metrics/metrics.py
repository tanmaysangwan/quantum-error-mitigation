import time
from typing import Callable

import numpy as np


def error_reduction(ideal_ev: float, noisy_ev: float, mitigated_ev: float) -> float:
    """Percentage reduction in error after mitigation. Returns 0 if no noise."""
    error_before = abs(noisy_ev - ideal_ev)
    error_after  = abs(mitigated_ev - ideal_ev)
    if error_before < 1e-10:
        return 0.0
    return (1.0 - error_after / error_before) * 100.0


def fidelity(ideal_ev: float, mitigated_ev: float) -> float:
    """Scalar fidelity: 1 - |mitigated - ideal|. Range [0, 1]."""
    return float(np.clip(1.0 - abs(mitigated_ev - ideal_ev), 0.0, 1.0))


def sampling_overhead(technique: str, **kwargs) -> float:
    """Return the circuit execution multiplier relative to an unmitigated run.

    MEM:  1 + 4 calibration circuits (one per basis state)
    ZNE:  number of noise scale factors used
    PEC:  gamma^n_gates (grows with noise level)
    CDR:  1 + num_training_circuits
    VD:   1 (single circuit run, just more shots)
    DD:   num_trials (averaged over multiple DD insertions)
    """
    technique = technique.upper()
    if technique == "MEM":
        return 1.0 + 4.0
    if technique == "ZNE":
        return float(kwargs.get("num_scale_factors", 3))
    if technique == "PEC":
        gamma  = kwargs.get("gamma", 1.0)
        n_gates = kwargs.get("n_gates", 3)
        return float(gamma ** n_gates)
    if technique == "CDR":
        return 1.0 + float(kwargs.get("num_training_circuits", 10))
    if technique == "VD":
        return 1.0
    if technique == "DD":
        return float(kwargs.get("num_trials", 10))
    return 1.0


def runtime_overhead(fn: Callable, baseline_fn: Callable) -> tuple[float, float, float]:
    """Measure wall-clock time of fn and baseline_fn. Returns (baseline_s, mitigated_s, ratio)."""
    t0 = time.perf_counter()
    baseline_fn()
    baseline_time = time.perf_counter() - t0

    t0 = time.perf_counter()
    fn()
    mitigated_time = time.perf_counter() - t0

    ratio = mitigated_time / baseline_time if baseline_time > 1e-9 else float("inf")
    return baseline_time, mitigated_time, ratio


def summarise(
    technique: str,
    ideal_ev: float,
    noisy_ev: float,
    mitigated_ev: float,
    overhead: float,
) -> dict:
    """Return a single flat dict with all metrics for one technique at one noise level."""
    return {
        "technique":        technique,
        "ideal_ev":         round(ideal_ev, 4),
        "noisy_ev":         round(noisy_ev, 4),
        "mitigated_ev":     round(mitigated_ev, 4),
        "error_before":     round(abs(noisy_ev - ideal_ev), 4),
        "error_after":      round(abs(mitigated_ev - ideal_ev), 4),
        "error_reduction_%": round(error_reduction(ideal_ev, noisy_ev, mitigated_ev), 1),
        "fidelity":         round(fidelity(ideal_ev, mitigated_ev), 4),
        "sampling_overhead": round(overhead, 3),
    }
