"""
UIDT v3.2 Error Propagation Analysis
=====================================
Systematic uncertainty quantification for canonical parameters.

Author: Philipp Rietz
License: CC BY 4.0
"""

import numpy as np
from scipy.optimize import fsolve

def uidt_system(params, C=0.277):
    """Coupled UIDT equations (same as verification_code.py)"""
    m_S, kappa, lambda_S = params
    Lambda = 1.0
    Delta_target = 1.71
    
    v = kappa * C / (Lambda * m_S**2)
    eq1 = m_S**2 * v + (lambda_S * v**3) / 6 - kappa * C / Lambda
    
    log_term = np.log(Lambda**2 / m_S**2) if m_S > 0 else 0
    Pi_S = (kappa**2 * C) / (4 * Lambda**2) * \
           (1 + log_term / (16 * np.pi**2))
    Delta_calc = np.sqrt(m_S**2 + Pi_S)
    eq2 = Delta_calc - Delta_target
    
    eq3 = 5 * kappa**2 - 3 * lambda_S
    
    return [eq1, eq2, eq3]


def propagate_errors():
    """
    Propagate uncertainties from input parameters.
    """
    print("="*70)
    print("ERROR PROPAGATION ANALYSIS")
    print("="*70)
    
    # Central values
    m_S_central = 1.705
    kappa_central = 0.500
    lambda_S_central = 0.417
    C_central = 0.277
    Delta_central = 1.71
    
    # Uncertainties
    delta_C = 0.014  # GeV^4
    delta_Delta = 0.08  # GeV
    eps_num = 0.001  # Numerical convergence
    
    # Error from gluon condensate
    print("\n1. Gluon Condensate Uncertainty:")
    params_plus_C = fsolve(uidt_system, [m_S_central, kappa_central, lambda_S_central], 
                            args=(C_central + delta_C,))
    params_minus_C = fsolve(uidt_system, [m_S_central, kappa_central, lambda_S_central], 
                             args=(C_central - delta_C,))
    
    dm_S_C = abs(params_plus_C[0] - params_minus_C[0]) / 2
    dkappa_C = abs(params_plus_C[1] - params_minus_C[1]) / 2
    dlambda_C = abs(params_plus_C[2] - params_minus_C[2]) / 2
    
    print(f"   δm_S(C) = ±{dm_S_C:.3f} GeV")
    print(f"   δκ(C) = ±{dkappa_C:.3f}")
    print(f"   δλ_S(C) = ±{dlambda_C:.3f}")
    
    # Error from lattice Delta (scaling estimate)
    print("\n2. Lattice Mass Gap Uncertainty:")
    dm_S_Delta = delta_Delta * m_S_central / Delta_central
    dkappa_Delta = delta_Delta * kappa_central / Delta_central * 0.6
    dlambda_Delta = delta_Delta * lambda_S_central / Delta_central * 0.5
    
    print(f"   δm_S(Δ) = ±{dm_S_Delta:.3f} GeV")
    print(f"   δκ(Δ) = ±{dkappa_Delta:.3f}")
    print(f"   δλ_S(Δ) = ±{dlambda_Delta:.3f}")
    
    # Total errors (quadrature sum)
    print("\n3. Total Systematic Uncertainties:")
    dm_S_tot = np.sqrt(eps_num**2 + dm_S_C**2 + dm_S_Delta**2)
    dkappa_tot = np.sqrt(eps_num**2 + dkappa_C**2 + dkappa_Delta**2)
    dlambda_tot = np.sqrt(eps_num**2 + dlambda_C**2 + dlambda_Delta**2)
    
    print(f"   δm_S(total) = ±{dm_S_tot:.3f} GeV")
    print(f"   δκ(total) = ±{dkappa_tot:.3f}")
    print(f"   δλ_S(total) = ±{dlambda_tot:.3f}")
    
    print(f"\n{'='*70}")
    print("FINAL PARAMETERS WITH ERRORS:")
    print(f"{'='*70}")
    print(f"m_S = {m_S_central:.3f} ± {dm_S_tot:.3f} GeV")
    print(f"κ = {kappa_central:.3f} ± {dkappa_tot:.3f}")
    print(f"λ_S = {lambda_S_central:.3f} ± {dlambda_tot:.3f}")
    print(f"{'='*70}")


if __name__ == "__main__":
    propagate_errors()