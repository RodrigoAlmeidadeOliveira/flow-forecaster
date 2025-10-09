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
from sklearn.model_selection import TimeSeriesSplit, RandomizedSearchCV
from sklearn.metrics import mean_absolute_error, mean_squared_error

try:
    from xgboost import XGBRegressor
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    warnings.warn("XGBoost not available. Install with: pip install xgboost")

warnings.filterwarnings('ignore')


class MLForecaster:
    """Machine Learning forecasting for throughput prediction"""

    def __init__(self, max_lag: int = 4, n_splits: int = 3):
        """
        Initialize ML Forecaster.

        Args:
            max_lag: Number of lag features to use
            n_splits: Number of splits for time series cross-validation
        """
        self.max_lag = max_lag
        self.n_splits = n_splits
        self.models = {}
        self.results = {}
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

    def train_models(self, data: np.ndarray):
        """
        Train multiple ML models.

        Args:
            data: Historical throughput data
        """
        X, y = self.prepare_features(data)

        if len(X) < self.n_splits + 1:
            raise ValueError(f"Insufficient data for {self.n_splits} splits. Need at least {self.n_splits + 1} samples.")

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
            models_config['XGBoost'] = self._get_tuned_xgb(X, y, tscv)

        # Train and evaluate each model
        for name, model in models_config.items():
            try:
                mae, rmse = self._evaluate_model(model, X, y, tscv)
                model.fit(X, y)  # Train on full dataset

                self.models[name] = model
                self.results[name] = {
                    'MAE': mae,
                    'RMSE': rmse,
                    'MAE_percent': (mae / np.mean(data)) * 100
                }
            except Exception as e:
                warnings.warn(f"Failed to train {name}: {str(e)}")

        self.trained = True

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
        """Get summary of model training results."""
        if not self.trained:
            return []

        results_list = []
        for model_name, metrics in self.results.items():
            results_list.append({
                'model': model_name,
                'mae': round(metrics['MAE'], 2),
                'rmse': round(metrics['RMSE'], 2),
                'mae_percent': round(metrics['MAE_percent'], 1)
            })

        return sorted(results_list, key=lambda x: x['mae'])

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
