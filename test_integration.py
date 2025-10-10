"""
Integration test for unified Monte Carlo simulation
"""

import sys
sys.path.insert(0, '.')

from monte_carlo_unified import run_unified_simulation

def test_all_modes():
    """Test all three simulation modes"""

    tp_samples = [5, 6, 7, 4, 8, 6, 5, 7, 6, 8, 5, 7]
    backlog = 50

    print("=" * 80)
    print("INTEGRATION TEST - Unified Monte Carlo Simulation")
    print("=" * 80)

    # Test 1: Simple mode
    print("\n✓ Testing SIMPLE mode...")
    try:
        result = run_unified_simulation(
            tp_samples=tp_samples,
            backlog=backlog,
            n_simulations=1000,
            mode='simple'
        )
        print(f"  P85: {result['percentile_stats']['p85']:.1f} weeks")
        print("  ✓ SIMPLE mode: PASSED")
    except Exception as e:
        print(f"  ✗ SIMPLE mode: FAILED - {e}")
        return False

    # Test 2: Weibull mode
    print("\n✓ Testing WEIBULL mode...")
    try:
        result = run_unified_simulation(
            tp_samples=tp_samples,
            backlog=backlog,
            n_simulations=1000,
            mode='weibull'
        )
        print(f"  P85: {result['percentile_stats']['p85']:.1f} weeks")
        print("  ✓ WEIBULL mode: PASSED")
    except Exception as e:
        print(f"  ✗ WEIBULL mode: FAILED - {e}")
        return False

    # Test 3: Complete mode
    print("\n✓ Testing COMPLETE mode...")
    try:
        result = run_unified_simulation(
            tp_samples=tp_samples,
            backlog=backlog,
            n_simulations=1000,
            mode='complete',
            team_size=10,
            min_contributors=2,
            max_contributors=5,
            s_curve_size=20
        )
        p85_entry = [r for r in result['resultsTable'] if r['Likelihood'] == 85][0]
        print(f"  P85 Duration: {p85_entry['Duration']} weeks")
        print(f"  P85 Effort: {p85_entry['Effort']} person-weeks")
        print("  ✓ COMPLETE mode: PASSED")
    except Exception as e:
        print(f"  ✗ COMPLETE mode: FAILED - {e}")
        return False

    print("\n" + "=" * 80)
    print("✓ ALL TESTS PASSED - Integration successful!")
    print("=" * 80)
    return True

if __name__ == "__main__":
    success = test_all_modes()
    sys.exit(0 if success else 1)
