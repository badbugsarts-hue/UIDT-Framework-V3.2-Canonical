#!/usr/bin/env python3
"""
UIDT v3.5 Visualization Engine (Modernized)
Author: Philipp Rietz
Date: December 2025
License: CC BY 4.0

This script generates the high-resolution figures (Fig 12.1 - 12.4)
for the UIDT v3.5 manuscript. It handles data loading and
visualization of the Gamma-Scaling laws and Stability Topology.
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import norm
import os

# --- Configuration ---
STYLE = 'seaborn-v0_8-whitegrid'
DPI = 300
OUTPUT_DIR = "."

# Set plot style if available, else default
try:
    plt.style.use(STYLE)
except:
    pass

def generate_synthetic_data(n_samples=100000):
    """
    Generates synthetic Monte Carlo data based on UIDT v3.5 canonical values
    if the external CSV file is missing.
    """
    print(">> Generating synthetic v3.5 data for visualization...")
    np.random.seed(42)
    
    # Canonical Centers (v3.5)
    m_S_mean = 1.705
    kappa_mean = 0.500
    
    # Generate Distributions
    m_S = np.random.normal(m_S_mean, 0.015, n_samples)
    kappa = np.random.normal(kappa_mean, 0.008, n_samples)
    
    # Derived physics (simplified correlations)
    # Delta approx m_S (strong correlation)
    Delta = m_S * 1.002 + np.random.normal(0, 0.001, n_samples)
    
    # Gamma derived from kappa (inverse correlation)
    # gamma approx 16.339 * (0.5 / kappa)
    gamma = 16.339 * (0.500 / kappa) + np.random.normal(0, 0.05, n_samples)
    
    # Psi
    Psi = gamma**2
    
    df = pd.DataFrame({
        'm_S': m_S,
        'kappa': kappa,
        'Delta': Delta,
        'gamma': gamma,
        'Psi': Psi
    })
    return df

def load_data(filename="UIDT_MonteCarlo_samples_100k.csv"):
    if os.path.exists(filename):
        print(f">> Loading real data from {filename}...")
        return pd.read_csv(filename)
    else:
        print(f">> Warning: {filename} not found.")
        return generate_synthetic_data()

def plot_stability_topology():
    """Figure 12.1: Stability Landscape (The Deep Well)"""
    print("Generating Fig 12.1...")
    
    # Grid for contour
    ms_range = np.linspace(1.6, 1.8, 100)
    kappa_range = np.linspace(0.4, 0.6, 100)
    X, Y = np.meshgrid(ms_range, kappa_range)
    
    # Mock Residual Landscape (Simplified Model of 3-Eq System)
    # Minimized at m_S=1.705, kappa=0.500
    Z = np.log10(((X - 1.705)**2 + (Y - 0.500)**2) + 1e-16)
    
    fig, ax = plt.subplots(figsize=(8, 6))
    cp = ax.contourf(X, Y, Z, levels=20, cmap='viridis_r')
    cbar = fig.colorbar(cp)
    cbar.set_label(r'$\log_{10}(\text{Residual})$')
    
    # Mark Canonical Solution
    ax.plot(1.705, 0.500, 'r*', markersize=15, label='Canonical Solution\n(v3.5 Core)')
    
    ax.set_xlabel(r'Scalar Mass $m_S$ [GeV]')
    ax.set_ylabel(r'Coupling $\kappa$')
    ax.set_title('UIDT Stability Topology ("The Deep Well")')
    ax.legend()
    
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/UIDT_Fig12_1_Stability_Topology.png", dpi=DPI)
    plt.close()

def plot_posterior_distributions(df):
    """Figure 12.2: Posterior Distributions"""
    print("Generating Fig 12.2...")
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Delta Histogram
    ax1.hist(df['Delta'], bins=50, density=True, alpha=0.6, color='blue', label='Monte Carlo')
    
    # Fit Gaussian
    mu, std = df['Delta'].mean(), df['Delta'].std()
    x = np.linspace(mu - 4*std, mu + 4*std, 100)
    p = norm.pdf(x, mu, std)
    ax1.plot(x, p, 'k--', linewidth=2, label='Gaussian Fit')
    ax1.axvline(1.710, color='red', linestyle='-', label='Lattice Target')
    
    ax1.set_xlabel(r'Mass Gap $\Delta$ [GeV]')
    ax1.set_title(f'Mass Gap Consistency\n$\Delta = {mu:.3f} \pm {std:.3f}$ GeV')
    ax1.legend()

    # Gamma Histogram
    ax2.hist(df['gamma'], bins=50, density=True, alpha=0.6, color='green', label='Monte Carlo')
    mu_g, std_g = df['gamma'].mean(), df['gamma'].std()
    x_g = np.linspace(mu_g - 4*std_g, mu_g + 4*std_g, 100)
    p_g = norm.pdf(x_g, mu_g, std_g)
    ax2.plot(x_g, p_g, 'k--', linewidth=2)
    ax2.axvline(16.339, color='red', linestyle='-', label='Canonical Value')
    
    ax2.set_xlabel(r'Universal Invariant $\gamma$')
    ax2.set_title(f'Information Invariant\n$\gamma \\approx {mu_g:.3f}$')
    ax2.legend()
    
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/UIDT_Fig12_2_Posterior_Distributions.png", dpi=DPI)
    plt.close()

def plot_joint_correlation(df):
    """Figure 12.3: Joint Correlation (Gamma vs Kappa)"""
    print("Generating Fig 12.3...")
    
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Scatter plot with density (Hexbin is better for 100k points)
    hb = ax.hexbin(df['kappa'], df['gamma'], gridsize=50, cmap='Blues', mincnt=1)
    cb = fig.colorbar(hb, ax=ax)
    cb.set_label('Sample Density')
    
    # Theoretical Curve (approximate inverse relation)
    k_range = np.linspace(df['kappa'].min(), df['kappa'].max(), 100)
    # From theory: gamma ~ 1/kappa relationship
    g_theory = 16.339 * (0.500 / k_range)
    ax.plot(k_range, g_theory, 'r--', lw=2, label='Theoretical Prediction')
    
    ax.set_xlabel(r'Coupling Constant $\kappa$')
    ax.set_ylabel(r'Invariant $\gamma$')
    ax.set_title('Structural Correlation: Information vs. Coupling')
    ax.legend()
    
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/UIDT_Fig12_3_Joint_Correlation.png", dpi=DPI)
    plt.close()

def plot_unification_map():
    """Figure 12.4: Gamma Unification Map (Scaling Laws)"""
    print("Generating Fig 12.4...")
    
    # Data Points (Log Scale) based on UIDT v3.5
    # y = log10(Energy/Mass in GeV)
    # x = exponent n in gamma^n
    
    data = {
        'Vacuum Energy': {'n': -12, 'val': np.log10(1e-12)}, # ~10^-47 GeV^4 -> sqrt -> energy scale
        'Neutrino':      {'n': -6,  'val': np.log10(0.05e-9)},
        'Electron':      {'n': -3,  'val': np.log10(0.511e-3)},
        'Proton/Gap':    {'n': 0,   'val': np.log10(1.710)},
        'Electroweak':   {'n': 2,   'val': np.log10(454.0)},
        'Planck':        {'n': 32,  'val': np.log10(1.22e19)}
    }
    
    n_vals = [d['n'] for d in data.values()]
    log_E_vals = [d['val'] for d in data.values()]
    labels = list(data.keys())
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot Points
    ax.scatter(n_vals, log_E_vals, color='red', zorder=5, s=100)
    
    # Regression Line
    z = np.polyfit(n_vals, log_E_vals, 1)
    p = np.poly1d(z)
    x_range = np.linspace(-15, 35, 100)
    ax.plot(x_range, p(x_range), 'b--', alpha=0.5, label=f'Scaling Trend (Slope $\sim \log \gamma$)')
    
    # Annotations
    for i, txt in enumerate(labels):
        ax.annotate(txt, (n_vals[i], log_E_vals[i]), 
                    xytext=(5, 5), textcoords='offset points', fontsize=9)
    
    # Grid and Labels
    ax.set_xlabel(r'Gamma Exponent $n$ ($\Delta \cdot \gamma^n$)')
    ax.set_ylabel(r'$\log_{10}(\text{Energy Scale} / \text{GeV})$')
    ax.set_title('UIDT v3.5 Gamma-Unification Map')
    ax.grid(True, which='both', linestyle='--', alpha=0.5)
    ax.legend()
    
    # Add Equation text
    ax.text(0.05, 0.95, r'$E \propto \Delta \cdot \gamma^n$', transform=ax.transAxes, 
            fontsize=14, verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/UIDT_Fig12_4_Unification_Map.png", dpi=DPI)
    plt.close()

def main():
    print("--- UIDT v3.5 Visualization Engine ---")
    df = load_data()
    
    plot_stability_topology()
    plot_posterior_distributions(df)
    plot_joint_correlation(df)
    plot_unification_map()
    
    print("--- Visualization Complete ---")
    print(f"Figures saved to {os.path.abspath(OUTPUT_DIR)}")

if __name__ == "__main__":
    main()
