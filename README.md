# Quantum Error Mitigation Framework

A Python framework for implementing, studying, and comparing Quantum Error Mitigation (QEM) techniques for NISQ-era quantum computers.

Built with [Qiskit](https://www.ibm.com/quantum/qiskit) and [Qiskit Aer](https://github.com/Qiskit/qiskit-aer) as part of an internship research project on near-term quantum error mitigation.


---

## Objectives

1. Study and model common noise sources on NISQ devices.
2. Implement major Quantum Error Mitigation techniques from scratch.
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
│   ├── benchmarks/        # Planned
│   ├── metrics/           # Planned
│   └── common/            # Planned
│
├── experiments/
│   ├── basics/            # Introductory Qiskit scripts (gates, measurement, drawing)
│   └── noise_demos/       # Standalone noise demonstration scripts
│
├── notebooks/
│   └── grovers_8q.ipynb   # Grover's algorithm (8 qubits)
│
├── tests/                 # Planned
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

All experiments are launched through `run.py`. Activate the environment first:

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
python run.py mem           # Measurement Error Mitigation (matrix inversion)
python run.py zne           # Zero Noise Extrapolation (linear fit)
python run.py pec           # Probabilistic Error Cancellation (custom scheme)
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

| Model | Gate targets |
|---|---|
| Depolarizing | H, CX |
| Amplitude damping | H, CX |
| Phase damping | H, CX |
| Readout error | All qubits (measurement) |
| Coherent gate error | H, CX (via RX rotation) |
| Combined | Depolarizing + amplitude + phase + readout |

### Simulator Backend (`src/backends/`)

- `run_circuit` — thin wrapper around `AerSimulator` supporting optional noise models and configurable shot count.

### Plotting Utilities (`src/plotting/`)

| Utility | Output |
|---|---|
| `circuit_plotter` | Circuit diagram PNG saved to `results/figures/` |
| `histogram_plotter` | Measurement histogram PNG (ideal / noisy / mitigated) |
| `zne_plotter` | Noise-scaling plot with linear extrapolation to zero noise |

### Error Mitigation (`src/mitigation/`)

| Technique | Status | Approach |
|---|---|---|
| Measurement Error Mitigation (MEM) | **Complete** | 4×4 calibration matrix, matrix inversion |
| Zero Noise Extrapolation (ZNE) | **Complete** | Linear extrapolation across noise scaling factors 1×, 2×, 3× |
| Probabilistic Error Cancellation (PEC) | **In progress** | Custom correction-factor scheme; Mitiq integration planned |

---

## Technologies

| Tool | Version | Purpose |
|---|---|---|
| Python | 3.12 | Runtime |
| [Qiskit](https://www.ibm.com/quantum/qiskit) | 2.4.2 | Circuit construction and execution |
| [Qiskit Aer](https://github.com/Qiskit/qiskit-aer) | 0.17.2 | Noisy quantum simulation |
| [Mitiq](https://mitiq.readthedocs.io/) | 1.0.0 | Error mitigation library (prepared for Phase II integration) |
| [Cirq](https://quantumai.google/cirq) | 1.6.1 | Mitiq backend dependency |
| [NumPy](https://numpy.org/) | 2.2.6 | Numerical computation |
| [SciPy](https://scipy.org/) | 1.17.1 | Scientific computing |
| [Matplotlib](https://matplotlib.org/) | 3.11.0 | Plotting and visualization |
| [JupyterLab](https://jupyter.org/) | 4.6.0 | Interactive notebooks |

---

## Future Work

- Full Mitiq integration for ZNE and PEC
- Clifford Data Regression (CDR)
- Virtual Distillation
- Dynamical Decoupling
- Automated benchmarking suite
- Performance metrics module (fidelity, sampling overhead)
- Unit and integration test suite

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
