# Quantum Error Mitigation Framework

A Python framework for implementing, studying, and comparing Quantum Error Mitigation (QEM) techniques for NISQ-era quantum computers.

Built with [Qiskit](https://www.ibm.com/quantum/qiskit), [Qiskit Aer](https://github.com/Qiskit/qiskit-aer), and [Mitiq](https://mitiq.readthedocs.io/) as part of an internship research project at DRDO, SAG Lab.

---

## Project Status

| Phase | Description | Status |
|-------|-------------|--------|
| Phase I  | Literature review + all 6 noise models implemented | ✅ Complete |
| Phase II | All 6 mitigation techniques implemented + metrics module | ✅ Complete |
| Phase III | Benchmarking — Bell, GHZ, QFT, VQE, QAOA circuits | 🔄 In Progress |
| Phase IV | Performance analysis, comparison study, scalability | 🔄 In Progress |

---

## Objectives

1. Study and model common noise sources on NISQ devices.
2. Implement all major Quantum Error Mitigation techniques.
3. Benchmark mitigation methods against standard quantum algorithms.
4. Analyze trade-offs between accuracy improvement and computational overhead.
5. Recommend suitable techniques for practical quantum applications.

---

## Repository Structure

```
quantum-error-mitigation/
│
├── src/
│   ├── circuits/          # Circuit builders: Bell, GHZ, QFT, VQE ansatz, QAOA
│   ├── noise_models/      # Six noise model implementations
│   ├── mitigation/        # All 6 QEM technique implementations + demo entry points
│   ├── backends/          # AerSimulator wrapper (run_circuit)
│   ├── plotting/          # Circuit, histogram, and ZNE plot utilities
│   ├── benchmarks/        # Automated benchmark suite + visualisation
│   ├── metrics/           # Fidelity, error reduction, sampling overhead metrics
│   └── common/            # Shared utilities
│
├── experiments/
│   ├── basics/            # Introductory Qiskit scripts (gates, measurement, drawing)
│   ├── noise_demos/       # Standalone noise demonstration scripts
│   ├── vqe_demo.py        # VQE H2 ground state energy with ZNE mitigation
│   └── qaoa_demo.py       # QAOA Max-Cut on 3-node triangle graph with ZNE mitigation
│
├── notebooks/
│   └── grovers_8q.ipynb   # Grover's algorithm (8 qubits)
│
├── tests/                 # Unit tests (in progress)
├── data/
│   ├── raw/
│   └── processed/
├── results/
│   ├── figures/
│   │   ├── ideal/         # Circuit diagrams and ideal histograms
│   │   ├── noisy/         # Noisy simulation histograms
│   │   ├── mitigated/     # Post-mitigation comparison plots
│   │   └── comparison/    # Benchmark heatmaps, fidelity lines, overhead charts
│   ├── data/
│   │   └── benchmark_results.csv   # Full results: 6 techniques × 3 circuits × 5 noise levels
│   └── reports/
├── docs/
│   ├── literature/
│   ├── notes/
│   └── report/
│
├── run.py                 # Unified CLI launcher for all experiments
├── requirements.txt
├── LICENSE
├── CONTRIBUTING.md
└── CHANGELOG.md
```

---

## Installation

### Prerequisites

- macOS or Linux
- Python 3.12

### Setup

```bash
git clone <repository-url>
cd quantum-error-mitigation

python3.12 -m venv qiskit-env
source qiskit-env/bin/activate

pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

---

## Running Experiments

All experiments are launched through `run.py`. Activate the virtual environment first:

```bash
source qiskit-env/bin/activate
```

### Noise Model Demonstrations

```bash
python run.py bell          # Bell state — ideal simulation
python run.py ghz           # GHZ state (3 qubits) — ideal simulation
python run.py depolarizing  # Depolarizing noise on Bell state
python run.py readout       # Readout (measurement) error on Bell state
python run.py phase         # Phase damping on Bell state
python run.py amplitude     # Amplitude damping on Bell state
python run.py coherent      # Coherent gate error on Bell state
python run.py combined      # All noise types combined on Bell state
```

### Error Mitigation Experiments

```bash
python run.py mem           # Measurement Error Mitigation
python run.py zne           # Zero Noise Extrapolation (circuit folding + Richardson)
python run.py pec           # Probabilistic Error Cancellation (Mitiq quasi-probability)
python run.py cdr           # Clifford Data Regression (Mitiq)
python run.py vd            # Virtual Distillation
python run.py dd            # Dynamical Decoupling (XX and XYXY sequences)
```

### Algorithm Benchmarks

```bash
python run.py vqe           # VQE — H2 ground state energy (ideal vs noisy vs ZNE)
python run.py qaoa          # QAOA — Max-Cut on 3-node triangle graph (ideal vs noisy vs ZNE)
```

### Full Benchmark Suite

```bash
python run.py benchmark     # All 6 techniques × Bell/GHZ/QFT × 5 noise levels → CSV
python run.py visualise     # Generate heatmaps, fidelity plots, overhead charts from CSV
```

---

## Implemented Features

### Circuits (`src/circuits/`)

| Circuit | Qubits | Description |
|---------|--------|-------------|
| Bell state | 2 | Maximally entangled 2-qubit state (H + CX) |
| GHZ state | N | N-qubit generalisation of Bell state |
| QFT | N | Quantum Fourier Transform on \|+⟩^N input |
| VQE ansatz | 2 | RY-RZ ansatz for H2 Hamiltonian ground state |
| QAOA | N | p=1 QAOA for Max-Cut (ZZ cost + RX mixer) |

### Noise Models (`src/noise_models/`)

| Model | Description |
|-------|-------------|
| Depolarizing | Random Pauli errors on H and CX gates |
| Amplitude damping | Energy relaxation (T1) on H and CX gates |
| Phase damping | Dephasing (T2) on H and CX gates |
| Readout error | Symmetric bit-flip on measurement |
| Coherent gate error | Systematic RX over/under-rotation |
| Combined | All above noise types simultaneously |

### Error Mitigation (`src/mitigation/`)

| Technique | Status | Method |
|-----------|--------|--------|
| Measurement Error Mitigation (MEM) | ✅ Complete | Calibration matrix inversion |
| Zero Noise Extrapolation (ZNE) | ✅ Complete | Circuit folding + linear & Richardson extrapolation |
| Probabilistic Error Cancellation (PEC) | ✅ Complete | Mitiq quasi-probability sampling |
| Clifford Data Regression (CDR) | ✅ Complete | Mitiq training circuit regression |
| Virtual Distillation (VD) | ✅ Complete | Tr(ρ²O)/Tr(ρ²) estimator |
| Dynamical Decoupling (DD) | ✅ Complete | Mitiq XX and XYXY pulse sequences |

### Benchmark Results (Phase III — simulator)

Automated benchmark: 6 techniques × 3 circuits (Bell, GHZ-3, QFT-3) × 5 noise levels (1–20%).
Full results in `results/data/benchmark_results.csv`.

| Technique | Avg Error Reduction | Sampling Overhead |
|-----------|--------------------|--------------------|
| MEM  | ~85% | 5× |
| ZNE  | ~90% | 3× |
| PEC  | ~75% | 1.5–2.5× |
| CDR  | ~80% | 11× |
| VD   | ~93% | 1× |
| DD   | ~5%  | 5× |

> Note: DD underperforms on the depolarizing model — it is most effective against T2 (dephasing) noise.

---

## Technologies

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.12 | Runtime |
| [Qiskit](https://www.ibm.com/quantum/qiskit) | 2.4.2 | Circuit construction and execution |
| [Qiskit Aer](https://github.com/Qiskit/qiskit-aer) | 0.17.2 | Noisy quantum simulation |
| [Mitiq](https://mitiq.readthedocs.io/) | 1.0.0 | PEC, CDR, DD mitigation |
| [Cirq](https://quantumai.google/cirq) | 1.6.1 | Mitiq backend dependency |
| [NumPy](https://numpy.org/) | 2.2.6 | Numerical computation |
| [SciPy](https://scipy.org/) | 1.17.1 | VQE optimisation (COBYLA) |
| [Matplotlib](https://matplotlib.org/) | 3.11.0 | Plotting and visualisation |
| [JupyterLab](https://jupyter.org/) | 4.6.0 | Interactive notebooks |

---

## Remaining Work

- [ ] QAOA + VQE integration into the automated benchmark suite
- [ ] Scalability analysis (vary qubit count, plot fidelity vs N)
- [ ] Unit tests for all mitigation functions
- [ ] Literature review report (`docs/literature/`)
- [ ] Comparative performance study (`results/reports/`)
- [ ] Final project report (`docs/report/`)

---

## References

- Temme, K., Bravyi, S., & Gambetta, J. M. (2017). *Error Mitigation for Short-Depth Quantum Circuits.* Physical Review Letters.
- Endo, S., Benjamin, S., & Li, Y. (2018). *Practical Quantum Error Mitigation for Near-Future Applications.* Physical Review X.
- Cai, Z. (2021). *Resource-efficient Purification-based Quantum Error Mitigation.*
- Kandala, A. et al. (2019). *Error Mitigation Extends the Computational Reach of a Noisy Quantum Processor.* Nature.
- [IBM Quantum — Error Mitigation and Suppression Techniques](https://quantum.cloud.ibm.com/docs/en/guides/error-mitigation-and-suppression-techniques)
- [Mitiq Documentation](https://mitiq.readthedocs.io/)

---

## License

MIT License — see [LICENSE](LICENSE) for details.
