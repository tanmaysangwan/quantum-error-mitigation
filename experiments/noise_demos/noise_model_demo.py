from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

qc = QuantumCircuit(2,2)

qc.h(0)
qc.cx(0,1)

# Noise inserted intentionally
qc.x(1)

qc.measure(0,0)
qc.measure(1,1)

sim = AerSimulator()

result = sim.run(qc, shots=1000).result()

print(result.get_counts())