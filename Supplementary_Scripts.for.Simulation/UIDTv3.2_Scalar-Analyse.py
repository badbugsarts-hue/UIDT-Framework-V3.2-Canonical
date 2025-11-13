import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

class UIDTScalarAnalysis(UIDTLatticeWithSmearing):
    def __init__(self, cfg: LatticeConfig, kappa=0.5, Lambda=1.0,
                 m_S=1.705, lambda_S=0.417, v_vev=0.0477):
        super().__init__(cfg, kappa, Lambda, m_S, lambda_S, v_vev)
        
    def scalar_field_correlator(self, dist_max=None):
        """
        Berechnet den zeitlichen Zwei-Punkt-Korrelator des Skalarfeldes C_S(t).
        C_S(t) = ⟨S(x,t) S(x,0)⟩ - ⟨S⟩²  (verbundener Korrelator)
        """
        xp_local = xp
        S = self.S
        Nt = self.Nt
        dist_max = dist_max if dist_max else Nt // 2
        
        # Räumliche Mittelung für jedes t
        S_t = xp_local.mean(S, axis=(0, 1, 2))  # Shape: (Nt,)
        
        # Verbundener Korrelator: subtrahiere VEV
        S_vev = xp_local.mean(S_t)
        S_t_connected = S_t - S_vev
        
        # Korrelator berechnen
        C_S = xp_local.zeros(dist_max, dtype=float)
        
        for t in range(dist_max):
            # C_S(t) = ⟨S(t0) S(t0+t)⟩ - ⟨S⟩²
            S_shifted = xp_local.roll(S_t_connected, -t)
            C_S[t] = xp_local.mean(S_t_connected * S_shifted)
            
        return to_cpu(C_S) if USE_CUPY else C_S
    
    def scalar_correlator_spatial(self, dist_max=None):
        """
        Räumlicher Korrelator für zusätzliche Massenbestimmung.
        C_S(r) = ⟨S(x) S(x+r)⟩ - ⟨S⟩²
        """
        xp_local = xp
        S = self.S
        Nx = self.Nx
        dist_max = dist_max if dist_max else Nx // 2
        
        # Räumlicher Korrelator in x-Richtung
        C_S_r = xp_local.zeros(dist_max, dtype=float)
        S_vev = xp_local.mean(S)
        S_connected = S - S_vev
        
        for r in range(dist_max):
            # Verschiebe in x-Richtung
            S_shifted = xp_local.roll(S_connected, -r, axis=0)
            # Räumliche und zeitliche Mittelung
            C_S_r[r] = xp_local.mean(S_connected * S_shifted)
            
        return to_cpu(C_S_r) if USE_CUPY else C_S_r

def scalar_mass_fit_model(t, A, m, B):
    """
    Fit-Modell für Skalarkorrelator: C(t) = A * exp(-m*t) + B * exp(-m*(Nt-t))
    Berücksichtigt periodische Randbedingungen.
    """
    return A * np.exp(-m * t) + B * np.exp(-m * (Nt_fit - t))

def extract_scalar_mass(C_S, a, Nt, t_min=1, t_max=None):
    """
    Extrahiert Skalarmasse aus Korrelator C_S(t) unter Berücksichtigung
    periodischer Randbedingungen.
    """
    if t_max is None:
        t_max = len(C_S) - 1
    
    t_values = np.arange(len(C_S))
    
    # Wähle Fit-Bereich
    mask = (t_values >= t_min) & (t_values <= t_max)
    t_fit = t_values[mask]
    C_fit = C_S[mask]
    
    # Startparameter schätzen
    A0 = C_S[t_min]
    m0 = -np.log(C_S[t_min+1] / C_S[t_min]) if C_S[t_min+1] > 0 else 0.5
    B0 = C_S[-1] if len(C_S) > 1 else A0 * 0.1
    
    global Nt_fit
    Nt_fit = Nt
    
    try:
        # Fit mit periodischen Randbedingungen
        popt, pcov = curve_fit(scalar_mass_fit_model, t_fit, C_fit, 
                              p0=[A0, m0, B0], maxfev=5000)
        
        m_latt = popt[1]
        m_err = np.sqrt(pcov[1,1]) if pcov is not None else 0.0
        
        # Konvertiere zu physikalischen Einheiten (GeV)
        m_phys = m_latt / a * 0.197  # a in fm, 0.197 GeV·fm
        m_err_phys = m_err / a * 0.197
        
        return m_phys, m_err_phys, popt
        
    except Exception as e:
        print(f"⚠️ Skalarmassen-Fit fehlgeschlagen: {e}")
        # Fallback: einfache exponentielle Anpassung
        try:
            def simple_exp(t, A, m):
                return A * np.exp(-m * t)
            
            popt, pcov = curve_fit(simple_exp, t_fit, C_fit, p0=[A0, m0])
            m_latt = popt[1]
            m_phys = m_latt / a * 0.197
            m_err_phys = np.sqrt(pcov[1,1]) / a * 0.197 if pcov is not None else 0.0
            
            return m_phys, m_err_phys, popt
            
        except Exception:
            return np.nan, np.nan, None

def run_scalar_mass_measurement(cfg: LatticeConfig, kappa=0.5, Lambda=1.0,
                               hmc_steps=10, step_size=0.02):
    """
    Spezialisierte Messung der Skalarmasse mit statistischer Analyse.
    """
    print("🔬 Starte Skalarmassen-Messung")
    
    lat = UIDTScalarAnalysis(cfg, kappa=kappa, Lambda=Lambda)
    
    # Datenspeicher
    scalar_correlators = []
    scalar_vevs = []
    acceptance_rates = []
    
    # Thermalisierung
    print("🔥 Thermalisierung...")
    for i in trange(cfg.N_therm):
        lat.hmc_trajectory_omelyan(n_steps=hmc_steps, step_size=step_size)
    
    # Messphase
    print("📊 Messphase - Skalarkorrelatoren sammeln...")
    acceptance_count = 0
    total_trajectories = 0
    
    for i in trange(cfg.N_meas):
        # HMC Updates
        for _ in range(cfg.N_skip):
            accepted, _ = lat.hmc_trajectory_omelyan(n_steps=hmc_steps, step_size=step_size)
            if accepted:
                acceptance_count += 1
            total_trajectories += 1
        
        # Skalar-Messungen
        C_S = lat.scalar_field_correlator(dist_max=min(cfg.N_temporal//2, 12))
        scalar_correlators.append(C_S)
        S_vev = float(xp.mean(lat.S))
        scalar_vevs.append(S_vev)
        
        if i % 100 == 0:
            print(f"   Trajektorie {i}: ⟨S⟩ = {S_vev:.4f}")
    
    acceptance_rate = acceptance_count / total_trajectories
    
    # Statistische Analyse
    print("📈 Statistische Analyse der Skalarmasse...")
    
    # Jackknife-Analyse für Korrelator und Masse
    def jackknife_scalar_mass(correlators, a, Nt):
        """Jackknife für Skalarmassen-Extraktion"""
        n_meas = len(correlators)
        masses = np.zeros(n_meas)
        
        for i in range(n_meas):
            # Jackknife-Stichprobe (lasse i-te Messung weg)
            jack_sample = [correlators[j] for j in range(n_meas) if j != i]
            C_avg = np.mean(jack_sample, axis=0)
            
            # Massen-Extraktion
            m, m_err, _ = extract_scalar_mass(C_avg, a, Nt, t_min=1, t_max=6)
            masses[i] = m
        
        m_mean = np.mean(masses)
        m_err = np.sqrt((n_meas - 1) / n_meas * np.sum((masses - m_mean)**2))
        
        return m_mean, m_err, masses
    
    # Hauptanalyse
    C_S_avg = np.mean(scalar_correlators, axis=0)
    C_S_err = np.std(scalar_correlators, axis=0) / np.sqrt(cfg.N_meas)
    
    # Autokorrelationszeit für Skalarkorrelator
    tau_int_S = integrated_autocorrelation_time(np.array([c[1] for c in scalar_correlators]))
    
    # Jackknife-Massenanalyse
    m_S_jack, m_S_err_jack, jack_samples = jackknife_scalar_mass(
        scalar_correlators, cfg.a, cfg.N_temporal
    )
    
    # Direkte Massen-Extraktion aus gemitteltem Korrelator
    m_S_direct, m_S_err_direct, fit_params = extract_scalar_mass(
        C_S_avg, cfg.a, cfg.N_temporal, t_min=1, t_max=6
    )
    
    # VEV-Statistik
    S_vev_mean = np.mean(scalar_vevs)
    S_vev_err = np.std(scalar_vevs) / np.sqrt(cfg.N_meas / (2 * tau_int_S))
    
    # Ergebnisse
    results = {
        'm_S': m_S_jack,  # Jackknife als primäres Ergebnis
        'm_S_err': m_S_err_jack,
        'm_S_direct': m_S_direct,
        'm_S_direct_err': m_S_err_direct,
        'S_vev': S_vev_mean,
        'S_vev_err': S_vev_err,
        'C_S_avg': C_S_avg,
        'C_S_err': C_S_err,
        'fit_params': fit_params,
        'acceptance_rate': acceptance_rate,
        'tau_int_S': tau_int_S,
        'jackknife_samples': jack_samples
    }
    
    # Plot-Ergebnisse
    _plot_scalar_mass_results(results, cfg, kappa)
    
    return results

def _plot_scalar_mass_results(results, cfg, kappa):
    """Plottet Skalarmassen-Ergebnisse"""
    C_S = results['C_S_avg']
    C_err = results['C_S_err']
    t_values = np.arange(len(C_S))
    
    plt.figure(figsize=(12, 5))
    
    # Korrelator-Plot
    plt.subplot(1, 2, 1)
    plt.errorbar(t_values, C_S, yerr=C_err, fmt='o-', capsize=5, label='Daten')
    
    # Fit-Kurve
    if results['fit_params'] is not None:
        t_fine = np.linspace(0, len(C_S)-1, 100)
        global Nt_fit
        Nt_fit = cfg.N_temporal
        fit_curve = scalar_mass_fit_model(t_fine, *results['fit_params'])
        plt.plot(t_fine, fit_curve, 'r-', label='Fit')
        
        # Fit-Bereich markieren
        t_fit = t_values[1:7]  # Beispiel-Bereich
        plt.axvspan(t_fit[0]-0.5, t_fit[-1]+0.5, alpha=0.2, color='gray', label='Fit-Bereich')
    
    plt.yscale('log')
    plt.xlabel('Zeitabstand t')
    plt.ylabel('C_S(t)')
    plt.title(f'Skalarkorrelator - κ={kappa}')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Jackknife-Verteilung
    plt.subplot(1, 2, 2)
    if 'jackknife_samples' in results:
        jack_samples = results['jackknife_samples']
        plt.hist(jack_samples, bins=20, alpha=0.7, edgecolor='black')
        plt.axvline(results['m_S'], color='red', linestyle='--', 
                   label=f'm_S = {results["m_S"]:.3f} ± {results["m_S_err"]:.3f} GeV')
        plt.xlabel('Skalarmasse m_S (GeV)')
        plt.ylabel('Häufigkeit')
        plt.title('Jackknife-Verteilung der Skalarmasse')
        plt.legend()
        plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f'scalar_mass_kappa_{kappa}.png', dpi=300, bbox_inches='tight')
    plt.close()

# 🔬 PHYSIKALISCHE INTERPRETATION

def interpret_scalar_mass_results(scalar_results, glueball_mass=0.61, glueball_mass_err=0.02):
    """
    Interpretiert die Skalarmassen-Ergebnisse im Kontext der Entkopplungsthese.
    """
    m_S = scalar_results['m_S']
    m_S_err = scalar_results['m_S_err']
    S_vev = scalar_results['S_vev']
    
    mass_ratio = m_S / glueball_mass
    mass_ratio_err = mass_ratio * np.sqrt((m_S_err/m_S)**2 + (glueball_mass_err/glueball_mass)**2)
    
    print("\n🔬 PHYSIKALISCHE INTERPRETATION DER SKALARMASSE")
    print("=" * 60)
    print(f"📊 Messergebnisse:")
    print(f"   • Skalarmasse m_S = {m_S:.3f} ± {m_S_err:.3f} GeV")
    print(f"   • Skalar-VEV ⟨S⟩ = {S_vev:.4f} ± {scalar_results['S_vev_err']:.4f}")
    print(f"   • Glueball-Masse m_G = {glueball_mass:.3f} ± {glueball_mass_err:.3f} GeV")
    print(f"   • Massenverhältnis m_S/m_G = {mass_ratio:.2f} ± {mass_ratio_err:.2f}")
    
    print("\n🎯 Schlussfolgerungen:")
    
    if mass_ratio > 1.5:
        print("   ✅ STARKES ENTKOPPLUNGSSIGNAL")
        print(f"   • m_S ≫ m_G ({mass_ratio:.1f}× schwerer)")
        print("   • UIDT-Skalar ist zu schwer, um niederenergetische SU(3)-Dynamik zu stören")
        print("   • Confinement und Glueball-Spektrum bleiben erhalten")
        
    elif mass_ratio > 1.0:
        print("   ⚠️  MODERATE ENTKOPPLUNG")
        print(f"   • m_S > m_G ({mass_ratio:.1f}× schwerer)") 
        print("   • Geringfügige Modifikationen der SU(3)-Dynamik möglich")
        print("   • Entkopplungsthese wird unterstützt")
        
    else:
        print("   ❌ MÖGLICHE KOPPLUNG")
        print(f"   • m_S ≤ m_G ({mass_ratio:.1f}×)")
        print("   • UIDT-Skalar könnte niederenergetische Dynamik beeinflussen")
        print("   • Weitere Untersuchungen notwendig")
    
    print(f"\n📈 Kondensationseigenschaften:")
    if S_vev > 0.1:
        print("   • Starkes Kondensat: ⟨S⟩ deutlich von Null verschieden")
        print("   • Symmetriebrechung des UIDT-Feldes bestätigt")
    elif S_vev > 0.01:
        print("   • Schwaches Kondensat: ⟨S⟩ > 0")
        print("   • UIDT-Feld in gekoppelter Phase")
    else:
        print("   • Kein Kondensat: ⟨S⟩ ≈ 0")
        print("   • UIDT-Feld möglicherweise in ungekoppelter Phase")
    
    return mass_ratio, mass_ratio_err

# 🎯 PRODUKTIONSLAUF FÜR SKALARMASSE

def production_scalar_mass_run():
    """Produktions-Lauf für Skalarmassen-Messung"""
    cfg = LatticeConfig(N_spatial=16, N_temporal=16, beta=6.0, a=0.1,
                       N_therm=500, N_meas=2000, N_skip=10, seed=42)
    
    print("🚀 STARTE PRODUKTIONS-LAUF FÜR SKALARMASSE")
    print("   Gitter: 16⁴, β=6.0, 2000 Messungen") 
    print("   UIDT-Parameter: κ=0.5, Λ=1.0")
    
    results = run_scalar_mass_measurement(cfg, kappa=0.5, 
                                        hmc_steps=10, step_size=0.02)
    
    return results

# 🔬 GESAMTANALYSE: STRINGSPANNUNG + SKALARMASSE

def complete_uidt_analysis():
    """
    Führt komplette UIDT-Analyse durch: Stringspannung + Skalarmasse.
    Liefert abschließenden Beweis für Entkopplungsthese.
    """
    print("⚛️  KOMPLETTE UIDT-ANALYSE - ENTKOPPLUNGSTHESE")
    print("=" * 60)
    
    # 1. Stringspannung messen
    print("\n1. 📏 Messung der Stringspannung...")
    string_results = production_string_tension_run()
    
    # 2. Skalarmasse messen  
    print("\n2. 🔬 Messung der Skalarmasse...")
    scalar_results = production_scalar_mass_run()
    
    # 3. Physikalische Interpretation
    print("\n3. 🎯 PHYSIKALISCHE SCHLUSSFOLGERUNG")
    print("=" * 60)
    
    # Stringspannungs-Interpretation
    sigma_uidt = string_results['sigma']
    sigma_pure_ym = 0.040  # Referenzwert reines SU(3)
    
    sigma_ratio = sigma_uidt / sigma_pure_ym
    print(f"📏 Stringspannung:")
    print(f"   • UIDT: σ = {sigma_uidt:.4f} ± {string_results['sigma_err']:.4f}")
    print(f"   • Reines SU(3): σ ≈ {sigma_pure_ym:.4f}") 
    print(f"   • Verhältnis: {sigma_ratio:.3f}")
    
    # Skalarmassen-Interpretation
    mass_ratio, mass_ratio_err = interpret_scalar_mass_results(scalar_results)
    
    # GESAMTBEWERTUNG
    print("\n🏁 GESAMTBEWERTUNG DER ENTKOPPLUNGSTHESE")
    print("=" * 60)
    
    evaluation_score = 0
    
    if abs(sigma_ratio - 1.0) < 0.1:
        print("✅ Stringspannung: UNVERÄNDERT")
        print("   • Confinement-Eigenschaften erhalten")
        evaluation_score += 1
    else:
        print("❌ Stringspannung: MODIFIZIERT")
        print("   • Mögliche Änderung der Confinement-Eigenschaften")
    
    if mass_ratio > 1.5:
        print("✅ Skalarmasse: STARK ENTKOPPELT") 
        print("   • Schweres UIDT-Feld stört SU(3)-Dynamik nicht")
        evaluation_score += 1
    elif mass_ratio > 1.0:
        print("⚠️  Skalarmasse: MODERAT ENTKOPPELT")
        print("   • Teilweise Entkopplung")
        evaluation_score += 0.5
    else:
        print("❌ Skalarmasse: GEKOPPELT")
        print("   • UIDT-Feld beeinflusst niederenergetische Dynamik")
    
    if scalar_results['S_vev'] > 0.05:
        print("✅ Kondensation: BESTÄTIGT")
        print("   • UIDT-Feld in gekoppelter Phase")
        evaluation_score += 1
    else:
        print("❌ Kondensation: NICHT NACHGEWIESEN")
        print("   • UIDT-Feld möglicherweise ungekoppelt")
    
    # FINALE BEWERTUNG
    print(f"\n🎯 ENTKOPPLUNGSTHESE: {evaluation_score}/3 PUNKTE")
    
    if evaluation_score >= 2.5:
        print("🏆 STARK UNTERSTÜTZT")
        print("   Die UIDT-Kopplung erhält die SU(3)-Dynamik bei gleichzeitiger Kondensation")
    elif evaluation_score >= 1.5:
        print("✅ TEILWEISE UNTERSTÜTZT") 
        print("   Eingeschränkte Entkopplung - weitere Untersuchungen empfohlen")
    else:
        print("❌ NICHT UNTERSTÜTZT")
        print("   UIDT-Feld modifiziert die SU(3)-Dynamik signifikant")
    
    return {
        'string_tension': string_results,
        'scalar_mass': scalar_results, 
        'evaluation_score': evaluation_score,
        'sigma_ratio': sigma_ratio,
        'mass_ratio': mass_ratio
    }

# Test-Lauf
if __name__ == "__main__":
    # Schneller Test
    cfg_test = LatticeConfig(N_spatial=8, N_temporal=8, beta=5.7, a=0.1,
                           N_therm=50, N_meas=100, N_skip=5, seed=123)
    
    test_results = run_scalar_mass_measurement(cfg_test, kappa=0.5)
    interpret_scalar_mass_results(test_results)
    
    # Für finale Physik-Ergebnisse:
    # complete_results = complete_uidt_analysis()