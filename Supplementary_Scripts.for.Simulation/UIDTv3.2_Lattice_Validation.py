def validate_cayley_hamiltonian(self, n_tests=1000):
    """
    Validierung der Cayley-Hamilton Exponentialfunktion gegen Standard expm.
    """
    print("🔍 Validierung Cayley-Hamilton vs Standard expm")
    
    max_error = 0.0
    avg_error = 0.0
    
    for i in range(n_tests):
        # Zufällige anti-hermitische Matrix erzeugen
        A_real = np.random.randn(3, 3)
        A_imag = np.random.randn(3, 3)
        A_herm = (A_real + 1j*A_imag + (A_real - 1j*A_imag).T) / 2  # Hermitesch
        A_antiherm = 1j * A_herm  # Anti-hermitisch
        
        # Beide Methoden berechnen
        exp_ch = su3_expm_cayley_hamiltonian(to_gpu(A_antiherm))
        exp_std = linalg_expm(to_gpu(A_antiherm))
        
        # Fehler berechnen
        error = np.max(np.abs(to_cpu(exp_ch) - to_cpu(exp_std)))
        max_error = max(max_error, error)
        avg_error += error
    
    avg_error /= n_tests
    
    print(f"✅ Maximaler Fehler: {max_error:.2e}")
    print(f"✅ Durchschnittlicher Fehler: {avg_error:.2e}")
    
    if max_error < 1e-10:
        print("🎉 Cayley-Hamilton validiert! Sehr hohe Genauigkeit.")
    elif max_error < 1e-6:
        print("✅ Cayley-Hamilton validiert! Ausreichende Genauigkeit für HMC.")
    else:
        print("⚠️  Cayley-Hamilton hat signifikante Fehler. Verwende Standard expm.")
    
    return max_error, avg_error