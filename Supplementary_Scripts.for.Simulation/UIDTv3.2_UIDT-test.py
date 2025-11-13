#!/usr/bin/env python3
"""
Test suite for UIDT v3.2 verification
"""

import pytest
import numpy as np
from uidt_verification import UIDTScientificVerification

class TestUIDTVerification:
    
    def setup_method(self):
        self.verifier = UIDTScientificVerification()
    
    def test_canonical_parameters_exist(self):
        """Test that canonical parameters are defined"""
        params = self.verifier.canonical_params
        assert 'm_S' in params
        assert 'kappa' in params
        assert 'lambda_S' in params
        assert 'gamma' in params
    
    def test_parameters_physical(self):
        """Test that parameters are physically reasonable"""
        params = self.verifier.canonical_params
        
        # Mass positive
        assert params['m_S'] > 0
        
        # Couplings in reasonable range
        assert 0 < params['kappa'] < 2
        assert 0 < params['lambda_S'] < 1
        
        # Gamma positive
        assert params['gamma'] > 0
    
    def test_vacuum_equation_verification(self):
        """Test vacuum equation verification"""
        result = self.verifier._verify_vacuum_equation()
        
        assert 'residual' in result
        assert 'score' in result
        assert 'status' in result
        
        # Residual should be very small
        assert result['residual'] < 1e-10
    
    def test_mass_gap_equation_verification(self):
        """Test mass gap equation verification"""
        result = self.verifier._verify_mass_gap_equation()
        
        assert 'deviation' in result
        assert 'score' in result
        assert 'status' in result
        
        # Deviation should be small
        assert result['deviation'] < 0.01
    
    def test_rg_fixed_point_verification(self):
        """Test RG fixed point verification"""
        result = self.verifier._verify_rg_fixed_point()
        
        assert 'residual' in result
        assert 'score' in result
        assert 'status' in result
        
        # Residual should be small
        assert result['residual'] < 0.01
    
    def test_complete_verification(self):
        """Test complete verification routine"""
        results = self.verifier.verify_canonical_solution()
        
        required_keys = ['vacuum', 'mass_gap', 'rg_fixed_point', 'derived', 'physics', 'overall_consistency']
        for key in required_keys:
            assert key in results
        
        # Overall consistency should be high
        assert results['overall_consistency']['overall_score'] > 0.9
    
    def test_empirical_predictions(self):
        """Test empirical predictions generation"""
        predictions = self.verifier.generate_empirical_predictions()
        
        assert 'glueball_spectrum' in predictions
        assert 'scalar_decays' in predictions
        assert 'phase_transition' in predictions
        
        # Should have specific glueball states
        spectrum = predictions['glueball_spectrum']['spectrum']
        expected_states = ['0++', '2++', '0-+', '1+-', '2-+']
        for state in expected_states:
            assert state in spectrum

if __name__ == "__main__":
    pytest.main([__file__, "-v"])