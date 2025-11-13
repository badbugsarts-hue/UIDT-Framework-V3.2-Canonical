def run_optimized_uidt_hmc(cfg: LatticeConfig, kappa=0.5, Lambda=1.0, 
                          use_omelyan=True, adaptive_stepsize=True):
    """
    Optimierte Haupt-HMC-Schleife mit allen Verbesserungen.
    """
    lat = UIDTLatticeOptimized(cfg, kappa=kappa, Lambda=Lambda)
    
    # Validierung
    lat.validate_cayley_hamiltonian()
    
    results = {
        'plaq_values': [],
        'S_values': [],
        'm_eff_values': [],
        'acceptance_rates': []
    }
    
    print("🔥 Starte optimierte UIDT HMC Simulation")
    
    for trajectory in range(cfg.N_therm + cfg.N_meas):
        if use_omelyan:
            accepted, delta_H = lat.omelyan_integrator_2nd_order()
        else:
            accepted, delta_H = lat.hmc_trajectory()
        
        # Adaptive Schrittweite
        if adaptive_stepsize and trajectory % 50 == 0:
            lat.adaptive_hmc_step_size()
        
        # Messungen nach Thermalisierung
        if trajectory >= cfg.N_therm and trajectory % cfg.N_skip == 0:
            plaq = - (3.0 / cfg.beta) * lat.wilson_action() / (lat.Nx * lat.Ny * lat.Nz * lat.Nt * 6.0)
            S_mean = float(xp.mean(lat.S))
            
            results['plaq_values'].append(float(plaq))
            results['S_values'].append(S_mean)
            results['acceptance_rates'].append(lat.acceptance_rate)
            
            if trajectory % 100 == 0:
                print(f"📊 Trajectory {trajectory}: Plaq={plaq:.4f}, "
                      f"<S>={S_mean:.4f}, Accept={lat.acceptance_rate:.3f}")
    
    # Performance-Report
    lat.performance_benchmark()
    
    return results, lat