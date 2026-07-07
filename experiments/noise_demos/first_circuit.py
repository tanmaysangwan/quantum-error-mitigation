# from qiskit import QuantumCircuit
# qc = QuantumCircuit(2,2)
# qc.h(0)
# qc.cx(0,1)
# qc.measure(0,0)
# qc.measure(1,1)
# print(qc)

# from qiskit import QuantumCircuit
# from qiskit_aer import AerSimulator

# qc = QuantumCircuit(2,2)

# qc.h(0)
# qc.cx(0,1)

# qc.measure(0,0)
# qc.measure(1,1)

# simulator = AerSimulator()

# job = simulator.run(qc, shots=1000)

# result = job.result()

# counts = result.get_counts()

# print(counts)
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
qc = QuantumCircuit(2,2)       #Gives 00 quantum and 2 classical bits
qc.h(0)                        #H gate:  now 50% 00 and 50% 10
qc.cx(0,1)                     #CNOT gate: (0,1) this means 0 is control bit and 1 is target bit
qc.measure_all()

simulator = AerSimulator()
job = simulator.run(qc, shots = 1000)
result = job.result()
counts = result.get_counts()
print(counts)