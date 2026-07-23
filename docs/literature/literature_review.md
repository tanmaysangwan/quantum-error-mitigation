# Literature Review: Quantum Error Mitigation for NISQ-Era Quantum Computers

**Project:** Design, Implementation, and Evaluation of Quantum Error Mitigation Techniques  
**Organisation:** DRDO, SAG Lab  
**Author:** Tanmay Sangwan  
**Date:** July 2026

---

## Table of Contents

1. Introduction and Motivation
2. NISQ Devices and the Error Problem
3. Quantum Noise Mechanisms
   - 3.1 Depolarizing Noise
   - 3.2 Amplitude Damping (T1 Relaxation)
   - 3.3 Phase Damping (T2 Dephasing)
   - 3.4 Readout Errors
   - 3.5 Coherent Gate Errors
   - 3.6 Combined and Crosstalk Noise
4. Quantum Error Correction vs Quantum Error Mitigation
5. Quantum Error Mitigation Techniques
   - 5.1 Zero Noise Extrapolation (ZNE)
   - 5.2 Probabilistic Error Cancellation (PEC)
   - 5.3 Clifford Data Regression (CDR)
   - 5.4 Virtual Distillation
   - 5.5 Measurement Error Mitigation (MEM)
   - 5.6 Dynamical Decoupling (DD)
6. Benchmark Circuits and Their Relevance
7. Tools and Frameworks
8. References

---

## 1. Introduction and Motivation

Quantum computing holds the promise of exponential speedups for a class of computationally
hard problems — integer factorisation, quantum chemistry simulation, combinatorial
optimisation, and linear algebra. These speedups are theoretically established through
algorithms such as Shor's algorithm (1994), Grover's search (1996), and the Harrow-Hassidim-
Lloyd algorithm (2009). However, translating these theoretical gains into practical advantage
on physical hardware remains an open engineering challenge.

The fundamental obstacle is noise. Physical qubits — whether realised as superconducting
transmons, trapped ions, photonic systems, or spin qubits — are profoundly fragile. They
interact with their environment on timescales comparable to gate operation times, leading to
coherence loss, gate imperfections, and measurement errors. A single unmitigated error can
corrupt the result of an entire quantum computation.

The current generation of quantum processors, termed Noisy Intermediate-Scale Quantum (NISQ)
devices [Preskill, 2018], contains 50 to several hundred qubits. These devices are too large
to simulate classically (beyond ~50 qubits) but too noisy and too small for full quantum error
correction (QEC), which requires thousands of physical qubits per logical qubit. This places
NISQ computing in an awkward intermediate regime: large enough to be classically intractable
but not reliable enough to run long computations without error.

Quantum Error Mitigation (QEM) has emerged as the practical response to this challenge.
Rather than preventing errors (as QEC does), QEM techniques accept that errors occur and
apply post-processing strategies to recover accurate expectation values from noisy measurement
data. This report surveys the theoretical foundations, practical implementations, and
comparative performance of the six primary QEM techniques implemented in this project.

---

## 2. NISQ Devices and the Error Problem

A NISQ device is characterised by:

- **Qubit count:** 50–1000 qubits, enough to explore problems beyond classical simulation
- **Gate fidelity:** Single-qubit gates achieve ~99.9% fidelity; two-qubit gates ~99–99.5%
- **Coherence times:** T1 (relaxation) and T2 (dephasing) on the order of 100μs–1ms for
  superconducting qubits, compared to gate times of ~50ns (single qubit) and ~200ns (CX)
- **Connectivity:** Limited qubit connectivity requiring SWAP gates that add further error

The "quantum volume" metric [Cross et al., 2019] provides a single-number characterisation of
device capability that accounts for qubit count, connectivity, and gate fidelity together.
IBM's best processors have reached quantum volume 512 (as of 2023), meaning they can reliably
execute random circuits up to approximately 9 qubits deep before errors dominate.

For a circuit with n two-qubit gates each with error rate ε, the probability that the entire
circuit executes without any error is approximately (1-ε)^n. At ε = 0.01 (1% gate error) and
n = 100 gates, this is (0.99)^100 ≈ 0.366 — meaning more than 60% of circuit executions
contain at least one error. This motivates mitigation rather than raw execution for any
non-trivial quantum algorithm.

---

## 3. Quantum Noise Mechanisms

Noise in quantum systems is described mathematically using quantum channels — completely
positive, trace-preserving (CPTP) maps that model how a quantum state ρ evolves under the
influence of its environment. The Kraus representation provides a general form:

```
ε(ρ) = Σ_k K_k ρ K_k†,   where   Σ_k K_k†K_k = I
```

Each Kraus operator K_k corresponds to a specific error process. The different noise models
below correspond to different choices of Kraus operators.

### 3.1 Depolarizing Noise

Depolarizing noise is the most commonly used noise model in quantum error mitigation research
because it is analytically tractable and approximates the average behaviour of gate errors on
real hardware. A single-qubit depolarizing channel with error probability p replaces the qubit
state ρ with a uniformly mixed state with probability p:

```
ε_dep(ρ) = (1 - p)ρ + (p/3)(XρX + YρY + ZρZ)
```

Equivalently, with probability p/3 each, one of the Pauli operators X, Y, or Z is applied
to the qubit. With probability 1-p the identity is applied (no error). This model is
symmetric in all three Pauli error directions, making it rotationally invariant in the Bloch
sphere sense.

For a two-qubit gate such as CNOT, a two-qubit depolarizing channel applies random tensor
products of Pauli operators on both qubits. The 15 non-identity two-qubit Paulis are each
applied with probability p/15.

Depolarizing noise is relevant to gate calibration errors, cosmic ray events, and any error
source that randomises the qubit state without preferential direction. Real superconducting
qubit gates exhibit approximately depolarizing noise for single-qubit gates, though two-qubit
gates often have additional coherent components.

**Implementation in this project:** `src/noise_models/depolarizing_noise.py` applies
depolarizing channels to H gates (1-qubit, rate p) and CX gates (2-qubit, rate p).

### 3.2 Amplitude Damping (T1 Relaxation)

Amplitude damping models energy relaxation from the excited state |1⟩ to the ground state
|0⟩. This captures the physical process of spontaneous emission — a qubit in the excited
state decays to the ground state by releasing a photon to the environment. The timescale for
this decay is T1 (longitudinal relaxation time).

The Kraus operators for the amplitude damping channel are:

```
K_0 = [[1, 0], [0, √(1-γ)]]      (no decay occurred)
K_1 = [[0, √γ], [0, 0]]          (decay occurred)
```

where γ = 1 - exp(-t/T1) is the probability of decay during gate time t. For typical
superconducting qubits with T1 ≈ 100μs and gate time t ≈ 50ns, γ ≈ 0.0005 per gate.
However, during idle periods (waiting for other qubits), qubits experience T1 decay
continuously, making idle-time management critical.

Amplitude damping is not symmetric — it always pushes the state toward |0⟩. This
asymmetry has practical implications: ZNE works less well under amplitude damping than
depolarizing noise because folded gates introduce additional idle time, increasing T1 decay.

**Implementation:** `src/noise_models/amplitude_damping.py`

### 3.3 Phase Damping (T2 Dephasing)

Phase damping (dephasing) describes the loss of quantum coherence in the computational basis
without energy exchange. The qubit retains its population (no |0⟩↔|1⟩ transitions) but loses
the phase relationship between |0⟩ and |1⟩ components. The T2 time characterises this decay.

The Kraus operators are:

```
K_0 = [[1, 0], [0, √(1-λ)]]      (no dephasing)
K_1 = [[0, 0], [0, √λ]]          (dephasing occurred)
```

where λ = 1 - exp(-t/T2) relates to the dephasing probability. In the Bloch sphere picture,
phase damping contracts the x and y components while leaving the z component intact.

T2 dephasing is particularly important for quantum algorithms with long idle periods between
gate operations, such as quantum phase estimation or QAOA with many qubits. Dynamical
Decoupling (Section 5.6) was specifically designed to suppress T2 dephasing.

Note that in practice T2 ≤ 2T1 — T2 is limited by T1 because T1 decay also contributes to
phase randomisation. For superconducting qubits, T2 is typically 50–200μs.

**Implementation:** `src/noise_models/phase_damping.py`

### 3.4 Readout Errors

Readout (measurement) error occurs when the classical outcome of measuring a qubit does not
match the actual quantum state. For a qubit in state |0⟩, the measurement returns 1 with
probability p(1|0); for a qubit in state |1⟩, the measurement returns 0 with probability
p(0|1). For symmetric readout error with rate ε:

```
Confusion matrix M = [[1-ε, ε], [ε, 1-ε]]
```

Readout errors are particularly significant because they occur on every shot of every circuit.
On IBM Quantum hardware, readout fidelity is typically 97–99%, making it one of the dominant
error sources for shallow circuits where gate errors are low.

Readout errors can be corrected using calibration matrices (see Section 5.5 on MEM), making
them one of the most tractable error types to mitigate.

**Implementation:** `src/noise_models/readout_error.py`

### 3.5 Coherent Gate Errors

Unlike stochastic noise (depolarizing, amplitude damping, phase damping), coherent gate errors
are systematic over-rotations or under-rotations of gate angles. If a physical RX(π) gate
consistently applies RX(π + δ) due to miscalibration, every circuit run experiences the same
deterministic error. The error is coherent because it preserves quantum coherence — it does
not mix the state.

The Kraus operator for a coherent error is simply the unitary rotation by the wrong angle.
This makes coherent errors harder to mitigate than stochastic errors: they do not average
out over many shots, and Richardson extrapolation (used by ZNE) is less effective because
the error does not scale linearly with a noise parameter in the same way as depolarizing noise.

Coherent errors arise from imperfect pulse calibration, drive frequency offsets, and
crosstalk between qubits. They can be partially suppressed by randomised benchmarking
(twirling), which converts coherent errors into effective depolarizing noise.

**Implementation:** `src/noise_models/coherent_gate_error.py`

### 3.6 Combined and Crosstalk Noise

Real quantum hardware exhibits all of the above noise types simultaneously, plus additional
effects such as qubit-qubit crosstalk (operations on one qubit perturbing neighbouring qubits),
leakage to non-computational states (|2⟩, |3⟩ for transmon qubits), and time-correlated
noise (non-Markovian effects where the error on one gate depends on the history of previous
gates).

A realistic combined noise model includes depolarizing gate errors, amplitude damping during
and between gates, phase damping from environmental fluctuations, and readout errors at
measurement. This project implements a combined model that layers all four stochastic noise
types simultaneously to approximate this realistic scenario.

**Implementation:** `src/noise_models/combined_noise.py`

---

## 4. Quantum Error Correction vs Quantum Error Mitigation

Before surveying mitigation techniques, it is important to understand why QEM — rather than
full QEC — is the appropriate approach for NISQ devices.

**Quantum Error Correction (QEC)** encodes a single logical qubit into multiple physical
qubits, using redundancy to detect and correct errors without measuring the logical qubit
directly. The surface code — the leading candidate for fault-tolerant quantum computing —
requires approximately 1000 physical qubits per logical qubit at realistic error rates (~0.1%)
to achieve a logical error rate below 10^-6 per gate. This overhead makes QEC impractical on
current devices with ≤1000 total physical qubits.

QEC also requires fault-tolerant gate sets, transversal operations, and ancilla management
that multiply the circuit depth substantially. A fault-tolerant Toffoli gate in the surface
code requires ~100 T gates each requiring magic state distillation — the overhead is staggering.

**Quantum Error Mitigation (QEM)** takes a fundamentally different approach: accept that
physical errors occur, run the noisy circuit many times, and use classical post-processing
to reconstruct an estimate of the ideal (noiseless) expectation value. QEM:

- Does NOT require extra qubits for encoding
- Does NOT need fault-tolerant gate sets
- DOES require additional circuit executions (sampling overhead)
- DOES increase the classical post-processing burden
- CAN only improve expectation values of observables, not produce full error-corrected states

The key insight is that for many near-term applications — variational quantum eigensolvers,
QAOA, quantum machine learning — the output of interest is an expectation value ⟨O⟩ rather
than a specific quantum state. QEM is sufficient for this goal.

The price paid is a polynomial overhead in circuit executions, which grows with noise level
and circuit size. This overhead is fundamentally unavoidable — information theory sets a lower
bound on how many noisy samples are required to reconstruct a noiseless expectation value.
Specifically, for PEC the overhead grows as γ² per gate, where γ > 1 depends on the error rate.

---

## 5. Quantum Error Mitigation Techniques

### 5.1 Zero Noise Extrapolation (ZNE)

**Original paper:** Temme, K., Bravyi, S., & Gambetta, J. M. (2017). "Error Mitigation for
Short-Depth Quantum Circuits." *Physical Review Letters*, 119(18), 180509.

**Core idea:** If the expectation value of an observable depends smoothly on the noise
strength λ, we can evaluate the circuit at several amplified noise levels λ, 3λ, 5λ, ... and
extrapolate back to the zero-noise limit λ → 0.

**Mathematical foundation:**

The noisy expectation value ⟨O⟩_λ can be written as a Taylor expansion in λ:

```
⟨O⟩_λ = ⟨O⟩_ideal + a₁λ + a₂λ² + ...
```

If we evaluate this at n noise levels λ₁, λ₂, ..., λₙ, we can fit a polynomial and
extrapolate to λ = 0. The Richardson extrapolation formula — which cancels the first n-1
error terms exactly — gives:

```
⟨O⟩_ideal ≈ Σᵢ [ Πⱼ≠ᵢ (λⱼ / (λⱼ - λᵢ)) ] × ⟨O⟩_λᵢ
```

This is a weighted combination of the noisy measurements at different noise levels.

**Noise amplification via circuit folding:**

On real hardware, the noise level cannot be directly controlled. Instead, noise is amplified
by *gate folding*: replacing each gate G with G · G† · G (one additional G†G pair, tripling
the noise contribution of that gate). More generally, replacing G with G · (G†G)^k multiplies
the gate's effective error rate by (2k+1). This is valid because G · G† = I exactly — the
additional gates cancel logically while adding physical noise.

The key advantage of circuit folding is that it works without any knowledge of the noise model.
No noise characterisation is required. The method is therefore highly practical for real hardware.

**Limitations:**
- Richardson extrapolation assumes noise is low-order polynomial in λ. At high noise levels
  where higher-order terms are significant, the extrapolation overfits
- Gate folding triples circuit depth at 3× scale factor, which is problematic for circuits
  already close to the coherence limit
- VQE parameterised circuits under folding may have different optimal parameters, causing
  extrapolation errors in variational algorithms

**Variants:**
- Linear extrapolation: fits a line through (λ₁, ⟨O⟩₁), (λ₂, ⟨O⟩₂), reads off intercept
- Richardson extrapolation: exact polynomial cancellation, more accurate with more points
- Exponential extrapolation: models ⟨O⟩_λ ≈ A·exp(-bλ), better for deeply noisy circuits

**Implementation:** `src/mitigation/zero_noise_extrapolation.py` implements gate folding,
linear extrapolation, and Richardson extrapolation. Demo: `src/mitigation/zne.py`.

---

### 5.2 Probabilistic Error Cancellation (PEC)

**Original paper:** Temme, K., Bravyi, S., & Gambetta, J. M. (2017). "Error Mitigation for
Short-Depth Quantum Circuits." *Physical Review Letters*, 119(18), 180509. (same paper as ZNE)

**Extended treatment:** Endo, S., Benjamin, S., & Li, Y. (2018). "Practical Quantum Error
Mitigation for Near-Future Applications." *Physical Review X*, 8(3), 031027.

**Core idea:** Every noisy quantum channel Λ can be written as a quasi-probability mixture of
implementable operations. By sampling from this quasi-probability distribution and combining
results with appropriate signs, the expectation value under the ideal (noise-free) channel
can be recovered.

**Mathematical foundation:**

For a single-qubit depolarizing channel Λ with error rate p, the ideal channel I (identity)
can be decomposed as:

```
I = Σ_i qᵢ Oᵢ ∘ Λ
```

where Oᵢ are additional Pauli operations and qᵢ are quasi-probabilities (real numbers,
some negative). The coefficients are:

```
q_I = (1 + 3/(4α)) / (4/α - 3)    where α = 1 - 4p/3
q_P = -1 / (4α(1 - 4p/3))         for each Pauli P ∈ {X, Y, Z}
```

The one-norm γ = Σᵢ |qᵢ| = |q_I| + |q_X| + |q_Y| + |q_Z| > 1 quantifies the sampling
overhead. To estimate ⟨O⟩_ideal unbiasedly, one samples Oᵢ with probability |qᵢ|/γ, applies
it to the circuit, measures, and multiplies by sign(qᵢ) × γ. Averaging over many samples
gives an unbiased estimator of the ideal expectation value.

For a circuit with n gates each with γ overhead, the total overhead is γⁿ — this is the
key limitation of PEC. At 5% error rate (p = 0.05), γ ≈ 1.23 per gate. For a 20-gate circuit,
the overhead is 1.23²⁰ ≈ 36×.

**Implementation:** `src/mitigation/probabilistic_error_cancellation.py` implements the
quasi-probability representation analytically, and uses Mitiq's `execute_with_pec` for
Monte Carlo sampling. Demo: `src/mitigation/pec.py`.

---

### 5.3 Clifford Data Regression (CDR)

**Original paper:** Czarnik, P., Arrasmith, A., Coles, P. J., & Cincio, L. (2021). "Error
Mitigation with Clifford Quantum-Circuit Data." *Quantum*, 5, 592.

**Core idea:** Clifford circuits can be simulated classically in polynomial time (Gottesman-
Knill theorem). If we take the target circuit, replace a fraction of its non-Clifford gates
with Clifford gates, we obtain training circuits that can be run on both the noisy device
and the ideal classical simulator. A linear model trained on the difference between noisy
and ideal values of the training circuits can then be applied to correct the noisy value of
the full target circuit.

**Mathematical foundation:**

Given a target circuit C with noisy expectation value E_noisy and ideal value E_ideal, CDR
constructs n training circuits {Cᵢ} by replacing some non-Clifford gates (RZ(θ) → RZ(π/2),
etc.). For each training circuit:

```
Cᵢ : (a_noisy_i, a_ideal_i)  where a_ideal_i is computed by classical simulation
```

A linear regression model fits:
```
E_ideal ≈ α × E_noisy + β
```

using the training pairs (a_noisy_i, a_ideal_i). The fitted model is then applied to the
noisy measurement of the original circuit to produce the mitigated estimate.

**Why Clifford training circuits work:** Clifford gates are the normaliser of the Pauli group
— they map Pauli operators to Pauli operators under conjugation. The Gottesman-Knill theorem
shows that circuits composed only of Clifford gates (H, CNOT, S, and their combinations) can
be simulated classically in O(n²) time using the stabiliser formalism. This means the ideal
expectation value of any Clifford training circuit can be computed exactly without a quantum
simulator, providing perfect training labels.

**Limitations:**
- Requires the circuit to have significant Clifford structure. Circuits with many non-Clifford
  gates (like QFT with arbitrary phase angles, or QAOA with optimal non-Clifford angles) have
  poor training circuit quality
- The linear model assumption may not hold far from the Clifford point
- Sampling overhead of 1 + n_training circuits (typically 10–20×)

**Implementation:** `src/mitigation/clifford_data_regression.py` uses Mitiq's
`execute_with_cdr`. Demo: `src/mitigation/cdr.py`.

---

### 5.4 Virtual Distillation

**Original paper:** Huggins, W. J., McArdle, S., O'Brien, T. E., Lee, J., Rubin, N. C.,
Babbush, R., ... & Kim, I. D. (2021). "Virtual distillation for quantum error mitigation."
*Physical Review X*, 11(4), 041036.

Also independently proposed as "Error mitigation by symmetry verification" and in:
Cai, Z. (2021). "Resource-efficient Purification-based Quantum Error Mitigation." arXiv:2107.07279.

**Core idea:** For a noisy quantum state ρ = ρ_ideal + ε_noise, the squared density matrix
ρ² has a noise contribution that is second-order in ε_noise. The estimator
Tr(ρ² O) / Tr(ρ²) therefore has reduced noise compared to the direct estimate Tr(ρO).

**Mathematical foundation:**

Let the ideal state be the pure state |ψ⟩⟨ψ|. Under noise, the prepared state is:
```
ρ = (1-ε)|ψ⟩⟨ψ| + ε · ρ_noise
```

The squared density matrix is:
```
ρ² = (1-ε)²|ψ⟩⟨ψ| + (1-ε)ε(|ψ⟩⟨ψ|ρ_noise + ρ_noise|ψ⟩⟨ψ|) + ε²ρ_noise²
```

For an observable O commuting with the state:
```
Tr(ρ² O) / Tr(ρ²) = ⟨ψ|O|ψ⟩ + O(ε²)
```

The error is second-order in ε, compared to first-order in ε for the raw estimator Tr(ρO).

**Practical estimator:**

In practice, ρ² is estimated without creating two copies of the circuit using the
measurement probability distribution. For a circuit producing measurement outcomes with
probabilities {P(s)}:

```
Tr(ρ²O) / Tr(ρ²) = Σ_s w(s) P(s)² / Σ_s P(s)²
```

where w(s) is the eigenvalue of O for bitstring s. This requires only one circuit execution
with high shot count (≥8192 for stable probability estimates).

**Limitations:**
- Requires high shot counts for stable P(s)² estimates
- Only provides error suppression to second order — for very noisy states the improvement
  is limited
- Assumes the noise is incoherent (mixed state). Coherent errors may not be suppressed
- Does not work if the ideal state has a flat measurement distribution (all P(s) ≈ 1/2ⁿ)

**Implementation:** `src/mitigation/virtual_distillation.py`. Demo: `src/mitigation/vd.py`.

---

### 5.5 Measurement Error Mitigation (MEM)

**Reference:** Bravyi, S., Sheldon, S., Kandala, A., Mckay, D. C., & Gambetta, J. M. (2021).
"Mitigating measurement errors in multiqubit experiments." *Physical Review A*, 103(4), 042605.

Also described in the IBM mthree package documentation:
https://www.ibm.com/quantum/blog/mthree-qiskit-extension

**Core idea:** Readout errors can be characterised by a calibration matrix M where
M[i,j] = P(measure state i | prepared state j). Given noisy counts, multiply by M⁻¹ to
recover the ideal counts.

**Mathematical foundation:**

For n qubits, the calibration matrix is 2ⁿ × 2ⁿ. Each column j is obtained by preparing
the basis state |j⟩ (e.g., |000⟩, |001⟩, ..., |111⟩ for 3 qubits) and measuring the
outcome distribution. The resulting matrix M satisfies:

```
p_noisy = M × p_ideal    →    p_ideal = M⁻¹ × p_noisy
```

where p_noisy and p_ideal are probability vectors over all 2ⁿ basis states. The corrected
probability vector may have small negative entries due to statistical noise; these are
clipped to zero and the vector is renormalised.

**Scalability challenge:** Full calibration requires 2ⁿ circuits (one per basis state), making
it exponentially expensive for large n. For n = 10 qubits, 1024 calibration circuits are
needed. Practical approaches use:
- Tensored calibration: assume independent readout errors per qubit, requiring only 2n circuits
- M3 (matrix-free measurement mitigation, IBM): solves the linear system iteratively without
  explicitly inverting M

**Implementation:** `src/mitigation/measurement_error_mitigation.py` and
`src/mitigation/calibration.py`. Demo: `src/mitigation/mem_demo.py`.

---

### 5.6 Dynamical Decoupling (DD)

**Foundational work:** Viola, L., Knill, E., & Lloyd, S. (1999). "Dynamical Decoupling of
Open Quantum Systems." *Physical Review Letters*, 82(12), 2417.

**Application to quantum computing:** Biercuk, M. J., Uys, H., VanDevender, A. P., Shiga,
N., Itano, W. M., & Bollinger, J. J. (2011). "Optimized dynamical decoupling in a model
quantum memory." *Nature*, 458(7241), 996–1000.

**Core idea:** Insert sequences of fast pulses (π rotations) into idle periods of a quantum
circuit to average out the effect of low-frequency environmental noise (dephasing). The
pulse sequences are designed so that the accumulated phase error integrates to zero over
each decoupling cycle.

**Mathematical foundation:**

Consider a qubit coupled to a bath with interaction Hamiltonian H_int = σ_z ⊗ B, where B
is a bath operator. During an idle period of duration T, the qubit accumulates a phase error:

```
U_error = exp(-i ∫₀ᵀ H_int dt)
```

If we insert two π pulses (X gates) at times T/4 and 3T/4, the X pulses flip the qubit:
```
U_DD = X · exp(-i H_int T/2) · X · exp(-i H_int T/2)
     = exp(+i H_int T/2) · exp(-i H_int T/2) = I  (to first order)
```

The sign change from the X pulse causes the phase error to cancel. This is the simplest
"bang-bang" decoupling. More sophisticated sequences:

- **XY-4 sequence:** X, Y, X, Y pulses — cancels both σ_z and σ_x coupling to first order
- **XYXY (XY-4):** Symmetric XY sequence — better performance, cancels more bath coupling terms
- **Uhrig DD:** Non-uniformly spaced pulses optimised for specific spectral densities

**Why DD works on T2 but not depolarizing noise:**

DD suppresses dephasing noise because dephasing acts as a slowly varying Z rotation during
idle time. The π pulses flip the qubit, reversing the sign of the accumulated Z phase.
However, depolarizing noise applies instantaneous random Pauli operators at gate application
time — there is no idle-time accumulation to reverse. This is why DD shows little benefit
in this project's depolarizing benchmark.

On real hardware with genuine T2 dephasing (e.g., from flux noise in superconducting circuits),
DD can extend effective coherence time by 2–5× and is routinely applied as preprocessing
before running QAOA, VQE, or other algorithms on IBM Quantum hardware.

**Implementation:** `src/mitigation/dynamical_decoupling.py` uses Mitiq's `execute_with_ddd`
with XX and XYXY pulse rules. Demo: `src/mitigation/dd.py`.

---

## 6. Benchmark Circuits and Their Relevance

### 6.1 Bell State

The Bell state |Φ⁺⟩ = (|00⟩ + |11⟩)/√2 is the simplest maximally entangled state, prepared
by a Hadamard gate followed by a CNOT:

```
|Φ⁺⟩ = CX · (H ⊗ I) |00⟩
```

It is the canonical 2-qubit benchmark because its ideal measurement distribution is exactly
50% |00⟩ and 50% |11⟩, giving ⟨ZZ⟩ = +1. Any noise source that introduces |01⟩ or |10⟩
outcomes reduces ⟨ZZ⟩ below 1. The Bell state is close to a Clifford circuit (H and CX are
both Clifford gates), making it well-suited for CDR.

### 6.2 GHZ State

The n-qubit GHZ state |GHZ⟩ = (|0...0⟩ + |1...1⟩)/√2 generalises the Bell state to n
qubits. It is prepared by H on qubit 0 followed by a chain of CNOT gates:

```
|GHZ⟩ = CX(n-1,n) · ... · CX(0,1) · (H ⊗ I^n-1) |0...0⟩
```

GHZ states are maximally multi-party entangled and are used to test the scaling of mitigation
techniques with qubit count. The circuit depth is O(N), making it a relatively shallow circuit.
GHZ states are also near-Clifford, benefiting CDR.

### 6.3 Quantum Fourier Transform (QFT)

The QFT performs the discrete Fourier transform on quantum amplitudes:

```
QFT|j⟩ = (1/√N) Σ_k exp(2πijk/N) |k⟩
```

It is a component of Shor's algorithm (period finding), quantum phase estimation, and the
hidden subgroup algorithm. The QFT requires O(N²) gates including controlled-phase rotations
with angles π/2^k for k = 1, ..., N-1. These non-Clifford gates make QFT a challenging
benchmark for CDR and a good test of ZNE and VD at larger qubit counts.

### 6.4 Variational Quantum Eigensolver (VQE)

VQE [Peruzzo et al., 2014] is a hybrid quantum-classical algorithm for finding the ground
state energy of a Hamiltonian. It prepares a parameterised ansatz state |ψ(θ)⟩, measures
the expectation value ⟨H⟩(θ) = ⟨ψ(θ)|H|ψ(θ)⟩, and uses a classical optimiser to minimise
this over the parameters θ.

In this project, VQE is applied to the H2 molecule Hamiltonian at equilibrium bond length
(1.4 bohr), using the BK-transformed Pauli decomposition:

```
H = -1.0524 II + 0.3979 ZI - 0.3979 IZ - 0.0113 ZZ + 0.1809 XX
```

The exact ground state energy is -1.8573 hartree (FCI). VQE with a hardware-efficient
RY-RZ ansatz achieves approximately -1.85 hartree ideally. Under 5% depolarizing noise,
the ansatz parameters COBYLA-optimises to a higher (worse) energy.

VQE is the prototypical near-term application motivating QEM research.

### 6.5 QAOA

The Quantum Approximate Optimization Algorithm [Farhi, Goldstone & Gutmann, 2014] solves
combinatorial optimisation problems by alternating between a cost unitary and a mixer unitary.
For the Max-Cut problem on graph G = (V, E):

```
Cost unitary:   U_C(γ) = exp(-iγ Σ_(u,v)∈E ZuZv/2) = product of RZZ gates
Mixer unitary:  U_B(β) = exp(-iβ Σ_v Xv) = product of RX gates
```

The p=1 QAOA circuit alternates one cost layer and one mixer layer. For the 4-node cycle graph
C4, the optimal parameters γ = 1.1517, β = 0.3724 achieve an expected cut value ≈ 3.0/4.0
(75% of optimal). QAOA is a non-Clifford, non-Hamiltonian-simulation circuit — its noise
response differs from both VQE and QFT, making it a valuable distinct benchmark.

---

## 7. Tools and Frameworks

### Qiskit (IBM Quantum)

Qiskit is IBM's open-source quantum computing framework, providing:
- **Circuit construction:** `QuantumCircuit` API for building quantum programs
- **Transpilation:** Circuit optimization and mapping to hardware gate sets
- **Primitives:** `Estimator` (expectation values) and `Sampler` (measurement distributions)
- **Qiskit Aer:** High-performance noisy quantum simulator with realistic noise models

Version used in this project: Qiskit 2.4.2, Qiskit Aer 0.17.2.

### Mitiq (Unitary Foundation)

Mitiq is an open-source Python library implementing quantum error mitigation techniques in a
hardware-agnostic way. It provides production implementations of ZNE, PEC, CDR, DD, and
other techniques that work with any circuit-based quantum backend (Qiskit, Cirq, Braket, etc.).

Key Mitiq functions used in this project:
- `execute_with_pec`: Monte Carlo quasi-probability sampling
- `execute_with_cdr`: Clifford Data Regression with near-Clifford training circuits
- `execute_with_ddd`: Dynamical Decoupling with configurable pulse rules
- `represent_operations_in_circuit_with_global_depolarizing_noise`: QPR construction

Version used: Mitiq 1.0.0 (requires Cirq 1.6.1 as backend dependency).

### NumPy and SciPy

NumPy provides the numerical linear algebra operations underlying calibration matrix
inversion (MEM) and Richardson extrapolation (ZNE). SciPy's COBYLA optimizer is used for
VQE parameter optimization.

---

## 8. References

1. **Temme, K., Bravyi, S., & Gambetta, J. M. (2017).** Error Mitigation for Short-Depth
   Quantum Circuits. *Physical Review Letters*, 119(18), 180509.
   https://doi.org/10.1103/PhysRevLett.119.180509
   *(Introduced ZNE and PEC)*

2. **Endo, S., Benjamin, S., & Li, Y. (2018).** Practical Quantum Error Mitigation for
   Near-Future Applications. *Physical Review X*, 8(3), 031027.
   https://doi.org/10.1103/PhysRevX.8.031027
   *(Extended PEC theory and practical implementation guidance)*

3. **Cai, Z. (2021).** Resource-efficient Purification-based Quantum Error Mitigation.
   arXiv:2107.07279.
   https://arxiv.org/abs/2107.07279
   *(Virtual Distillation / quantum purification approach)*

4. **Kandala, A. et al. (2019).** Error Mitigation Extends the Computational Reach of a
   Noisy Quantum Processor. *Nature*, 567, 491–495.
   https://doi.org/10.1038/s41586-019-1040-7
   *(Experimental demonstration of ZNE on IBM hardware for VQE)*

5. **Czarnik, P., Arrasmith, A., Coles, P. J., & Cincio, L. (2021).** Error Mitigation with
   Clifford Quantum-Circuit Data. *Quantum*, 5, 592.
   https://doi.org/10.22331/q-2021-11-26-592
   *(CDR original paper)*

6. **Huggins, W. J. et al. (2021).** Virtual Distillation for Quantum Error Mitigation.
   *Physical Review X*, 11(4), 041036.
   https://doi.org/10.1103/PhysRevX.11.041036
   *(Virtual Distillation original paper)*

7. **Viola, L., Knill, E., & Lloyd, S. (1999).** Dynamical Decoupling of Open Quantum
   Systems. *Physical Review Letters*, 82(12), 2417.
   https://doi.org/10.1103/PhysRevLett.82.2417
   *(Dynamical Decoupling foundational paper)*

8. **Bravyi, S., Sheldon, S., Kandala, A., Mckay, D. C., & Gambetta, J. M. (2021).**
   Mitigating measurement errors in multiqubit experiments. *Physical Review A*, 103(4), 042605.
   https://doi.org/10.1103/PhysRevA.103.042605
   *(Measurement Error Mitigation calibration matrix method)*

9. **Preskill, J. (2018).** Quantum Computing in the NISQ Era and Beyond. *Quantum*, 2, 79.
   https://doi.org/10.22331/q-2018-08-06-79
   *(Introduced the term "NISQ"; defines the era and challenges)*

10. **Peruzzo, A. et al. (2014).** A variational eigenvalue solver on a photonic quantum
    processor. *Nature Communications*, 5, 4213.
    https://doi.org/10.1038/ncomms5213
    *(Original VQE paper)*

11. **Farhi, E., Goldstone, J., & Gutmann, S. (2014).** A Quantum Approximate Optimization
    Algorithm. arXiv:1411.4028.
    https://arxiv.org/abs/1411.4028
    *(Original QAOA paper)*

12. **Cross, A. W., Bishop, L. S., Sheldon, S., Nation, P. D., & Gambetta, J. M. (2019).**
    Validating quantum computers using randomized model circuits. *Physical Review A*, 100(3),
    032328.
    https://doi.org/10.1103/PhysRevA.100.032328
    *(Quantum Volume metric)*

13. **IBM Quantum Documentation.** Error Mitigation and Suppression Techniques.
    https://quantum.cloud.ibm.com/docs/en/guides/error-mitigation-and-suppression-techniques

14. **Mitiq Documentation.** Core Concepts — Mitiq 1.0.0.
    https://mitiq.readthedocs.io/en/stable/

15. **IBM Quantum Blog.** M3: Matrix-free Measurement Mitigation.
    https://www.ibm.com/quantum/blog/mthree-qiskit-extension

---

*This literature review covers the theoretical foundations of all noise models and mitigation
techniques implemented in this project. For experimental results and quantitative comparison,
see `results/reports/comparative_performance_study.md`.*
