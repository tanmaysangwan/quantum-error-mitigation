from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error

qc = QuantumCircuit(2, 2)

qc.h(0)
qc.cx(0, 1)

qc.measure([0, 1], [0, 1])

print("Quantum Circuit:\n")
print(qc.draw())

noise_model = NoiseModel()

error_1 = depolarizing_error(0.02, 1)
error_2 = depolarizing_error(0.05, 2)

noise_model.add_all_qubit_quantum_error(error_1, ['h'])
noise_model.add_all_qubit_quantum_error(error_2, ['cx'])

simulator = AerSimulator(noise_model=noise_model)

job = simulator.run(qc, shots=4096)
result = job.result()

counts = result.get_counts()

print("\nMeasurement Counts")
print(counts)