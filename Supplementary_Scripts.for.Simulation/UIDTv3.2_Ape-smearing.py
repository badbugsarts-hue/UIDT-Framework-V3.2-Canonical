import numpy as np
from scipy.optimize import curve_fit
from tqdm import trange

def project_to_SU3(Q, xp_local=xp):
    """
    Robustes SU(3)-Projektion via Polarzerlegung für 3x3 Matrizen.
    Verwendet die analytische Methode für maximale GPU-Performance.
    """
    if len(Q.shape) == 6:  # Batch-Projektion (Nx, Ny, Nz, Nt, 4, 3, 3)
        original_shape = Q.shape
        Q_flat = Q.reshape(-1, 3, 3)
        result = xp_local.zeros_like(Q_flat)
        
        for i in range(Q_flat.shape[0]):
            result[i] = _single_su3_projection(Q_flat[i], xp_local)
        
        return result.reshape(original_shape)
    else:
        return _single_su3_projection(Q, xp_local)

def _single_su3_projection(Q, xp_local):
    """SU(3) Projektion für einzelne 3x3 Matrix"""
    # 1. Polarzerlegung: Q = U * H mit U unitär, H hermitesch
    # Für kleine Matrizen: U = Q * (Q^† Q)^{-1/2}
    
    Q_dag = Q.conj().T
    Q_dag_Q = Q_dag @ Q
    
    # (Q^† Q)^{-1/2} via Eigenwertzerlegung
    if xp_local is cp:
        # CuPy Eigenwertzerlegung
        eigvals, eigvecs = xp_local.linalg.eigh(Q_dag_Q)
        inv_sqrt = eigvecs @ xp_local.diag(1.0 / xp_local.sqrt(eigvals)) @ eigvecs.conj().T
    else:
        # NumPy Eigenwertzerlegung  
        eigvals, eigvecs = np.linalg.eigh(Q_dag_Q)
        inv_sqrt = eigvecs @ np.diag(1.0 / np.sqrt(eigvals)) @ eigvecs.conj().T
    
    U = Q @ inv_sqrt
    
    # 2. Projektion auf det(U) = 1
    det_U = xp_local.linalg.det(U)
    phase = det_U / xp_local.abs(det_U)
    U = U / phase**(1/3)
    
    return U

class UIDTLatticeWithSmearing(UIDTLatticeOptimized):
    def __init__(self, cfg: LatticeConfig, kappa=0.5, Lambda=1.0,
                 m_S=1.705, lambda_S=0.417, v_vev=0.0477):
        super().__init__(cfg, kappa, Lambda, m_S, lambda_S, v_vev)
        
    def ape_smear(self, U_in, alpha=0.5, N_iter=10):
        """
        Vollständig vektorisierte APE-Smearing Implementierung.
        """
        xp_local = xp
        U = U_in.copy()
        
        for iteration in range(N_iter):
            U_new = xp_local.zeros_like(U)
            
            for mu in range(4):
                staple_sum = xp_local.zeros((self.Nx, self.Ny, self.Nz, self.Nt, 3, 3), dtype=complex)
                
                for nu in range(4):
                    if nu == mu:
                        continue
                    
                    # Positive Stapler: U_ν(x) U_μ(x+ν) U_ν†(x+μ)
                    U_nu = U[..., nu, :, :]
                    U_mu_plus_nu = self._shift_matrix(U[..., mu, :, :], nu, +1)
                    U_nu_plus_mu_dag = self._shift_matrix(U[..., nu, :, :], mu, +1).conj().transpose(0,1,2,3,5,4)
                    
                    staple_pos = U_nu @ U_mu_plus_nu @ U_nu_plus_mu_dag
                    
                    # Negative Stapler: U_ν†(x-ν) U_μ(x-ν) U_ν(x-ν+μ)  
                    U_nu_minus_nu_dag = self._shift_matrix(U[..., nu, :, :], nu, -1).conj().transpose(0,1,2,3,5,4)
                    U_mu_minus_nu = self._shift_matrix(U[..., mu, :, :], nu, -1)
                    U_nu_minus_nu_plus_mu = self._shift_matrix(
                        self._shift_matrix(U[..., nu, :, :], nu, -1), mu, +1
                    )
                    
                    staple_neg = U_nu_minus_nu_dag @ U_mu_minus_nu @ U_nu_minus_nu_plus_mu
                    
                    staple_sum += staple_pos + staple_neg
                
                # Kombiniere originalen Link mit Staplern
                Q = (1.0 - alpha) * U[..., mu, :, :] + (alpha / 6.0) * staple_sum
                
                # Projektion auf SU(3)
                U_new[..., mu, :, :] = project_to_SU3(Q, xp_local)
            
            U = U_new
        
        return U
    
    def _shift_matrix(self, matrices, direction, shift):
        """Verschiebt Matrizen entlang einer Gitterrichtung"""
        if direction == 0:  # x-Richtung
            return xp.roll(matrices, shift, axis=0)
        elif direction == 1:  # y-Richtung
            return xp.roll(matrices, shift, axis=1)
        elif direction == 2:  # z-Richtung
            return xp.roll(matrices, shift, axis=2)
        elif direction == 3:  # t-Richtung
            return xp.roll(matrices, shift, axis=3)
    
    def smeared_wilson_loop(self, R, T, N_APE=10, alpha_APE=0.5):
        """
        Misst Wilson-Loop W(R,T) mit APE-gesmearten Links.
        """
        # Smearing nur für die Messung
        U_smeared = self.ape_smear(self.U, alpha=alpha_APE, N_iter=N_APE)
        
        # Wilson-Loop Berechnung
        W_total = xp.zeros((), dtype=complex)
        count = 0
        
        for x in range(self.Nx):
            for y in range(self.Ny): 
                for z in range(self.Nz):
                    for t in range(self.Nt):
                        # Rechteckige Schleife R×T in x-t Ebene
                        loop_product = xp.eye(3, dtype=complex)
                        
                        # Pfad 1: R Schritte in x-Richtung
                        for r in range(R):
                            x_pos = (x + r) % self.Nx
                            loop_product = loop_product @ U_smeared[x_pos, y, z, t, 0]
                        
                        # Pfad 2: T Schritte in t-Richtung  
                        for tau in range(T):
                            t_pos = (t + tau) % self.Nt
                            x_pos = (x + R) % self.Nx
                            loop_product = loop_product @ U_smeared[x_pos, y, z, t_pos, 3]
                        
                        # Pfad 3: R Schritte zurück in -x-Richtung
                        for r in range(R):
                            x_pos = (x + R - r - 1) % self.Nx
                            t_pos = (t + T) % self.Nt
                            # Verwendet dagger von U in -x Richtung
                            U_dag = U_smeared[x_pos, y, z, t_pos, 0].conj().T
                            loop_product = loop_product @ U_dag
                        
                        # Pfad 4: T Schritte zurück in -t-Richtung
                        for tau in range(T):
                            t_pos = (t + T - tau - 1) % self.Nt
                            U_dag = U_smeared[x, y, z, t_pos, 3].conj().T
                            loop_product = loop_product @ U_dag
                        
                        W_total += xp.trace(loop_product)
                        count += 1
        
        return xp.real(W_total) / (3.0 * count)  # Normalisiert

def cornel_potential(R, V0, alpha, sigma):
    """Cornel-Potential V(R) = V0 + α/R + σR"""
    R_safe = np.maximum(R, 0.1)  # Vermeidet Division durch Null
    return V0 + alpha / R_safe + sigma * R_safe

def extract_potential_from_wilson_loops(W_means, W_errors, T_ratio=1):
    """
    Extrahiert Potential V(R) aus Wilson-Loops mittels Ratio-Methode.
    V(R) = -log[ W(R, T+1) / W(R, T) ]
    """
    R_max, T_max = W_means.shape
    
    V_R = np.zeros(R_max)
    V_R_err = np.zeros(R_max)
    
    for R in range(1, R_max + 1):
        if T_ratio < T_max:
            # Ratio berechnen
            ratio = W_means[R-1, T_ratio] / W_means[R-1, T_ratio-1]
            
            # Vermeide numerische Probleme
            if ratio > 0:
                V_R[R-1] = -np.log(ratio)
                
                # Fehlerfortpflanzung
                rel_err1 = W_errors[R-1, T_ratio] / W_means[R-1, T_ratio]
                rel_err2 = W_errors[R-1, T_ratio-1] / W_means[R-1, T_ratio-1]
                V_R_err[R-1] = np.sqrt(rel_err1**2 + rel_err2**2) * abs(V_R[R-1])
            else:
                V_R[R-1] = np.nan
                V_R_err[R-1] = np.nan
    
    return V_R, V_R_err

def run_string_tension_complete(cfg: LatticeConfig, kappa=0.5, Lambda=1.0,
                               R_max=6, T_max=8, hmc_steps=10, step_size=0.02,
                               N_APE_smear=10, alpha_APE=0.5):
    """
    Vollständige Stringspannungs-Messung mit APE-Smearing und statistischer Analyse.
    """
    print("🏹 Starte Stringspannungs-Messung mit APE-Smearing")
    
    lat = UIDTLatticeWithSmearing(cfg, kappa=kappa, Lambda=Lambda)
    
    # Datenspeicher für Wilson-Loops
    W_loops = np.zeros((R_max, T_max, cfg.N_meas), dtype=float)
    
    # Thermalisierung
    print("🔥 Thermalisierung...")
    for i in trange(cfg.N_therm):
        lat.hmc_trajectory_omelyan(n_steps=hmc_steps, step_size=step_size)
    
    # Messphase
    print("📊 Messphase - Wilson-Loops sammeln...")
    acceptance_count = 0
    total_trajectories = 0
    
    for i in trange(cfg.N_meas):
        # HMC Updates
        for _ in range(cfg.N_skip):
            accepted, _ = lat.hmc_trajectory_omelyan(n_steps=hmc_steps, step_size=step_size)
            if accepted:
                acceptance_count += 1
            total_trajectories += 1
        
        # Wilson-Loop Messungen für alle R, T
        for R in range(1, R_max + 1):
            for T in range(1, T_max + 1):
                W_val = lat.smeared_wilson_loop(R, T, N_APE=N_APE_smear, alpha_APE=alpha_APE)
                W_loops[R-1, T-1, i] = to_cpu(W_val) if USE_CUPY else float(W_val)
    
    acceptance_rate = acceptance_count / total_trajectories
    
    # Statistische Analyse
    print("📈 Statistische Analyse...")
    
    # Mittelwerte und einfache Fehler
    W_means = np.mean(W_loops, axis=2)
    W_stds = np.std(W_loops, axis=2)
    
    # Autokorrelationszeit für jede Wilson-Loop Größe
    tau_ints = np.zeros((R_max, T_max))
    for R in range(R_max):
        for T in range(T_max):
            tau_ints[R, T] = integrated_autocorrelation_time(W_loops[R, T, :])
    
    # Effektive Fehler mit tau_int Korrektur
    W_errors = W_stds / np.sqrt(cfg.N_meas / (2 * tau_ints))
    
    # Potential Extraktion
    print("🔍 Extrahiere Quark-Potential...")
    V_R, V_R_err = extract_potential_from_wilson_loops(W_means, W_errors, T_ratio=2)
    
    # Fit des Cornel-Potentials
    print("📐 Fitte Cornel-Potential...")
    R_values = np.arange(1, R_max + 1)
    
    # Entferne NaN Werte für Fit
    valid_mask = ~np.isnan(V_R) & ~np.isnan(V_R_err) & (V_R_err > 0)
    R_fit = R_values[valid_mask]
    V_fit = V_R[valid_mask]
    V_err_fit = V_R_err[valid_mask]
    
    if len(R_fit) >= 3:  # Mindestens 3 Punkte für Fit
        try:
            # Startparameter: [V0, alpha, sigma]
            p0 = [0.1, -0.3, 0.05]
            bounds = ([-np.inf, -1.0, 0.0], [np.inf, 0.0, 1.0])
            
            popt, pcov = curve_fit(cornel_potential, R_fit, V_fit, 
                                  p0=p0, sigma=V_err_fit, 
                                  bounds=bounds, absolute_sigma=True)
            
            perr = np.sqrt(np.diag(pcov))
            
            sigma_result = popt[2]
            sigma_error = perr[2]
            fit_quality = np.sqrt(np.mean(((V_fit - cornel_potential(R_fit, *popt)) / V_err_fit)**2))
            
        except Exception as e:
            print(f"⚠️ Fit fehlgeschlagen: {e}")
            sigma_result, sigma_error, fit_quality = np.nan, np.nan, np.nan
            popt = None
    else:
        print("⚠️ Nicht genug gültige Datenpunkte für Fit")
        sigma_result, sigma_error, fit_quality = np.nan, np.nan, np.nan
        popt = None
    
    # Ergebnisse zusammenfassen
    results = {
        'sigma': sigma_result,
        'sigma_err': sigma_error,
        'fit_quality': fit_quality,
        'fit_params': popt,
        'V_R': V_R,
        'V_R_err': V_R_err,
        'W_means': W_means,
        'W_errors': W_errors,
        'tau_ints': tau_ints,
        'acceptance_rate': acceptance_rate,
        'R_values': R_values
    }
    
    # Plot-Ergebnisse
    if popt is not None:
        _plot_string_tension_results(results, cfg, kappa)
    
    return results

def _plot_string_tension_results(results, cfg, kappa):
    """Plottet die Stringspannungs-Ergebnisse"""
    import matplotlib.pyplot as plt
    
    R = results['R_values']
    V_R = results['V_R']
    V_err = results['V_R_err']
    
    plt.figure(figsize=(10, 6))
    
    # Datenpunkte
    plt.errorbar(R, V_R, yerr=V_err, fmt='o', label='Daten', capsize=5)
    
    # Fit-Kurve
    if results['fit_params'] is not None:
        R_fine = np.linspace(0.5, R.max() + 0.5, 100)
        V_fit = cornel_potential(R_fine, *results['fit_params'])
        plt.plot(R_fine, V_fit, 'r-', label='Cornel-Potential Fit')
        
        sigma_text = f'$\sigma = {results["sigma"]:.4f} \pm {results["sigma_err"]:.4f}$'
        plt.text(0.05, 0.95, sigma_text, transform=plt.gca().transAxes,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
    
    plt.xlabel('Abstand R')
    plt.ylabel('Potential V(R)')
    plt.title(f'Stringspannung - κ={kappa}, β={cfg.beta}')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.savefig(f'string_tension_kappa_{kappa}.png', dpi=300, bbox_inches='tight')
    plt.close()

# Test-Funktion für schnelle Validierung
def test_string_tension_small():
    """Schneller Test mit kleinem Gitter"""
    cfg = LatticeConfig(N_spatial=8, N_temporal=8, beta=5.7, a=0.1,
                       N_therm=20, N_meas=50, N_skip=2, seed=12345)
    
    results = run_string_tension_complete(cfg, kappa=0.5, R_max=4, T_max=4,
                                        hmc_steps=5, step_size=0.05,
                                        N_APE_smear=5)
    
    print(f"\n🎯 Stringspannung Ergebnis:")
    print(f"   σ = {results['sigma']:.4f} ± {results['sigma_err']:.4f}")
    print(f"   Fit-Qualität (χ²/dof): {results['fit_quality']:.2f}")
    print(f"   Akzeptanzrate: {results['acceptance_rate']:.3f}")
    
    return results

if __name__ == "__main__":
    # Test ausführen
    test_results = test_string_tension_small()