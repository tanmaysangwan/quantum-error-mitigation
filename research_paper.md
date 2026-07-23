---
title: "Comparative Evaluation of Quantum Error Mitigation Techniques for NISQ-Era Quantum Computers"
author:
  - Tanmay Sangwan
affiliation: "Defence Research and Development Organisation (DRDO), Scientific Analysis Lab (SAG Lab); B.Tech Computer Science and Engineering"
date: "July 2026"
format:
  columns: 2
---

<style>
  .ieee-paper { column-count: 2; column-gap: 0.25in; text-align: justify; font-family: "Times New Roman", Times, serif; font-size: 10pt; line-height: 1.15; }
  .ieee-paper h1, .ieee-paper h2, .ieee-paper h3, .ieee-paper .title-block, .ieee-paper .abstract, .ieee-paper table, .ieee-paper figure { column-span: all; }
  .ieee-paper h1 { font-size: 24pt; text-align: center; margin-bottom: 0.2em; }
  .ieee-paper .authors { text-align: center; font-size: 11pt; margin-bottom: 0.5em; }
  .ieee-paper .abstract { font-size: 9pt; margin: 1em 0; }
  .ieee-paper .abstract-title { font-weight: bold; font-style: italic; display: inline; }
  .ieee-paper h2 { font-size: 10pt; font-weight: bold; text-transform: uppercase; margin-top: 0.8em; }
  .ieee-paper h3 { font-size: 10pt; font-weight: bold; font-style: italic; margin-top: 0.6em; }
  .ieee-paper table { font-size: 8pt; border-collapse: collapse; width: 100%; margin: 0.5em 0; }
  .ieee-paper th, .ieee-paper td { border: 1px solid #333; padding: 3px 5px; text-align: center; }
  .ieee-paper th { font-weight: bold; background: #f5f5f5; }
  .ieee-paper .caption { font-size: 8pt; text-align: center; font-style: italic; margin-top: 0.2em; }
  .ieee-paper .references { font-size: 8pt; column-span: all; }
  .ieee-paper .references ol { padding-left: 1.2em; }
  .ieee-paper .references li { margin-bottom: 0.4em; text-align: left; }
</style>

<div class="ieee-paper">

<div class="title-block">

# Comparative Evaluation of Quantum Error Mitigation Techniques for NISQ-Era Quantum Computers

<div class="authors">

**Tanmay Sangwan**<br>
Defence Research and Development Organisation (DRDO), Scientific Analysis Lab (SAG Lab)<br>
B.Tech Computer Science and Engineering

</div>

<div class="abstract">

<span class="abstract-title">Abstract—</span>
Near-term quantum processors operate in the Noisy Intermediate-Scale Quantum (NISQ) regime, where gate fidelities of 99–99.9% and limited coherence times make unmitigated computation unreliable. Quantum Error Mitigation (QEM) offers a practical alternative to full error correction by recovering accurate expectation values through classical post-processing of noisy measurement data. We present a unified open-source framework implementing six QEM techniques—Measurement Error Mitigation (MEM), Zero Noise Extrapolation (ZNE), Probabilistic Error Cancellation (PEC), Clifford Data Regression (CDR), Virtual Distillation (VD), and Dynamical Decoupling (DD)—and evaluate them systematically on five benchmark circuits (Bell, GHZ-3, QFT-3, QAOA-C4, and VQE for H₂) across five depolarizing noise levels (1%–20%) using Qiskit Aer. Our results on 145 benchmark configurations show that no single technique dominates: CDR achieves perfect fidelity on near-Clifford circuits but fails on QFT (0% fidelity); PEC delivers 100% error reduction at ≤10% noise but collapses above 15%; VD maintains 78–99% error reduction on deep circuits with only 1× sampling overhead; and MEM achieves 95–100% error reduction on QFT at moderate-to-high noise. We provide quantitative recommendations for technique selection based on circuit structure, noise regime, and sampling budget.

</div>

**Index Terms—** Quantum error mitigation, NISQ computing, zero noise extrapolation, virtual distillation, Clifford data regression, probabilistic error cancellation, measurement error mitigation, dynamical decoupling.

</div>

## I. Introduction

Quantum computing promises exponential speedups for problems including integer factorisation [1], combinatorial optimisation [11], and quantum chemistry simulation [10]. Realising these advantages on physical hardware remains an open engineering challenge. Physical qubits—whether implemented as superconducting transmons, trapped ions, or photonic systems—decoherence on timescales comparable to gate operation times, corrupting computational results through gate imperfections, energy relaxation, dephasing, and readout errors.

The current generation of quantum processors, termed NISQ devices [9], contains 50–1000 qubits. These systems are large enough to explore classically intractable problem sizes yet too noisy and too small for fault-tolerant quantum error correction (QEC), which requires thousands of physical qubits per logical qubit at current error rates. For a circuit with *n* two-qubit gates each at error rate ε = 0.01, the probability of error-free execution is approximately (1−ε)ⁿ; at *n* = 100 gates this yields only 36.6% success probability.

Quantum Error Mitigation (QEM) addresses this gap by accepting that errors occur during circuit execution and applying classical post-processing to recover accurate expectation values ⟨*O*⟩ from noisy measurement data [1], [2]. Unlike QEC, QEM requires no additional qubits and operates on existing hardware, at the cost of increased sampling overhead. Techniques such as Zero Noise Extrapolation (ZNE) [1], [4], Probabilistic Error Cancellation (PEC) [1], [2], Clifford Data Regression (CDR) [5], Virtual Distillation (VD) [3], [6], Measurement Error Mitigation (MEM) [8], and Dynamical Decoupling (DD) [7] have been demonstrated individually on hardware and in simulation, but systematic cross-technique comparison under controlled conditions remains limited.

This paper presents the design, implementation, and empirical evaluation of a modular QEM framework developed at DRDO SAG Lab. Our contributions are:

1. **A unified mitigation framework** implementing all six major QEM techniques with generic evaluator interfaces, decoupling observable computation from mitigation logic and enabling reuse across circuit types.

2. **A comprehensive benchmark suite** evaluating 5 circuits × 6 techniques × 5 noise levels (145 experiment configurations), with circuit-specific observables and a dual-path VQE evaluation (Estimator-based ZNE and counts-based MEM/CDR/VD/DD).

3. **Quantitative performance analysis** revealing technique-specific operating regimes, scalability characteristics (2–8 qubits), and practical selection guidelines for NISQ applications.

## II. Background

### A. NISQ Noise Mechanisms

Noise in quantum systems is modelled as completely positive, trace-preserving (CPTP) channels ε(ρ) = Σₖ *K*ₖ ρ *K*ₖ†. The six noise models implemented in our framework cover the dominant error sources on superconducting hardware:

- **Depolarizing noise:** With probability *p*, applies random Pauli errors; the standard model for gate calibration errors.
- **Amplitude damping (T1):** Energy relaxation from |1⟩ → |0⟩; asymmetric and accumulates during idle periods.
- **Phase damping (T2):** Dephasing without energy exchange; the primary target of dynamical decoupling.
- **Readout error:** Symmetric bit-flip confusion at measurement, characterised by a calibration matrix **M**.
- **Coherent gate error:** Systematic over/under-rotation from pulse miscalibration; does not average over shots.
- **Combined noise:** Layered depolarizing, T1, T2, and readout errors for worst-case testing.

All benchmark experiments use depolarizing noise applied to H (single-qubit) and CX (two-qubit) gates at rates *p* ∈ {0.01, 0.05, 0.10, 0.15, 0.20}, enabling direct comparison with QEM literature [1], [2].

### B. QEM Problem Formulation

Given a quantum circuit *U* preparing state ρ = *U*|0⟩⟨0|*U*† and an observable *O*, the ideal expectation value is ⟨*O*⟩_ideal = Tr(ρ *O*). Under noise channel ε, the noisy state becomes ρ̃ = ε(ρ) and the measured value ⟨*O*⟩_noisy = Tr(ρ̃ *O*) deviates from the ideal. A QEM technique *T* produces an estimate ⟨*O*⟩_mit = *T*(⟨*O*⟩_noisy, auxiliary data) with reduced error |⟨*O*⟩_mit − ⟨*O*⟩_ideal| < |⟨*O*⟩_noisy − ⟨*O*⟩_ideal|.

We quantify performance using:

- **Fidelity:** *F* = max(0, 1 − |⟨*O*⟩_mit − ⟨*O*⟩_ideal| / range), clipped to [0, 1].
- **Error reduction:** (1 − |error_after| / |error_before|) × 100%.
- **Sampling overhead:** Multiplicative factor of additional circuit executions relative to a single unmitigated run.

## III. Methodology

### A. Framework Architecture

The framework is structured as a Python package with clean module separation: `src/circuits/` (Bell, GHZ, QFT, VQE, QAOA builders), `src/noise_models/` (six noise implementations), `src/mitigation/` (six QEM techniques), `src/backends/` (AerSimulator wrapper), `src/metrics/` (fidelity, error reduction, sampling overhead), and `src/benchmarks/` (automated benchmark and scalability analysis). All techniques accept generic evaluator functions—`evaluator(counts) → float` for counts-based methods and `observable(bitstring) → float` for VD—decoupling mitigation from circuit-specific observable computation.

Tools: Qiskit 2.4.2, Qiskit Aer 0.17.2, Mitiq 1.0.0 (PEC, CDR, DD), NumPy/SciPy (MEM inversion, Richardson extrapolation, VQE COBYLA optimisation).

### B. Mitigation Techniques

**MEM** builds a 2ⁿ calibration matrix by preparing each computational basis state under readout noise and applies matrix inversion: **p**_ideal = **M**⁻¹ · **p**_noisy, with non-negativity clipping [8]. Sampling overhead: 5× (4 calibration circuits + 1 target).

**ZNE** amplifies gate noise via gate folding—replacing each gate *G* with *G*·(*G*†·*G*)^*k* for odd scale factors—and extrapolates to zero noise using Richardson polynomial weights [1]. Scale factors {1, 3, 5}; overhead: 3×.

**PEC** inverts the depolarizing channel via quasi-probability representations and Monte Carlo sampling through Mitiq's `execute_with_pec` [2]. Overhead grows as γⁿ where γ is the one-norm per gate; at *p* = 0.15, γ ≈ 1.95.

**CDR** trains a linear regression model on near-Clifford surrogate circuits to predict zero-noise expectation values [5]. Uses 10–20 training circuits; overhead: 11–21×.

**VD** estimates Tr(ρ²*O*)/Tr(ρ²) from a single noisy measurement distribution, suppressing mixed-state noise without circuit overhead [3], [6]. Requires ≥8192 shots; overhead: 1×.

**DD** inserts XX or XYXY pulse sequences into idle windows via Mitiq's `execute_with_ddd` [7]. Five trials averaged; overhead: 5×. Designed for T2 dephasing, not depolarizing gate noise.

### C. Benchmark Design

**TABLE I: BENCHMARK CIRCUITS AND OBSERVABLES**

| Circuit | Qubits | Depth | Observable | Range |
|---------|--------|-------|------------|-------|
| Bell | 2 | O(1) | ⟨ZZ⟩ = P(00)+P(11)−P(01)−P(10) | [−1, 1] |
| GHZ-3 | 3 | O(N) | P(000) + P(111) | [0, 1] |
| QFT-3 | 3 | O(N²) | P(000) | [0, 1] |
| QAOA-C4 | 4 | O(p·E) | Expected Max-Cut value | [0, 4] |
| VQE (H₂) | 2 | O(1) | Ground state energy (ZNE) / ⟨ZZ⟩ (counts) | Hartree / [−1, 1] |

The automated benchmark (`benchmark.py`) runs all applicable technique–circuit combinations at five noise levels with 1024–8192 shots per execution on Qiskit Aer. VQE uses a dual-path approach: ZNE via Aer Estimator with gate folding on the H₂ Hamiltonian; MEM, CDR, VD, and DD via counts on the bound ansatz circuit from `build_vqe_circuit()`. PEC is excluded from VQE because COBYLA-optimised rotation angles lack closed-form quasi-probability decompositions.

A separate scalability study evaluates ZNE and VD on GHZ and QFT circuits from 2 to 8 qubits at fixed 5% depolarizing noise.

## IV. Experimental Results

### A. Cross-Circuit Average Fidelity

**TABLE II: AVERAGE FIDELITY ACROSS NOISE LEVELS (1%–20%)**

| Technique | Bell | GHZ-3 | QFT-3 | QAOA-C4 | VQE | Overall |
|-----------|------|-------|-------|---------|-----|---------|
| MEM | 0.977 | 0.981 | **0.985** | 0.953 | **0.985** | **0.976** |
| ZNE | **0.988** | 0.977 | 0.941 | 0.742 | 0.808† | 0.891 |
| PEC | 0.659 | 0.704 | 0.600 | 0.001 | N/A | 0.491 |
| CDR | **1.000** | **1.000** | 0.000 | 0.009 | 0.093 | 0.420 |
| VD | 0.991 | 0.986 | 0.963 | 0.712 | 0.779 | 0.886 |
| DD | 0.918 | 0.883 | 0.617 | 0.630 | 0.371 | 0.684 |

†VQE ZNE uses Estimator-based energy evaluation; other VQE techniques use counts-based ⟨ZZ⟩.

MEM achieves the highest overall average fidelity (0.976), driven by strong performance on QFT-3 (0.985) and VQE counts path (0.985). CDR achieves perfect fidelity (1.000) on Bell and GHZ-3 but zero on QFT-3. PEC averages 0.491 due to catastrophic failure on QAOA-C4 (0.001) and high-noise instability.

### B. Bell State: Technique Robustness Across Noise

**TABLE III: BELL STATE ERROR REDUCTION (%) BY NOISE LEVEL**

| Technique | 1% | 5% | 10% | 15% | 20% |
|-----------|-----|-----|------|------|------|
| MEM | −122.2 | +33.9 | +77.6 | +78.9 | +94.6 |
| ZNE | +86.1 | +100.0 | +100.0 | +100.0 | +73.2 |
| PEC | +100.0 | +100.0 | +100.0 | −253.1 | −203.6 |
| CDR | +100.0 | +100.0 | +100.0 | +100.0 | +100.0 |
| VD | +99.6 | +97.7 | +94.2 | +90.6 | +88.8 |
| DD | +4.4 | +2.4 | +4.1 | −1.4 | +6.8 |

At 1% noise, the unmitigated Bell fidelity is 0.9912 (error 0.0088). ZNE recovers 0.9988 (+86.1% reduction); CDR and PEC achieve exact recovery (1.0); VD reaches 1.0 (99.6% reduction). MEM degrades to 0.9805 (−122.2%) because calibration matrix inversion amplifies statistical fluctuations when gate noise is negligible.

At 15% noise, PEC collapses: mitigated expectation 0.4758 versus ideal 1.0 (−253.1% reduction), as quasi-probability variance γ² per gate overwhelms the 100-sample Monte Carlo estimator. ZNE and CDR maintain perfect recovery; VD degrades gracefully to 0.986 (90.6% reduction).

### C. QFT-3: Deep Circuit Performance

QFT-3 is the most noise-sensitive benchmark (depth O(N²), non-Clifford controlled-phase gates). At 20% noise, unmitigated fidelity drops to 0.5393.

**TABLE IV: QFT-3 FIDELITY AND ERROR REDUCTION AT SELECTED NOISE LEVELS**

| Technique | 5% noise (F / Red%) | 10% noise (F / Red%) | 20% noise (F / Red%) |
|-----------|---------------------|----------------------|----------------------|
| MEM | 0.9922 / +94.5 | 1.0000 / +100.0 | 0.9834 / +96.4 |
| ZNE | 0.9675 / +77.2 | 0.9774 / +90.7 | 0.8220 / +61.4 |
| PEC | 1.0000 / +100.0 | 1.0000 / +100.0 | 1.0000 / +100.0 |
| CDR | 0.0000 / −601.4 | 0.0000 / −312.9 | 0.0000 / −117.1 |
| VD | 0.9947 / +96.3 | 0.9775 / +90.7 | 0.8977 / +77.8 |
| DD | 0.7237 / −93.8 | 0.5178 / −99.1 | 0.3064 / −50.5 |

CDR fails completely on QFT at all noise levels—the near-Clifford training circuits cannot approximate non-Clifford controlled-phase gates. MEM and VD are the most reliable performers; ZNE degrades at 20% noise as 5× gate folding triples an already-deep circuit. DD worsens results under depolarizing noise (expected: DD targets T2 dephasing, not gate noise).

### D. Variational Algorithms: QAOA and VQE

QAOA-C4 (4-qubit Max-Cut, ideal cut value 3.01) reveals technique sensitivity to non-Clifford structure. At 10% noise, MEM achieves 93.1% error reduction (fidelity 0.9648); ZNE achieves 40.1% (fidelity 0.6965); VD achieves 79.4% (fidelity 0.8954). PEC and CDR produce fidelity ≈ 0 at all noise levels—the quasi-probability representations and Clifford training data cannot capture QAOA's rotation-angle-dependent cost landscape.

For VQE H₂ ground state (exact energy −1.857 hartree), MEM on the counts path achieves 86.6–99.3% error reduction across all noise levels (fidelity 0.9888–0.9956). ZNE via Estimator underperforms: 2.6% reduction at 1% noise, becoming negative (−10.4%) at 10% noise, as gate folding shifts the variational landscape away from the COBYLA-optimised parameters. VD on VQE counts achieves 33.0–85.9% error reduction (fidelity 0.5253–0.9902).

### E. Sampling Overhead

**TABLE V: SAMPLING OVERHEAD BY TECHNIQUE**

| Technique | Overhead | Range (this study) |
|-----------|----------|---------------------|
| VD | 1× | Fixed |
| PEC | 1.04×–2.54× | Grows with noise level |
| ZNE | 3× | Fixed (3 scale factors) |
| MEM | 5× | Fixed (4 calibration circuits) |
| DD | 5× | Fixed (5 trials) |
| CDR | 11×–21× | 10–20 training circuits |

VD offers the lowest overhead while maintaining competitive fidelity. CDR's 11–21× overhead is only justified on near-Clifford circuits where it achieves perfect correction.

### F. Scalability (2–8 Qubits, 5% Noise)

On GHZ circuits (depth O(N)), both ZNE and VD maintain fidelity ≥ 0.977 across 2–8 qubits. On QFT circuits (depth O(N²)), VD maintains fidelity ≥ 0.990 at all qubit counts, while ZNE degrades from 0.999 (2 qubits) to 0.877 (8 qubits). At 8 qubits, QFT requires ~56 gates; ZNE's 5× folded circuit reaches ~280 gates, exceeding the effective coherence budget and causing Richardson extrapolation to overfit shot noise.

## V. Discussion

### A. Technique Comparison and Trade-offs

Our benchmark reveals three distinct technique classes:

**Near-Clifford specialists (CDR, PEC):** CDR achieves 100% error reduction on Bell and GHZ-3 at all noise levels but fails catastrophically on QFT (−3371% at 1% noise), QAOA, and VQE. PEC achieves perfect correction at ≤10% noise on shallow circuits but variance explodes above 15% (Bell: −253% at 15% noise). Both require circuit structure assumptions—Clifford proximity for CDR, tractable gate noise representations for PEC—that break on variational and deep non-Clifford circuits.

**General-purpose mitigators (ZNE, VD):** ZNE is the most reliable default for shallow circuits (Bell: 86–100% reduction) but degrades on deep circuits (QFT at 20%: 61%) and variational algorithms (VQE ZNE: negative at ≥5% noise). VD provides consistent performance across all circuit types (QFT at 20%: 78% reduction) with only 1× overhead, making it preferred when sampling budget is constrained or circuit depth grows with qubit count.

**Domain-specific correctors (MEM, DD):** MEM excels when readout errors dominate (QFT at 10%: 100% reduction; VQE: 87–99%) but harms results at very low noise (Bell at 1%: −122%). DD provides minimal benefit under depolarizing noise (Bell: 2–7%) but is designed for T2 dephasing suppression and should be evaluated under phase-damping models on real hardware.

### B. Practical Recommendations

Based on our empirical results, we recommend:

1. **Low-depth entanglement (Bell, GHZ) at ≤5% noise:** PEC or CDR for peak accuracy; VD as a low-overhead alternative.

2. **Medium-depth circuits at 5–10% noise:** ZNE or VD; prefer VD for circuits with depth scaling O(N²).

3. **Deep circuits (QFT-type):** MEM + VD combination; MEM for readout, VD for gate errors.

4. **Variational algorithms (VQE, QAOA):** MEM for counts-based observables (83–99% on QAOA); ZNE via Estimator for energy estimation at ≤5% noise only.

5. **Minimal sampling budget:** VD exclusively (1× overhead, 34–99% error reduction across conditions).

6. **Real hardware with T2-dominated noise:** Apply DD as preprocessing before ZNE or MEM.

### C. Limitations

All experiments use depolarizing gate noise on Qiskit Aer; real hardware exhibits T1/T2 decay, crosstalk, and time-correlated errors that may alter relative technique rankings—particularly for DD. PEC used 100 Monte Carlo samples per data point; production deployments typically require thousands. Hyperparameters (ZNE scale factors, CDR training count, DD sequence) were fixed rather than circuit-adaptive. Hardware validation on IBM Quantum processors remains future work.

## VI. Conclusion

We designed, implemented, and systematically evaluated a modular QEM framework covering six noise models and six mitigation techniques. Across 145 benchmark configurations on five representative circuits and five noise levels, we find that no single technique dominates: CDR and PEC offer peak performance within narrow operating regimes (near-Clifford, low noise); MEM is indispensable for readout-dominated error at moderate-to-high noise; VD provides the best balance of accuracy, reliability, and sampling efficiency across diverse circuit types; and ZNE remains a practical default for shallow circuits despite scalability limitations.

For general-purpose NISQ deployment, we recommend a layered strategy: **MEM (readout correction) + VD (gate error suppression)**, with ZNE as backup for shallow circuits where VD's high shot requirement is prohibitive. CDR and PEC should be reserved for circuits matching their structural assumptions. DD should be applied on hardware with genuine T2 dephasing. This framework and its benchmark suite provide a reproducible foundation for extending QEM evaluation to additional noise models, hardware backends, and application-specific circuits.

<div class="references">

## References

[1] K. Temme, S. Bravyi, and J. M. Gambetta, "Error mitigation for short-depth quantum circuits," *Phys. Rev. Lett.*, vol. 119, no. 18, p. 180509, 2017. [Online]. Available: https://doi.org/10.1103/PhysRevLett.119.180509

[2] S. Endo, S. Benjamin, and Y. Li, "Practical quantum error mitigation for near-future applications," *Phys. Rev. X*, vol. 8, no. 3, p. 031027, 2018. [Online]. Available: https://doi.org/10.1103/PhysRevX.8.031027

[3] Z. Cai, "Resource-efficient purification-based quantum error mitigation," arXiv:2107.07279, 2021. [Online]. Available: https://arxiv.org/abs/2107.07279

[4] A. Kandala *et al.*, "Error mitigation extends the computational reach of a noisy quantum processor," *Nature*, vol. 567, pp. 491–495, 2019. [Online]. Available: https://doi.org/10.1038/s41586-019-1040-7

[5] P. Czarnik, A. Arrasmith, P. J. Coles, and L. Cincio, "Error mitigation with Clifford quantum-circuit data," *Quantum*, vol. 5, p. 592, 2021. [Online]. Available: https://doi.org/10.22331/q-2021-11-26-592

[6] W. J. Huggins *et al.*, "Virtual distillation for quantum error mitigation," *Phys. Rev. X*, vol. 11, no. 4, p. 041036, 2021. [Online]. Available: https://doi.org/10.1103/PhysRevX.11.041036

[7] L. Viola, E. Knill, and S. Lloyd, "Dynamical decoupling of open quantum systems," *Phys. Rev. Lett.*, vol. 82, no. 12, p. 2417, 1999. [Online]. Available: https://doi.org/10.1103/PhysRevLett.82.2417

[8] S. Bravyi, S. Sheldon, A. Kandala, D. C. Mckay, and J. M. Gambetta, "Mitigating measurement errors in multiqubit experiments," *Phys. Rev. A*, vol. 103, no. 4, p. 042605, 2021. [Online]. Available: https://doi.org/10.1103/PhysRevA.103.042605

[9] J. Preskill, "Quantum computing in the NISQ era and beyond," *Quantum*, vol. 2, p. 79, 2018. [Online]. Available: https://doi.org/10.22331/q-2018-08-06-79

[10] A. Peruzzo *et al.*, "A variational eigenvalue solver on a photonic quantum processor," *Nature Commun.*, vol. 5, p. 4213, 2014. [Online]. Available: https://doi.org/10.1038/ncomms5213

[11] E. Farhi, J. Goldstone, and S. Gutmann, "A quantum approximate optimization algorithm," arXiv:1411.4028, 2014. [Online]. Available: https://arxiv.org/abs/1411.4028

[12] A. W. Cross, L. S. Bishop, S. Sheldon, P. D. Nation, and J. M. Gambetta, "Validating quantum computers using randomized model circuits," *Phys. Rev. A*, vol. 100, no. 3, p. 032328, 2019. [Online]. Available: https://doi.org/10.1103/PhysRevA.100.032328

[13] IBM Quantum Documentation, "Error mitigation and suppression techniques." [Online]. Available: https://quantum.cloud.ibm.com/docs/en/guides/error-mitigation-and-suppression-techniques

[14] Mitiq Documentation, "Core concepts — Mitiq 1.0.0." [Online]. Available: https://mitiq.readthedocs.io/en/stable/

[15] IBM Quantum Blog, "M3: Matrix-free measurement mitigation." [Online]. Available: https://www.ibm.com/quantum/blog/mthree-qiskit-extension

</div>

</div>
