"""
qaoa.py

QAOA (Quantum Approximate Optimization Algorithm) circuit builder.

Solves the Max-Cut problem on a weighted graph using a p=1 QAOA ansatz.
The circuit alternates between a cost unitary (ZZ interactions encoding the
graph edges) and a mixer unitary (X rotations on every qubit).

Default graph: 3-node triangle (edges 0-1, 1-2, 0-2) — fully connected,
giving a clear Max-Cut problem with a known optimal cut of 2.

Observable: Cut value = sum of (1 - ZiZj)/2 over edges.
Expectation value range: [0, num_edges].
"""

import numpy as np
from qiskit import QuantumCircuit


# Default 3-node triangle graph — same qubit count as GHZ/QFT benchmarks.
_DEFAULT_EDGES   = [(0, 1), (1, 2), (0, 2)]
_DEFAULT_WEIGHTS = [1.0,    1.0,    1.0]

# Optimal QAOA p=1 angles for the triangle graph (analytically derived).
OPTIMAL_GAMMA = np.pi / 4   # cost unitary angle
OPTIMAL_BETA  = np.pi / 8   # mixer unitary angle


def create_qaoa(
    num_qubits: int = 3,
    edges: list[tuple[int, int]] | None = None,
    weights: list[float] | None = None,
    gamma: float = OPTIMAL_GAMMA,
    beta: float = OPTIMAL_BETA,
) -> QuantumCircuit:
    """Build a p=1 QAOA circuit for Max-Cut on the given graph.

    Args:
        num_qubits: Number of qubits (= number of graph nodes).
        edges:      List of (u, v) edge pairs. Defaults to triangle graph.
        weights:    Edge weights. Defaults to all-ones.
        gamma:      Cost unitary angle (ZZ rotation depth). Default: π/4.
        beta:       Mixer unitary angle (X rotation). Default: π/8.

    Returns:
        A QuantumCircuit with measurements on all qubits.

    Circuit structure (p=1 QAOA):
        1. Equal superposition:  H on every qubit
        2. Cost unitary:         RZZ(2γ·w) for each edge (u, v) with weight w
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
    # RZZ(θ) = CX · RZ(θ) · CX — decomposes into native CX + RZ gates.
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


def qaoa_cut_value(counts: dict, edges: list[tuple[int, int]], weights: list[float] | None = None) -> float:
    """Compute the expected Max-Cut value from measurement counts.

    Cut value for bitstring s: sum over edges (u,v) of w * (su XOR sv).
    Returns the probability-weighted average cut value.

    Args:
        counts:  {bitstring: count} measurement results.
        edges:   Graph edges used in the circuit.
        weights: Edge weights. Defaults to all-ones.

    Returns:
        Expected cut value in [0, num_edges].
    """
    if weights is None:
        weights = [1.0] * len(edges)

    total = sum(counts.values())
    if total == 0:
        return 0.0

    expected_cut = 0.0
    for bitstring, count in counts.items():
        # Qiskit bitstrings are right-to-left: bitstring[-(q+1)] = qubit q.
        bits = [int(bitstring[-(q + 1)]) for q in range(len(bitstring))]
        cut  = sum(w * (bits[u] ^ bits[v]) for (u, v), w in zip(edges, weights))
        expected_cut += (count / total) * cut

    return expected_cut
