"""
qaoa.py

QAOA (Quantum Approximate Optimization Algorithm) circuit builder.

Solves the Max-Cut problem on a weighted graph using a p=1 QAOA ansatz.
The circuit alternates between a cost unitary (ZZ interactions encoding the
graph edges) and a mixer unitary (X rotations on every qubit).

Default graph: 4-node cycle C4 (edges 0-1, 1-2, 2-3, 3-0).
  - Max-Cut = 4  (alternating partition: {0,2} vs {1,3})
  - Random baseline cut = 2.0
  - p=1 QAOA achieves ~3.0 (75% of optimal), clearly above the noise floor.
  - Max-cut bitstrings: |0101⟩ and |1010⟩ dominate the ideal distribution.

Observable: Cut value = sum over edges of (su XOR sv).
Range: [0, num_edges].
"""

import numpy as np
from qiskit import QuantumCircuit


# Default 4-node cycle graph C4.
_DEFAULT_EDGES   = [(0, 1), (1, 2), (2, 3), (3, 0)]
_DEFAULT_WEIGHTS = [1.0,    1.0,    1.0,    1.0]

# Numerically optimal p=1 QAOA angles for C4 Max-Cut.
# These are found by maximising <C> over (gamma, beta) for the C4 cost Hamiltonian.
# At these angles the circuit achieves ~3.0 / 4.0 expected cut value.
OPTIMAL_GAMMA = 1.1517   # radians  (~0.3666 π)
OPTIMAL_BETA  = 0.3724   # radians  (~0.1185 π)


def create_qaoa(
    num_qubits: int = 4,
    edges: list[tuple[int, int]] | None = None,
    weights: list[float] | None = None,
    gamma: float = OPTIMAL_GAMMA,
    beta: float = OPTIMAL_BETA,
) -> QuantumCircuit:
    """Build a p=1 QAOA circuit for Max-Cut on the given graph.

    Args:
        num_qubits: Number of qubits (= number of graph nodes). Default: 4 (C4).
        edges:      List of (u, v) edge pairs. Defaults to C4 cycle graph.
        weights:    Edge weights. Defaults to all-ones.
        gamma:      Cost unitary angle. Default: numerically optimal for C4.
        beta:       Mixer unitary angle. Default: numerically optimal for C4.

    Returns:
        A QuantumCircuit with measurements on all qubits.

    Circuit structure (p=1 QAOA):
        1. Equal superposition:  H on every qubit
        2. Cost unitary:         RZZ(2γ·w) per edge — decomposed as CX·RZ(2γw)·CX
        3. Mixer unitary:        RX(2β) on every qubit
        4. Measure all qubits
    """
    if num_qubits < 2:
        raise ValueError("QAOA requires at least 2 qubits.")

    if edges is None:
        edges = _DEFAULT_EDGES
    if weights is None:
        weights = [1.0] * len(edges)

    if len(edges) != len(weights):
        raise ValueError("edges and weights must have the same length.")

    circuit = QuantumCircuit(num_qubits, num_qubits)

    # Step 1 — Equal superposition: |+>^n
    for q in range(num_qubits):
        circuit.h(q)

    # Step 2 — Cost unitary: RZZ(2γ·w) for each edge.
    # RZZ(θ) = CX · RZ(θ) · CX — native gates already used across the codebase.
    for (u, v), w in zip(edges, weights):
        angle = 2.0 * gamma * w
        circuit.cx(u, v)
        circuit.rz(angle, v)
        circuit.cx(u, v)

    # Step 3 — Mixer unitary: RX(2β) on every qubit.
    for q in range(num_qubits):
        circuit.rx(2.0 * beta, q)

    # Step 4 — Measure all qubits.
    circuit.measure(range(num_qubits), range(num_qubits))

    return circuit


def qaoa_cut_value(
    counts: dict,
    edges: list[tuple[int, int]] | None = None,
    weights: list[float] | None = None,
) -> float:
    """Compute the expected Max-Cut value from measurement counts.

    Cut value for bitstring s = sum over edges (u,v) of w * (su XOR sv).
    Returns the probability-weighted average cut value.

    Args:
        counts:  {bitstring: count} measurement results.
        edges:   Graph edges. Defaults to C4 edges.
        weights: Edge weights. Defaults to all-ones.

    Returns:
        Expected cut value in [0, num_edges].
    """
    if edges is None:
        edges = _DEFAULT_EDGES
    if weights is None:
        weights = [1.0] * len(edges)

    total = sum(counts.values())
    if total == 0:
        return 0.0

    expected_cut = 0.0
    for bitstring, count in counts.items():
        # Qiskit bitstrings are right-to-left: bitstring[-(q+1)] = qubit q.
        # Strip spaces — Mitiq/Cirq may return space-separated bitstrings.
        bs   = bitstring.replace(" ", "")
        bits = [int(bs[-(q + 1)]) for q in range(len(bs))]
        cut  = sum(w * (bits[u] ^ bits[v]) for (u, v), w in zip(edges, weights))
        expected_cut += (count / total) * cut

    return expected_cut
