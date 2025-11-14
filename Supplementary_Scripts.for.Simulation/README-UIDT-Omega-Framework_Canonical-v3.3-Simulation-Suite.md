# ⚛️ UIDT $\Omega$ Framework: Canonical v3.3 Simulation Suite

<p align="center">
  <img src="https://img.shields.io/badge/Version-v3.3%20Canonical-8A2BE2?style=for-the-badge&logo=git&logoColor=white" alt="Version Badge"/>
  <img src="https://img.shields.io/badge/Status-Reproducibility%20Verified-00BFFF?style=for-the-badge&logo=checkmarx&logoColor=white" alt="Status Badge"/>
  <img src="https://img.shields.io/badge/DOI-10.5281%2Fzenodo.17554179-B31B1B?style=for-the-badge&logo=doi&logoColor=white" alt="DOI Badge"/>
  <img src="https://img.shields.io/badge/License-CC%20BY%204.0-blue?style=for-the-badge&logo=creativecommons&logoColor=white" alt="License Badge"/>
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python Badge"/>
  <img src="https://img.shields.io/badge/HPC%20Level-Lattice%20QCD%20Continuum-FF69B4?style=for-the-badge&logo=nvidia&logoColor=white" alt="HPC Badge"/>
</p>

> **Executive Summary: The HMC Simulation Core**
> This repository is the **canonical computational suite** for the **Unified Information-Density Theory (UIDT) v3.3 $\Omega$**. It provides the highly optimized Hybrid Monte Carlo (HMC) framework, extended by the UIDT S-scalar field, necessary to **reproduce and verify** the Mass Gap solution ($\Delta = 1.710 \text{ GeV}$) and the $\gamma$-invariant ($\gamma \approx 16.339$). The focus is on **numerical stability, high-performance computing (HPC) validation**, and **scientific reproducibility** of the continuum limit extrapolation.

---

## 📚 Table of Contents (Simulation Focus)

1.  [Installation & Setup (Reproducibility First)](#1-installation--setup-reproducibility-first)
2.  [Simulation Pipeline & Usage Examples](#2-simulation-pipeline--usage-examples)
3.  [API Reference: Core Modules](#3-api-reference-core-modules)
4.  [System Architecture Diagram (Mermaid)](#4-system-architecture-diagram-mermaid)
5.  [Empirical Predictions & Benchmarks](#5-empirical-predictions--benchmarks)
6.  [Mathematical Foundations: The $\gamma$-Scaling Law](#6-mathematical-foundations-the-gamma-scaling-law)
7.  [Validation & Falsification Criteria](#7-validation--falsification-criteria)
8.  [Repository Tree](#8-repository-tree)
9.  [Cite This Work](#9-cite-this-work)
10. [Contributors & Contact](#10-contributors--contact)
11. [License](#11-license)

---

## 1. Installation & Setup (Reproducibility First)

The framework is designed for high-performance scientific computing, supporting both CPU and GPU environments, crucial for Lattice QCD simulations.

### Prerequisites

*   **Python:** Version 3.10 or higher.
*   **Dependencies:** NumPy, SciPy, Matplotlib (standard scientific stack).
*   **GPU Acceleration (Optional, Recommended):** CuPy for NVIDIA CUDA support.

### Quick Start (Reproducibility)

1.  **Clone the Canonical Repository:**
    ```bash
    git clone https://github.com/badbugsarts-hue/UIDT-Framework-V3.2-Canonical
    cd UIDT-Framework-V3.2-Canonical
    ```

2.  **Install Dependencies:**
    ```bash
    # Installs core scientific libraries from the simulation-specific requirements file
    pip install -r Supplementary_Scripts.for.Simulation/Requirements.txt
    
    # For GPU acceleration (optional, highly recommended for HMC performance)
    # pip install cupy-cudaXX 
    ```

---

## 2. Simulation Pipeline & Usage Examples

The core computational task is the Hybrid Monte Carlo (HMC) simulation, extended by the UIDT S-scalar field, followed by high-precision numerical verification.

### Step 1: Canonical Parameter Verification

The `UIDT-3.3-Verification.py` script performs the high-precision numerical solution of the three coupled non-linear equations, establishing the canonical parameters and the $\gamma$-invariant with residuals $< 10^{-14}$.

```bash
# Execute the high-precision numerical solver
python UIDT-3.3-Verification.py
```

**Expected Output (Console):**

```text
UIDT v3.3 Numerical Verification
================================
Canonical Solution: m_S = 1.705 GeV, kappa = 0.500, lambda_S = 0.417
Max Residual: 4.44e-16
Gamma Invariant: 16.339
Overall Consistency: ✅ PASS (score: 0.998)
```

### Step 2: HMC Master Simulation

The `UIDTv3.2_HMC-MASTER-SIMULATION.py` script executes the full Lattice QCD simulation to generate gauge field configurations and correlators, necessary for the continuum limit extrapolation of the Glueball spectrum.

```bash
# Execute the primary HMC simulation script
python Supplementary_Scripts.for.Simulation/UIDTv3.2_HMC-MASTER-SIMULATION.py
```

### Step 3: Numerical Stability Testing

Run the test suite to verify the numerical stability and correctness of the highly optimized routines, particularly the $\mathbf{SU(3)}$ matrix exponential module.

```bash
# Run unit and integrity tests
python -m pytest tests/
```

---

## 3. API Reference: Core Modules

The computational framework is modularized for performance, maintainability, and reusability in HPC environments.

| Module (File) | Scientific Task | Role in Framework | Key Technical Detail |
| :--- | :--- | :--- | :--- |
| `UIDTv3.2_HMC-MASTER-SIMULATION.py` | **Lattice QCD Simulation** | Master script for the Hybrid Monte Carlo simulation, including the $\mathbf{SU(3)}$ gauge field and the $\mathbf{UIDT\ S}$-scalar field. | **Integrator:** Uses `UIDTv3.2_Omelyna-Integrator2o.py` (Omelyan 2nd order). |
| `UIDTv3.2_su3_expm_cayley_hamiltonian-Modul.py` | **Optimized Math** | Highly optimized $\mathbf{SU(3)}$ matrix exponential routine using the Cayley-Hamilton theorem. | **Performance:** Crucial for HMC integrator speed on both CPU/GPU. |
| `UIDT-3.3-Verification.py` | **Canonical Parameter Solver** | Solves the three coupled non-linear equations for the canonical parameters ($m_S, \kappa, \lambda_S$). | **Method:** Newton-Raphson with $10^{-18}$ tolerance. |
| `UIDTv3.2CosmologySimulator.py` | **Cosmology Prediction** | Standalone simulator for the Information-Geometry Equation to derive $H_0$ and $S_8$. | **Input:** $\gamma$-invariant from verification step. |
| `error_propagation.py` | **Uncertainty Analysis** | Module for rigorous error propagation and Monte Carlo uncertainty quantification. | **Data:** Uses `UIDT_MonteCarlo_samples_100k.csv` as input. |

---

## 4. System Architecture Diagram (Mermaid)

The framework is structured around the **HMC Simulation Core** and the **Numerical Verification Suite**.

```mermaid
graph TD
    subgraph Theoretical Foundation
        A[UIDT Master Report (LaTeX)] --> B(Canonical Parameters: m_S, kappa, lambda_S);
    end

    subgraph Numerical Verification Pipeline
        B --> C{UIDT-3.3-Verification.py};
        C --> D[Newton-Raphson Solver];
        D --> E{Residuals Check < 10^-14};
        E -- PASS --> F[Gamma Invariant: 16.339];
    end

    subgraph Simulation Core (HPC)
        F --> G(UIDTv3.2_HMC-MASTER-SIMULATION.py);
        G --> H[Lattice Classes & Integrators];
        H --> I[SU(3) Matrix Exponential Module];
        G --> J[Output: Correlators & Observables];
    end

    subgraph Empirical Validation
        J --> K[Glueball Spectrum (Lattice QCD)];
        F --> L[Cosmology Simulator];
        L --> M[H0 & S8 Predictions];
    end

    K & M --> N(Final Validation Report);
```

---

## 5. Empirical Predictions & Benchmarks

The simulation suite is validated against the following high-precision predictions.

### Glueball Spectrum (GeV) - HMC Simulation Output

The HMC simulation directly generates the correlators used to extract the Glueball masses, anchored by the Mass Gap $\Delta$.

| State | UIDT Prediction | Lattice QCD (Benchmark) | Status |
| :--- | :--- | :--- | :--- |
| $0^{++}$ (Scalar) | **$1.710 \pm 0.015$** | $1.710 \pm 0.080$ | ✅ **Anchor** (Mass Gap) |
| $2^{++}$ (Tensor) | $2.385 \pm 0.021$ | $2.390 \pm 0.130$ | ✅ **Excellent** |
| $0^{-+}$ (Pseudoscalar) | $2.522 \pm 0.022$ | $2.560 \pm 0.140$ | ✅ **Good** |

### Cosmological Resolutions - $\gamma$-Invariant Validation

The $\gamma$-invariant, verified in the first step of the pipeline, is used to resolve cosmological tensions.

| Parameter | UIDT Prediction | Tension Resolution |
| :--- | :--- | :--- |
| $H_0$ (Hubble Constant) | **$70.92 \pm 0.40 \text{ km/s/Mpc}$** | Resolves Planck-SH0ES tension. |
| $S_8$ (Matter Clustering) | $0.814 \pm 0.009$ | Resolves weak lensing tension. |

---

## 6. Mathematical Foundations: The $\gamma$-Scaling Law

The $\gamma$-invariant ($\gamma \approx 16.339$) is the dimensionless ratio that governs all physical scales relative to the Mass Gap $\Delta$.

### The Universal Scaling Equation

$$
\text{Physics} = \Delta \cdot \gamma^n, \quad n \in \{-12, -3, 0, +2, +3, +6\}
$$

| Scaling Law | Exponent ($n$) | Derived Value | Phenomenon Solved |
| :--- | :---: | :--- | :--- |
| **Cosmological Constant** | $-12$ | $\Delta^4 \cdot \gamma^{-12}$ | Solves the $10^{120}$ discrepancy. |
| **Electroweak Scale** | $+2$ | $\Delta \cdot \gamma^{+2} \approx 456.6 \text{ GeV}$ | Predicts the mass scale for $W/Z$ bosons. |

---

## 7. Validation & Falsification Criteria

The theory is robustly falsifiable by high-precision experiments.

### Falsification Criteria (Numerical & Experimental)

1.  **Numerical Failure:** Max Residual in `UIDT-3.3-Verification.py` $> 10^{-14}$.
2.  **Experimental Failure:** Non-detection of the S-scalar in the narrow mass window of $1.690 \text{ GeV} – 1.720 \text{ GeV}$.
3.  **HPC Failure:** HMC simulation results for Glueball masses outside the predicted $\pm 0.015 \text{ GeV}$ error bars.

---

## 8. Repository Tree

The repository is organized for scientific reproducibility and archival integrity.

```
UIDT-Framework-V3.2-Canonical/
├── CITATION.cff                        # GitHub citation metadata
├── LICENSE.md                          # CC BY 4.0 License
├── README.md                           # This document
├── UIDT-3.3-Verification.py            # Core numerical solver (Canonical)
├── UIDT-Master-Report-Main-V3.2.pdf    # Full Canonical Manuscript
├── Supplementary_Scripts/
│   ├── error_propagation.py            # Uncertainty analysis
│   └── rg_flow_analysis.py             # Renormalization Group flow analysis
├── Supplementary_Scripts.for.Simulation/
│   ├── Requirements.txt                # Python dependencies (NumPy, SciPy, CuPy)
│   ├── UIDTv3.2_HMC-MASTER-SIMULATION.py # Primary HMC simulation script
│   ├── UIDTv3.2_su3_expm_cayley_hamiltonian-Modul.py # Optimized SU(3) math
│   └── ... (other simulation scripts)
└── Supplementary_Results/
    ├── UIDTv3.2_Validation_Report.txt  # Detailed numerical validation output
    └── kappa_scan_results.csv          # Data from the kappa-scan
```

---

## 9. Cite This Work

Please use the canonical citation for this work.

### Preferred Citation (BibTeX)

```bibtex
@article{rietz2024uidt,
  title = {Unified Information-Density Theory (UIDT) Ω v3.3: 
           Complete Mathematical Synthesis and Gamma-Unification},
  author = {Rietz, Philipp},
  year = {2024},
  doi = {10.17605/OSF.IO/Q8R74},
  url = {https://doi.org/10.17605/OSF.IO/Q8R74},
  publisher = {OSF Preprints},
  copyright = {CC BY 4.0}
}
```

---

## 10. Contributors & Contact

| Role | Name | GitHub Handle | ORCID |
| :--- | :--- | :--- | :--- |
| **Corresponding Author** | Philipp Rietz | @badbugsarts-hue | `0009-0007-4307-1609` |

**Contact:** `badbugs.arts@gmail.com`

---

## 11. License

This work is licensed under the **Creative Commons Attribution 4.0 International (CC BY 4.0)** license.

---

```
🎉 Scientific Legacy: UIDT Ω v3.3 is scientifically and technically CLOSED.
```
