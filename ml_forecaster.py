"""
ML Forecaster Module
Implements Machine Learning models for throughput forecasting
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple, List, Optional
import warnings
from datetime import datetime, timedelta

# ML imports
from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor
from sklearn.model_selection import TimeSeriesSplit, RandomizedSearchCV, KFold, train_test_split, GridSearchCV
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.base import clone

try:
    from xgboost import XGBRegressor
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    warnings.warn("XGBoost not available. Install with: pip install xgboost")

warnings.filterwarnings('ignore')


class MLForecaster:
    """Machine Learning forecasting for throughput prediction"""

    def __init__(self, max_lag: int = 4, n_splits: int = 5, validation_size: float = 0.2):
        """
        Initialize ML Forecaster.

        Args:
            max_lag: Number of lag features to use
            n_splits: Number of K-folds for cross-validation (default: 5)
            validation_size: Proportion of data for validation set (default: 0.2 = 20%)
        """
        self.max_lag = max_lag
        self.n_splits = n_splits
        self.validation_size = validation_size
        self.models = {}
        self.results = {}
        self.cv_scores = {}
        self.trained = False

    def prepare_features(self, data: np.ndarray) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Prepare lagged features for ML models.

        Args:
            data: Historical throughput data

        Returns:
            X: Feature matrix with lags
            y: Target variable
        """
        df = pd.DataFrame({'y': data})

        # Create lag features
        for lag in range(1, self.max_lag + 1):
            df[f'lag_{lag}'] = df['y'].shift(lag)

        # Add rolling statistics
        df['rolling_mean_3'] = df['y'].shift(1).rolling(window=3).mean()
        df['rolling_std_3'] = df['y'].shift(1).rolling(window=3).std()

        # Remove NaN rows
        df_clean = df.dropna()

        if len(df_clean) < self.max_lag + 1:
            raise ValueError(f"Insufficient data after creating lags. Need: {self.max_lag + 1}, got: {len(df_clean)}")

        lag_cols = [f'lag_{i}' for i in range(1, self.max_lag + 1)]
        feature_cols = lag_cols + ['rolling_mean_3', 'rolling_std_3']

        X = df_clean[feature_cols]
        y = df_clean['y']

        return X, y

    def train_models(self, data: np.ndarray, use_kfold_cv: bool = True):
        """
        Train multiple ML models using K-Fold Cross-Validation protocol.

        Args:
            data: Historical throughput data
            use_kfold_cv: If True, use complete K-Fold CV protocol (default: True)
        """
        X, y = self.prepare_features(data)

        # Minimum data requirement: validation_size + n_splits for CV
        min_samples = max(self.n_splits + 2, int(1 / (1 - self.validation_size)) + self.n_splits)
        if len(X) < min_samples:
            raise ValueError(f"Insufficient data for K-Fold CV. Need at least {min_samples} samples, got {len(X)}.")

        print(f"\n{'='*60}")
        print(f"ML MODEL TRAINING - K-FOLD CROSS-VALIDATION PROTOCOL")
        print(f"{'='*60}")
        print(f"Total samples: {len(X)}")
        print(f"Training set: {int(len(X) * (1-self.validation_size))} samples (80%)")
        print(f"Validation set: {int(len(X) * self.validation_size)} samples (20%)")
        print(f"K-Folds: {self.n_splits}")
        print(f"{'='*60}\n")

        tscv = TimeSeriesSplit(n_splits=self.n_splits)

        # Model configurations
        models_config = {
            'RandomForest': RandomForestRegressor(
                n_estimators=100,
                max_depth=5,
                min_samples_split=2,
                random_state=42
            ),
            'HistGradient_Median': HistGradientBoostingRegressor(
                loss='squared_error',
                max_iter=100,
                max_depth=5,
                random_state=42
            ),
            'HistGradient_P10': HistGradientBoostingRegressor(
                loss='quantile',
                quantile=0.10,
                max_iter=100,
                max_depth=5,
                random_state=42
            ),
            'HistGradient_P90': HistGradientBoostingRegressor(
                loss='quantile',
                quantile=0.90,
                max_iter=100,
                max_depth=5,
                random_state=42
            )
        }

        # Add XGBoost if available
        if XGBOOST_AVAILABLE:
            models_config['XGBoost'] = XGBRegressor(
                objective='reg:squarederror',
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                random_state=42
            )

        # Train and evaluate each model
        for name, model in models_config.items():
            try:
                if use_kfold_cv:
                    # Use complete K-Fold CV protocol with Grid Search
                    cv_results, best_model = self._cross_validate_with_kfold(model, X, y, name)
                    self.cv_scores[name] = cv_results

                    # Train final model on ALL data (train + validation) with best hyperparameters
                    final_model = clone(best_model)
                    final_model.fit(X, y)

                    self.models[name] = final_model
                    self.results[name] = {
                        'MAE': cv_results['mae_mean'],
                        'RMSE': cv_results['rmse_mean'],
                        'MAE_percent': (cv_results['mae_mean'] / np.mean(data)) * 100,
                        'MAE_std': cv_results['mae_std'],
                        'RMSE_std': cv_results['rmse_std'],
                        'R2_mean': cv_results['r2_mean'],
                        'R2_std': cv_results['r2_std'],
                        'val_MAE': cv_results['val_mae'],
                        'val_RMSE': cv_results['val_rmse'],
                        'val_R2': cv_results['val_r2'],
                        'best_params': cv_results.get('best_params', None)
                    }
                else:
                    # Use simple time series CV (legacy)
                    mae, rmse = self._evaluate_model(model, X, y, tscv)
                    model.fit(X, y)

                    self.models[name] = model
                    self.results[name] = {
                        'MAE': mae,
                        'RMSE': rmse,
                        'MAE_percent': (mae / np.mean(data)) * 100
                    }
            except Exception as e:
                warnings.warn(f"Failed to train {name}: {str(e)}")

        self.trained = True
        print(f"\n{'='*60}")
        print(f"TRAINING COMPLETE - {len(self.models)} models trained successfully")
        print(f"{'='*60}\n")

    def _get_tuned_xgb(self, X: pd.DataFrame, y: pd.Series, tscv) -> XGBRegressor:
        """Train XGBoost with hyperparameter tuning."""
        param_grid = {
            'n_estimators': [50, 100],
            'max_depth': [3, 5],
            'learning_rate': [0.05, 0.1]
        }

        search = RandomizedSearchCV(
            XGBRegressor(objective='reg:squarederror', random_state=42),
            param_grid,
            n_iter=5,
            cv=tscv,
            scoring='neg_mean_absolute_error',
            n_jobs=-1,
            random_state=42
        )
        search.fit(X, y)
        return search.best_estimator_

    def _evaluate_model(self, model, X: pd.DataFrame, y: pd.Series, tscv) -> Tuple[float, float]:
        """Evaluate model using time series cross-validation."""
        maes, rmses = [], []

        for train_idx, test_idx in tscv.split(X):
            X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
            y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)

            maes.append(mean_absolute_error(y_test, y_pred))
            rmses.append(np.sqrt(mean_squared_error(y_test, y_pred)))

        return np.mean(maes), np.mean(rmses)

    def _get_param_grid(self, model_name: str) -> Dict:
        """Get hyperparameter grid for each model type."""
        if 'RandomForest' in model_name:
            return {
                'n_estimators': [50, 100, 150],
                'max_depth': [3, 5, 7],
                'min_samples_split': [2, 5]
            }
        elif 'XGBoost' in model_name:
            return {
                'n_estimators': [50, 100, 150],
                'max_depth': [3, 5, 7],
                'learning_rate': [0.01, 0.05, 0.1]
            }
        elif 'HistGradient' in model_name:
            return {
                'max_iter': [50, 100, 150],
                'max_depth': [3, 5, 7],
                'learning_rate': [0.01, 0.05, 0.1]
            }
        else:
            return {}

    def _cross_validate_with_kfold(self, model, X: pd.DataFrame, y: pd.Series,
                                    model_name: str) -> Tuple[Dict[str, float], any]:
        """
        Perform K-Fold Cross-Validation following the complete protocol:
        1. Split data into 80% training + 20% validation
        2. Apply Grid Search on validation set for hyperparameter tuning
        3. Apply K-Fold CV on the 80% training set with best hyperparameters
        4. Calculate mean and std of metrics across folds

        Args:
            model: ML model to evaluate
            X: Feature matrix
            y: Target variable
            model_name: Name of the model for logging

        Returns:
            Tuple of (cv_results dict, best_model)
        """
        # Step 1: Split into training (80%) and validation (20%)
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=self.validation_size, random_state=42, shuffle=False
        )

        print(f"\n{model_name} - K-Fold Cross-Validation ({self.n_splits} folds):")
        print("=" * 60)

        # Step 2: Grid Search for hyperparameter tuning using validation set
        param_grid = self._get_param_grid(model_name)
        best_model = model
        best_params = None

        if param_grid:
            print(f"\nPerforming Grid Search for hyperparameter tuning...")
            print(f"Parameter grid: {param_grid}")

            try:
                # Use K-Fold on training set for Grid Search
                kfold_gs = KFold(n_splits=min(3, self.n_splits), shuffle=True, random_state=42)

                grid_search = GridSearchCV(
                    estimator=model,
                    param_grid=param_grid,
                    cv=kfold_gs,
                    scoring='neg_mean_absolute_error',
                    n_jobs=-1,
                    verbose=0
                )

                grid_search.fit(X_train, y_train)
                best_model = grid_search.best_estimator_
                best_params = grid_search.best_params_

                # Evaluate on validation set
                y_val_pred_gs = best_model.predict(X_val)
                val_mae_gs = mean_absolute_error(y_val, y_val_pred_gs)

                print(f"Best hyperparameters: {best_params}")
                print(f"Best CV score (MAE): {-grid_search.best_score_:.3f}")
                print(f"Validation set MAE: {val_mae_gs:.3f}")
            except Exception as e:
                print(f"Grid Search failed: {str(e)}")
                print(f"Using default hyperparameters")
                best_model = model
                best_params = None
        else:
            print(f"\nNo parameter grid defined for {model_name}, using default hyperparameters")

        # Step 3: K-Fold Cross-Validation on training set (80%) with best model
        kfold = KFold(n_splits=self.n_splits, shuffle=True, random_state=42)

        fold_maes = []
        fold_rmses = []
        fold_r2s = []

        print(f"\nK-Fold Cross-Validation Results:")
        print("-" * 60)

        for fold_num, (train_idx, test_idx) in enumerate(kfold.split(X_train), 1):
            # Get fold data
            X_fold_train = X_train.iloc[train_idx]
            X_fold_test = X_train.iloc[test_idx]
            y_fold_train = y_train.iloc[train_idx]
            y_fold_test = y_train.iloc[test_idx]

            # Train model on this fold with best hyperparameters
            # Clone the best_model to avoid modifying the original
            fold_model = clone(best_model)
            fold_model.fit(X_fold_train, y_fold_train)
            y_pred = fold_model.predict(X_fold_test)

            # Calculate metrics
            mae = mean_absolute_error(y_fold_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_fold_test, y_pred))
            r2 = r2_score(y_fold_test, y_pred)

            fold_maes.append(mae)
            fold_rmses.append(rmse)
            fold_r2s.append(r2)

            print(f"Fold {fold_num}: MAE={mae:.3f}, RMSE={rmse:.3f}, R²={r2:.3f}")

        # Step 4: Calculate mean and std across folds
        cv_results = {
            'mae_mean': np.mean(fold_maes),
            'mae_std': np.std(fold_maes),
            'rmse_mean': np.mean(fold_rmses),
            'rmse_std': np.std(fold_rmses),
            'r2_mean': np.mean(fold_r2s),
            'r2_std': np.std(fold_r2s),
            'folds': self.n_splits,
            'best_params': best_params
        }

        print(f"\nCross-Validation Summary:")
        print(f"  MAE:  {cv_results['mae_mean']:.3f} ± {cv_results['mae_std']:.3f}")
        print(f"  RMSE: {cv_results['rmse_mean']:.3f} ± {cv_results['rmse_std']:.3f}")
        print(f"  R²:   {cv_results['r2_mean']:.3f} ± {cv_results['r2_std']:.3f}")

        # Step 5: Train final model on full training set and evaluate on validation set
        best_model.fit(X_train, y_train)
        y_val_pred = best_model.predict(X_val)

        val_mae = mean_absolute_error(y_val, y_val_pred)
        val_rmse = np.sqrt(mean_squared_error(y_val, y_val_pred))
        val_r2 = r2_score(y_val, y_val_pred)

        cv_results['val_mae'] = val_mae
        cv_results['val_rmse'] = val_rmse
        cv_results['val_r2'] = val_r2

        print(f"\nFinal Validation Set Performance:")
        print(f"  MAE:  {val_mae:.3f}")
        print(f"  RMSE: {val_rmse:.3f}")
        print(f"  R²:   {val_r2:.3f}")
        print("=" * 60)

        return cv_results, best_model

    def forecast(self, data: np.ndarray, steps: int = 4,
                 model_name: str = 'RandomForest') -> Dict[str, np.ndarray]:
        """
        Generate forecasts for future periods.

        Args:
            data: Historical throughput data
            steps: Number of periods to forecast
            model_name: Name of model to use (or 'ensemble' for all models)

        Returns:
            Dictionary with forecasts from each model
        """
        if not self.trained:
            self.train_models(data)

        forecasts = {}
        last_values = data[-self.max_lag - 3:]  # Include rolling window data

        if model_name == 'ensemble':
            # Get forecasts from all models
            for name in self.models.keys():
                forecasts[name] = self._forecast_recursive(name, last_values, steps)
        else:
            # Get forecast from specific model
            if model_name not in self.models:
                raise ValueError(f"Model {model_name} not found. Available: {list(self.models.keys())}")
            forecasts[model_name] = self._forecast_recursive(model_name, last_values, steps)

        return forecasts

    def _forecast_recursive(self, model_name: str, last_values: np.ndarray, steps: int) -> np.ndarray:
        """Make recursive multi-step forecast."""
        model = self.models[model_name]
        predictions = []
        history = list(last_values)

        for _ in range(steps):
            # Prepare features
            recent = np.array(history[-self.max_lag:])
            rolling_mean = np.mean(history[-(self.max_lag+2):-1])
            rolling_std = np.std(history[-(self.max_lag+2):-1])

            features = list(recent) + [rolling_mean, rolling_std]
            X_step = pd.DataFrame([features], columns=[
                *[f'lag_{i}' for i in range(1, self.max_lag + 1)],
                'rolling_mean_3', 'rolling_std_3'
            ])

            # Make prediction
            pred = model.predict(X_step)[0]
            pred = max(0, pred)  # Ensure non-negative
            predictions.append(pred)
            history.append(pred)

        return np.array(predictions)

    def get_ensemble_forecast(self, forecasts: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        """
        Calculate ensemble statistics from multiple model forecasts.

        Args:
            forecasts: Dictionary of forecasts from different models

        Returns:
            Dictionary with ensemble statistics
        """
        all_forecasts = np.array(list(forecasts.values()))

        return {
            'mean': np.mean(all_forecasts, axis=0),
            'median': np.median(all_forecasts, axis=0),
            'p10': np.percentile(all_forecasts, 10, axis=0),
            'p25': np.percentile(all_forecasts, 25, axis=0),
            'p75': np.percentile(all_forecasts, 75, axis=0),
            'p90': np.percentile(all_forecasts, 90, axis=0),
            'std': np.std(all_forecasts, axis=0)
        }

    def get_results_summary(self) -> List[Dict]:
        """Get summary of model training results with K-Fold CV metrics."""
        if not self.trained:
            return []

        results_list = []
        for model_name, metrics in self.results.items():
            result = {
                'model': model_name,
                'mae': round(metrics['MAE'], 2),
                'rmse': round(metrics['RMSE'], 2),
                'mae_percent': round(metrics['MAE_percent'], 1)
            }

            # Add K-Fold CV metrics if available
            if 'MAE_std' in metrics:
                result['mae_std'] = round(metrics['MAE_std'], 2)
                result['rmse_std'] = round(metrics['RMSE_std'], 2)
                result['r2_mean'] = round(metrics['R2_mean'], 3)
                result['r2_std'] = round(metrics['R2_std'], 3)
                result['val_mae'] = round(metrics['val_MAE'], 2)
                result['val_rmse'] = round(metrics['val_RMSE'], 2)
                result['val_r2'] = round(metrics['val_R2'], 3)

            # Add best hyperparameters if available
            if metrics.get('best_params'):
                result['best_params'] = metrics['best_params']

            results_list.append(result)

        return sorted(results_list, key=lambda x: x['mae'])

    def walk_forward_validation(self, data: np.ndarray, forecast_steps: int = 4,
                                test_size: float = 0.2) -> Dict:
        """
        Perform walk-forward validation using the last 20% of data.

        Args:
            data: Historical throughput data
            forecast_steps: Number of steps to forecast ahead (from UI parameter)
            test_size: Proportion of data to use for testing (default: 0.2 = 20%)

        Returns:
            Dictionary with walk-forward validation results per model
        """
        if not self.trained:
            raise ValueError("Models must be trained before performing walk-forward validation")

        # Calculate split point (use last 20% for testing)
        n_samples = len(data)
        n_test = max(forecast_steps, int(n_samples * test_size))
        n_train = n_samples - n_test

        if n_train < self.max_lag + 3:
            raise ValueError(f"Insufficient training data. Need at least {self.max_lag + 3} samples for training.")

        print(f"\n{'='*60}")
        print(f"WALK-FORWARD VALIDATION")
        print(f"{'='*60}")
        print(f"Total samples: {n_samples}")
        print(f"Training samples: {n_train} (80%)")
        print(f"Test samples: {n_test} (20%)")
        print(f"Forecast steps: {forecast_steps}")
        print(f"{'='*60}\n")

        wf_results = {}

        # Perform walk-forward for each model
        for model_name in self.models.keys():
            print(f"\n{model_name} - Walk-Forward Validation:")
            print("-" * 60)

            predictions = []
            actuals = []
            forecast_origins = []

            # Walk forward through the test set
            for i in range(n_train, n_samples, forecast_steps):
                # Use data up to current point for training
                train_data = data[:i]

                # Determine how many steps we can actually forecast
                remaining_samples = n_samples - i
                steps_to_forecast = min(forecast_steps, remaining_samples)

                if steps_to_forecast == 0:
                    break

                # Get actual values for this forecast window
                actual_values = data[i:i + steps_to_forecast]

                # Make forecast
                try:
                    last_values = train_data[-self.max_lag - 3:]
                    forecast = self._forecast_recursive(model_name, last_values, steps_to_forecast)

                    predictions.extend(forecast)
                    actuals.extend(actual_values)
                    forecast_origins.append(i)

                    print(f"Origin {i}: Forecasted {steps_to_forecast} steps - MAE: {mean_absolute_error([actual_values], [forecast[:steps_to_forecast]]):.3f}")

                except Exception as e:
                    print(f"Warning: Forecast failed at origin {i}: {str(e)}")
                    continue

            # Calculate metrics for this model
            if len(predictions) > 0 and len(actuals) > 0:
                predictions = np.array(predictions)
                actuals = np.array(actuals)

                mae = mean_absolute_error(actuals, predictions)
                rmse = np.sqrt(mean_squared_error(actuals, predictions))
                r2 = r2_score(actuals, predictions)
                mape = np.mean(np.abs((actuals - predictions) / np.maximum(actuals, 0.1))) * 100  # Avoid division by zero

                wf_results[model_name] = {
                    'predictions': predictions.tolist(),
                    'actuals': actuals.tolist(),
                    'forecast_origins': forecast_origins,
                    'mae': mae,
                    'rmse': rmse,
                    'r2': r2,
                    'mape': mape,
                    'n_forecasts': len(forecast_origins),
                    'n_points': len(predictions)
                }

                print(f"\nSummary Statistics:")
                print(f"  MAE:  {mae:.3f}")
                print(f"  RMSE: {rmse:.3f}")
                print(f"  R²:   {r2:.3f}")
                print(f"  MAPE: {mape:.2f}%")
                print(f"  Number of forecast origins: {len(forecast_origins)}")
                print(f"  Total predicted points: {len(predictions)}")
            else:
                print(f"Warning: No valid predictions for {model_name}")
                wf_results[model_name] = {
                    'error': 'No valid predictions generated',
                    'predictions': [],
                    'actuals': [],
                    'forecast_origins': [],
                    'mae': None,
                    'rmse': None,
                    'r2': None,
                    'mape': None,
                    'n_forecasts': 0,
                    'n_points': 0
                }

        print(f"\n{'='*60}")
        print(f"WALK-FORWARD VALIDATION COMPLETE")
        print(f"{'='*60}\n")

        return wf_results

    def assess_forecast_risk(self, data: np.ndarray) -> Dict:
        """
        Assess risk of using ML forecasts based on data characteristics.

        Returns:
            Dictionary with risk assessment
        """
        # Analyze recent trends
        recent_window = min(8, len(data) // 2)
        recent_mean = np.mean(data[-recent_window:])
        overall_mean = np.mean(data)

        # Calculate volatility
        cv = np.std(data) / np.mean(data) if np.mean(data) > 0 else 0

        # Check for outliers
        q75, q25 = np.percentile(data, [75, 25])
        iqr = q75 - q25
        outliers = np.sum(np.abs(data - np.median(data)) > 1.5 * iqr)

        # Risk factors
        high_volatility = cv > 0.5
        strong_trend = abs(recent_mean / overall_mean - 1) > 0.3
        many_outliers = outliers > len(data) * 0.15

        risk_count = sum([high_volatility, strong_trend, many_outliers])

        return {
            'risk_level': 'HIGH' if risk_count >= 2 else 'MEDIUM' if risk_count == 1 else 'LOW',
            'volatility_cv': round(cv, 2),
            'trend_deviation_pct': round((recent_mean / overall_mean - 1) * 100, 1),
            'outlier_pct': round((outliers / len(data)) * 100, 1),
            'recommend_monte_carlo': risk_count >= 2,
            'warning': 'High uncertainty detected - consider Monte Carlo simulation' if risk_count >= 2 else None
        }
