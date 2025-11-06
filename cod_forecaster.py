"""
Cost of Delay (CoD) Forecaster
Random Forest model for predicting weekly delay cost
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

import warnings
warnings.filterwarnings('ignore')


def _to_native(value):
    if isinstance(value, np.generic):
        if isinstance(value, np.integer):
            return int(value)
        if isinstance(value, np.floating):
            return float(value)
        if isinstance(value, np.bool_):
            return bool(value)
    return value


class CoDForecaster:
    """
    Machine Learning forecaster for Cost of Delay (CoD) estimation.
    Predicts weekly delay cost (R$/week) based on project characteristics.
    """

    def __init__(self, n_splits: int = 5):
        """
        Initialize CoD Forecaster.

        Args:
            n_splits: Number of K-folds for cross-validation
        """
        self.n_splits = n_splits
        self.models = {}
        self.scaler = StandardScaler()
        self.feature_names = []
        self.project_types = []  # Store project types seen during training
        self.trained = False

    def prepare_features(self, projects_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Prepare features for CoD prediction.

        Args:
            projects_df: DataFrame with project characteristics

        Expected columns:
            - budget_millions: Budget in R$ millions
            - duration_weeks: Expected duration in weeks
            - team_size: Number of people
            - num_stakeholders: Number of stakeholders
            - business_value: Business value score (0-100)
            - complexity: Complexity level (1-5)
            - project_type: Type (encoded)
            - risk_level: Risk level (encoded)
            - cod_weekly: Target - weekly CoD in R$ (for training)

        Returns:
            X: Feature matrix
            y: Target variable (cod_weekly)
        """
        # Feature engineering
        features = pd.DataFrame()

        # Direct features
        features['budget_millions'] = projects_df['budget_millions']
        features['duration_weeks'] = projects_df['duration_weeks']
        features['team_size'] = projects_df['team_size']
        features['num_stakeholders'] = projects_df['num_stakeholders']
        features['business_value'] = projects_df['business_value']
        features['complexity'] = projects_df['complexity']

        # Derived features
        features['budget_per_week'] = projects_df['budget_millions'] * 1_000_000 / projects_df['duration_weeks']
        features['budget_per_person'] = projects_df['budget_millions'] * 1_000_000 / projects_df['team_size']
        features['stakeholder_density'] = projects_df['num_stakeholders'] / projects_df['team_size']
        features['value_per_week'] = projects_df['business_value'] / projects_df['duration_weeks']

        # Calculate risk level if not provided
        if 'risk_level' not in projects_df.columns:
            projects_df['risk_level'] = projects_df.get('complexity', 3)

        features['risk_complexity_score'] = projects_df['risk_level'] * projects_df['complexity']

        # One-hot encoding for categorical
        if 'project_type' in projects_df.columns:
            # During training, store the unique types
            if not self.trained:
                self.project_types = sorted(projects_df['project_type'].unique().tolist())

            # Create dummies for all known types
            for ptype in self.project_types:
                features[f'type_{ptype}'] = (projects_df['project_type'] == ptype).astype(int)

        # Store feature names
        if not self.trained:
            self.feature_names = features.columns.tolist()

        # Target
        y = projects_df['cod_weekly'] if 'cod_weekly' in projects_df.columns else None

        return features, y

    def train_models(
        self,
        projects_df: pd.DataFrame,
        use_hyperparam_search: bool = False,
        search_iterations: int = 20,
        random_state: int = 42,
    ):
        """
        Train multiple CoD prediction models.

        Args:
            projects_df: Historical projects with actual CoD data
        """
        X, y = self.prepare_features(projects_df)

        if y is None or len(X) < 10:
            raise ValueError("Insufficient training data. Need at least 10 projects with CoD data.")

        print(f"\n{'='*60}")
        print(f"CoD MODEL TRAINING - K-FOLD CROSS-VALIDATION")
        print(f"{'='*60}")
        print(f"Total samples: {len(X)}")
        print(f"Features: {len(self.feature_names)}")
        print(f"{'='*60}\n")

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=random_state, shuffle=True
        )

        # Scale features (fit on training set first)
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # Model configurations
        models_results = {}

        # Random Forest with optional hyperparameter search
        print("\nRandomForest - Training:")
        print("-" * 60)
        rf_base = RandomForestRegressor(random_state=random_state, n_jobs=1)

        if use_hyperparam_search:
            param_distributions = {
                'n_estimators': np.arange(150, 401, 10),
                'max_depth': [None] + list(range(6, 21)),
                'min_samples_split': np.arange(2, 11),
                'min_samples_leaf': np.arange(1, 6),
                'max_features': ['auto', 'sqrt', 0.5, 0.7, 0.9],
                'bootstrap': [True, False],
            }
            rf_search = RandomizedSearchCV(
                estimator=rf_base,
                param_distributions=param_distributions,
                n_iter=search_iterations,
                cv=self.n_splits,
                scoring='neg_mean_absolute_error',
                n_jobs=1,
                random_state=random_state,
                verbose=1,
            )
            rf_search.fit(X_train_scaled, y_train)
            best_rf = rf_search.best_estimator_
            best_params = {key: _to_native(val) for key, val in rf_search.best_params_.items()}
            print(f"Best RF params: {best_params}")
        else:
            best_rf = RandomForestRegressor(
                n_estimators=200,
                max_depth=10,
                min_samples_split=3,
                min_samples_leaf=2,
                random_state=random_state,
                n_jobs=1,
            )
            best_rf.fit(X_train_scaled, y_train)
            best_params = {
                'n_estimators': 200,
                'max_depth': 10,
                'min_samples_split': 3,
                'min_samples_leaf': 2,
                'random_state': random_state,
                'n_jobs': 1,
            }

        y_pred_rf = best_rf.predict(X_test_scaled)
        rf_mae = mean_absolute_error(y_test, y_pred_rf)
        rf_rmse = np.sqrt(mean_squared_error(y_test, y_pred_rf))
        rf_r2 = r2_score(y_test, y_pred_rf)
        rf_mape = np.mean(np.abs((y_test - y_pred_rf) / y_test)) * 100

        print("\nRandomForest Test Set Performance:")
        print(f"  MAE:  R$ {rf_mae:,.0f}/semana")
        print(f"  RMSE: R$ {rf_rmse:,.0f}/semana")
        print(f"  R²:   {rf_r2:.3f}")
        print(f"  MAPE: {rf_mape:.1f}%")

        models_results['RandomForest'] = {
            'model': best_rf,
            'mae': rf_mae,
            'rmse': rf_rmse,
            'r2': rf_r2,
            'mape': rf_mape,
            'best_params': best_params,
        }

        # Gradient Boosting (baseline)
        print("\nGradientBoosting - Training:")
        print("-" * 60)
        gb_model = GradientBoostingRegressor(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.07,
            random_state=random_state
        )
        gb_model.fit(X_train_scaled, y_train)

        y_pred_gb = gb_model.predict(X_test_scaled)
        gb_mae = mean_absolute_error(y_test, y_pred_gb)
        gb_rmse = np.sqrt(mean_squared_error(y_test, y_pred_gb))
        gb_r2 = r2_score(y_test, y_pred_gb)
        gb_mape = np.mean(np.abs((y_test - y_pred_gb) / y_test)) * 100

        print("\nGradientBoosting Test Set Performance:")
        print(f"  MAE:  R$ {gb_mae:,.0f}/semana")
        print(f"  RMSE: R$ {gb_rmse:,.0f}/semana")
        print(f"  R²:   {gb_r2:.3f}")
        print(f"  MAPE: {gb_mape:.1f}%")

        models_results['GradientBoosting'] = {
            'model': gb_model,
            'mae': gb_mae,
            'rmse': gb_rmse,
            'r2': gb_r2,
            'mape': gb_mape,
            'best_params': None,
        }

        # Refit scaler on full dataset and train final models on all data
        self.scaler.fit(X)
        X_full_scaled = self.scaler.transform(X)

        # Refit RandomForest on full data with best params
        rf_full_params = dict(best_params)
        rf_full_params.setdefault('random_state', random_state)
        rf_full_params.setdefault('n_jobs', 1)
        rf_full = RandomForestRegressor(**rf_full_params)
        rf_full.fit(X_full_scaled, y)
        models_results['RandomForest']['model'] = rf_full

        # Refit GradientBoosting on full data
        gb_full = GradientBoostingRegressor(
            n_estimators=gb_model.n_estimators,
            max_depth=gb_model.max_depth,
            learning_rate=gb_model.learning_rate,
            random_state=random_state
        )
        gb_full.fit(X_full_scaled, y)
        models_results['GradientBoosting']['model'] = gb_full

        # Persist results
        self.models = models_results

        self.trained = True
        print(f"\n{'='*60}")
        print(f"CoD TRAINING COMPLETE - {len(self.models)} models trained")
        print(f"{'='*60}\n")

    def predict_cod(self, project: Dict, model_name: str = 'RandomForest') -> Dict:
        """
        Predict Cost of Delay for a project.

        Args:
            project: Dictionary with project characteristics
            model_name: Name of model to use

        Returns:
            Dictionary with CoD predictions
        """
        if not self.trained:
            raise ValueError("Models not trained. Call train_models() first.")

        # Prepare features
        project_df = pd.DataFrame([project])
        X, _ = self.prepare_features(project_df)
        X_scaled = self.scaler.transform(X)

        # Predict with selected model
        model = self.models[model_name]['model']
        cod_weekly = model.predict(X_scaled)[0]

        # Get predictions from all models (for ensemble)
        all_predictions = []
        for m_name, m_data in self.models.items():
            pred = m_data['model'].predict(X_scaled)[0]
            all_predictions.append(pred)

        cod_weekly_mean = np.mean(all_predictions)
        cod_weekly_std = np.std(all_predictions)

        return {
            'cod_weekly': float(cod_weekly),
            'cod_weekly_mean': float(cod_weekly_mean),
            'cod_weekly_std': float(cod_weekly_std),
            'cod_daily': float(cod_weekly / 7),
            'cod_monthly': float(cod_weekly * 4.33),
            'model_used': model_name,
            'confidence_interval_95': (
                float(cod_weekly_mean - 1.96 * cod_weekly_std),
                float(cod_weekly_mean + 1.96 * cod_weekly_std)
            )
        }

    def calculate_total_cod(self, cod_weekly: float, delay_weeks: float) -> Dict:
        """
        Calculate total Cost of Delay.

        Args:
            cod_weekly: Weekly CoD in R$
            delay_weeks: Number of weeks delayed

        Returns:
            Dictionary with total CoD calculations
        """
        total_cod = cod_weekly * delay_weeks

        return {
            'cod_weekly': float(cod_weekly),
            'delay_weeks': float(delay_weeks),
            'total_cod': float(total_cod),
            'total_cod_formatted': f"R$ {total_cod:,.2f}"
        }

    def get_feature_importance(self, model_name: str = 'RandomForest') -> pd.DataFrame:
        """
        Get feature importance from trained model.

        Args:
            model_name: Name of model

        Returns:
            DataFrame with feature importance
        """
        if not self.trained:
            raise ValueError("Models not trained.")

        model = self.models[model_name]['model']

        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_

            importance_df = pd.DataFrame({
                'feature': self.feature_names,
                'importance': importances
            }).sort_values('importance', ascending=False)

            return importance_df
        else:
            return None


def generate_sample_cod_data(n_samples: int = 100) -> pd.DataFrame:
    """
    Generate synthetic CoD training data for demonstration.

    Args:
        n_samples: Number of samples to generate

    Returns:
        DataFrame with synthetic project data and CoD values
    """
    np.random.seed(42)

    data = []
    project_types = ['ERP', 'CRM', 'Analytics', 'Mobile', 'Web']

    for i in range(n_samples):
        budget = np.random.uniform(0.5, 10.0)  # R$ millions
        duration = np.random.randint(8, 52)  # weeks
        team_size = np.random.randint(3, 20)
        stakeholders = np.random.randint(2, 15)
        business_value = np.random.uniform(20, 100)
        complexity = np.random.randint(1, 6)
        risk_level = np.random.randint(1, 6)
        project_type = np.random.choice(project_types)

        # Calculate realistic CoD based on project characteristics
        base_cod = budget * 1_000_000 * 0.02  # 2% of budget per week
        value_factor = business_value / 50  # Higher value = higher CoD
        complexity_factor = complexity / 3
        stakeholder_factor = stakeholders / 10

        cod_weekly = base_cod * value_factor * complexity_factor * (1 + stakeholder_factor * 0.5)
        cod_weekly += np.random.normal(0, cod_weekly * 0.15)  # Add noise
        cod_weekly = max(1000, cod_weekly)  # Minimum R$ 1,000/week

        data.append({
            'budget_millions': budget,
            'duration_weeks': duration,
            'team_size': team_size,
            'num_stakeholders': stakeholders,
            'business_value': business_value,
            'complexity': complexity,
            'risk_level': risk_level,
            'project_type': project_type,
            'cod_weekly': cod_weekly
        })

    return pd.DataFrame(data)
