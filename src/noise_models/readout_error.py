from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, ReadoutError

qc = QuantumCircuit(2,2)

qc.h(0)
qc.cx(0,1)

qc.measure([0,1],[0,1])

print(qc.draw())

noise_model = NoiseModel()

readout_error = ReadoutError(
[
    [0.95,0.05],
    [0.10,0.90]
]
)

noise_model.add_all_qubit_readout_error(
    readout_error
)

simulator = AerSimulator(
    noise_model=noise_model
)

result = simulator.run(
    qc,
    shots=4096
).result()

counts = result.get_counts()

print("\nReadout Error Result\n")
print(counts)