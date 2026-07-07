from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, amplitude_damping_error

qc = QuantumCircuit(1,1)

qc.x(0)

qc.measure(0,0)

noise_model = NoiseModel()

error = amplitude_damping_error(0.8) #80% error

noise_model.add_all_qubit_quantum_error(
    error,
    ['x']
)

sim = AerSimulator(noise_model=noise_model)

result = sim.run(
    qc,
    shots=1000
).result()

print(result.get_counts())