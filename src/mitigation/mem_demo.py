#It creates the Bell State, introduces readout noise, performs calibration, applies mitigation, and compares the results.
import matplotlib.pyplot as plt 

from src.backends.simulator import run_circuit  
from src.circuits.bell_state import create_bell_state  
from src.mitigation.measurement_error_mitigation import build_calibration_matrix, mitigate_counts  
from src.noise_models.readout_error import create_readout_error_model  
from src.plotting.circuit_plotter import save_circuit  
from src.plotting.histogram_plotter import save_histogram  


def main():
    circuit = create_bell_state()  # Build the Bell-state circuit.
    save_circuit(circuit, "bell_state_mem", category="ideal")  # Save the ideal circuit image.

    ideal_counts = run_circuit(circuit)  # Run the circuit without noise.
    save_histogram(ideal_counts, "bell_state_mem", category="ideal")  # Save the ideal histogram.

    noise_model = create_readout_error_model(0.05)  # Add a 5% readout error.
    noisy_counts = run_circuit(circuit, noise_model=noise_model)  # Run the Bell circuit with readout noise.
    save_histogram(noisy_counts, "bell_state_mem", category="noisy")  # Save the noisy histogram.

    calibration_matrix = build_calibration_matrix(noise_model)  # Learn the measurement-error matrix.
    mitigated_counts = mitigate_counts(noisy_counts, calibration_matrix)  # Correct the noisy counts with MEM.
    save_histogram(mitigated_counts, "bell_state_mem", category="mitigated")  # Save the mitigated histogram.

    print("Calibration Matrix:\n")  # Show the learned matrix.
    print(calibration_matrix)  # Print the matrix values.
    print("\nIdeal Counts:")  # Label the ideal counts.
    print(ideal_counts)  # Print the ideal Bell counts.
    print("\nNoisy Counts:")  # Label the noisy counts.
    print(noisy_counts)  # Print the noisy Bell counts.
    print("\nMitigated Counts:")  # Label the mitigated counts.
    print(mitigated_counts)  # Print the MEM-corrected counts.

    plt.show() 


if __name__ == "__main__":
    main()