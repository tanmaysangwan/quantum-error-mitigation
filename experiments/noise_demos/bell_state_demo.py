from pathlib import Path
from src.plotting.circuit_plotter import save_circuit
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt

from src.circuits.bell_state import create_bell_state


def main():
    circuit = create_bell_state()
    save_circuit(circuit, "bell_state")

    simulator = AerSimulator()

    result = simulator.run(circuit, shots=1024).result()

    counts = result.get_counts()

    print(circuit.draw())
    print("\nMeasurement Counts:")
    print(counts)

    output_dir = Path("results/figures")
    output_dir.mkdir(parents=True, exist_ok=True)

    histogram = plot_histogram(counts)
    histogram.savefig(output_dir / "bell_state_histogram.png")

    plt.show()


if __name__ == "__main__":
    main()