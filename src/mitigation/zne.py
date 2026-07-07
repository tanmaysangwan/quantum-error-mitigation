import numpy as np

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error

noise_levels = [0.05, 0.10, 0.20]

probabilities = []

for noise in noise_levels:

    qc = QuantumCircuit(2,2)

    qc.h(0)
    qc.cx(0,1)

    qc.measure([0,1],[0,1])

    noise_model = NoiseModel()

    error1 = depolarizing_error(noise,1)
    error2 = depolarizing_error(noise,2)

    noise_model.add_all_qubit_quantum_error(error1,['h'])
    noise_model.add_all_qubit_quantum_error(error2,['cx'])

    sim = AerSimulator(noise_model=noise_model)

    result = sim.run(qc,shots=1000).result()

    counts = result.get_counts()

    correct = counts.get('00',0) + counts.get('11',0)

    probability = correct/1000

    probabilities.append(probability)

print("Noise Levels")
print(noise_levels)

print()

print("Correct Probabilities")
print(probabilities)

coefficients = np.polyfit(
    noise_levels,
    probabilities,
    1
)

m = coefficients[0]

c = coefficients[1]

print()

print("Best Fit Line")

print(f"y = {m:.4f}x + {c:.4f}")

print()

print("Predicted Zero Noise Probability")

print(c)