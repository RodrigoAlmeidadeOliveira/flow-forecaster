"""
Test suite for Cost of Delay (CoD) Forecaster
"""

import numpy as np
import pandas as pd
from cod_forecaster import CoDForecaster, generate_sample_cod_data


def test_sample_data_generation():
    """Test synthetic data generation."""
    print("\n" + "="*60)
    print("TEST 1: Sample Data Generation")
    print("="*60)

    df = generate_sample_cod_data(n_samples=50)

    assert len(df) == 50, "Should generate 50 samples"
    assert 'cod_weekly' in df.columns, "Should have cod_weekly column"
    assert all(df['cod_weekly'] > 0), "All CoD values should be positive"

    print(f"✓ Generated {len(df)} samples")
    print(f"✓ CoD range: R$ {df['cod_weekly'].min():,.2f} - R$ {df['cod_weekly'].max():,.2f}/week")
    print("\nSample data (first 5 rows):")
    print(df[['budget_millions', 'duration_weeks', 'team_size', 'business_value', 'cod_weekly']].head())


def test_cod_training():
    """Test CoD model training."""
    print("\n" + "="*60)
    print("TEST 2: CoD Model Training")
    print("="*60)

    # Generate training data
    df = generate_sample_cod_data(n_samples=100)

    # Initialize and train
    forecaster = CoDForecaster(n_splits=3)
    forecaster.train_models(df)

    assert forecaster.trained, "Model should be trained"
    assert len(forecaster.models) > 0, "Should have trained models"
    assert 'RandomForest' in forecaster.models, "Should have RandomForest model"

    print("\n✓ Models trained successfully")
    print(f"✓ Number of models: {len(forecaster.models)}")
    print(f"✓ Feature count: {len(forecaster.feature_names)}")


def test_cod_prediction():
    """Test CoD prediction."""
    print("\n" + "="*60)
    print("TEST 3: CoD Prediction")
    print("="*60)

    # Generate training data
    df = generate_sample_cod_data(n_samples=100)

    # Train model
    forecaster = CoDForecaster(n_splits=3)
    forecaster.train_models(df)

    # Test project
    test_project = {
        'budget_millions': 5.0,
        'duration_weeks': 26,
        'team_size': 10,
        'num_stakeholders': 8,
        'business_value': 75,
        'complexity': 4,
        'risk_level': 3,
        'project_type': 'ERP'
    }

    # Predict
    result = forecaster.predict_cod(test_project)

    assert 'cod_weekly' in result, "Should have cod_weekly prediction"
    assert result['cod_weekly'] > 0, "CoD should be positive"
    assert 'cod_daily' in result, "Should have daily CoD"
    assert 'cod_monthly' in result, "Should have monthly CoD"
    assert 'confidence_interval_95' in result, "Should have confidence interval"

    print("\n✓ Prediction successful")
    print(f"\nTest Project:")
    print(f"  Budget: R$ {test_project['budget_millions']} milhões")
    print(f"  Duration: {test_project['duration_weeks']} weeks")
    print(f"  Team: {test_project['team_size']} people")
    print(f"  Business Value: {test_project['business_value']}")
    print(f"  Complexity: {test_project['complexity']}/5")

    print(f"\nPredicted CoD:")
    print(f"  Weekly:  R$ {result['cod_weekly']:,.2f}")
    print(f"  Daily:   R$ {result['cod_daily']:,.2f}")
    print(f"  Monthly: R$ {result['cod_monthly']:,.2f}")
    print(f"  95% CI:  R$ {result['confidence_interval_95'][0]:,.2f} - R$ {result['confidence_interval_95'][1]:,.2f}")


def test_total_cod_calculation():
    """Test total CoD calculation."""
    print("\n" + "="*60)
    print("TEST 4: Total CoD Calculation")
    print("="*60)

    forecaster = CoDForecaster()

    cod_weekly = 50_000.0  # R$ 50k per week
    delay_weeks = 8  # 8 weeks delayed

    result = forecaster.calculate_total_cod(cod_weekly, delay_weeks)

    expected_total = cod_weekly * delay_weeks
    assert result['total_cod'] == expected_total, "Total CoD calculation incorrect"

    print(f"\n✓ Total CoD calculation verified")
    print(f"  Weekly CoD: R$ {cod_weekly:,.2f}")
    print(f"  Delay: {delay_weeks} weeks")
    print(f"  Total CoD: {result['total_cod_formatted']}")


def test_feature_importance():
    """Test feature importance extraction."""
    print("\n" + "="*60)
    print("TEST 5: Feature Importance")
    print("="*60)

    # Generate training data
    df = generate_sample_cod_data(n_samples=100)

    # Train model
    forecaster = CoDForecaster(n_splits=3)
    forecaster.train_models(df)

    # Get feature importance
    importance_df = forecaster.get_feature_importance()

    assert importance_df is not None, "Should return feature importance"
    assert len(importance_df) > 0, "Should have features"
    assert 'feature' in importance_df.columns, "Should have feature column"
    assert 'importance' in importance_df.columns, "Should have importance column"

    print("\n✓ Feature importance extracted successfully")
    print("\nTop 10 Most Important Features:")
    print(importance_df.head(10).to_string(index=False))


def test_model_metrics():
    """Test model performance metrics."""
    print("\n" + "="*60)
    print("TEST 6: Model Performance Metrics")
    print("="*60)

    # Generate training data
    df = generate_sample_cod_data(n_samples=100)

    # Train model
    forecaster = CoDForecaster(n_splits=3)
    forecaster.train_models(df)

    print("\n✓ Model Metrics:")
    for model_name, model_data in forecaster.models.items():
        print(f"\n{model_name}:")
        print(f"  MAE:  R$ {model_data['mae']:,.2f}/week")
        print(f"  RMSE: R$ {model_data['rmse']:,.2f}/week")
        print(f"  R²:   {model_data['r2']:.3f}")
        print(f"  MAPE: {model_data['mape']:.1f}%")


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*60)
    print("COST OF DELAY (CoD) FORECASTER - TEST SUITE")
    print("="*60)

    try:
        test_sample_data_generation()
        test_cod_training()
        test_cod_prediction()
        test_total_cod_calculation()
        test_feature_importance()
        test_model_metrics()

        print("\n" + "="*60)
        print("ALL TESTS PASSED ✓")
        print("="*60 + "\n")

        return True

    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = run_all_tests()
    exit(0 if success else 1)
