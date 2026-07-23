import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import n_local
from qiskit.quantum_info import SparsePauliOp
from qiskit_aer.primitives import Estimator
from qiskit_aer.noise import NoiseModel
from scipy.optimize import minimize


# H2 Hamiltonian Pauli decomposition at equilibrium bond length (1.4 bohr).
H2_HAMILTONIAN = SparsePauliOp.from_list([
    ("II", -1.0523732),
    ("ZI", +0.3979374),
    ("IZ", -0.3979374),
    ("ZZ", -0.0112801),
    ("XX", +0.1809312),
])

H2_EXACT_ENERGY = -1.857275  # FCI ground state energy (hartree)


def create_vqe_ansatz() -> object:
    """Build the 2-qubit RY-RZ ansatz with 1 CX entangler layer (8 parameters)."""
    return n_local(2, ["ry", "rz"], "cx", reps=1)


def run_vqe(noise_model: NoiseModel | None = None, maxiter: int = 200) -> tuple[float, np.ndarray]:
    """Run VQE and return (ground_state_energy, optimal_parameters).

    Uses COBYLA optimiser. Ideal noise_model=None gives the best variational estimate.
    """
    ansatz    = create_vqe_ansatz()
    estimator = Estimator(backend_options={"noise_model": noise_model} if noise_model else {})

    def cost(params):
        return estimator.run([ansatz], [H2_HAMILTONIAN], [params]).result().values[0]

    result = minimize(cost, np.zeros(ansatz.num_parameters),
                      method="COBYLA", options={"maxiter": maxiter})
    return float(result.fun), result.x


def evaluate_energy(params: np.ndarray, noise_model: NoiseModel | None = None) -> float:
    """Evaluate <H> at fixed params under the given noise model."""
    ansatz    = create_vqe_ansatz()
    estimator = Estimator(backend_options={"noise_model": noise_model} if noise_model else {})
    return float(estimator.run([ansatz], [H2_HAMILTONIAN], [params]).result().values[0])


def build_vqe_circuit(params: np.ndarray) -> QuantumCircuit:
    """Return the bound ansatz with measurements — for counts-based mitigation techniques."""
    ansatz = create_vqe_ansatz()
    bound  = ansatz.assign_parameters(params)
    bound.measure_all()
    return bound
