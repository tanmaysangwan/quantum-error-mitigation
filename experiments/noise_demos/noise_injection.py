from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error

qc = QuantumCircuit(2,2)

qc.h(0)
qc.cx(0,1)

qc.measure(0,0)
qc.measure(1,1)

noise_model = NoiseModel()

error1 = depolarizing_error(0.3, 1)
error2 = depolarizing_error(0.3, 2)

noise_model.add_all_qubit_quantum_error(
    error1,
    ['h']
)

noise_model.add_all_qubit_quantum_error(
    error2,
    ['cx']
)
sim = AerSimulator(
    noise_model=noise_model
)

result = sim.run(
    qc,
    shots=1000
).result()

counts = result.get_counts()

print(counts)