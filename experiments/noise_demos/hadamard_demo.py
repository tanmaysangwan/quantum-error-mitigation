from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

qc = QuantumCircuit(1)

qc.h(0)
qc.measure_all()

sim = AerSimulator()

result = sim.run(qc, shots=1000).result()

print(result.get_counts())