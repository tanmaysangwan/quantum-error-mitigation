from pathlib import Path

from qiskit import QuantumCircuit


def save_circuit(circuit: QuantumCircuit, filename: str, category: str = "ideal") -> None:
    output_dir = Path("results/figures") / category
    output_dir.mkdir(parents=True, exist_ok=True)

    figure = circuit.draw(output="mpl")
    figure.savefig(output_dir / f"{filename}_circuit.png")
