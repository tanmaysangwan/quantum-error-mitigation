import matplotlib.pyplot as plt

from src.backends.simulator import run_circuit
from src.circuits.bell_state import create_bell_state
from src.mitigation.zero_noise_extrapolation import (
    calculate_expectation_value,
    linear_extrapolation,
)
from src.noise_models.depolarizing_noise import create_depolarizing_noise_model
from src.plotting.circuit_plotter import save_circuit
from src.plotting.histogram_plotter import save_histogram
from src.plotting.zne_plotter import save_zne_plot


def main():
    circuit = create_bell_state()  # Create the Bell-state circuit.

    save_circuit(
        circuit,
        "bell_state_zne",
        category="ideal",
    )  # Save the circuit.

    ideal_counts = run_circuit(circuit)  # Run the ideal circuit.

    save_histogram(
        ideal_counts,
        "bell_state_zne",
        category="ideal",
    )  # Save the ideal histogram.

    noise_factors = [1, 2, 3]  # Noise scaling factors.
    error_probability = 0.02  # Base depolarizing probability.

    expectation_values = []  # Store expectation values.

    for factor in noise_factors:

        noise_model = create_depolarizing_noise_model(
            error_probability * factor,
        )  # Scale the noise.

        counts = run_circuit(
            circuit,
            noise_model=noise_model,
        )  # Run the noisy circuit.

        save_histogram(
            counts,
            f"bell_state_zne_{factor}x",
            category="noisy",
        )  # Save the histogram.

        expectation = calculate_expectation_value(counts)  # Calculate <ZZ>.

        expectation_values.append(expectation)  # Store expectation.

        print(f"{factor}x Noise Counts:")
        print(counts)
        print(f"Expectation Value: {expectation:.4f}\n")

    mitigated_expectation = linear_extrapolation(
        noise_factors,
        expectation_values,
    )  # Estimate the zero-noise value.

    print("=" * 40)
    print("Zero Noise Extrapolation")
    print("=" * 40)
    print(f"Noise Factors      : {noise_factors}")
    print(f"Expectation Values : {expectation_values}")
    print(f"Zero Noise Estimate: {mitigated_expectation:.4f}")

    save_zne_plot(
        noise_factors,
        expectation_values,
        mitigated_expectation,
        "bell_state",
    )  # Save the extrapolation graph.

    plt.show()


if __name__ == "__main__":
    main()