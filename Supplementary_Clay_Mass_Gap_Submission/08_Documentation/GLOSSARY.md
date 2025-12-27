# UIDT v3.6.1 — Glossary of Terms

## Technical Terminology for Clay Mathematics Institute Reviewers

---

## A

### Asymptotic Freedom
The property of non-abelian gauge theories (like QCD) whereby the coupling constant decreases at high energies. Discovered by Gross, Wilczek, and Politzer (Nobel Prize 2004).

### Auxiliary Field
A field introduced to simplify the Lagrangian structure (e.g., the Nakanishi-Lautrup field B in gauge fixing). Does not propagate physical degrees of freedom.

---

## B

### Banach Fixed-Point Theorem
**Central to this proof.** States that a contraction mapping on a complete metric space has exactly one fixed point. If T: X → X with |T(x) - T(y)| ≤ L|x - y| and L < 1, then ∃! x* such that T(x*) = x*.

### Beta Function
The function β(g) = dg/d(ln μ) describing how coupling constants run with energy scale μ. For Yang-Mills: β(g) = -b₀g³/(16π²) with b₀ = 11N_c/3 for SU(N_c).

### BRST Symmetry
Becchi-Rouet-Stora-Tyutin symmetry. A global fermionic symmetry that encodes gauge invariance after gauge fixing. The BRST charge Q satisfies Q² = 0 (nilpotency).

---

## C

### Cluster Decomposition
The property that correlation functions factorize for widely separated field insertions, ensuring locality of the theory.

### Confinement
The phenomenon whereby color-charged particles (quarks, gluons) cannot exist as free particles; they are always bound in color-neutral hadrons.

### Contraction Mapping
A function T: X → X satisfying |T(x) - T(y)| ≤ L|x - y| for some L < 1. Guarantees unique fixed point by Banach theorem.

---

## D

### Dyson-Schwinger Equations
The quantum equations of motion relating n-point correlation functions to (n+1)-point functions. Non-perturbative analog of classical Euler-Lagrange equations.

---

## E

### Euclidean QFT
Quantum field theory formulated in Euclidean signature (++++) rather than Minkowski (-+++). Connected to Minkowski theory via Osterwalder-Schrader reconstruction.

---

## F

### Faddeev-Popov Ghosts
Anticommuting scalar fields (c, c̄) introduced to properly quantize non-abelian gauge theories. Cancel unphysical polarization contributions.

### Fixed Point (RG)
A point in coupling space where all beta functions vanish: β(g*) = 0. Can be UV (asymptotic safety) or IR.

### Functional Renormalization Group (FRG)
Exact RG formulation using the Wetterich equation for the flowing effective action Γ_k.

---

## G

### Gap Equation
Self-consistent equation for the mass gap. In UIDT: Δ² = m_S² + radiative corrections.

### Ghost Number
A conserved quantum number: gh(c) = +1, gh(c̄) = -1, gh(other) = 0. Physical states have ghost number zero.

### Glueball
A bound state consisting purely of gluons. The lightest (0⁺⁺) has mass ~1.7 GeV according to lattice QCD.

### Gluon Condensate
The vacuum expectation value ⟨(α_s/π)G²⟩ ≈ 0.277 GeV⁴. A measure of non-perturbative QCD dynamics.

---

## H

### Hilbert Space (Physical)
The space of physical states H_phys = ker(Q)/im(Q), where Q is the BRST charge. States in im(Q) are null.

---

## K

### Kugo-Ojima Criterion
A condition ensuring color confinement: the ghost propagator must be more singular than 1/k² in the infrared.

---

## L

### Lattice QCD
Non-perturbative regularization of QCD on a discrete spacetime lattice. Provides numerical validation of analytical results.

### Lipschitz Constant
The constant L in |T(x) - T(y)| ≤ L|x - y|. For contraction, L < 1 is required. In this proof: L = 4.35 × 10⁻⁵.

---

## M

### Mass Gap
**The central object of this proof.** Defined as Δ = inf(Spec(H) \ {0}), the smallest non-zero eigenvalue of the Hamiltonian. Proven value: Δ* = 1.710 GeV.

### Millennium Prize Problem
One of seven problems designated by the Clay Mathematics Institute in 2000, each carrying a $1 million prize. Yang-Mills existence and mass gap is Problem 4.

---

## N

### Nakanishi-Lautrup Field
The auxiliary field B in the BRST formulation satisfying sB = 0, s(c̄) = B.

### Nilpotency
The property Q² = 0 of the BRST charge. Essential for defining physical state space.

### Non-minimal Coupling
The interaction term (κ/Λ)S·Tr(F²) coupling the scalar field to the Yang-Mills field strength.

---

## O

### Osterwalder-Schrader Axioms
Axioms for Euclidean QFT that guarantee reconstruction of a Wightman theory in Minkowski space. Key axiom: reflection positivity.

---

## P

### Physical State
A state |ψ⟩ satisfying Q|ψ⟩ = 0 (BRST-closed) that is not of the form Q|χ⟩ (BRST-exact). Elements of H_phys.

---

## R

### Reflection Positivity
The Euclidean axiom Σᵢⱼ c̄ᵢcⱼ S(θxᵢ, xⱼ) ≥ 0, where θ is time reflection. Ensures positivity of the Hilbert space norm.

### Renormalization Group (RG)
The mathematical framework describing how physics changes with energy scale. Flow is governed by beta functions.

---

## S

### Scalar Field
A Lorentz-invariant field transforming as S → S under Lorentz transformations. The UIDT scalar S(x) has dimension 1.

### Slavnov-Taylor Identities
Ward identities for non-abelian gauge theories. Encode BRST symmetry at the level of the effective action.

### Spectral Gap
Synonym for mass gap: the gap between the vacuum and the first excited state in the energy spectrum.

---

## T

### Taylor's Theorem
The non-renormalization theorem for the ghost-gluon vertex: Z_g · Z_c^(1/2) · Z_A^(1/2) = 1.

### Transversality
The property k_μ D^μν(k) = 0 of the gluon propagator, ensuring only physical polarizations propagate.

---

## U

### UIDT (Unified Information-Density Theory)
The theoretical framework developed in this work. Version 3.6.1 is the canonical release.

### Unitarity
Conservation of probability: S†S = 1 for the S-matrix. Verified via the optical theorem.

### UV Fixed Point
A fixed point approached as μ → ∞. In UIDT: (κ*, λ_S*) = (0.500, 0.417) satisfying 5κ² = 3λ_S.

---

## V

### VEV (Vacuum Expectation Value)
The expectation value ⟨S⟩ = v ≠ 0 of the scalar field in the vacuum. Canonical value: v = 47.7 MeV.

---

## W

### Wetterich Equation
The exact flow equation for the effective average action: ∂_t Γ_k = (1/2) Tr[(Γ_k^(2) + R_k)^(-1) ∂_t R_k].

### Wightman Axioms
Axioms for relativistic QFT in Minkowski space: Lorentz covariance, spectral condition, locality, positivity.

---

## Y

### Yang-Mills Theory
Non-abelian gauge theory based on compact Lie groups. The action is S = -(1/4)∫d⁴x Tr(F_μν F^μν).

---

## Z

### z-score
Statistical measure of deviation: z = |x - μ|/σ. For lattice comparison, z = 0.00σ (Chen 2006) indicates perfect agreement.

### Zinn-Justin Master Equation
The condition (Γ, Γ) = 0 encoding BRST invariance of the effective action, where (·,·) is the antibracket.

---

## Canonical Constants Summary

| Symbol | Name | Value | Unit |
|--------|------|-------|------|
| Δ* | Mass Gap | 1.710 ± 0.015 | GeV |
| v | VEV | 47.7 ± 5.3 | MeV |
| γ | Universal Invariant | 16.339 ± 0.002 | — |
| κ | Non-minimal Coupling | 0.500 ± 0.017 | — |
| λ_S | Scalar Self-Coupling | 0.417 ± 0.013 | — |
| L | Lipschitz Constant | 4.35 × 10⁻⁵ | — |
| 𝒞 | Gluon Condensate | 0.277 | GeV⁴ |

---

**END OF GLOSSARY**
