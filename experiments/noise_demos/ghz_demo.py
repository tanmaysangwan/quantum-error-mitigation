import matplotlib.pyplot as plt

from src.backends.simulator import run_circuit
from src.circuits.ghz import create_ghz_state
from src.plotting.circuit_plotter import save_circuit
from src.plotting.histogram_plotter import save_histogram


def main():
    circuit = create_ghz_state(3)

    save_circuit(circuit, "ghz")

    counts = run_circuit(circuit)

    print(circuit.draw())
    print("\nMeasurement Counts:")
    print(counts)

    save_histogram(counts, "ghz")

    plt.show()


if __name__ == "__main__":
    main()