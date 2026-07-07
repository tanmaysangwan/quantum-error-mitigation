# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

### Planned
- Zero Noise Extrapolation (ZNE) — full Mitiq integration
- Probabilistic Error Cancellation (PEC) — full implementation
- Clifford Data Regression (CDR)
- Virtual Distillation
- Dynamical Decoupling
- Automated benchmarking runner
- Performance metrics module (fidelity, expectation values, sampling overhead)
- Visualization dashboard

---

## [0.1.0] — 2025

### Added
- Initial project structure as a professional software framework
- Noise model implementations: amplitude damping, coherent gate error,
  combined noise, depolarizing noise, phase damping, readout error
- Error mitigation prototypes: MEM (matrix inversion), ZNE (linear extrapolation),
  PEC (weighted sampling concept)
- Experiment scripts: Bell state, Hadamard, HZH gate, noise injection demos,
  amplitude damping demo
- Grover's algorithm notebook (8 qubits)
- Basics module: single qubit gates, multi-qubit gates, measurement, circuit drawing
- `requirements.txt` with pinned dependencies
