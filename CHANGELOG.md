# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

### In Progress
- Probabilistic Error Cancellation (PEC) — Mitiq integration
- Full Mitiq wiring for ZNE and PEC backends

### Planned
- Clifford Data Regression (CDR)
- Virtual Distillation
- Dynamical Decoupling
- Automated benchmarking suite
- Performance metrics module (fidelity, expectation values, sampling overhead)
- Unit and integration test suite
- Visualization dashboard

---

## [0.4.0] — 2025

### Added
- Python environment migrated from 3.13 to 3.12 for broader package compatibility
- Mitiq 1.0.0 and Cirq 1.6.1 installed and verified in the virtual environment
- `qiskit-env` virtualenv rebuilt from scratch under Python 3.12.13
- All previously pinned dependencies reinstalled and confirmed working under Python 3.12

### Notes
- NumPy pinned to 2.2.6 and SciPy to 1.17.1 to satisfy Mitiq 1.0.0 constraints
- All four core experiments (`bell`, `ghz`, `mem`, `zne`) verified end-to-end after migration

---

## [0.3.0] — 2025

### Added
- **Probabilistic Error Cancellation (PEC)** — custom correction-factor implementation in `src/mitigation/probabilistic_error_cancellation.py`
- PEC demo entry point `src/mitigation/pec.py` wired into `run.py` as `python run.py pec`
- `run.py` unified experiment launcher — all experiments runnable via a single CLI entry point
- `EXPERIMENTS` registry mapping short names to experiment `main()` functions

### Changed
- All experiment `noise_demos/` scripts refactored to expose a `main()` function for use by `run.py`
- `src/mitigation/mem_demo.py` and `src/mitigation/zne.py` likewise refactored to expose `main()`

---

## [0.2.0] — 2025

### Added
- **Measurement Error Mitigation (MEM)** — full implementation using 4×4 calibration matrix and matrix inversion
  - `src/mitigation/calibration.py` — calibration circuit builder for all 4 two-qubit basis states
  - `src/mitigation/measurement_error_mitigation.py` — `build_calibration_matrix` and `mitigate_counts`
  - `src/mitigation/mem_demo.py` — end-to-end MEM demo on Bell state with readout noise
- **Zero Noise Extrapolation (ZNE)** — linear extrapolation across noise scaling factors 1×, 2×, 3×
  - `src/mitigation/zero_noise_extrapolation.py` — `linear_extrapolation` and `calculate_expectation_value`
  - `src/mitigation/zne.py` — end-to-end ZNE demo on Bell state with depolarizing noise
- **ZNE plotter** — `src/plotting/zne_plotter.py` saves extrapolation graph to `results/figures/mitigated/`
- Results saved to structured `results/figures/` subdirectories: `ideal/`, `noisy/`, `mitigated/`

---

## [0.1.0] — 2025

### Added
- Initial project structure as a modular software framework
- **Circuits**
  - `src/circuits/bell_state.py` — reusable Bell state circuit builder
  - `src/circuits/ghz.py` — N-qubit GHZ state circuit builder
- **Noise models** (all in `src/noise_models/`)
  - `depolarizing_noise.py` — depolarizing error on H and CX gates
  - `amplitude_damping.py` — amplitude damping error on H and CX gates
  - `phase_damping.py` — phase damping error on H and CX gates
  - `readout_error.py` — symmetric readout error on all qubits
  - `coherent_gate_error.py` — coherent unitary error via RX rotation
  - `combined_noise.py` — depolarizing + amplitude damping + phase damping + readout combined
- **Simulator backend** — `src/backends/simulator.py` wrapping `AerSimulator` with optional noise model
- **Plotting utilities**
  - `src/plotting/circuit_plotter.py` — saves circuit diagrams as PNG
  - `src/plotting/histogram_plotter.py` — saves measurement histograms as PNG
- **Noise demo experiments** (all in `experiments/noise_demos/`)
  - `bell_state_demo.py`, `ghz_demo.py`
  - `depolarizing_noise_demo.py`, `readout_error_demo.py`, `phase_damping_demo.py`
  - `amplitude_damping_demo.py`, `coherent_gate_error_demo.py`, `combined_noise_demo.py`
- **Basics experiments** (`experiments/basics/`)
  - `hello_qubit.py`, `single_qubit_gates.py`, `multiqubit_gates.py`
  - `quantum_measurement.py`, `circuit_draw.py`
- **Notebook** — `notebooks/grovers_8q.ipynb` (Grover's algorithm, 8 qubits)
- `requirements.txt` with fully pinned dependencies
- MIT License
