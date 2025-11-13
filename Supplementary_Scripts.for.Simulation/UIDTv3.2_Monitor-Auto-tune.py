def adaptive_hmc_step_size(self, target_acceptance=0.8, adjustment_rate=0.05):
    """
    Automatische Anpassung der Schrittweite basierend auf Akzeptanzrate.
    """
    current_rate = self.acceptance_rate
    
    if current_rate < target_acceptance - 0.1:
        # Zu niedrige Akzeptanz: kleinere Schritte
        self.step_size *= (1.0 - adjustment_rate)
        print(f"🔻 Step size decreased to {self.step_size:.4f} (acceptance: {current_rate:.3f})")
    elif current_rate > target_acceptance + 0.1:
        # Zu hohe Akzeptanz: größere Schritte (effizienter)
        self.step_size *= (1.0 + adjustment_rate)
        print(f"🔺 Step size increased to {self.step_size:.4f} (acceptance: {current_rate:.3f})")
    
    return self.step_size

def performance_benchmark(self, n_trajectories=100):
    """
    Benchmark der Performance-Optimierungen.
    """
    print("🚀 Performance Benchmark für UIDT HMC")
    print("=" * 50)
    
    import time
    
    # Test mit verschiedenen Methoden
    methods = {
        'Original Leapfrog': self.hmc_trajectory,
        'Omelyan + Cayley-Hamilton': self.omelyan_integrator_2nd_order
    }
    
    for name, method in methods.items():
        print(f"\n📊 Testing: {name}")
        
        times = []
        acceptances = []
        
        for i in range(n_trajectories):
            start_time = time.time()
            accepted, delta_H = method()
            end_time = time.time()
            
            times.append(end_time - start_time)
            acceptances.append(accepted)
        
        avg_time = np.mean(times)
        acceptance_rate = np.mean(acceptances)
        
        print(f"   ⏱️  Average time: {avg_time:.4f}s")
        print(f"   ✅ Acceptance rate: {acceptance_rate:.3f}")
        print(f"   🎯 Performance: {1/avg_time:.2f} trajectories/s")
    
    return times, acceptances