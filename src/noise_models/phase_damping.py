from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, phase_damping_error

qc = QuantumCircuit(2,2)

qc.h(0)
qc.cx(0,1)

qc.measure([0,1],[0,1])

print(qc.draw())

noise_model = NoiseModel()

phase_error = phase_damping_error(0.20)

noise_model.add_all_qubit_quantum_error(
    phase_error,
    ['h','x']
)

simulator = AerSimulator(
    noise_model=noise_model
)

result = simulator.run(
    qc,
    shots=4096
).result()

counts = result.get_counts()

print("\nPhase Damping Result\n")
print(counts)