#!/usr/bin/env python3
"""
Test script for K-Fold Cross-Validation implementation
"""

import numpy as np
from ml_forecaster import MLForecaster

# Create sample throughput data (30 data points)
np.random.seed(42)
sample_data = np.random.poisson(lam=5, size=30) + np.random.normal(0, 1, 30)
sample_data = np.maximum(sample_data, 1)  # Ensure positive values

print("="*80)
print("TESTING K-FOLD CROSS-VALIDATION PROTOCOL")
print("="*80)
print(f"\nSample data: {len(sample_data)} throughput values")
print(f"Mean: {np.mean(sample_data):.2f}, Std: {np.std(sample_data):.2f}")
print(f"Data: {sample_data}")

# Initialize ML Forecaster with K-Fold CV parameters
forecaster = MLForecaster(
    max_lag=4,
    n_splits=5,       # 5-fold cross-validation
    validation_size=0.2  # 20% validation set
)

# Train models using K-Fold CV protocol
print("\n" + "="*80)
print("TRAINING MODELS WITH K-FOLD CV + GRID SEARCH")
print("="*80)

try:
    forecaster.train_models(sample_data, use_kfold_cv=True)

    print("\n" + "="*80)
    print("TRAINING RESULTS SUMMARY")
    print("="*80)

    for model_name, metrics in forecaster.results.items():
        print(f"\n{model_name}:")
        print(f"  Cross-Validation (5-fold):")
        print(f"    MAE:  {metrics['MAE']:.3f} ± {metrics['MAE_std']:.3f}")
        print(f"    RMSE: {metrics['RMSE']:.3f} ± {metrics['RMSE_std']:.3f}")
        print(f"    R²:   {metrics['R2_mean']:.3f} ± {metrics['R2_std']:.3f}")
        print(f"  Validation Set:")
        print(f"    MAE:  {metrics['val_MAE']:.3f}")
        print(f"    RMSE: {metrics['val_RMSE']:.3f}")
        print(f"    R²:   {metrics['val_R2']:.3f}")
        if metrics.get('best_params'):
            print(f"  Best Hyperparameters: {metrics['best_params']}")

    # Test forecasting
    print("\n" + "="*80)
    print("TESTING FORECASTING")
    print("="*80)

    forecasts = forecaster.forecast(sample_data, steps=4, model_name='ensemble')

    print(f"\nForecasts for next 4 periods:")
    for model_name, forecast in forecasts.items():
        print(f"  {model_name}: {forecast}")

    ensemble_stats = forecaster.get_ensemble_forecast(forecasts)
    print(f"\nEnsemble Statistics:")
    print(f"  Mean:   {ensemble_stats['mean']}")
    print(f"  Median: {ensemble_stats['median']}")
    print(f"  P10:    {ensemble_stats['p10']}")
    print(f"  P90:    {ensemble_stats['p90']}")

    print("\n" + "="*80)
    print("TEST COMPLETED SUCCESSFULLY!")
    print("="*80)

except Exception as e:
    print(f"\n{'='*80}")
    print(f"ERROR: {str(e)}")
    print(f"{'='*80}")
    import traceback
    traceback.print_exc()
