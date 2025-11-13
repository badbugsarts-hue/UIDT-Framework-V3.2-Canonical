class UIDTLatticeOptimized(SU3Lattice):
    def __init__(self, cfg: LatticeConfig, kappa=0.5, Lambda=1.0,
                 m_S=1.705, lambda_S=0.417, v_vev=0.0477):
        super().__init__(cfg)
        self.kappa = kappa
        self.Lambda = Lambda
        self.m_S = m_S
        self.lambda_S = lambda_S
        self.v_vev = v_vev
        
        # Optimierte Initialisierung
        shapeS = (self.Nx, self.Ny, self.Nz, self.Nt)
        rng = np.random.RandomState(cfg.seed + 7)
        S_init = (v_vev + 1e-3 * rng.randn(*shapeS)).astype(float)
        self.S = to_gpu(S_init)
        self.Ps = to_gpu(xp.zeros_like(self.S))
        self.Pu = None
        
        # Performance-Monitoring
        self.acceptance_rate = 0.0
        self.avg_delta_H = 0.0
        
    def update_U_vectorized(self, Pu, step_size):
        """
        Vollständig vektorisierte U-Update mit Cayley-Hamilton.
        ️️️️️️➡️ 10-50x schneller als einzelne Matrix-Exponentiale
        """
        # Anti-hermitische Matrix für SU(3) Exponential
        A = 1j * Pu * step_size
        
        # Batch-Update aller Links gleichzeitig
        expA = su3_expm_hybrid(A)
        
        # Vektorisierte Matrix-Multiplikation
        self.U = xp.matmul(expA, self.U)
        
    def update_S_vectorized(self, Ps, step_size):
        """Vektorisierte S-Feld Update"""
        self.S = self.S + step_size * Ps
        
    def gauge_force_vectorized(self):
        """
        Vollständig vektorisierte Gauge-Force Berechnung.
        Nutzt periodische Randbedingungen via xp.roll.
        """
        U = self.U
        beta = self.cfg.beta
        
        # Initialisiere Force-Tensor
        F = xp.zeros_like(U, dtype=complex)
        
        # Berechne Staple für jede Richtung μ
        for mu in range(4):
            staple_sum = xp.zeros_like(U[..., 0, :, :])
            
            for nu in range(4):
                if nu == mu:
                    continue
                    
                # Positive Staple: U_ν(x+μ) U_μ†(x+ν) U_ν†(x)
                U_nu_x_plus_mu = self.roll_matrix(U, nu, mu, forward=True)
                U_mu_x_plus_nu_dag = self.roll_matrix(U, mu, nu, forward=True).conj().transpose(0,1,2,3,5,4)
                U_nu_x_dag = U[..., nu, :, :].conj().transpose(0,1,2,3,5,4)
                
                staple_pos = xp.matmul(U_nu_x_plus_mu, 
                                     xp.matmul(U_mu_x_plus_nu_dag, U_nu_x_dag))
                
                # Negative Staple: U_ν†(x+μ-ν) U_μ(x-ν) U_ν(x-ν)
                U_nu_dag_x_plus_mu_minus_nu = self.roll_matrix(U, nu, mu, forward=True, shift_nu=-1).conj().transpose(0,1,2,3,5,4)
                U_mu_x_minus_nu = self.roll_matrix(U, mu, nu, forward=False)
                U_nu_x_minus_nu = self.roll_matrix(U, nu, nu, forward=False)
                
                staple_neg = xp.matmul(U_nu_dag_x_plus_mu_minus_nu,
                                     xp.matmul(U_mu_x_minus_nu, U_nu_x_minus_nu))
                
                staple_sum += staple_pos + staple_neg
            
            # Force für Richtung μ: F_μ = -β/3 * staple_sum * U_μ†
            F_mu = - (beta / 3.0) * xp.matmul(staple_sum, U[..., mu, :, :].conj().transpose(0,1,2,3,5,4))
            
            # Projektion auf spurfreie hermitesche Matrizen
            F_mu_herm = (F_mu + F_mu.conj().transpose(0,1,2,3,5,4)) / 2
            trace = xp.trace(F_mu_herm, axis1=-2, axis2=-1)
            F_mu_trless = F_mu_herm - (trace[..., xp.newaxis, xp.newaxis] / 3.0) * xp.eye(3, dtype=complex)
            
            F[..., mu, :, :] = F_mu_trless
        
        return F
    
    def roll_matrix(self, U, mu, nu, forward=True, shift_nu=0):
        """
        Hilfsfunktion für periodische Verschiebungen von U-Matrizen.
        """
        shifts = [0, 0, 0, 0]
        shift_amount = 1 if forward else -1
        
        if nu == 0:  # x-Richtung
            shifts[0] = shift_amount
        elif nu == 1:  # y-Richtung  
            shifts[1] = shift_amount
        elif nu == 2:  # z-Richtung
            shifts[2] = shift_amount
        elif nu == 3:  # t-Richtung
            shifts[3] = shift_amount
            
        # Zusätzlicher Shift für negative Staple
        if shift_nu == -1:
            if nu == 0: shifts[0] = -1
            elif nu == 1: shifts[1] = -1
            elif nu == 2: shifts[2] = -1
            elif nu == 3: shifts[3] = -1
        
        return xp.roll(U, shifts, axis=(0,1,2,3))[..., mu, :, :]