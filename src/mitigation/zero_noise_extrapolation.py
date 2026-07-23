import numpy as np
from qiskit import QuantumCircuit


def fold_gates(circuit: QuantumCircuit, scale_factor: int) -> QuantumCircuit:
    """Amplify noise by replacing each gate G with G·(G†·G)^k, where k=(scale_factor-1)/2."""
    if scale_factor < 1 or scale_factor % 2 == 0:
        raise ValueError(f"scale_factor must be an odd integer >= 1, got {scale_factor}.")
    if scale_factor == 1:
        return circuit.copy()

    gate_data    = [instr for instr in circuit.data if instr.operation.name != "measure"]
    measure_data = [instr for instr in circuit.data if instr.operation.name == "measure"]

    folded    = QuantumCircuit(*circuit.qregs, *circuit.cregs)
    num_pairs = (scale_factor - 1) // 2

    for instr in gate_data:
        folded.append(instr.operation, instr.qubits, instr.clbits)
        for _ in range(num_pairs):
            folded.append(instr.operation.inverse(), instr.qubits, instr.clbits)
            folded.append(instr.operation, instr.qubits, instr.clbits)

    for instr in measure_data:
        folded.append(instr.operation, instr.qubits, instr.clbits)

    return folded


def linear_extrapolation(noise_factors: list, expectation_values: list) -> float:
    """Fit a line through (noise_factor, ev) points and return the y-intercept (zero-noise estimate)."""
    coefficients = np.polyfit(noise_factors, expectation_values, 1)
    return float(coefficients[1])


def richardson_extrapolation(noise_factors: list, expectation_values: list) -> float:
    """Cancel leading-order noise terms using analytically derived weights. Requires >=2 points."""
    if len(noise_factors) < 2:
        raise ValueError("Richardson extrapolation requires at least 2 data points.")

    lambdas = np.array(noise_factors, dtype=float)
    values  = np.array(expectation_values, dtype=float)
    n       = len(lambdas)
    estimate = 0.0

    for i in range(n):
        weight = np.prod([lambdas[j] / (lambdas[j] - lambdas[i]) for j in range(n) if j != i])
        estimate += weight * values[i]

    return float(estimate)


def calculate_expectation_value(counts: dict) -> float:
    """Compute <ZZ> = P(00)+P(11)-P(01)-P(10) from measurement counts."""
    total = sum(counts.values())
    if total == 0:
        return 0.0
    return (counts.get("00", 0) + counts.get("11", 0)
            - counts.get("01", 0) - counts.get("10", 0)) / total
