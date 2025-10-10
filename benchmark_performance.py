"""
Performance Benchmark - Weibull vs Random Element Sampling
"""

import time
import sys
sys.path.insert(0, '.')

from monte_carlo_unified import run_unified_simulation
import numpy as np

def benchmark_simulation(mode, n_simulations, description):
    """Benchmark a simulation mode"""

    tp_samples = [5, 6, 7, 4, 8, 6, 5, 7, 6, 8, 5, 7]
    backlog = 50

    print(f"\n{'='*80}")
    print(f"BENCHMARK: {description}")
    print(f"{'='*80}")
    print(f"Mode: {mode}")
    print(f"Simulations: {n_simulations:,}")
    print(f"Backlog: {backlog}")

    start_time = time.time()

    if mode == 'complete':
        result = run_unified_simulation(
            tp_samples=tp_samples,
            backlog=backlog,
            n_simulations=n_simulations,
            mode=mode,
            team_size=10,
            min_contributors=2,
            max_contributors=5,
            s_curve_size=20
        )
    else:
        result = run_unified_simulation(
            tp_samples=tp_samples,
            backlog=backlog,
            n_simulations=n_simulations,
            mode=mode
        )

    end_time = time.time()
    elapsed = end_time - start_time

    print(f"\nResults:")
    print(f"  P50: {result['percentile_stats']['p50']} weeks")
    print(f"  P85: {result['percentile_stats']['p85']} weeks")
    print(f"  Execution Time: {elapsed:.3f} seconds")
    print(f"  Simulations/second: {n_simulations/elapsed:,.0f}")
    print(f"  Time per simulation: {(elapsed/n_simulations)*1000:.3f} ms")

    return elapsed, result

def main():
    print("\n" + "="*80)
    print("PERFORMANCE BENCHMARK - Monte Carlo Simulation")
    print("="*80)

    # Test different simulation sizes
    test_configs = [
        ('simple', 1000, 'Simple Mode - 1K simulations'),
        ('simple', 10000, 'Simple Mode - 10K simulations'),
        ('simple', 100000, 'Simple Mode - 100K simulations'),
        ('complete', 1000, 'Complete Mode - 1K simulations'),
        ('complete', 10000, 'Complete Mode - 10K simulations'),
        ('complete', 100000, 'Complete Mode - 100K simulations'),
    ]

    results = {}

    for mode, n_sims, desc in test_configs:
        elapsed, result = benchmark_simulation(mode, n_sims, desc)
        results[desc] = {
            'elapsed': elapsed,
            'sims_per_sec': n_sims / elapsed,
            'mode': mode,
            'n_sims': n_sims
        }

    # Summary
    print("\n" + "="*80)
    print("PERFORMANCE SUMMARY")
    print("="*80)
    print(f"\n{'Description':<45} {'Time (s)':<12} {'Sims/sec':<15}")
    print("-"*80)

    for desc, data in results.items():
        print(f"{desc:<45} {data['elapsed']:>8.3f}s    {data['sims_per_sec']:>10,.0f}")

    # Performance analysis
    print("\n" + "="*80)
    print("PERFORMANCE ANALYSIS")
    print("="*80)

    simple_10k = results['Simple Mode - 10K simulations']
    complete_10k = results['Complete Mode - 10K simulations']

    print(f"\nSimple Mode (10K):")
    print(f"  Time: {simple_10k['elapsed']:.3f}s")
    print(f"  Rate: {simple_10k['sims_per_sec']:,.0f} sims/sec")

    print(f"\nComplete Mode (10K):")
    print(f"  Time: {complete_10k['elapsed']:.3f}s")
    print(f"  Rate: {complete_10k['sims_per_sec']:,.0f} sims/sec")

    overhead = (complete_10k['elapsed'] / simple_10k['elapsed'] - 1) * 100
    print(f"\nComplete Mode Overhead: {overhead:.1f}%")

    # Check if Weibull is the bottleneck
    print("\n" + "="*80)
    print("POTENTIAL BOTTLENECK ANALYSIS")
    print("="*80)
    print("\nWeibull distribution fitting happens once per simulation run.")
    print("Sample generation happens once per week in the simulation.")
    print("\nFor 100K simulations with ~9 weeks average:")
    print(f"  Estimated Weibull samples needed: ~900,000")
    print(f"  Actual time for 100K sims (simple): {results['Simple Mode - 100K simulations']['elapsed']:.3f}s")

    print("\n✓ Benchmark complete!")

if __name__ == "__main__":
    main()
