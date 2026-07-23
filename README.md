# Quantum Error Mitigation Framework

A Python research framework for implementing, benchmarking, and comparing Quantum Error
Mitigation (QEM) techniques for Noisy Intermediate-Scale Quantum (NISQ) computers.

This project was developed as part of a B.Tech internship project at SAG Lab, DRDO. It uses
Qiskit, Qiskit Aer, and Mitiq to study how classical post-processing and circuit-level
mitigation can improve noisy quantum simulation results without requiring full quantum error
correction.

---

## Project Status

| Phase | Description | Status |
|-------|-------------|--------|
| Phase I | Literature review and implementation of six NISQ noise models | Complete |
| Phase II | Implementation of six QEM techniques and metrics module | Complete |
| Phase III | Benchmarking on Bell, GHZ, QFT, QAOA, and VQE circuits | Complete |
| Phase IV | Performance analysis, scalability study, reports, and final documentation | Complete |

Current verification: `89 passed` via `./qiskit-env/bin/python -m pytest -q`.

---

## Objectives

1. Study common NISQ noise sources and model them using Qiskit Aer.
2. Implement major Quantum Error Mitigation techniques in a modular Python framework.
3. Benchmark mitigation methods on representative quantum circuits and algorithms.
4. Compare accuracy improvement, sampling overhead, runtime, and scalability.
5. Produce practical recommendations for selecting mitigation techniques.

---

## Repository Structure

```text
quantum-error-mitigation/
├── src/
│   ├── circuits/          # Bell, GHZ, QFT, VQE, and QAOA circuit builders
│   ├── noise_models/      # Six NISQ noise model implementations
│   ├── mitigation/        # MEM, ZNE, PEC, CDR, VD, and DD implementations
│   ├── backends/          # Qiskit Aer simulator wrapper
│   ├── benchmarks/        # Automated benchmark, visualisation, scalability analysis
│   ├── metrics/           # Fidelity proxy, error reduction, overhead, summaries
│   └── plotting/          # Circuit, histogram, comparison, and ZNE plot helpers
├── experiments/
│   ├── basics/            # Introductory Qiskit scripts
│   ├── noise_demos/       # Standalone demonstrations for each noise model
│   ├── vqe_demo.py        # VQE H2 energy experiment
│   └── qaoa_demo.py       # QAOA Max-Cut experiment
├── notebooks/
│   └── grovers_8q.ipynb   # Exploratory Grover's algorithm notebook
├── tests/                 # 89 pytest tests
├── results/
│   ├── data/
│   │   └── benchmark_results.csv
│   ├── figures/
│   │   ├── ideal/
│   │   ├── noisy/
│   │   ├── mitigated/
│   │   └── comparison/
│   └── reports/
├── docs/
│   ├── literature/literature_review.md
│   └── report/final_project_report.md
├── run.py
├── requirements.txt
├── pytest.ini
├── CONTRIBUTING.md
├── CHANGELOG.md
└── LICENSE
```

---

## Implemented Components

### Benchmark Circuits

| Circuit | Qubits | Purpose |
|---------|--------|---------|
| Bell state | 2 | Baseline entanglement and ZZ expectation testing |
| GHZ state | N | Multi-qubit entanglement and scaling behavior |
| QFT | N | Deeper non-Clifford circuit with O(N^2) depth |
| QAOA-C4 | 4 | Max-Cut variational optimization benchmark |
| VQE H2 | 2 | Quantum chemistry variational energy benchmark |

### Noise Models

| Model | Physical meaning |
|-------|------------------|
| Depolarizing noise | Random Pauli gate errors |
| Amplitude damping | T1 energy relaxation from `|1>` to `|0>` |
| Phase damping | T2 dephasing without energy exchange |
| Readout error | Classical bit-flip during measurement |
| Coherent gate error | Systematic over/under-rotation |
| Combined noise | Layered gate, damping, dephasing, and readout errors |

### Mitigation Techniques

| Technique | Implementation |
|-----------|----------------|
| MEM | Calibration matrix construction and inverse-based count correction |
| ZNE | Gate folding with linear and Richardson extrapolation |
| PEC | Mitiq quasi-probability sampling with depolarizing representations |
| CDR | Mitiq near-Clifford training circuit regression |
| VD | Squared-density probability estimator `Tr(rho^2 O) / Tr(rho^2)` |
| DD | Mitiq XX/XYXY dynamical decoupling sequence insertion |

---

## Benchmark Summary

The automated benchmark covers 145 configurations:

- Bell, GHZ-3, QFT-3, and QAOA-C4: 4 circuits x 6 techniques x 5 noise levels = 120 rows
- VQE H2: 5 techniques x 5 noise levels = 25 rows
- PEC is excluded from VQE because the optimized arbitrary rotations do not have a simple
  closed-form quasi-probability representation in this implementation.

Data source: `results/data/benchmark_results.csv`

Key findings:

- No single mitigation technique dominates all circuit types.
- MEM gives the best overall average fidelity proxy in the current benchmark.
- CDR works extremely well on near-Clifford circuits such as Bell and GHZ, but fails on
  strongly non-Clifford circuits such as QFT and QAOA.
- PEC is effective on small, low-noise circuits but becomes unstable as quasi-probability
  variance grows.
- VD is the lowest-overhead general-purpose method and scales better than ZNE on QFT.
- DD underperforms under depolarizing noise, which is expected because DD is designed mainly
  for dephasing-dominated idle-time noise.

Important measurement note: the reported `fidelity` column is an observable-level fidelity
proxy, not full quantum state fidelity. It is used to compare how close each mitigated
observable is to the ideal reference value.

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

The local virtual environment directory `qiskit-env/` is intentionally ignored by Git.

---

## Running the Project

Activate the environment first:

```bash
source qiskit-env/bin/activate
```

### Noise Model Demonstrations

```bash
python run.py bell
python run.py ghz
python run.py depolarizing
python run.py readout
python run.py phase
python run.py amplitude
python run.py coherent
python run.py combined
```

### Mitigation Experiments

```bash
python run.py mem
python run.py zne
python run.py pec
python run.py cdr
python run.py vd
python run.py dd
```

### Algorithm Experiments

```bash
python run.py vqe
python run.py qaoa
```

### Full Benchmark and Analysis

```bash
python run.py benchmark
python run.py visualise
python run.py scalability
```

### Tests

```bash
python run.py test
python -m pytest -q
```

---

## Main Outputs

| Output | Location |
|--------|----------|
| Benchmark CSV | `results/data/benchmark_results.csv` |
| Comparison figures | `results/figures/comparison/` |
| Individual circuit/noise figures | `results/figures/ideal/`, `results/figures/noisy/`, `results/figures/mitigated/` |
| Literature review | `docs/literature/literature_review.md` |
| Final Markdown report | `docs/report/final_project_report.md` |
| Comparative performance study | `results/reports/comparative_performance_study.md` |

---

## Technologies

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.12 | Runtime |
| Qiskit | 2.4.2 | Quantum circuit construction |
| Qiskit Aer | 0.17.2 | Noisy quantum simulation |
| Mitiq | 1.0.0 | PEC, CDR, and DD mitigation workflows |
| NumPy | 2.2.6 | Numerical computation |
| SciPy | 1.17.1 | VQE optimization |
| Matplotlib | 3.11.0 | Plotting and visualisation |
| JupyterLab | 4.6.0 | Notebook experiments |

---

## Current Limitations

- All main results are simulator-based; real hardware validation is still future work.
- DD should be re-tested with a realistic T1/T2 noise model instead of only depolarizing noise.
- PEC uses limited Monte Carlo samples in the benchmark, so high-noise PEC results are affected
  by estimator variance.
- VQE uses an energy-based path for ZNE and a counts-based ZZ proxy for MEM/CDR/VD/DD.
- Generated figures and reports are runtime outputs; keep them in submission artifacts when
  sharing the project outside Git.

---

## References

- Temme, K., Bravyi, S., & Gambetta, J. M. (2017). *Error Mitigation for Short-Depth Quantum Circuits.*
- Endo, S., Benjamin, S., & Li, Y. (2018). *Practical Quantum Error Mitigation for Near-Future Applications.*
- Cai, Z. (2021). *Resource-efficient Purification-based Quantum Error Mitigation.*
- Kandala, A. et al. (2019). *Error Mitigation Extends the Computational Reach of a Noisy Quantum Processor.*
- IBM Quantum documentation on error mitigation and suppression.
- Mitiq documentation.

---

## License

MIT License. See `LICENSE` for details.
