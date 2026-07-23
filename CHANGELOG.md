# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

### Notes
- The core internship project is complete. Remaining work is research extension work, not
  unfinished implementation.
- Real hardware execution, calibrated T1/T2 backend modeling, QAOA p>1, VQD, and
  noise-adaptive PEC are future research directions.

---

## [1.0.0] - 2026-07

### Added
- Completed all four planned project phases:
  - Phase I: literature review and six NISQ noise models.
  - Phase II: six Quantum Error Mitigation techniques and reusable metrics.
  - Phase III: automated benchmark suite over Bell, GHZ, QFT, QAOA, and VQE.
  - Phase IV: performance analysis, scalability study, and final project documentation.
- Added full benchmark coverage for 145 experiment configurations:
  - Bell, GHZ-3, QFT-3, and QAOA-C4 across six techniques and five noise levels.
  - VQE H2 across five applicable techniques and five noise levels.
- Added `src/benchmarks/benchmark.py` for automated CSV generation.
- Added `src/benchmarks/visualise.py` for comparison plots and heatmaps.
- Added `src/benchmarks/scalability.py` for ZNE vs VD scaling from 2 to 8 qubits.
- Added QFT, QAOA-C4, and VQE benchmark circuits.
- Added counts-based VQE support through `build_vqe_circuit()`.
- Added QAOA-C4 Max-Cut observable support through `qaoa_cut_value()`.
- Added final benchmark data at `results/data/benchmark_results.csv`.
- Added final report at `docs/report/final_project_report.md`.
- Added literature review at `docs/literature/literature_review.md`.
- Added comparative performance study at `results/reports/comparative_performance_study.md`.
- Added 89 pytest tests covering circuits, metrics, mitigation functions, and noise models.

### Changed
- Updated ZNE to use gate folding with scale factors 1x, 3x, and 5x.
- Added Richardson extrapolation alongside linear extrapolation.
- Replaced the early PEC heuristic with a Mitiq quasi-probability sampling workflow.
- Generalized mitigation functions to accept circuit-specific evaluator or observable callbacks.
- Updated the benchmark to use circuit-appropriate observable ranges:
  - Bell: ZZ expectation in `[-1, 1]`.
  - GHZ/QFT: probability-style observables in `[0, 1]`.
  - QAOA-C4: expected cut value in `[0, 4]`.
  - VQE: energy path for ZNE and counts-based ZZ proxy for other applicable methods.
- Updated `run.py` so all demos, benchmarks, visualisation, scalability, and tests are available
  through `python run.py <name>`.
- Updated project documentation to state the final completed status.

### Fixed
- Removed deprecated Qiskit `CircuitInstruction` tuple-unpacking in ZNE by using
  `instr.operation`, `instr.qubits`, and `instr.clbits`.
- Fixed QAOA benchmark design by switching from a weak K3 test case to C4 Max-Cut with
  numerically selected p=1 angles.
- Fixed QAOA bitstring handling for Mitiq/Cirq-style spaced bitstrings.
- Fixed stale project-status text in README and changelog.
- Confirmed test suite passes with `89 passed`.

### Known Limitations
- Results are based on Qiskit Aer simulation rather than real quantum hardware.
- The reported `fidelity` metric is an observable-level fidelity proxy, not full state fidelity.
- DD is evaluated primarily under depolarizing noise, while it is more appropriate for
  dephasing-dominated T2 noise.
- PEC uses limited Monte Carlo samples in the benchmark, so high-noise PEC results include
  estimator variance.
- VQE uses mixed evaluation paths: ZNE uses Hamiltonian energy estimation, while MEM/CDR/VD/DD
  use a counts-based ZZ observable proxy.

---

## [0.4.0] - 2025-07

### Added
- Code audit for Phase I and early Phase II implementation.
- README project status table and technology table.
- Phase II completion checklist.

### Notes
- Early PEC implementation was identified as a correction heuristic rather than full
  quasi-probability PEC.
- ZNE still used simple noise scaling at this stage; gate folding was planned.

---

## [0.3.1] - 2025

### Notes
- Python environment confirmed stable under Python 3.12.13.
- Early experiments verified end-to-end: `bell`, `ghz`, `mem`, `zne`, and `pec`.
- Result figures saved under `results/figures/`.

---

## [0.3.0] - 2025

### Added
- Early Probabilistic Error Cancellation demo.
- PEC demo entry point wired into `run.py`.
- Unified experiment launcher through `run.py`.
- Experiment registry mapping short names to `main()` functions.

### Changed
- Refactored noise demo scripts to expose `main()`.
- Refactored MEM and ZNE demos to expose `main()`.

---

## [0.2.0] - 2025

### Added
- Measurement Error Mitigation using calibration matrix inversion.
- Calibration circuit generation for two-qubit basis states.
- Zero Noise Extrapolation prototype.
- ZNE plotting helper.
- Structured result figure folders.

---

## [0.1.0] - 2025

### Added
- Initial project structure.
- Bell and GHZ circuit builders.
- First set of noise models:
  - Depolarizing noise.
  - Amplitude damping.
  - Phase damping.
  - Readout error.
  - Coherent gate error.
  - Combined noise.
- Qiskit Aer simulator backend wrapper.
- Circuit and histogram plotting helpers.
- Introductory Qiskit experiments.
- Grover's algorithm exploratory notebook.
- Fully pinned `requirements.txt`.
- MIT License.
