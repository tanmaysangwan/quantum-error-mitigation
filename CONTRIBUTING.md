# Contributing

Thank you for your interest in contributing to this project. This document covers everything you need to get started.

---

## Development Setup

### Prerequisites

- Python 3.12
- Git

### Steps

```bash
# Clone the repository
git clone <repository-url>
cd quantum-error-mitigation

# Create a virtual environment using Python 3.12
python3.12 -m venv qiskit-env
source qiskit-env/bin/activate

# Upgrade packaging tools
pip install --upgrade pip setuptools wheel

# Install all dependencies
pip install -r requirements.txt
```

---

## Running the Project

All experiments are launched through `run.py`:

```bash
python run.py bell
python run.py mem
python run.py zne
# etc.
```

Run `python run.py` with no arguments to list all available experiment names.

---

## Code Style

- Follow [PEP 8](https://peps.python.org/pep-0008/) for all Python code.
- Use `snake_case` for file names, function names, and variable names.
- Keep all modules importable — avoid top-level side effects in `src/`.
- Add a brief comment or docstring at the top of each new module describing its purpose.
- Inline comments should explain *why*, not *what*.

---

## Project Structure

| Directory | Purpose |
|---|---|
| `src/circuits/` | Reusable circuit builders. Importable by experiments and mitigation modules. |
| `src/noise_models/` | Noise model factories returning a configured `NoiseModel`. |
| `src/mitigation/` | Error mitigation implementations. Each technique gets its own module. |
| `src/backends/` | Simulator wrappers. Keep backend-specific logic isolated here. |
| `src/plotting/` | Plot generation utilities. Should only save files and return figures. |
| `experiments/noise_demos/` | Standalone runnable demo scripts. Each must expose a `main()` function. |
| `experiments/basics/` | Introductory Qiskit experiments. |
| `notebooks/` | Jupyter notebooks for interactive exploration. |
| `tests/` | Unit and integration tests (pytest). |
| `results/` | Generated figures and data. Not committed to version control. |

---

## Adding a New Noise Model

1. Create `src/noise_models/<name>.py` with a factory function `create_<name>_noise_model(...)` that returns a `NoiseModel`.
2. Create `experiments/noise_demos/<name>_demo.py` with a `main()` function that demonstrates it.
3. Register the demo in `run.py` under an appropriate short name.

## Adding a New Mitigation Technique

1. Create `src/mitigation/<technique>.py` with the core implementation logic.
2. Create a corresponding demo entry point `src/mitigation/<technique>_demo.py` exposing `main()`.
3. Register it in `run.py`.
4. Document it in `README.md` and add a changelog entry to `CHANGELOG.md`.

## Adding a New Circuit

1. Create `src/circuits/<name>.py` with a builder function `create_<name>(...)` returning a `QuantumCircuit`.
2. Import and use it from experiments or mitigation demos as needed.

---

## Dependency Management

- Do not introduce new dependencies without discussion.
- If a dependency is added, pin it to an exact version in `requirements.txt`.
- Verify that new packages are compatible with Python 3.12, Qiskit 2.4.2, and Qiskit Aer 0.17.2.

---

## Pull Requests

- Keep changes focused — one feature or fix per pull request.
- Write a clear description of what changed and why.
- Verify that `python run.py bell`, `python run.py mem`, and `python run.py zne` all run without errors before submitting.
- Do not modify `requirements.txt` version pins unless there is a documented compatibility reason.

---

## Commit Messages

Use the imperative present tense and keep the subject line under 72 characters:

```
Add phase damping noise model
Fix calibration matrix indexing for two-qubit states
Update ZNE plotter to support variable noise factor lists
```

---

## License

By contributing, you agree that your contributions will be licensed under the MIT License that covers this project.
