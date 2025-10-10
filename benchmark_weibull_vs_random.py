"""
Benchmark: Weibull vs Random Element Sampling
Direct comparison of the two sampling methods
"""

import time
import numpy as np
import random
import scipy.stats as stats

# Weibull method
class WeibullFitter:
    def __init__(self, throughput_data: np.ndarray):
        self.data = throughput_data
        self.shape, self.loc, self.scale = stats.weibull_min.fit(throughput_data, floc=0)
        self.mean = stats.weibull_min.mean(self.shape, scale=self.scale)
        self.std = stats.weibull_min.std(self.shape, scale=self.scale)

    def generate_sample(self) -> float:
        return stats.weibull_min.rvs(self.shape, scale=self.scale)

# Random element method
def random_integer(min_val: int, max_val: int) -> int:
    return random.randint(min_val, max_val)

def random_element(array):
    return array[random_integer(0, len(array) - 1)]

def benchmark_sampling_methods():
    print("="*80)
    print("BENCHMARK: Weibull vs Random Element Sampling")
    print("="*80)

    tp_samples = [5, 6, 7, 4, 8, 6, 5, 7, 6, 8, 5, 7]
    n_samples = 1_000_000

    print(f"\nThroughput samples: {tp_samples}")
    print(f"Number of samples to generate: {n_samples:,}")

    # Benchmark 1: Weibull fitting overhead
    print("\n" + "-"*80)
    print("1. WEIBULL FITTING (one-time cost)")
    print("-"*80)

    start = time.time()
    weibull_fitter = WeibullFitter(np.array(tp_samples))
    fit_time = time.time() - start

    print(f"   Fitting time: {fit_time*1000:.3f} ms")
    print(f"   Shape: {weibull_fitter.shape:.3f}")
    print(f"   Scale: {weibull_fitter.scale:.3f}")

    # Benchmark 2: Weibull sampling
    print("\n" + "-"*80)
    print("2. WEIBULL SAMPLING")
    print("-"*80)

    start = time.time()
    weibull_samples = [max(0, round(weibull_fitter.generate_sample())) for _ in range(n_samples)]
    weibull_time = time.time() - start

    print(f"   Time: {weibull_time:.3f} seconds")
    print(f"   Samples/sec: {n_samples/weibull_time:,.0f}")
    print(f"   Time per sample: {(weibull_time/n_samples)*1000000:.3f} µs")
    print(f"   Mean: {np.mean(weibull_samples):.2f}")
    print(f"   Std: {np.std(weibull_samples):.2f}")

    # Benchmark 3: Random element sampling
    print("\n" + "-"*80)
    print("3. RANDOM ELEMENT SAMPLING (old method)")
    print("-"*80)

    start = time.time()
    random_samples = [random_element(tp_samples) for _ in range(n_samples)]
    random_time = time.time() - start

    print(f"   Time: {random_time:.3f} seconds")
    print(f"   Samples/sec: {n_samples/random_time:,.0f}")
    print(f"   Time per sample: {(random_time/n_samples)*1000000:.3f} µs")
    print(f"   Mean: {np.mean(random_samples):.2f}")
    print(f"   Std: {np.std(random_samples):.2f}")

    # Comparison
    print("\n" + "="*80)
    print("PERFORMANCE COMPARISON")
    print("="*80)

    slowdown = (weibull_time / random_time - 1) * 100

    print(f"\nRandom Element: {random_time:.3f}s")
    print(f"Weibull:        {weibull_time:.3f}s")
    print(f"Slowdown:       {slowdown:+.1f}%")
    print(f"\nWeibull is {weibull_time/random_time:.2f}x slower than random_element")

    # Simulate realistic scenario
    print("\n" + "="*80)
    print("REALISTIC SIMULATION SCENARIO")
    print("="*80)

    n_simulations = 10_000
    avg_weeks = 9
    total_samples = n_simulations * avg_weeks

    print(f"\nScenario: {n_simulations:,} simulations × {avg_weeks} weeks avg")
    print(f"Total samples needed: {total_samples:,}")

    # Weibull overhead
    weibull_total = fit_time + (total_samples * (weibull_time / n_samples))
    random_total = total_samples * (random_time / n_samples)

    print(f"\nWeibull method:")
    print(f"  Fitting: {fit_time*1000:.3f} ms")
    print(f"  Sampling: {(weibull_total - fit_time):.3f}s")
    print(f"  Total: {weibull_total:.3f}s")

    print(f"\nRandom method:")
    print(f"  Total: {random_total:.3f}s")

    overhead = (weibull_total / random_total - 1) * 100
    print(f"\nOverhead: {overhead:+.1f}%")

    print("\n✓ Benchmark complete!")

if __name__ == "__main__":
    benchmark_sampling_methods()
