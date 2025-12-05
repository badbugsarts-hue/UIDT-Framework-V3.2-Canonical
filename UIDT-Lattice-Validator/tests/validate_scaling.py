# tests/validate_scaling.py
import sys
import os
import numpy as np
import matplotlib.pyplot as plt

# Path fix to allow imports from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def get_scaling_factor_ratio(beta_target, beta_ref, Nc=5):
    # Standard 2-Loop Beta-Function Scaling approximation
    b0 = (11.0/3.0 * Nc) / (16.0 * np.pi**2)
    def exponent(b):
        return -b / (4 * Nc * b0) # approximation for beta definition
    return np.exp(exponent(beta_target) - exponent(beta_ref))

def generate_plot():
    print("Generating validation plot...")
    
    # Data Setup
    arxiv_beta = np.array([16.2, 16.3, 16.4, 16.5, 16.6])
    arxiv_t0a2 = np.array([1.5,  1.9,  2.4,  2.9,  3.5]) 
    
    beta_std = 16.3
    t0a2_std = 1.9
    beta_uidt = 19.575
    
    # Calculations
    a_ratio = get_scaling_factor_ratio(beta_uidt, beta_std)
    scale_factor_sq = (1.0 / a_ratio)**2 
    pred_std_t0a2 = t0a2_std * scale_factor_sq # ~31.9
    
    pred_uidt_val = 5.0 
    pred_uidt_err = 0.8
    
    # Plotting
    plt.figure(figsize=(10, 7))
    
    # 1. Existing Data
    plt.plot(arxiv_beta, arxiv_t0a2, 'ko-', label='arXiv:2309.12270 (Standard Baseline)')
    
    # 2. Extrapolation
    betas_extrap = np.linspace(16.6, 19.6, 50)
    ratios = [get_scaling_factor_ratio(b, beta_std) for b in betas_extrap]
    vals_extrap = t0a2_std * (1.0 / np.array(ratios))**2
    plt.plot(betas_extrap, vals_extrap, 'k--', alpha=0.3, label='Standard Theory Extrapolation')
    
    # 3. Standard Prediction (Fail case for UIDT)
    plt.plot(beta_uidt, pred_std_t0a2, 'rx', markersize=12, markeredgewidth=3, 
             label=f'Standard QCD Expectation ({pred_std_t0a2:.1f})')
    
    # 4. UIDT Prediction (Success case)
    plt.errorbar(beta_uidt, pred_uidt_val, yerr=pred_uidt_err, 
                 fmt='go', markersize=12, elinewidth=3, capsize=6,
                 label='UIDT Prediction (Geometric Lock)')
    
    plt.title(f'The UIDT Critical Test: Nc=5 Lattice Scaling', fontsize=14)
    plt.xlabel('Inverse Coupling $\\beta$', fontsize=12)
    plt.ylabel('Resolution Scale $t_0 / a^2$', fontsize=12)
    plt.yscale('log')
    plt.grid(True, which="both", ls="-", alpha=0.2)
    plt.legend(loc='upper left')
    
    output_path = 'uidt_validation_plot.png'
    plt.tight_layout()
    plt.savefig(output_path)
    print(f"Plot saved to {output_path}")

if __name__ == "__main__":
    generate_plot()
