import numpy as np

from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel
from qiskit_aer.noise import coherent_unitary_error

qc = QuantumCircuit(2,2)

qc.h(0)
qc.cx(0,1)

qc.measure([0,1],[0,1])

print(qc.draw())

theta = np.pi/60

faulty_gate = Operator(
[
    [np.cos(theta),-np.sin(theta)],
    [np.sin(theta), np.cos(theta)]
]
)

noise = NoiseModel()

coherent_error = coherent_unitary_error(
    faulty_gate
)

noise.add_all_qubit_quantum_error(
    coherent_error,
    ['h']
)

simulator = AerSimulator(
    noise_model=noise
)

result = simulator.run(
    qc,
    shots=4096
).result()

counts = result.get_counts()

print("\nCoherent Gate Error\n")
print(counts)