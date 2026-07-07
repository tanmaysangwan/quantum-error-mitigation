# Quantum Error Mitigation Framework

A Python framework for implementing, analyzing, and comparing Quantum Error Mitigation (QEM) techniques for NISQ-era quantum computers.

Built with [Qiskit](https://www.ibm.com/quantum/qiskit) and [Qiskit Aer](https://github.com/Qiskit/qiskit-aer) as part of an internship research project on near-term quantum error mitigation.

---

## Project Status

**Phase I complete** — noise models implemented and validated.  
**Phase II in progress** — error mitigation prototypes (MEM, ZNE, PEC) under active development.  
Benchmarking, metrics, and visualization modules are planned for upcoming phases.

---

## Objectives

1. Study and model common noise sources in NISQ devices.
2. Implement major Quantum Error Mitigation techniques.
3. Benchmark mitigation methods against standard quantum algorithms.
4. Analyze trade-offs between accuracy improvement and computational overhead.

---

## Repository Structure

```
quantum-error-mitigation/
│
├── src/
│   ├── circuits/        # Reusable quantum circuit definitions (Bell, GHZ, QFT, VQE, QAOA)
│   ├── noise_models/    # Noise model implementations (depolarizing, amplitude damping, etc.)
│   ├── mitigation/      # Error mitigation modules (MEM, ZNE, PEC, and future techniques)
│   ├── benchmarks/      # Automated benchmarking utilities (planned)
│   ├── metrics/         # Performance metrics: fidelity, expectation values, overhead (planned)
│   ├── backends/        # Backend wrappers: Aer simulator, IBM Quantum Runtime (planned)
│   ├── plotting/        # Plot generation for results and comparisons (planned)
│   └── common/          # Shared utilities: I/O, logging, validation (planned)
│
├── experiments/
│   ├── basics/          # Introductory Qiskit circuit experiments
│   ├── noise_demos/     # Standalone noise demonstration scripts
│   ├── ghz/             # GHZ state experiments (planned)
│   ├── qft/             # Quantum Fourier Transform experiments (planned)
│   ├── vqe/             # VQE experiments (planned)
│   └── qaoa/            # QAOA experiments (planned)
│
├── notebooks/           # Jupyter notebooks for interactive exploration
├── tests/               # Unit and integration tests (planned)
├── data/
│   ├── raw/             # Raw experimental output
│   └── processed/       # Cleaned and aggregated data
├── results/
│   ├── figures/         # Generated plots
│   └── reports/         # Final output reports
├── configs/             # Configuration files (planned)
├── docs/                # Notes, literature, and project reports
│
├── requirements.txt
├── LICENSE
├── CONTRIBUTING.md
└── CHANGELOG.md
```

---

## Installation

### Prerequisites

- macOS / Linux
- Python 3.11 or 3.13 (Homebrew recommended on macOS)

### Setup

```bash
# Clone the repository
git clone <repository-url>
cd quantum-error-mitigation

# Create a virtual environment
python3 -m venv qiskit-env

# Activate it
source qiskit-env/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## Activating the Virtual Environment

Always activate before running any code:

```bash
source qiskit-env/bin/activate
```

To open in VS Code with the correct interpreter:

```bash
source qiskit-env/bin/activate
code .
```

---

## Running Experiments

All experiment scripts are self-contained and runnable directly.

```bash
# Activate environment first
source qiskit-env/bin/activate

# Noise model demonstrations
python experiments/noise_demos/hadamard_demo.py
python experiments/noise_demos/noise_injection.py
python experiments/noise_demos/amplitude_damping_demo.py

# Error mitigation prototypes
python src/mitigation/mem_demo.py
python src/mitigation/zne.py
python src/mitigation/pec.py

# Noise model implementations
python src/noise_models/depolarizing_noise.py
python src/noise_models/amplitude_damping.py
python src/noise_models/phase_damping.py
python src/noise_models/readout_error.py
python src/noise_models/coherent_gate_error.py
python src/noise_models/combined_noise.py

# Basics
python experiments/basics/single_qubit_gates.py
python experiments/basics/multiqubit_gates.py
```

---

## Current Progress

| Module | Status |
|---|---|
| Noise Models (depolarizing, amplitude damping, phase damping, readout, coherent, combined) | Done |
| Measurement Error Mitigation (MEM) | Prototype |
| Zero Noise Extrapolation (ZNE) | Prototype |
| Probabilistic Error Cancellation (PEC) | Prototype |
| Clifford Data Regression (CDR) | Planned |
| Virtual Distillation | Planned |
| Dynamical Decoupling | Planned |
| Benchmarking Suite | Planned |
| Performance Metrics | Planned |
| Visualization Dashboard | Planned |

---

## Technologies

| Tool | Purpose |
|---|---|
| [Qiskit](https://www.ibm.com/quantum/qiskit) | Quantum circuit construction and execution |
| [Qiskit Aer](https://github.com/Qiskit/qiskit-aer) | Noisy quantum simulation |
| [Mitiq](https://mitiq.readthedocs.io/) | Error mitigation library (planned integration) |
| [NumPy](https://numpy.org/) | Numerical computation |
| [SciPy](https://scipy.org/) | Scientific computing |
| [Matplotlib](https://matplotlib.org/) | Plotting and visualization |
| [JupyterLab](https://jupyter.org/) | Interactive notebooks |

---

## References

- Temme, K., Bravyi, S., & Gambetta, J. M. (2017). *Error Mitigation for Short-Depth Quantum Circuits.*
- Endo, S., Benjamin, S., & Li, Y. (2018). *Practical Quantum Error Mitigation for Near-Future Applications.*
- Kandala, A. et al. (2019). *Error Mitigation Extends the Computational Reach of a Noisy Quantum Processor.*
- [IBM Quantum — Error Mitigation and Suppression Techniques](https://quantum.cloud.ibm.com/docs/en/guides/error-mitigation-and-suppression-techniques)
- [Mitiq Documentation](https://mitiq.readthedocs.io/)

---

## License

MIT License — see [LICENSE](LICENSE) for details.
