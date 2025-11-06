#!/usr/bin/env python3
"""
Offline training utility for the Cost of Delay model.
Loads a CSV dataset, performs hyperparameter search, saves the best model,
and records metrics for auditing (suggestions #1 and #2).
"""
import argparse
import json
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from joblib import dump
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import RandomizedSearchCV, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from cod_forecaster import CoDForecaster


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Train and persist a tuned Cost of Delay model."
    )
    parser.add_argument(
        "--dataset",
        default="data/cod_training_sample.csv",
        help="Path to the CSV dataset with CoD training data.",
    )
    parser.add_argument(
        "--model-dir",
        default="models",
        help="Directory where the trained model pipeline will be saved.",
    )
    parser.add_argument(
        "--metrics-dir",
        default="logs",
        help="Directory where the metrics JSON will be stored.",
    )
    parser.add_argument(
        "--model-name",
        default="cod_random_forest.pkl",
        help="Filename for the persisted model pipeline.",
    )
    parser.add_argument(
        "--metrics-name",
        default="cod_training_metrics.json",
        help="Filename for the metrics record.",
    )
    parser.add_argument(
        "--test-size",
        type=float,
        default=0.2,
        help="Test split ratio (between 0 and 1).",
    )
    parser.add_argument(
        "--random-state",
        type=int,
        default=42,
        help="Random state for reproducibility.",
    )
    parser.add_argument(
        "--n-search-iterations",
        type=int,
        default=30,
        help="Number of parameter combinations for RandomizedSearchCV.",
    )
    return parser.parse_args()


def load_dataset(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")
    df = pd.read_csv(path)
    required_columns = {
        "budget_millions",
        "duration_weeks",
        "team_size",
        "num_stakeholders",
        "business_value",
        "complexity",
        "cod_weekly",
    }
    missing = required_columns.difference(df.columns)
    if missing:
        raise ValueError(f"Dataset missing required columns: {', '.join(sorted(missing))}")
    if len(df) < 40:
        raise ValueError("Dataset must contain at least 40 rows for reliable tuning.")
    return df


def build_pipeline(random_state: int) -> Pipeline:
    return Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            ("model", RandomForestRegressor(random_state=random_state)),
        ]
    )


def randomized_search(pipeline: Pipeline, n_iter: int, random_state: int) -> RandomizedSearchCV:
    param_distributions = {
        "model__n_estimators": np.arange(150, 401, 10),
        "model__max_depth": [None] + list(range(6, 21)),
        "model__min_samples_split": np.arange(2, 11),
        "model__min_samples_leaf": np.arange(1, 6),
        "model__max_features": ["auto", "sqrt", 0.5, 0.7, 0.9],
        "model__bootstrap": [True, False],
    }
    search = RandomizedSearchCV(
        estimator=pipeline,
        param_distributions=param_distributions,
        n_iter=n_iter,
        cv=5,
        scoring="neg_mean_absolute_error",
        n_jobs=-1,
        verbose=1,
        random_state=random_state,
    )
    return search


def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    mae = mean_absolute_error(y_true, y_pred)
    rmse = mean_squared_error(y_true, y_pred, squared=False)
    r2 = r2_score(y_true, y_pred)
    mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
    return {
        "mae": float(mae),
        "rmse": float(rmse),
        "r2": float(r2),
        "mape": float(mape),
    }


def main() -> None:
    args = parse_args()
    dataset_path = Path(args.dataset)
    df = load_dataset(dataset_path)

    forecaster = CoDForecaster(n_splits=5)
    X, y = forecaster.prepare_features(df)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=args.test_size,
        random_state=args.random_state,
        shuffle=True,
    )

    pipeline = build_pipeline(args.random_state)
    search = randomized_search(pipeline, args.n_search_iterations, args.random_state)
    search.fit(X_train, y_train)

    best_pipeline = search.best_estimator_
    y_pred = best_pipeline.predict(X_test)
    metrics = compute_metrics(y_test.values, y_pred)

    model_dir = Path(args.model_dir)
    model_dir.mkdir(parents=True, exist_ok=True)
    model_path = model_dir / args.model_name
    dump(best_pipeline, model_path)

    metrics_dir = Path(args.metrics_dir)
    metrics_dir.mkdir(parents=True, exist_ok=True)
    metrics_path = metrics_dir / args.metrics_name

    record = {
        "timestamp": datetime.utcnow().isoformat(),
        "dataset_path": str(dataset_path.resolve()),
        "rows": int(len(df)),
        "columns": sorted(df.columns.tolist()),
        "model_path": str(model_path.resolve()),
        "search_best_params": search.best_params_,
        "test_metrics": metrics,
    }

    if metrics_path.exists():
        with metrics_path.open("r", encoding="utf-8") as f:
            history = json.load(f)
            if not isinstance(history, list):
                history = [history]
    else:
        history = []
    history.append(record)

    with metrics_path.open("w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)

    print("Training complete.")
    print(f"Best parameters: {search.best_params_}")
    print("Test metrics:")
    for key, value in metrics.items():
        if key in {"mae", "rmse"}:
            print(f"  {key.upper()}: R$ {value:,.2f}/week")
        elif key == "mape":
            print(f"  {key.upper()}: {value:.2f}%")
        else:
            print(f"  {key.upper()}: {value:.3f}")
    print(f"Model saved to: {model_path}")
    print(f"Metrics log updated at: {metrics_path}")


if __name__ == "__main__":
    main()
