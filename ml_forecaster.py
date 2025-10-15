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
from sklearn.linear_model import Ridge, Lasso
from sklearn.model_selection import TimeSeriesSplit, RandomizedSearchCV, KFold, train_test_split, GridSearchCV
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.base import clone
from sklearn.neighbors import KNeighborsRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR

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
            ),
            'Ridge': Pipeline([
                ('scaler', StandardScaler()),
                ('ridge', Ridge())
            ]),
            'Lasso': Pipeline([
                ('scaler', StandardScaler()),
                ('lasso', Lasso(max_iter=5000))
            ]),
            'KNN': Pipeline([
                ('scaler', StandardScaler()),
                ('knn', KNeighborsRegressor(n_neighbors=5))
            ]),
            'SVR_RBF': Pipeline([
                ('scaler', StandardScaler()),
                ('svr', SVR(kernel='rbf', C=1.0, epsilon=0.1, gamma='scale'))
            ])
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
                    self._ensure_valid_neighbors(final_model, len(X))
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
        """Get hyperparameter grid for each model type (optimized for low memory)."""
        if 'RandomForest' in model_name:
            return {
                'n_estimators': [50, 100],
                'max_depth': [3, 5],
                'min_samples_split': [2]
            }
        elif 'XGBoost' in model_name:
            return {
                'n_estimators': [50, 100],
                'max_depth': [3, 5],
                'learning_rate': [0.05, 0.1]
            }
        elif 'HistGradient' in model_name:
            return {
                'max_iter': [50, 100],
                'max_depth': [3, 5],
                'learning_rate': [0.05, 0.1]
            }
        elif 'Ridge' in model_name:
            return {
                'ridge__alpha': [0.1, 1.0, 10.0]
            }
        elif 'Lasso' in model_name:
            return {
                'lasso__alpha': [0.01, 0.1, 1.0],
                'lasso__max_iter': [2000, 5000]
            }
        elif 'KNN' in model_name:
            return {
                'knn__n_neighbors': [2, 3, 5],
                'knn__weights': ['uniform', 'distance']
            }
        elif 'SVR' in model_name:
            return {
                'svr__C': [1.0, 5.0],
                'svr__epsilon': [0.05, 0.1],
                'svr__gamma': ['scale']
            }
        else:
            return {}

    def _ensure_valid_neighbors(self, estimator, sample_size: int):
        """Ensure kNN-based estimators respect available sample size."""
        if sample_size <= 0 or estimator is None:
            return

        max_neighbors = max(1, sample_size)

        try:
            if hasattr(estimator, 'named_steps') and 'knn' in estimator.named_steps:
                current = estimator.named_steps['knn'].n_neighbors
                if current > max_neighbors and hasattr(estimator, 'set_params'):
                    estimator.set_params(knn__n_neighbors=max_neighbors)
            elif hasattr(estimator, 'n_neighbors'):
                current = getattr(estimator, 'n_neighbors', max_neighbors)
                if current > max_neighbors and hasattr(estimator, 'set_params'):
                    estimator.set_params(n_neighbors=max_neighbors)
        except Exception:
            # Silently ignore adjustments if the estimator does not support them
            pass

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
            try:
                # Use K-Fold on training set for Grid Search
                kfold_gs = KFold(n_splits=min(3, self.n_splits), shuffle=True, random_state=42)

                if 'KNN' in model_name and 'knn__n_neighbors' in param_grid:
                    min_train_size = len(X_train)
                    for train_idx, _ in kfold_gs.split(X_train):
                        min_train_size = min(min_train_size, len(train_idx))
                    feasible_neighbors = sorted({n for n in param_grid['knn__n_neighbors'] if n <= min_train_size})
                    if not feasible_neighbors:
                        feasible_neighbors = [max(1, min_train_size)]
                    param_grid['knn__n_neighbors'] = feasible_neighbors
                    print(f"Adjusted kNN neighbor grid based on available samples: {feasible_neighbors}")

                print(f"\nPerforming Grid Search for hyperparameter tuning...")
                print(f"Parameter grid: {param_grid}")

                grid_search = GridSearchCV(
                    estimator=model,
                    param_grid=param_grid,
                    cv=kfold_gs,
                    scoring='neg_mean_absolute_error',
                    n_jobs=1,  # Changed from -1 to 1 to reduce memory usage on Fly.io (1GB RAM)
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
            self._ensure_valid_neighbors(fold_model, len(X_fold_train))
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
        self._ensure_valid_neighbors(best_model, len(X_train))
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
        """Make recursive multi-step forecast using a stored model."""
        model = self.models[model_name]
        return self._forecast_with_model(model, last_values, steps)

    def _forecast_with_model(self, model, last_values: np.ndarray, steps: int) -> np.ndarray:
        """Run recursive multi-step forecast with a provided estimator."""
        history = list(np.asarray(last_values, dtype=float))

        if len(history) < self.max_lag + 2:
            raise ValueError(
                f"Need at least {self.max_lag + 2} historical points, got {len(history)}")

        predictions = []

        for _ in range(steps):
            recent = np.array(history[-self.max_lag:])
            rolling_window = history[-(self.max_lag + 2):-1] if len(history) >= self.max_lag + 2 else history
            rolling_mean = float(np.mean(rolling_window))
            rolling_std = float(np.std(rolling_window))

            features = list(recent) + [rolling_mean, rolling_std]
            X_step = pd.DataFrame([features], columns=[
                *[f'lag_{i}' for i in range(1, self.max_lag + 1)],
                'rolling_mean_3', 'rolling_std_3'
            ])

            pred = float(model.predict(X_step)[0])
            pred = max(0.0, pred)
            predictions.append(pred)
            history.append(pred)

        return np.array(predictions, dtype=float)

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

        data = np.asarray(data, dtype=float)
        n_samples = len(data)

        max_test_points = n_samples - (self.max_lag + 3)
        if max_test_points <= 0:
            raise ValueError(
                f"Insufficient data for walk-forward validation. Need at least {self.max_lag + 4} samples.")

        if forecast_steps > max_test_points:
            raise ValueError(
                f"Forecast steps ({forecast_steps}) exceed available test window ({max_test_points}).")

        n_test = max(forecast_steps, int(np.ceil(n_samples * test_size)))
        n_test = min(n_test, max_test_points)
        n_train = n_samples - n_test

        if n_train < self.max_lag + 3:
            raise ValueError(
                f"Insufficient training data. Need at least {self.max_lag + 3} samples for training.")

        train_ratio = (n_train / n_samples) * 100
        test_ratio = (n_test / n_samples) * 100

        print(f"\n{'=' * 60}")
        print("WALK-FORWARD VALIDATION")
        print(f"{'=' * 60}")
        print(f"Total samples: {n_samples}")
        print(f"Training samples: {n_train} ({train_ratio:.1f}%)")
        print(f"Test samples: {n_test} ({test_ratio:.1f}%)")
        print(f"Forecast horizon per origin: {forecast_steps}")
        print(f"{'=' * 60}\n")

        wf_results: Dict[str, Dict] = {}

        for model_name, base_model in self.models.items():
            print(f"\n{model_name} - Walk-Forward Validation:")
            print("-" * 60)

            predictions: List[float] = []
            actuals: List[float] = []
            indices: List[int] = []
            forecast_origins: List[int] = []
            per_origin: List[Dict] = []

            for origin in range(n_train, n_samples, forecast_steps):
                train_data = data[:origin]

                if len(train_data) < self.max_lag + 3:
                    print(f"Skipping origin {origin}: insufficient training history.")
                    continue

                remaining_samples = n_samples - origin
                steps_to_forecast = min(forecast_steps, remaining_samples)
                if steps_to_forecast <= 0:
                    break

                actual_values = data[origin:origin + steps_to_forecast]
                origin_indices = list(range(origin, origin + steps_to_forecast))

                try:
                    X_train, y_train = self.prepare_features(train_data)
                    if len(X_train) == 0:
                        print(f"Skipping origin {origin}: no features after lag preparation.")
                        continue

                    wf_model = clone(base_model)
                    self._ensure_valid_neighbors(wf_model, len(X_train))
                    wf_model.fit(X_train, y_train)

                    history_slice = train_data[-(self.max_lag + 3):]
                    forecast_values = self._forecast_with_model(
                        wf_model,
                        history_slice,
                        steps_to_forecast
                    )

                    origin_mae = mean_absolute_error(actual_values, forecast_values)
                    origin_rmse = np.sqrt(mean_squared_error(actual_values, forecast_values))
                    origin_mape = float(np.mean(
                        np.abs(actual_values - forecast_values) /
                        np.maximum(np.abs(actual_values), 1e-3)
                    ) * 100)

                    predictions.extend(forecast_values.tolist())
                    actuals.extend(actual_values.tolist())
                    indices.extend(origin_indices)
                    forecast_origins.append(origin)
                    per_origin.append({
                        'origin': origin,
                        'indices': origin_indices,
                        'steps': steps_to_forecast,
                        'actual': actual_values.tolist(),
                        'predicted': forecast_values.tolist(),
                        'mae': float(origin_mae),
                        'rmse': float(origin_rmse),
                        'mape': origin_mape
                    })

                    print(f"Origin {origin}: steps={steps_to_forecast} | MAE={origin_mae:.3f} | RMSE={origin_rmse:.3f} | MAPE={origin_mape:.2f}%")

                except Exception as exc:
                    print(f"Warning: Forecast failed at origin {origin}: {exc}")
                    continue

            if predictions and actuals:
                predictions_np = np.array(predictions, dtype=float)
                actuals_np = np.array(actuals, dtype=float)

                mae = mean_absolute_error(actuals_np, predictions_np)
                rmse = np.sqrt(mean_squared_error(actuals_np, predictions_np))
                r2 = r2_score(actuals_np, predictions_np)
                mape = float(np.mean(
                    np.abs(actuals_np - predictions_np) /
                    np.maximum(np.abs(actuals_np), 1e-3)
                ) * 100)
                smape_denominator = np.abs(actuals_np) + np.abs(predictions_np)
                smape = float(np.mean(
                    np.where(smape_denominator == 0, 0,
                             2 * np.abs(actuals_np - predictions_np) /
                             np.maximum(smape_denominator, 1e-3))
                ) * 100)
                median_ae = float(np.median(np.abs(actuals_np - predictions_np)))

                wf_results[model_name] = {
                    'predictions': predictions,
                    'actuals': actuals,
                    'indices': indices,
                    'forecast_origins': forecast_origins,
                    'mae': float(mae),
                    'rmse': float(rmse),
                    'r2': float(r2),
                    'mape': mape,
                    'smape': smape,
                    'median_ae': median_ae,
                    'n_forecasts': len(forecast_origins),
                    'n_points': len(predictions),
                    'train_size': int(n_train),
                    'test_size': int(n_test),
                    'test_start_index': int(n_train),
                    'per_origin': per_origin
                }

                print("\nSummary Statistics:")
                print(f"  MAE:  {mae:.3f}")
                print(f"  RMSE: {rmse:.3f}")
                print(f"  R²:   {r2:.3f}")
                print(f"  MAPE: {mape:.2f}%")
                print(f"  sMAPE:{smape:.2f}%")
                print(f"  Forecast origins: {len(forecast_origins)}")
                print(f"  Total evaluated points: {len(predictions)}")
            else:
                print(f"Warning: No valid predictions for {model_name}")
                wf_results[model_name] = {
                    'error': 'No valid predictions generated',
                    'predictions': [],
                    'actuals': [],
                    'indices': [],
                    'forecast_origins': [],
                    'mae': None,
                    'rmse': None,
                    'r2': None,
                    'mape': None,
                    'smape': None,
                    'median_ae': None,
                    'n_forecasts': 0,
                    'n_points': 0,
                    'train_size': int(n_train),
                    'test_size': int(n_test),
                    'test_start_index': int(n_train),
                    'per_origin': []
                }

        print(f"\n{'=' * 60}")
        print("WALK-FORWARD VALIDATION COMPLETE")
        print(f"{'=' * 60}\n")

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
