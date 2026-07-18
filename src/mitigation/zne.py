import matplotlib.pyplot as plt

from src.backends.simulator import run_circuit
from src.circuits.bell_state import create_bell_state
from src.mitigation.zero_noise_extrapolation import (
    calculate_expectation_value,
    fold_gates,
    linear_extrapolation,
    richardson_extrapolation,
)
from src.noise_models.depolarizing_noise import create_depolarizing_noise_model
from src.plotting.circuit_plotter import save_circuit
from src.plotting.histogram_plotter import save_histogram
from src.plotting.zne_plotter import save_zne_plot


def main():
    circuit = create_bell_state()  # Create the Bell-state circuit.

    save_circuit(circuit, "bell_state_zne", category="ideal")  # Save ideal circuit.

    ideal_counts = run_circuit(circuit)  # Run ideal (noiseless) circuit.
    ideal_expectation = calculate_expectation_value(ideal_counts)

    save_histogram(ideal_counts, "bell_state_zne", category="ideal")  # Save ideal histogram.

    # A single fixed noise model — noise scaling is done by circuit folding,
    # not by increasing the error probability. This matches how ZNE works on
    # real hardware where the noise level cannot be directly controlled.
    noise_model = create_depolarizing_noise_model(0.02)

    # Odd scale factors: 1× (original), 3× (one G†G pair), 5× (two G†G pairs).
    noise_factors = [1, 3, 5]
    expectation_values = []

    for scale_factor in noise_factors:
        folded_circuit = fold_gates(circuit, scale_factor)  # Amplify noise via gate folding.

        save_circuit(
            folded_circuit,
            f"bell_state_zne_{scale_factor}x_folded",
            category="noisy",
        )  # Save folded circuit diagram.

        counts = run_circuit(folded_circuit, noise_model=noise_model)  # Run under fixed noise.

        save_histogram(
            counts,
            f"bell_state_zne_{scale_factor}x",
            category="noisy",
        )  # Save noisy histogram.

        expectation = calculate_expectation_value(counts)  # Calculate <ZZ>.
        expectation_values.append(expectation)

        print(f"{scale_factor}× Folded — Counts: {counts}")
        print(f"   <ZZ>: {expectation:.4f}\n")

    # --- Linear extrapolation ---
    linear_estimate = linear_extrapolation(noise_factors, expectation_values)

    # --- Richardson extrapolation ---
    richardson_estimate = richardson_extrapolation(noise_factors, expectation_values)

    print("=" * 50)
    print("Zero Noise Extrapolation Results (Circuit Folding)")
    print("=" * 50)
    print(f"Noise Scale Factors  : {noise_factors}")
    print(f"Expectation Values   : {[round(e, 4) for e in expectation_values]}")
    print(f"Ideal Reference <ZZ> : {ideal_expectation:.4f}")
    print(f"Linear Estimate      : {linear_estimate:.4f}")
    print(f"Richardson Estimate  : {richardson_estimate:.4f}")
    print()

    # Error from ideal for each method.
    linear_error    = abs(linear_estimate    - ideal_expectation)
    richardson_error = abs(richardson_estimate - ideal_expectation)
    print(f"Linear error from ideal    : {linear_error:.4f}")
    print(f"Richardson error from ideal: {richardson_error:.4f}")
    better = "Richardson" if richardson_error < linear_error else "Linear"
    print(f"Better estimate            : {better}")

    save_zne_plot(
        noise_factors,
        expectation_values,
        richardson_estimate,   # Use Richardson as the primary plotted estimate.
        "bell_state",
    )  # Save the ZNE plot.

    plt.show()


if __name__ == "__main__":
    main()
