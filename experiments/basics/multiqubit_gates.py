from qiskit import QuantumCircuit

qc = QuantumCircuit(2)

qc.h(0)
qc.cx(0,1)
qc.cz(0,1)
qc.swap(0,1)

print(qc)