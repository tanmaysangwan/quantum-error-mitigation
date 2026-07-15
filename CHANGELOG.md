# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

### In Progress
- Probabilistic Error Cancellation (PEC) — replacing custom correction heuristic with proper
  quasi-probability implementation via Mitiq
- ZNE upgrade — circuit folding for gate-level noise amplification; Richardson/polynomial extrapolation

### Planned (Phase II completion)
- Clifford Data Regression (CDR) via Mitiq
- Metrics module: fidelity, expectation value accuracy, error reduction %, sampling overhead
- Fix: remove duplicate `plt.show()` in `zne_plotter.py`
- Unit tests for all mitigation functions

### Planned (Phase III & IV)
- QFT, VQE, QAOA benchmark circuits
- Automated benchmarking suite across noise levels and circuit depths
- Performance comparison table (ZNE vs PEC vs MEM vs CDR)
- Dynamical Decoupling
- Virtual Distillation
- Visualization dashboard

---

## [0.4.0] — 2025-07

### Added
- Code audit completed — full review of all Phase I and Phase II implementation against
  project specification; issues identified and documented in Phase II completion checklist
- README updated — project status table, Phase II checklist, technologies table updated
- CHANGELOG updated to reflect current state and remaining work

### Notes
- PEC custom correction scheme confirmed as a heuristic approximation, not true
  quasi-probability PEC; replacement with Mitiq PEC is the next priority
- ZNE circuit uses error-probability scaling rather than circuit folding; upgrade planned

---

## [0.3.1] — 2025

### Notes
- Python environment confirmed stable under 3.12.13
- All five experiments (`bell`, `ghz`, `mem`, `zne`, `pec`) verified end-to-end
- Result figures saved to `results/figures/ideal/`, `noisy/`, and `mitigated/`

---

## [0.3.0] — 2025

### Added
- **Probabilistic Error Cancellation (PEC)** — custom correction-factor implementation
  in `src/mitigation/probabilistic_error_cancellation.py`
- PEC demo entry point `src/mitigation/pec.py` wired into `run.py` as `python run.py pec`
- `run.py` unified experiment launcher — all experiments runnable via a single CLI entry point
- `EXPERIMENTS` registry mapping short names to experiment `main()` functions

### Changed
- All `experiments/noise_demos/` scripts refactored to expose a `main()` function
- `src/mitigation/mem_demo.py` and `src/mitigation/zne.py` likewise refactored to expose `main()`

---

## [0.2.0] — 2025

### Added
- **Measurement Error Mitigation (MEM)** — full implementation using 4×4 calibration matrix
  and matrix inversion
  - `src/mitigation/calibration.py` — calibration circuit builder for all 4 two-qubit basis states
  - `src/mitigation/measurement_error_mitigation.py` — `build_calibration_matrix` and
    `mitigate_counts`
  - `src/mitigation/mem_demo.py` — end-to-end MEM demo on Bell state with readout noise
- **Zero Noise Extrapolation (ZNE)** — linear extrapolation across noise scaling factors 1×, 2×, 3×
  - `src/mitigation/zero_noise_extrapolation.py` — `linear_extrapolation` and
    `calculate_expectation_value`
  - `src/mitigation/zne.py` — end-to-end ZNE demo on Bell state with depolarizing noise
- **ZNE plotter** — `src/plotting/zne_plotter.py` saves extrapolation graph to
  `results/figures/mitigated/`
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
- **Simulator backend** — `src/backends/simulator.py` wrapping `AerSimulator` with optional
  noise model
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
