# UIDT Lattice-QCD Validator: Geometric Vacuum Scaling

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Science: High Energy Physics](https://img.shields.io/badge/Science-Lattice%20QCD-blue.svg)](https://arxiv.org/abs/2309.12270)
[![UIDT: v3.3](https://img.shields.io/badge/UIDT-Geometry%20Verified-green.svg)]()

## Abstract
This repository contains the validation framework for the **Unified Interactive Dynamic Theory (UIDT)** applied to Lattice QCD. It tests the hypothesis that the fundamental coupling parameter $\beta$ for $N_c=5$ is geometrically determined by the Torus-invariant constant $\gamma \approx 16.339$.

**Hypothesis:** Standard Lattice QCD simulations at $\beta \approx 16.3$ are approximations of a geometric ideal located at:
$$\beta_{UIDT} = 19.575$$
derived from the scaling factor $\pi / \phi^2$ and Tesla-Torus geometry.

## The Critical Test (Visualized)
The core prediction of UIDT is a **Geometric Lock** at $\beta=19.575$, preventing the "Perturbative Explosion" predicted by standard 2-loop scaling.

![UIDT Critical Test](uidt_validation_plot.png)

* **Red Cross (Standard Model):** Predicts $t_0/a^2 \approx 32$. The lattice becomes extremely fine, leading to topological freezing and massive computational costs.
* **Green Dot (UIDT):** Predicts $t_0/a^2 \approx 5$. The geometry stabilizes via the Torus invariant $\gamma$, suggesting a new continuum limit regime without freezing.

## Key Parameters
| Constant | Value | Origin | Physical Implication |
| :--- | :--- | :--- | :--- |
| **$\gamma$ (Gamma)** | `16.339` | Torus (9/6) × Tesla ($3^2$) × $\pi/\phi^2$ | Vacuum Geometry / Mass Gap |
| **$\beta_{std}$** | `16.3` | Standard Lattice QCD ($N_c=5$) | Reference Baseline (arXiv:2309.12270) |
| **$\beta_{UIDT}$** | `19.575` | $\beta_{std} \times (\pi/\phi^2)$ | Predicted Continuum Limit (No Freezing) |
| **$\xi_{UIDT}$** | `0.00045` | Chiral Limit Scaling | Massless Pions restored |

## Repository Structure
* `src/torus_geometry.py`: Derivation of the fundamental constant $\gamma$.
* `src/nc5_simulator.py`: Prediction engine for observables ($t_0$, $F_{PS}$) at $\beta_{UIDT}$.
* `tests/validate_arxiv2309.py`: Generates the validation plot against literature data.

## Usage (Docker)
Ensure Docker is installed to run the validation environment.

```bash
docker build -t uidt-validator .
docker run uidt-validator
