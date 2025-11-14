import numpy as np

def rigorous_uidt_test():
    """Testable predictions without circular reasoning"""
    
    # Lattice QCD established values
    Lambda_QCD = 0.340  # GeV
    mass_gap_experimental = 1.710  # GeV
    mass_gap_lattice_error = 0.085  # ~5% uncertainty
    
    # UIDT correction (must be dimensionally consistent)
    def uidt_mass_gap(kappa, v, Lambda_scale):
        """
        Dimensionally consistent correction:
        [κ] = GeV⁻¹, [v] = GeV, [Λ] = GeV
        Δ² = Λ²_QCD + α_s κ² v² Λ²_QCD / Λ²
        """
        alpha_s = 0.5  # at 1 GeV
        base_term = Lambda_QCD**2
        correction = alpha_s * kappa**2 * v**2 * Lambda_QCD**2 / Lambda_scale**2
        return np.sqrt(base_term + correction)
    
    # Test parameter space
    kappa_range = np.linspace(0.1, 2.0, 50)  # GeV⁻¹
    v_range = np.linspace(0.01, 0.1, 50)     # GeV
    Lambda_scale = 1.0                       # GeV
    
    best_fit = None
    min_error = float('inf')
    
    for kappa in kappa_range:
        for v in v_range:
            prediction = uidt_mass_gap(kappa, v, Lambda_scale)
            error = abs(prediction - mass_gap_experimental)
            
            if error < min_error and error <= mass_gap_lattice_error:
                min_error = error
                best_fit = (kappa, v, prediction, error)
    
    return best_fit

# Run the test
result = rigorous_uidt_test()
if result:
    kappa, v, prediction, error = result
    print(f"Best UIDT fit: κ = {kappa:.3f} GeV⁻¹, v = {v:.3f} GeV")
    print(f"Predicted Δ = {prediction:.3f} GeV, Error = {error:.3f} GeV")
    print(f"Within lattice uncertainties: {error <= 0.085}")
else:
    print("No UIDT parameters reproduce lattice mass gap within uncertainties")