# Changelog & Version History

All notable changes to the **Unified Information-Density Theory (UIDT)** framework will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [v3.5.6] - Canonical Release - 2025-12-09
### 🚀 Major Features (Three-Pillar Architecture)
* **Pillar I (QFT):** Established analytical derivation of Mass Gap $\Delta = 1.710$ GeV with residuals $< 10^{-14}$.
* **Pillar II (Cosmology):** Recalibrated to **2025 DESI DR2** & **JWST CCHP** data.
    * Updated Hubble Constant to **$H_0 = 70.4$ km/s/Mpc** (previously 70.92).
    * Updated Holographic Scale to **$\lambda = 0.66$ nm** (previously 0.854 nm).
* **Pillar III (Lab):** Added specific predictions for Casimir anomalies (+0.59%).

### ✨ New Mechanisms
* **99-Step RG Cascade:** Formalized the mechanism suppressing Vacuum Energy by 120 orders of magnitude ($\gamma^{-12}$ scaling).
* **SMDS Hypothesis:** Added "Supermassive Dark Seeds" model for JWST early galaxy formation ($z > 10$) with He II $\lambda 1640$ signatures.
* **Unification Map:** Added `UIDT-3.5-Verification-visual.py` to plot the universal scaling law across 120 orders of magnitude.

### 🛠 Technical Improvements
* **Metadata Overhaul:** Updated `metadata.xml`, `CITATION.cff`, and `.zenodo.json` to reflect the new DOI `10.5281/zenodo.17835201`.
* **Web Dashboard:** Redesigned `metadata.html` into a responsive "Science Dashboard" with evidence classification.
* **Docker:** Optimized `Dockerfile` for Python 3.10-slim and reproducibility.

---

## [v3.5.5] - 2025-12-08
### 🧪 Experimental Predictions
* Introduced the "Temple Visualization" (precursor to Three-Pillar Architecture).
* Refined Gamma-Evolution $\gamma(z)$ with a quadratic fit for dynamical Dark Energy ($w(z) > -1$).

---

## [v3.5] - 2025-12-07
### 📦 Evidence Classification
* **Added:** Explicit classification system (Category A-D) to distinguish between mathematical proofs and cosmological models.
* **Changed:** Complete rewrite of the codebase for Python 3.10+ compatibility.
* **Added:** CI/CD Pipelines (`.github/workflows`) for automated integrity checks.

---

## [v3.4] - 2025-12-06
### 🛡️ Conservative Revision
* **Added:** `biblatex.cfg` with "Evidence-Based Citation Style".
* **Changed:** Shifted language from "Final Truth" to "Proposed Framework" to meet peer-review standards.

---

## [v3.3] - ⚠️ REVOKED - 2025-11-01
### ❌ Status: Withdrawn
* **Reason:** Data corruption in the externally formatted PDF artifacts.
* **Issues:** Inconsistent parameter rounding led to a false divergence in the cosmology sector.
* **Action:** All DOI references to v3.3 (`...17596783`) are formally superseded by v3.5.6. Users are advised to **discard** v3.3 datasets.

---

## [v3.2] - Technical Note - 2025-11-09
### 🔄 Recalculation
* **Fixed:** Corrected the Gamma Invariant from preliminary estimates ($\sim 12.5$) to the derived value **$\gamma \approx 16.3$**.
* **Added:** Independent `fsolve` verification script to prove solution uniqueness.
* **Removed:** Dependence on legacy "Ultra Report" parameters.

---

## [v3.0 - v3.1] - Initial Drafts - Oct 2025
### 🚧 Beta Phase
* Initial Python implementation of the 3-Equation System.
* Identified the "Branch 2" (non-perturbative) false solution.

---

## [v16.x] - "Ultra Report" Legacy - Early 2025
### 🦕 Superseded
* Monolithic PDF reports lacking code reproducibility.
* **Status:** Replaced by the modular UIDT Framework repository.

---
*License: CC BY 4.0 | Maintained by: Philipp Rietz*