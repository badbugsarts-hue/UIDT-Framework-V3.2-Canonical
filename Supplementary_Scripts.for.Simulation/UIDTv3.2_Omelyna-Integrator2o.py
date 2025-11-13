def omelyan_integrator_2nd_order(self, n_steps=10, step_size=0.02, lambda_omelyan=0.193):
    """
    Omelyan-Integrator 2. Ordnung für optimale Energieerhaltung.
    λ ≈ 0.193 minimiert den Fehler 4. Ordnung.
    """
    # Omelyan-Koeffizienten
    xi = lambda_omelyan
    gamma = 0.5 - xi
    
    # Initiale Momenta
    self.Pu = self.random_momenta()
    self.Ps = xp.array(np.random.randn(self.Nx, self.Ny, self.Nz, self.Nt), dtype=float)
    
    # Store initial configuration for Metropolis
    U_old = self.U.copy()
    S_old = self.S.copy()
    Pu_old = self.Pu.copy()
    Ps_old = self.Ps.copy()
    
    # Initial Hamiltonian
    H_initial = self._compute_hamiltonian()
    
    # --- OMELYAN INTEGRATOR ---
    
    # 1. Initial half step for momenta
    gauge_F = self.gauge_force_vectorized()
    scalar_F = self.scalar_force_field_vectorized()
    
    self.Pu = self.Pu - xi * step_size * gauge_F
    self.Ps = self.Ps - xi * step_size * scalar_F
    
    # 2. Multiple steps
    for step in range(n_steps):
        # Update coordinates (first half)
        self.update_U_vectorized(self.Pu, gamma * step_size)
        self.update_S_vectorized(self.Ps, 0.5 * step_size)
        
        # Force computation at new position
        gauge_F = self.gauge_force_vectorized()
        scalar_F = self.scalar_force_field_vectorized()
        
        # Update momenta (full step)
        self.Pu = self.Pu - (1 - 2*xi) * step_size * gauge_F
        self.Ps = self.Ps - (1 - 2*xi) * step_size * scalar_F
        
        # Update coordinates (second half)
        self.update_U_vectorized(self.Pu, gamma * step_size)
        self.update_S_vectorized(self.Ps, 0.5 * step_size)
        
        # Final force update (except last step)
        if step < n_steps - 1:
            gauge_F = self.gauge_force_vectorized()
            scalar_F = self.scalar_force_field_vectorized()
            self.Pu = self.Pu - 2*xi * step_size * gauge_F
            self.Ps = self.Ps - 2*xi * step_size * scalar_F
    
    # 3. Final half step for momenta
    gauge_F = self.gauge_force_vectorized()
    scalar_F = self.scalar_force_field_vectorized()
    self.Pu = self.Pu - (1 - xi) * step_size * gauge_F
    self.Ps = self.Ps - (1 - xi) * step_size * scalar_F
    
    # --- METROPOLIS TEST ---
    H_final = self._compute_hamiltonian()
    delta_H = float(H_final - H_initial)
    
    # Acceptance decision
    accepted = False
    if xp.random.rand() < xp.exp(-delta_H):
        accepted = True
        self.acceptance_rate = 0.9 * self.acceptance_rate + 0.1
    else:
        # Reject: restore old configuration
        self.U = U_old
        self.S = S_old
        self.acceptance_rate = 0.9 * self.acceptance_rate
    
    self.avg_delta_H = 0.9 * self.avg_delta_H + 0.1 * abs(delta_H)
    
    return accepted, delta_H

def _compute_hamiltonian(self):
    """Berechnet Gesamt-Hamiltonian für Metropolis-Test"""
    # Kinetische Energie
    def kinetic_energy_Pu(Pu):
        Pu_flat = Pu.reshape(-1, 3, 3)
        traces = xp.real(xp.trace(xp.matmul(Pu_flat, Pu_flat), axis1=1, axis2=2))
        return 0.5 * xp.sum(traces)
    
    kin_gauge = kinetic_energy_Pu(self.Pu)
    kin_scalar = 0.5 * xp.sum(self.Ps**2)
    
    # Potentielle Energie (Action)
    pot_energy = self.uidt_action()
    
    return pot_energy + kin_gauge + kin_scalar