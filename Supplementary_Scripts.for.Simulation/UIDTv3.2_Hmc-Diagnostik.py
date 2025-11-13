import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from tqdm import trange
import warnings
warnings.filterwarnings('ignore')

# ============ ERWEITERTE DIAGNOSTIK ============

def run_full_hmc_simulation(config=None):
    """
    Vollständige HMC-Simulation mit erweiterter Diagnostik
    """
    if config is None:
        config = LatticeConfig(
            N_spatial=12, N_temporal=24, beta=5.7, a=0.12,
            N_therm=1000, N_meas=3000, N_skip=10,
            kappa=0.5, Lambda=1.0, m_S=1.705, lambda_S=0.417, v_vev=0.0477
        )
    
    print("🚀 Starte vollständige UIDT HMC-Simulation")
    print(f"   Gitter: {config.N_spatial}³×{config.N_temporal}")
    print(f"   Parameter: β={config.beta}, κ={config.kappa}, a={config.a} fm")
    
    # Initialisiere Lattice
    lattice = UIDTLatticeHMC(config)
    
    # Tracking-Variablen
    lattice.action_history = []
    lattice.plaquette_history = []
    lattice.acceptance_rate = []
    acceptance_count = 0
    total_trajectories = 0
    
    # Thermalisierung
    print("🔥 Thermalisierung...")
    for i in trange(config.N_therm):
        accepted, delta_H = lattice.hmc_trajectory_omelyan()
        if accepted:
            acceptance_count += 1
        total_trajectories += 1
        
        lattice.action_history.append(lattice.uidt_action())
        lattice.plaquette_history.append(- (3.0 / config.beta) * lattice.wilson_action() / 
                                       (config.N_spatial**3 * config.N_temporal * 6.0))
        lattice.acceptance_rate.append(acceptance_count / total_trajectories)
    
    # Messphase
    print("📊 Messphase...")
    S_vev_measurements = []
    correlators = []
    
    for i in trange(config.N_meas):
        # HMC Updates
        for _ in range(config.N_skip):
            accepted, delta_H = lattice.hmc_trajectory_omelyan()
            if accepted:
                acceptance_count += 1
            total_trajectories += 1
            
            # Tracking
            lattice.action_history.append(lattice.uidt_action())
            plaq = - (3.0 / config.beta) * lattice.wilson_action() / (config.N_spatial**3 * config.N_temporal * 6.0)
            lattice.plaquette_history.append(plaq)
            lattice.acceptance_rate.append(acceptance_count / total_trajectories)
        
        # Messungen
        S_vev = float(np.mean(lattice.S))
        S_vev_measurements.append(S_vev)
        
        C = simple_correlator(lattice, t_max=min(12, config.N_temporal))
        correlators.append(C)
    
    # Statistische Analyse
    C_array = np.array(correlators)
    C_avg = np.mean(C_array, axis=0)
    C_err = np.std(C_array, axis=0) / np.sqrt(len(correlators))
    
    # Massenextraktion
    m_glueball, m_err = extract_mass_exponential(C_avg, config.a)
    
    # Vergleich mit Lattice QCD
    lattice_qcd_mass = 1.710  # GeV
    lattice_qcd_err = 0.080   # GeV
    
    z_score = abs(m_glueball - lattice_qcd_mass) / np.sqrt(m_err**2 + lattice_qcd_err**2)
    
    print(f"\n📊 ERGEBNISSE:")
    print(f"   Glueball-Masse: {m_glueball:.3f} ± {m_err:.3f} GeV")
    print(f"   Lattice QCD:    {lattice_qcd_mass:.3f} ± {lattice_qcd_err:.3f} GeV")
    print(f"   Z-Score:        {z_score:.2f}σ")
    
    if z_score < 2:
        print("  → Kompatibel mit Standard Lattice QCD")
    elif z_score < 3:
        print("  → Moderate Abweichung (weitere Tests nötig)")
    else:
        print("  → SIGNIFIKANTE ABWEICHUNG! Potentieller UIDT-Effekt")
    
    # Visualisierung
    plot_hmc_diagnostics(lattice, correlators, C_avg, C_err, config)
    
    return lattice, S_vev_measurements, correlators

def simple_correlator(lattice, t_max=10):
    """
    Vereinfachter Glueball-Korrelator
    C(t) = ⟨O(t) O†(0)⟩, O = Σ_x Tr[P_xy(x,t)]
    """
    Nx, Ny, Nz = lattice.cfg.N_spatial, lattice.cfg.N_spatial, lattice.cfg.N_spatial
    C = np.zeros(t_max)
    
    for t_sep in range(t_max):
        O_source = 0.0
        O_sink = 0.0
        
        # Summiere über Raumpunkte
        for x in range(Nx):
            for y in range(Ny):
                for z in range(Nz):
                    # Source bei t=0
                    P_source = lattice.plaquette(x, y, z, 0, 0, 1)  # x-y Ebene
                    O_source += np.real(np.trace(P_source))
                    
                    # Sink bei t=t_sep
                    if t_sep < lattice.cfg.N_temporal:
                        P_sink = lattice.plaquette(x, y, z, t_sep, 0, 1)
                        O_sink += np.real(np.trace(P_sink))
        
        C[t_sep] = O_source * O_sink / (Nx * Ny * Nz)**2
    
    return C

def extract_mass_exponential(C, a, t_min=2, t_max=6):
    """
    Extrahiere Masse aus C(t) ~ A exp(-m t)
    Via effektiver Masse: m_eff(t) = ln[C(t)/C(t+1)]
    """
    # Effektive Masse (numerisch stabiler)
    m_eff = []
    for t in range(t_min, min(t_max, len(C)-1)):
        if C[t] > 0 and C[t+1] > 0:
            m_eff.append(np.log(C[t] / C[t+1]))
    
    if len(m_eff) < 2:
        return np.nan, np.nan
    
    # Plateau-Mittelwert
    m_lattice = np.mean(m_eff)
    m_lattice_err = np.std(m_eff) / np.sqrt(len(m_eff))
    
    # Konvertiere zu physikalischen Einheiten
    hbar_c = 0.1973  # GeV·fm
    m_phys_gev = (m_lattice / a) * hbar_c
    m_err_gev = (m_lattice_err / a) * hbar_c
    
    return m_phys_gev, m_err_gev

def integrated_autocorr_time(data, max_lag=100):
    """
    Integrierte Autokorrelationszeit
    τ_int = 1/2 + Σ_{t=1}^∞ ρ(t)
    """
    data = np.array(data) - np.mean(data)
    n = len(data)
    
    autocorr = np.correlate(data, data, mode='full')[n-1:] / (n * np.var(data))
    
    tau_int = 0.5
    for t in range(1, min(max_lag, len(autocorr))):
        if autocorr[t] < 0.01:  # Cutoff für kleine Korrelationen
            break
        tau_int += autocorr[t]
    
    return max(0.5, tau_int)

def plot_hmc_diagnostics(lattice, correlators, C_avg, C_err, config):
    """Umfassende Visualisierung"""
    
    fig = plt.figure(figsize=(16, 12))
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
    
    # 1. Akzeptanzrate Historie
    ax1 = fig.add_subplot(gs[0, 0])
    if len(lattice.acceptance_rate) > 50:
        accept_smooth = np.convolve(lattice.acceptance_rate, 
                                     np.ones(50)/50, mode='valid')
        ax1.plot(accept_smooth, color='blue', alpha=0.7)
    ax1.axhline(0.7, color='red', linestyle='--', 
                label='Optimal (70%)')
    ax1.set_xlabel('HMC Trajektorie')
    ax1.set_ylabel('Akzeptanzrate')
    ax1.set_title('HMC Akzeptanz')
    ax1.legend()
    ax1.grid(alpha=0.3)
    
    # 2. Action-Zeitreihe
    ax2 = fig.add_subplot(gs[0, 1])
    if hasattr(lattice, 'action_history'):
        ax2.plot(lattice.action_history, color='green', alpha=0.6, linewidth=0.5)
    ax2.set_xlabel('Konfiguration')
    ax2.set_ylabel('S_total')
    ax2.set_title('Action-Verlauf')
    ax2.grid(alpha=0.3)
    
    # 3. Plaquette-Verteilung
    ax3 = fig.add_subplot(gs[0, 2])
    if hasattr(lattice, 'plaquette_history'):
        ax3.hist(lattice.plaquette_history, bins=50, density=True, 
                 alpha=0.7, color='purple', edgecolor='black')
        plaq_mean = np.mean(lattice.plaquette_history)
        plaq_std = np.std(lattice.plaquette_history)
        ax3.axvline(plaq_mean, color='red', linestyle='--', 
                    label=f'⟨P⟩ = {plaq_mean:.5f}')
    ax3.set_xlabel('⟨Plaquette⟩')
    ax3.set_ylabel('Häufigkeit')
    ax3.set_title('Plaquette-Verteilung')
    ax3.legend()
    ax3.grid(alpha=0.3)
    
    # 4. Korrelator mit Fehlerbalken
    ax4 = fig.add_subplot(gs[1, 0])
    t_data = np.arange(len(C_avg))
    ax4.errorbar(t_data, C_avg, yerr=C_err, fmt='o-', 
                 capsize=4, label='UIDT', color='blue')
    ax4.set_yscale('log')
    ax4.set_xlabel('t [Gittereinheiten]')
    ax4.set_ylabel('C(t)')
    ax4.set_title('Glueball-Korrelator')
    ax4.legend()
    ax4.grid(alpha=0.3, which='both')
    
    # 5. Effektive Masse
    ax5 = fig.add_subplot(gs[1, 1])
    m_eff = []
    m_eff_err = []
    t_eff = []
    
    for t in range(1, len(C_avg)-1):
        if C_avg[t] > 0 and C_avg[t+1] > 0:
            m = np.log(C_avg[t] / C_avg[t+1])
            # Fehler via Gauß-Propagation
            m_err = np.sqrt((C_err[t]/C_avg[t])**2 + (C_err[t+1]/C_avg[t+1])**2)
            
            m_eff.append(m)
            m_eff_err.append(m_err)
            t_eff.append(t)
    
    if len(m_eff) > 0:
        ax5.errorbar(t_eff, m_eff, yerr=m_eff_err, fmt='s-', 
                     capsize=3, color='red', label='m_eff(t)')
        
        # Plateau-Region markieren
        if len(m_eff) >= 6:
            plateau_val = np.mean(m_eff[2:6])
            ax5.axhline(plateau_val, color='green', linestyle='--', 
                        label=f'Plateau: {plateau_val:.3f}')
            ax5.fill_between([2, 6], plateau_val-0.05, plateau_val+0.05, 
                             alpha=0.2, color='green')
    
    ax5.set_xlabel('t [Gittereinheiten]')
    ax5.set_ylabel('m_eff(t) [Gittereinheiten]')
    ax5.set_title('Effektive Masse')
    ax5.legend()
    ax5.grid(alpha=0.3)
    
    # 6. S-Feld VEV Historie
    ax6 = fig.add_subplot(gs[1, 2])
    # Hier müssten S_vev_measurements übergeben werden
    ax6.set_xlabel('Konfiguration')
    ax6.set_ylabel('⟨S⟩ [GeV]')
    ax6.set_title('Skalarfeld VEV')
    ax6.grid(alpha=0.3)
    
    # 7. Autokorrelation (Action)
    ax7 = fig.add_subplot(gs[2, 0])
    if hasattr(lattice, 'action_history'):
        action_data = np.array(lattice.action_history) - np.mean(lattice.action_history)
        autocorr = np.correlate(action_data, action_data, mode='full')
        autocorr = autocorr[len(autocorr)//2:] / autocorr[len(autocorr)//2]
        
        lag_max = min(200, len(autocorr))
        ax7.plot(range(lag_max), autocorr[:lag_max], color='blue')
        ax7.axhline(0, color='black', linestyle='-', linewidth=0.5)
        ax7.axhline(np.exp(-1), color='red', linestyle='--', 
                    label='e⁻¹ Schwelle')
        
        # Integrierte Autokorrelationszeit
        tau_int = integrated_autocorr_time(lattice.action_history)
        ax7.axvline(tau_int, color='green', linestyle='--', 
                    label=f'τ_int = {tau_int:.1f}')
    
    ax7.set_xlabel('Lag')
    ax7.set_ylabel('Autokorrelation')
    ax7.set_title('Action Autokorrelation')
    ax7.legend()
    ax7.grid(alpha=0.3)
    
    # 8. Korrelator-Matrix (alle Messungen)
    ax8 = fig.add_subplot(gs[2, 1])
    correlator_matrix = np.array(correlators).T
    im = ax8.imshow(correlator_matrix[:10, :100], aspect='auto', 
                    cmap='viridis', interpolation='nearest')
    ax8.set_xlabel('Messung #')
    ax8.set_ylabel('t [Gittereinheiten]')
    ax8.set_title('Korrelator-Zeitreihe')
    plt.colorbar(im, ax=ax8, label='C(t)')
    
    # 9. Vergleich mit Lattice QCD
    ax9 = fig.add_subplot(gs[2, 2])
    
    # Berechne finale Masse
    m_uidt, m_uidt_err = extract_mass_exponential(C_avg, config.a)
    
    if not np.isnan(m_uidt):
        categories = ['UIDT\n(diese Sim.)', 'Lattice QCD\n(PDG 2024)']
        masses = [m_uidt, 1.710]
        errors = [m_uidt_err, 0.080]
        colors = ['blue', 'red']
        
        bars = ax9.bar(categories, masses, yerr=errors, capsize=10, 
                       color=colors, alpha=0.6, edgecolor='black')
        
        # Z-Score annotieren
        z_score = abs(m_uidt - 1.710) / np.sqrt(m_uidt_err**2 + 0.080**2)
        ax9.text(0.5, max(masses)*1.05, f'Z = {z_score:.2f}σ', 
                 ha='center', fontsize=12, fontweight='bold')
    
    ax9.set_ylabel('m_{0++} [GeV]')
    ax9.set_title('Glueball-Masse Vergleich')
    ax9.grid(axis='y', alpha=0.3)
    
    # Suptitle mit Parametern
    fig.suptitle(
        f'UIDT Lattice QCD: {config.N_spatial}³×{config.N_temporal}, '
        f'β={config.beta}, κ={config.kappa}, a={config.a} fm',
        fontsize=14, fontweight='bold'
    )
    
    plt.savefig('uidt_hmc_full_diagnostics.png', dpi=300, bbox_inches='tight')
    print("\n✓ Diagnostik-Plot gespeichert: uidt_hmc_full_diagnostics.png")

# ============ PARAMETER-SCANS ============

def parameter_scan_kappa():
    """
    Systematischer κ-Scan
    Ziel: Finde κ-Bereich, der mit Lattice QCD kompatibel ist
    """
    kappa_values = np.linspace(0.1, 1.0, 10)
    results = []
    
    base_config = LatticeConfig(
        N_spatial=12,
        N_temporal=24,
        beta=5.7,
        a=0.12,
        N_therm=500,  # Kürzer für Scan
        N_meas=1000,
        N_skip=5,
        kappa=0.5,  # wird überschrieben
        Lambda=1.0
    )
    
    print("\n" + "="*60)
    print("PARAMETER-SCAN: κ ∈ [0.1, 1.0]")
    print("="*60)
    
    for i, kappa in enumerate(kappa_values):
        print(f"\n[{i+1}/{len(kappa_values)}] κ = {kappa:.3f}")
        print("-" * 40)
        
        base_config.kappa = kappa
        
        try:
            # Verkürzte Simulation
            lattice = UIDTLatticeHMC(base_config)
            
            # Schnelle Thermalisierung
            for _ in range(100):
                lattice.hmc_trajectory_omelyan()
            
            # Messungen
            correlators = []
            S_vevs = []
            for _ in range(50):  # Weniger Messungen
                for _ in range(5):
                    lattice.hmc_trajectory_omelyan()
                C = simple_correlator(lattice)
                correlators.append(C)
                S_vevs.append(float(np.mean(lattice.S)))
            
            C_avg = np.mean(correlators, axis=0)
            m_glueball, m_err = extract_mass_exponential(C_avg, base_config.a)
            S_vev_avg = np.mean(S_vevs)
            
            # Vergleich mit Lattice QCD
            z_score = abs(m_glueball - 1.710) / np.sqrt(m_err**2 + 0.080**2)
            
            results.append({
                'kappa': kappa,
                'm_glueball': m_glueball,
                'm_err': m_err,
                'S_vev': S_vev_avg,
                'z_score': z_score
            })
            
            print(f"   m_glueball = {m_glueball:.3f} ± {m_err:.3f} GeV")
            print(f"   ⟨S⟩ = {S_vev_avg:.4f}")
            print(f"   Z-Score = {z_score:.2f}σ")
            
        except Exception as e:
            print(f"   ❌ Fehler: {e}")
            results.append({
                'kappa': kappa,
                'm_glueball': np.nan,
                'm_err': np.nan,
                'S_vev': np.nan,
                'z_score': np.nan
            })
    
    return results

def plot_kappa_scan(results):
    """Visualisiere κ-Scan Ergebnisse"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Filtere gültige Ergebnisse
    valid_results = [r for r in results if not np.isnan(r['m_glueball'])]
    
    if not valid_results:
        print("❌ Keine gültigen Ergebnisse für Plot")
        return
    
    kappas = [r['kappa'] for r in valid_results]
    masses = [r['m_glueball'] for r in valid_results]
    mass_errs = [r['m_err'] for r in valid_results]
    S_vevs = [r['S_vev'] for r in valid_results]
    z_scores = [r['z_score'] for r in valid_results]
    
    # Plot 1: Glueball-Masse vs κ
    ax1.errorbar(kappas, masses, yerr=mass_errs, fmt='o-', capsize=4, 
                 color='blue', label='UIDT Simulation')
    ax1.axhline(1.710, color='red', linestyle='--', 
                label='Lattice QCD (1.710 GeV)')
    ax1.fill_between(kappas, 1.710-0.080, 1.710+0.080, 
                     alpha=0.2, color='red', label='Lattice Fehler')
    ax1.set_xlabel('κ (UIDT Kopplung)')
    ax1.set_ylabel('m_glueball [GeV]')
    ax1.set_title('Glueball-Masse vs UIDT-Kopplung')
    ax1.legend()
    ax1.grid(alpha=0.3)
    
    # Plot 2: Z-Score und ⟨S⟩ vs κ
    ax2_twin = ax2.twinx()
    
    # Z-Score
    line1 = ax2.plot(kappas, z_scores, 's-', color='red', 
                     label='Z-Score (vs LQCD)', linewidth=2)
    ax2.axhline(2.0, color='red', linestyle=':', alpha=0.7, 
                label='2σ Grenze')
    ax2.axhline(3.0, color='red', linestyle='--', alpha=0.7, 
                label='3σ Grenze')
    ax2.set_ylabel('Z-Score', color='red')
    ax2.tick_params(axis='y', labelcolor='red')
    
    # ⟨S⟩
    line2 = ax2_twin.plot(kappas, S_vevs, 'o-', color='blue', 
                          label='⟨S⟩', linewidth=2)
    ax2_twin.set_ylabel('⟨S⟩ [VEV]', color='blue')
    ax2_twin.tick_params(axis='y', labelcolor='blue')
    
    # Kombinierte Legende
    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax2.legend(lines, labels, loc='upper left')
    
    ax2.set_xlabel('κ (UIDT Kopplung)')
    ax2.set_title('Kompatibilität & Kondensation')
    ax2.grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('kappa_scan_results.png', dpi=300, bbox_inches='tight')
    print("✓ κ-Scan Plot gespeichert: kappa_scan_results.png")

# ============ BETA-SCAN FÜR KONTINUUMSLIMES ============

def beta_scan_continuum_limit():
    """
    β-Scan zur Untersuchung des Kontinuumslimes
    Verschiedene β-Werte entsprechen verschiedenen Gitterabständen a
    """
    beta_values = [5.6, 5.7, 5.8, 5.9, 6.0]
    a_values = [0.15, 0.12, 0.10, 0.08, 0.07]  # Typische Werte für SU(3)
    
    results = []
    
    print("\n" + "="*60)
    print("KONTINUUMSLIMES: β-SCAN")
    print("="*60)
    
    for beta, a in zip(beta_values, a_values):
        print(f"\nβ = {beta}, a = {a:.3f} fm")
        print("-" * 30)
        
        config = LatticeConfig(
            N_spatial=12,
            N_temporal=24,
            beta=beta,
            a=a,
            N_therm=500,
            N_meas=1000,
            N_skip=5,
            kappa=0.5,
            Lambda=1.0
        )
        
        try:
            # Schnelle Simulation
            lattice = UIDTLatticeHMC(config)
            
            for _ in range(100):
                lattice.hmc_trajectory_omelyan()
            
            correlators = []
            for _ in range(50):
                for _ in range(5):
                    lattice.hmc_trajectory_omelyan()
                C = simple_correlator(lattice)
                correlators.append(C)
            
            C_avg = np.mean(correlators, axis=0)
            m_glueball, m_err = extract_mass_exponential(C_avg, a)
            
            # Physikalische Masse in GeV
            m_phys = m_glueball
            
            results.append({
                'beta': beta,
                'a': a,
                'm_glueball': m_phys,
                'm_err': m_err
            })
            
            print(f"   m_glueball = {m_phys:.3f} ± {m_err:.3f} GeV")
            
        except Exception as e:
            print(f"   ❌ Fehler: {e}")
            results.append({
                'beta': beta,
                'a': a,
                'm_glueball': np.nan,
                'm_err': np.nan
            })
    
    return results

def plot_continuum_limit(results):
    """Visualisiere Kontinuumslimes"""
    valid_results = [r for r in results if not np.isnan(r['m_glueball'])]
    
    if len(valid_results) < 3:
        print("❌ Nicht genug Daten für Kontinuumslimes")
        return
    
    betas = [r['beta'] for r in valid_results]
    a_values = [r['a'] for r in valid_results]
    masses = [r['m_glueball'] for r in valid_results]
    mass_errs = [r['m_err'] for r in valid_results]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Plot 1: Masse vs Gitterabstand
    ax1.errorbar(a_values, masses, yerr=mass_errs, fmt='s-', 
                 capsize=5, color='purple', label='UIDT Simulation')
    ax1.axhline(1.710, color='red', linestyle='--', 
                label='Kontinuumswert (1.710 GeV)')
    
    # Linearer Fit für Extrapolation a→0
    if len(a_values) >= 3:
        try:
            coeffs = np.polyfit(a_values, masses, 1)
            a_fine = np.linspace(0, max(a_values)*1.1, 100)
            mass_fit = np.polyval(coeffs, a_fine)
            ax1.plot(a_fine, mass_fit, '--', color='gray', 
                     label=f'Linearer Fit: {coeffs[0]:.2f}a + {coeffs[1]:.2f}')
            
            # Extrapolation zu a=0
            m_continuum = coeffs[1]
            ax1.axhline(m_continuum, color='green', linestyle=':', 
                        label=f'Extrapoliert: {m_continuum:.3f} GeV')
        except:
            pass
    
    ax1.set_xlabel('Gitterabstand a [fm]')
    ax1.set_ylabel('m_glueball [GeV]')
    ax1.set_title('Kontinuumslimes (a → 0)')
    ax1.legend()
    ax1.grid(alpha=0.3)
    ax1.invert_xaxis()  # a wird kleiner → Kontinuum
    
    # Plot 2: Masse vs β
    ax2.errorbar(betas, masses, yerr=mass_errs, fmt='o-', 
                 capsize=5, color='orange')
    ax2.set_xlabel('β (Kopplung)')
    ax2.set_ylabel('m_glueball [GeV]')
    ax2.set_title('Glueball-Masse vs β')
    ax2.grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('continuum_limit.png', dpi=300, bbox_inches='tight')
    print("✓ Kontinuumslimes Plot gespeichert: continuum_limit.png")

# ============ HAUPTAUSFÜHRUNG ============

if __name__ == "__main__":
    print("\n" + "█"*60)
    print("█" + " "*15 + "UIDT LATTICE QCD ANALYSE" + " "*18 + "█")
    print("█" + " "*10 + "Vollständige Parameterscans" + " "*19 + "█")  
    print("█"*60 + "\n")
    
    # 1. Hauptsimulation
    print("🎯 1. VOLLSTÄNDIGE HMC-SIMULATION")
    lattice, S_vev_data, correlator_data = run_full_hmc_simulation()
    
    # 2. κ-Scan
    print("\n🎯 2. κ-PARAMETER-SCAN")
    kappa_results = parameter_scan_kappa()
    plot_kappa_scan(kappa_results)
    
    # 3. Kontinuumslimes
    print("\n🎯 3. KONTINUUMSLIMES-ANALYSE") 
    continuum_results = beta_scan_continuum_limit()
    plot_continuum_limit(continuum_results)
    
    print("\n" + "="*60)
    print("ANALYSE ABGESCHLOSSEN")
    print("="*60)
    
    # Zusammenfassung
    print("\n📋 ZUSAMMENFASSUNG:")
    print("   1. Vollständige HMC-Simulation mit Diagnostik")
    print("   2. κ-Scan zur Identifikation kompatibler Parameter")
    print("   3. β-Scan für Kontinuumslimes-Extrapolation")
    print("\n📊 Ergebnisse in Plots gespeichert:")
    print("   - uidt_hmc_full_diagnostics.png")
    print("   - kappa_scan_results.png") 
    print("   - continuum_limit.png")