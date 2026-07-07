from qiskit import QuantumCircuit

qc = QuantumCircuit(1)

qc.x(0)
qc.y(0)
qc.z(0)
qc.h(0)
qc.s(0)
qc.t(0)

print(qc)