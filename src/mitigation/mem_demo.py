import numpy as np

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, ReadoutError

qc = QuantumCircuit(1, 1)

qc.measure(0, 0)

readout_error = ReadoutError([
    [0.95, 0.05],               #Callibration Matrix
    [0.03, 0.97]
])

# Create a Noise Model
noise_model = NoiseModel()

# Add readout error to every qubit
noise_model.add_all_qubit_readout_error(readout_error)



sim = AerSimulator(noise_model=noise_model)

job = sim.run(qc, shots=1000)

result = job.result()

counts = result.get_counts()

print("Measured Counts:")
print(counts)

M = np.array([
    [0.95, 0.03],
    [0.05, 0.97]
])

print("\nCalibration Matrix:")
print(M)


M_inverse = np.linalg.inv(M)

print("\nInverse Calibration Matrix:")
print(M_inverse)

measured_vector = np.array([
    counts.get('0', 0),
    counts.get('1', 0)
])

print("\nMeasured Vector:")
print(measured_vector)

corrected_vector = M_inverse @ measured_vector

print("\nCorrected Vector:")
print(corrected_vector)

corrected_counts = {
    '0': round(corrected_vector[0]),
    '1': round(corrected_vector[1])
}

print("\nCorrected Counts:")
print(corrected_counts)