# Quantum Error Mitigation Framework

A Python framework for implementing, studying, and comparing Quantum Error Mitigation (QEM) techniques for NISQ-era quantum computers.

Built with [Qiskit](https://www.ibm.com/quantum/qiskit), [Qiskit Aer](https://github.com/Qiskit/qiskit-aer), and [Mitiq](https://mitiq.readthedocs.io/) as part of an internship research project on near-term quantum error mitigation.

---

## Project Status

| Phase | Status | Notes |
|---|---|---|
| Phase I — Noise Modelling | ✅ Complete | All 6 noise models implemented and validated |
| Phase II — Error Mitigation | 🔄 In Progress | MEM complete · ZNE complete · PEC in progress · CDR planned |
| Phase III — Benchmarking | ⏳ Planned | QFT, VQE, QAOA circuits pending |
| Phase IV — Performance Analysis | ⏳ Planned | Metrics module pending |

**Current focus:** Completing Phase II — replacing the custom PEC heuristic with proper quasi-probability PEC via Mitiq, upgrading ZNE to use circuit folding, implementing CDR, and building the metrics module.

---

## Objectives

1. Study and model common noise sources on NISQ devices.
2. Implement major Quantum Error Mitigation techniques from scratch and via Mitiq.
3. Benchmark mitigation methods against standard quantum circuits.
4. Analyze trade-offs between accuracy improvement and computational overhead.

---

## Repository Structure

```
quantum-error-mitigation/
│
├── src/
│   ├── circuits/          # Reusable circuit builders: Bell state, GHZ state
│   ├── noise_models/      # Six noise model implementations
│   ├── mitigation/        # MEM, ZNE, PEC implementations + demo entry points
│   ├── backends/          # AerSimulator wrapper (run_circuit)
│   ├── plotting/          # Circuit, histogram, and ZNE plot utilities
│   ├── benchmarks/        # Planned — QFT, VQE, QAOA circuits
│   ├── metrics/           # Planned — fidelity, accuracy, overhead metrics
│   └── common/            # Planned — shared utilities
│
├── experiments/
│   ├── basics/            # Introductory Qiskit scripts (gates, measurement, drawing)
│   └── noise_demos/       # Standalone noise demonstration scripts
│
├── notebooks/
│   └── grovers_8q.ipynb   # Grover's algorithm (8 qubits)
│
├── tests/                 # Planned — unit and integration test suite
├── data/
│   ├── raw/
│   └── processed/
├── results/
│   ├── figures/
│   │   ├── ideal/         # Circuit diagrams and ideal histograms
│   │   ├── noisy/         # Noisy simulation histograms
│   │   └── mitigated/     # Post-mitigation histograms and ZNE plots
│   ├── data/
│   └── reports/
├── docs/
│   ├── literature/
│   ├── notes/
│   └── report/
│
├── run.py
├── requirements.txt
├── LICENSE
├── CONTRIBUTING.md
└── CHANGELOG.md
```

---

## Installation

### Prerequisites

- macOS or Linux
- Python 3.12 (recommended: install via [Homebrew](https://brew.sh/) on macOS)

### Setup

```bash
# Clone the repository
git clone <repository-url>
cd quantum-error-mitigation

# Create a virtual environment using Python 3.12
python3.12 -m venv qiskit-env

# Activate it
source qiskit-env/bin/activate

# Upgrade packaging tools
pip install --upgrade pip setuptools wheel

# Install all dependencies
pip install -r requirements.txt
```

---

## Running Experiments

All experiments are launched through `run.py`. Activate the virtual environment first:

```bash
source qiskit-env/bin/activate
```

### Benchmark Circuits

```bash
python run.py bell          # Bell state — ideal simulation
python run.py ghz           # GHZ state (3 qubits) — ideal simulation
```

### Noise Model Demonstrations

```bash
python run.py depolarizing  # Depolarizing noise on Bell state
python run.py readout       # Readout (measurement) error on Bell state
python run.py phase         # Phase damping on Bell state
python run.py amplitude     # Amplitude damping on Bell state
python run.py coherent      # Coherent gate error on Bell state
python run.py combined      # All noise types combined on Bell state
```

### Error Mitigation Experiments

```bash
python run.py mem           # Measurement Error Mitigation (calibration matrix inversion)
python run.py zne           # Zero Noise Extrapolation (linear fit, noise scaling 1×–3×)
python run.py pec           # Probabilistic Error Cancellation (custom correction scheme)
```

Each experiment prints results to the terminal and saves circuit diagrams and measurement histograms to `results/figures/`.

---

## Implemented Features

### Circuits (`src/circuits/`)

| Circuit | Description |
|---|---|
| Bell state | 2-qubit maximally entangled state (H + CNOT) |
| GHZ state | N-qubit generalisation of the Bell state |

### Noise Models (`src/noise_models/`)

| Model | Gate Targets | Parameter |
|---|---|---|
| Depolarizing | H, CX | error probability |
| Amplitude damping | H, CX | damping parameter γ |
| Phase damping | H, CX | dephasing parameter γ |
| Readout error | All qubits (measurement) | flip probability |
| Coherent gate error | H, CX | RX rotation angle |
| Combined | H, CX + all qubits | single error probability |

### Simulator Backend (`src/backends/`)

`run_circuit` — thin wrapper around `AerSimulator` with optional noise model and configurable shot count.

### Plotting Utilities (`src/plotting/`)

| Utility | Output |
|---|---|
| `circuit_plotter` | Circuit diagram PNG saved to `results/figures/` |
| `histogram_plotter` | Measurement histogram PNG (ideal / noisy / mitigated) |
| `zne_plotter` | Noise-scaling scatter plot with linear extrapolation line |

### Error Mitigation (`src/mitigation/`)

| Technique | Status | Implementation |
|---|---|---|
| Measurement Error Mitigation (MEM) | ✅ Complete | 4×4 calibration matrix, matrix inversion |
| Zero Noise Extrapolation (ZNE) | ✅ Complete | Linear extrapolation, noise scaling 1×/2×/3× |
| Probabilistic Error Cancellation (PEC) | 🔄 In Progress | Custom correction-factor scheme; proper quasi-probability implementation via Mitiq planned |
| Clifford Data Regression (CDR) | ⏳ Planned | Mitiq integration |

---

## Technologies

| Tool | Version | Purpose |
|---|---|---|
| Python | 3.12 | Runtime |
| [Qiskit](https://www.ibm.com/quantum/qiskit) | 2.4.2 | Circuit construction and execution |
| [Qiskit Aer](https://github.com/Qiskit/qiskit-aer) | 0.17.2 | Noisy quantum simulation |
| [Mitiq](https://mitiq.readthedocs.io/) | 1.0.0 | Error mitigation library |
| [Cirq](https://quantumai.google/cirq) | 1.6.1 | Mitiq backend dependency |
| [NumPy](https://numpy.org/) | 2.2.6 | Numerical computation |
| [SciPy](https://scipy.org/) | 1.17.1 | Scientific computing |
| [Matplotlib](https://matplotlib.org/) | 3.11.0 | Plotting and visualization |
| [JupyterLab](https://jupyter.org/) | 4.6.0 | Interactive notebooks |

---

## Phase II Completion Checklist

- [x] MEM — calibration matrix + matrix inversion
- [x] ZNE — linear extrapolation across noise scaling factors
- [ ] ZNE — upgrade to circuit folding (gate-level noise amplification)
- [ ] ZNE — add Richardson / polynomial extrapolation
- [ ] PEC — replace custom heuristic with proper quasi-probability implementation via Mitiq
- [ ] CDR — implement Clifford Data Regression via Mitiq
- [ ] Metrics module — fidelity, expectation value accuracy, error reduction %, sampling overhead
- [ ] Fix: remove duplicate `plt.show()` call in `zne_plotter.py`
- [ ] Unit tests for mitigation functions

---

## Planned Work (Phase III & IV)

- QFT, VQE, and QAOA benchmark circuits
- Automated benchmarking suite across noise levels and circuit depths
- Performance comparison table (ZNE vs PEC vs MEM vs CDR)
- Dynamical Decoupling
- Virtual Distillation

---

## References

- Temme, K., Bravyi, S., & Gambetta, J. M. (2017). *Error Mitigation for Short-Depth Quantum Circuits.* Physical Review Letters.
- Endo, S., Benjamin, S., & Li, Y. (2018). *Practical Quantum Error Mitigation for Near-Future Applications.* Physical Review X.
- Kandala, A. et al. (2019). *Error Mitigation Extends the Computational Reach of a Noisy Quantum Processor.* Nature.
- [IBM Quantum — Error Mitigation and Suppression Techniques](https://quantum.cloud.ibm.com/docs/en/guides/error-mitigation-and-suppression-techniques)
- [Mitiq Documentation](https://mitiq.readthedocs.io/)

---

## License

MIT License — see [LICENSE](LICENSE) for details.
