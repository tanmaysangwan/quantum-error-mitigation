# Contributing

Thank you for your interest in contributing to this project.

## Development Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd quantum-error-mitigation
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv qiskit-env
   source qiskit-env/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Code Style

- Follow [PEP 8](https://peps.python.org/pep-0008/) for all Python code.
- Use `snake_case` for file names, function names, and variable names.
- Keep module-level scripts runnable as standalone programs.
- Add a brief docstring or comment block at the top of each new file describing its purpose.

## Project Structure

- **`src/`** — reusable framework code. Modules here should be importable by experiments.
- **`experiments/`** — standalone runnable scripts. Each script demonstrates or benchmarks something specific.
- **`notebooks/`** — Jupyter notebooks for interactive exploration.
- **`tests/`** — unit and integration tests (pytest).
- **`data/`** — raw and processed experimental data (not committed).
- **`results/`** — generated figures and reports (not committed).

## Adding a New Experiment

1. Place the script in the appropriate `experiments/` subdirectory.
2. If the experiment uses a reusable circuit, define the circuit in `src/circuits/` and import it.
3. If the experiment uses a noise model, define the model in `src/noise_models/` and import it.

## Adding a New Mitigation Technique

1. Add the implementation module to `src/mitigation/`.
2. Update `src/mitigation/__init__.py` with a note about the new module.
3. Add a corresponding experiment script to the relevant `experiments/` subdirectory.

## Pull Requests

- Keep changes focused. One feature or fix per pull request.
- Include a clear description of what was changed and why.
- Ensure all existing scripts continue to run without errors before submitting.
