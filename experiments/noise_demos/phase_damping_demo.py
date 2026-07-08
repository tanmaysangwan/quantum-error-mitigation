import matplotlib.pyplot as plt

from src.backends.simulator import run_circuit
from src.circuits.bell_state import create_bell_state
from src.noise_models.phase_damping import create_phase_damping_noise_model
from src.plotting.circuit_plotter import save_circuit
from src.plotting.histogram_plotter import save_histogram


def main():
    circuit = create_bell_state()

    save_circuit(circuit, "bell_state_phase_damping", category="noisy")

    noise_model = create_phase_damping_noise_model(0.05)

    counts = run_circuit(
        circuit=circuit,
        noise_model=noise_model,
    )

    print(circuit.draw())
    print("\nMeasurement Counts:")
    print(counts)

    save_histogram(counts, "bell_state_phase_damping", category="noisy")

    plt.show()


if __name__ == "__main__":
    main()