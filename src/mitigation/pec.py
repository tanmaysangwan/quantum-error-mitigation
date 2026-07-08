import matplotlib.pyplot as plt  # Display histogram windows.

from src.backends.simulator import run_circuit  # Run circuits.
from src.circuits.bell_state import create_bell_state  # Bell-state circuit.
from src.noise_models.depolarizing_noise import create_depolarizing_noise_model  # Noise model.
from src.plotting.circuit_plotter import save_circuit  # Save circuit image.
from src.plotting.histogram_plotter import save_histogram  # Save histogram image.
from src.mitigation.probabilistic_error_cancellation import (
    calculate_error_probability,
    probabilistic_error_cancellation,
)


def main():
    circuit = create_bell_state()  # Create the Bell-state circuit.

    save_circuit(
        circuit,
        "bell_state_pec",
        category="ideal",
    )  # Save the circuit.

    ideal_counts = run_circuit(circuit)  # Run the ideal circuit.

    save_histogram(
        ideal_counts,
        "bell_state_pec",
        category="ideal",
    )  # Save the ideal histogram.

    noise_model = create_depolarizing_noise_model(
        0.05,
    )  # Apply depolarizing noise.

    noisy_counts = run_circuit(
        circuit,
        noise_model=noise_model,
    )  # Run the noisy circuit.

    save_histogram(
        noisy_counts,
        "bell_state_pec",
        category="noisy",
    )  # Save the noisy histogram.

    error_probability = calculate_error_probability(
        ideal_counts,
        noisy_counts,
    )  # Estimate the error probability.

    mitigated_counts = probabilistic_error_cancellation(
        noisy_counts,
        error_probability,
    )  # Apply PEC.

    save_histogram(
        mitigated_counts,
        "bell_state_pec",
        category="mitigated",
    )  # Save the mitigated histogram.

    print("=" * 40)
    print("Probabilistic Error Cancellation")
    print("=" * 40)

    print(f"Estimated Error Probability: {error_probability:.4f}\n")

    print("Ideal Counts:")
    print(ideal_counts)

    print("\nNoisy Counts:")
    print(noisy_counts)

    print("\nMitigated Counts:")
    print(mitigated_counts)

    plt.show()


if __name__ == "__main__":
    main()