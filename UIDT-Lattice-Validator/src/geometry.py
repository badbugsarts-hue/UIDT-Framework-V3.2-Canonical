# src/geometry.py
import math

class UIDTGeometry:
    """
    Core class defining the geometric constants of the Unified Interactive Dynamic Theory.
    Based on the interaction of Torus geometry (Tesla 3-6-9) and Golden Ratio scaling.
    """
    def __init__(self):
        self.phi = (1 + math.sqrt(5)) / 2  # Golden Ratio
        self.pi = math.pi
        
        # The fundamental geometric scaling factor (Circle to Golden Rectangle)
        # Value: ~1.2009366
        self.geom_factor = self.pi / (self.phi**2)

    def calculate_gamma(self):
        """
        Derives the fundamental UIDT constant gamma.
        Origin: 
          - Torus Ratio (9/6 = 1.5)
          - Tesla Scaling (3^2 = 9)
          - Geometric Correction (pi/phi^2)
        
        Returns:
            float: Gamma (~16.339 in idealized theory, ~16.21 pure geometry)
        """
        torus_ratio = 9/6
        tesla_scale = 3**2
        
        gamma = torus_ratio * tesla_scale * self.geom_factor
        return gamma

    def get_beta_correction(self, beta_lattice_std=16.3):
        """
        Scales a standard Lattice QCD beta parameter to its geometric ideal.
        
        Args:
            beta_lattice_std (float): The standard operating point (e.g., from arXiv:2309.12270)
            
        Returns:
            float: The corrected beta value where geometric locking occurs.
        """
        return beta_lattice_std * self.geom_factor
