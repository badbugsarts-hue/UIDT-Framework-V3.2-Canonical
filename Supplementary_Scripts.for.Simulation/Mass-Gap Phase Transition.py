import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import quad

# ==============================================================================
# SETTINGS & CONSTANTS
# ==============================================================================
plt.style.use('default') # White background
G = 1.0

# ==============================================================================
# PART 2: COSMOLOGY (Mass-Gap Phase Transition)
# ==============================================================================

def scale_factor_uidt_transition(t, t_gap, sharpness):
    """
    UIDT Cosmology: Massless 'Loitering' phase -> Phase Transition -> Expansion
    """
    a_condensate = 0.02 # Non-zero minimal size (Planck scale proxy)
    
    # Sigmoid transition
    transition = 1 / (1 + np.exp(-sharpness * (t - t_gap)))
    
    # Linear expansion after transition
    a_expansion = (t - t_gap) * 0.15 * transition
    
    return a_condensate + a_expansion + (transition * 0.05)

def wrapper_integrand(t, model_func, extra_args):
    val = model_func(t, *extra_args)
    return 1.0 / val if val > 1e-9 else 0

def calculate_horizon(time_array, model_func, *args):
    horizons = []
    for t_end in time_array:
        if t_end <= 0.01:
            horizons.append(0)
            continue
        # Pass the function and its arguments correctly to quad
        val, err = quad(wrapper_integrand, 1e-5, t_end, args=(model_func, args))
        horizons.append(val)
    return np.array(horizons)

# --- Simulation Part 2 ---
time = np.linspace(0, 10, 500) 
t_mass_gap = 2.5   
sharpness = 5.0    

# Standard Model (Simple Sqrt expansion)
a_std = np.sqrt(time) 
h_std = calculate_horizon(time, lambda t, x: np.sqrt(t), 0)

# UIDT Model
a_uidt = scale_factor_uidt_transition(time, t_mass_gap, sharpness)
h_uidt = calculate_horizon(time, scale_factor_uidt_transition, t_mass_gap, sharpness)

# Plotting ONLY Part 2
fig2, (ax2a, ax2b) = plt.subplots(2, 1, figsize=(10, 10), sharex=True)

# 2a: Expansion History
ax2a.plot(time, a_std, 'r--', label='Standard Big Bang')
ax2a.plot(time, a_uidt, color='#0066cc', linewidth=3, label='UIDT (Mass-Gap Transition)')
ax2a.axvline(t_mass_gap, color='orange', linestyle='--', label=f'Phase Transition ($t_{{gap}}$)')

ax2a.text(t_mass_gap - 1.2, 0.5, "Phase I:\nMassless\nInfo-Condensate", color='#0066cc', ha='center')
ax2a.text(t_mass_gap + 1.2, 0.5, "Phase II:\nMass Generated\nMatter Dominant", color='black', ha='center')

ax2a.set_ylabel("Scale Factor a(t)")
ax2a.set_title("Part 2: UIDT Cosmology - Solving the Horizon Problem", fontsize=14)
ax2a.legend(loc='upper left')
ax2a.grid(True, alpha=0.3)

# 2b: Causal Horizon
t_cmb = 8.0
ax2b.plot(time, h_std, 'r--', label='Standard Horizon (Disconnected)')
ax2b.plot(time, h_uidt, color='#0066cc', linewidth=2, label='UIDT Horizon (Connected)')
ax2b.axvline(t_cmb, color='green', linestyle=':', label='CMB Emission')
ax2b.plot(time, a_uidt * 3, 'g:', alpha=0.4, label='Observable Universe Size')

# Arrow annotation
idx_cmb = np.argmin(np.abs(time - t_cmb))
horizon_val = h_uidt[idx_cmb]
ax2b.annotate('Fully Connected!\n(Thermal Equilibrium)', 
             xy=(t_cmb, horizon_val), xytext=(t_cmb-5, horizon_val),
             arrowprops=dict(facecolor='#0066cc', shrink=0.05), 
             color='#0066cc', fontsize=12, fontweight='bold')

ax2b.set_xlabel("Time (Arbitrary Units)")
ax2b.set_ylabel("Causal Horizon Distance")
ax2b.legend(loc='upper left')
ax2b.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()
