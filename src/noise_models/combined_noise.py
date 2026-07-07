from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit_aer.noise import *

qc = QuantumCircuit(2,2)

qc.h(0)
qc.cx(0,1)

qc.measure([0,1],[0,1])

print(qc.draw())

noise_model = NoiseModel()

dep_error = depolarizing_error(0.02,1)

amp_error = amplitude_damping_error(0.10)

phase_error = phase_damping_error(0.10)

readout = ReadoutError(
[
    [0.96,0.04],
    [0.08,0.92]
]
)

noise_model.add_all_qubit_quantum_error(
    dep_error,
    ['x','h']
)

noise_model.add_all_qubit_quantum_error(
    amp_error,
    ['x']
)

noise_model.add_all_qubit_quantum_error(
    phase_error,
    ['h']
)

noise_model.add_all_qubit_readout_error(
    readout
)

simulator = AerSimulator(
    noise_model=noise_model
)

result = simulator.run(
    qc,
    shots=4096
).result()

counts = result.get_counts()

print("\nCombined Noise Result\n")
print(counts)