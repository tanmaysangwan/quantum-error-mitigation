from pathlib import Path

import matplotlib.pyplot as plt
from qiskit import QuantumCircuit


def save_circuit(
    circuit: QuantumCircuit,
    filename: str,
    category: str = "ideal",
    title: str | None = None,
) -> None:
    """
    Save a quantum circuit diagram as a PNG.

    Colours: Hadamard = blue, CNOT = red, X = orange, Measure = green.

    Args:
        circuit:  The QuantumCircuit to draw.
        filename: Base filename (no extension).
        category: Subfolder — 'ideal', 'noisy', or 'mitigated'.
        title:    Optional title shown above the diagram.
    """
    output_dir = Path("results/figures") / category
    output_dir.mkdir(parents=True, exist_ok=True)

    figure = circuit.draw(
        output="mpl",
        style={
            "fontsize":     13,
            "subfontsize":  10,
            "displaycolor": {
                "h":       ["#2196F3", "#FFFFFF"],
                "cx":      ["#F44336", "#FFFFFF"],
                "x":       ["#FF9800", "#FFFFFF"],
                "measure": ["#4CAF50", "#FFFFFF"],
            },
        },
    )

    if title:
        figure.suptitle(title, fontsize=13, fontweight="bold", y=1.02)

    figure.savefig(
        output_dir / f"{filename}_circuit.png",
        dpi=150,
        bbox_inches="tight",
    )
