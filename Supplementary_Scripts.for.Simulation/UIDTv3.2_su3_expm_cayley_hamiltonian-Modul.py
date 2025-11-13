import numpy as np
from scipy.linalg import expm
import cupy as cp
from cupyx.scipy.linalg import expm as cupy_expm

# GPU/CPU Handling
xp = cp if cp else np
linalg_expm = cupy_expm if cp else expm

def su3_expm_cayley_hamiltonian(A, xp_local=xp):
    """
    GPU-optimierte SU(3) Exponentialfunktion via Cayley-Hamilton Theorem.
    A: anti-hermitische Matrix (i * hermitesch), shape (...,3,3)
    Returns exp(A) in SU(3)
    
    Basierend auf: 
    F. Driencourt, "Efficient computation of the exponential of a matrix" 
    und analytische SU(3) Lösungen via charakteristischem Polynom.
    """
    # Für anti-hermitische Matrix: A = i*H mit H hermitesch
    # Charakteristisches Polynom: det(λI - A) = λ³ + c₁λ + c₀ = 0 (wegen spurfrei)
    
    # Koeffizienten des charakteristischen Polynoms
    A2 = xp_local.matmul(A, A)
    A3 = xp_local.matmul(A2, A)
    
    # Spur-basierte Koeffizienten (effizienter als Determinante)
    tr_A2 = xp_local.trace(A2, axis1=-2, axis2=-1)
    tr_A3 = xp_local.trace(A3, axis1=-2, axis2=-1)
    
    # Für spurfreie anti-hermitische Matrizen
    c0 = xp_local.linalg.det(A)  # c₀ = det(A)
    c1 = -0.5 * tr_A2            # c₁ = -½ tr(A²)
    
    # Norm q = sqrt(-c₁/3)
    q = xp_local.sqrt(-c1 / 3.0 + 1e-15)  # Stabilität für kleine Werte
    
    # Reshape für Broadcasting
    q = q[..., xp_local.newaxis, xp_local.newaxis]
    c0 = c0[..., xp_local.newaxis, xp_local.newaxis]
    
    # θ = arccos(c₀/(2q³)) mit Stabilitäts-Clipping
    q3 = q**3
    arg = c0 / (2.0 * q3 + 1e-15)
    arg = xp_local.clip(arg, -1.0, 1.0)  # Numerische Stabilität
    
    theta = xp_local.arccos(arg)
    
    # Koeffizienten u₀, u₁, u₂ für exp(A) = u₀I + u₁A + u₂A²
    u0 = xp_local.exp(-2j * q * xp_local.cos(theta/3))
    
    # Komplexe Exponentialterme
    exp_plus = xp_local.exp(1j * q * (xp_local.cos(theta/3) + xp_local.sqrt(3)*xp_local.sin(theta/3)))
    exp_minus = xp_local.exp(1j * q * (xp_local.cos(theta/3) - xp_local.sqrt(3)*xp_local.sin(theta/3)))
    
    u1 = (exp_plus + exp_minus - 2 * u0) / (3 * q**2 + 1e-15)
    u2 = (exp_plus + exp_minus - u0) / (3 * q**2 + 1e-15)
    
    return u0 * xp_local.eye(3, dtype=complex) + u1 * A + u2 * A2

def su3_expm_hybrid(A, xp_local=xp):
    """
    Hybride Exponentialfunktion: Cayley-Hamilton für normale Matrizen,
    Fallback auf Standard expm für singuläre/schlecht-konditionierte Fälle.
    """
    try:
        return su3_expm_cayley_hamiltonian(A, xp_local)
    except (xp.linalg.LinAlgError, ValueError):
        # Fallback auf Standard-Exponentialfunktion
        if xp_local is cp and hasattr(cp, 'linalg'):
            return cupy_expm(A)
        else:
            # Auf CPU zurückfallen
            A_cpu = cp.asnumpy(A) if xp_local is cp else A
            result = expm(A_cpu)
            return cp.asarray(result) if xp_local is cp else result