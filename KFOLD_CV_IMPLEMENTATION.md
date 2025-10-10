# K-Fold Cross-Validation Implementation

## Overview

This document describes the complete K-Fold Cross-Validation protocol implementation for Machine Learning features in the Project Forecaster system.

## Protocol Description

The implementation follows a rigorous cross-validation protocol designed to ensure robust model evaluation and hyperparameter tuning:

### 1. Data Split (80/20)

The dataset is first divided into:
- **Training Set (80%)**: Used for K-Fold cross-validation and hyperparameter tuning
- **Validation Set (20%)**: Reserved for final model evaluation

```python
X_train, X_val, y_train, y_val = train_test_split(
    X, y, test_size=0.2, random_state=42, shuffle=False
)
```

### 2. Grid Search for Hyperparameter Tuning

Grid Search is performed on the training set (80%) using K-Fold cross-validation:

```python
grid_search = GridSearchCV(
    estimator=model,
    param_grid=param_grid,
    cv=kfold_gs,  # 3-fold or 5-fold
    scoring='neg_mean_absolute_error',
    n_jobs=-1
)
```

**Hyperparameter Grids:**

- **RandomForest:**
  - `n_estimators`: [50, 100, 150]
  - `max_depth`: [3, 5, 7]
  - `min_samples_split`: [2, 5]

- **XGBoost:**
  - `n_estimators`: [50, 100, 150]
  - `max_depth`: [3, 5, 7]
  - `learning_rate`: [0.01, 0.05, 0.1]

- **HistGradient:**
  - `max_iter`: [50, 100, 150]
  - `max_depth`: [3, 5, 7]
  - `learning_rate`: [0.01, 0.05, 0.1]

### 3. K-Fold Cross-Validation (5 folds)

After finding the best hyperparameters, 5-fold cross-validation is performed on the training set:

```python
kfold = KFold(n_splits=5, shuffle=True, random_state=42)

for fold_num, (train_idx, test_idx) in enumerate(kfold.split(X_train), 1):
    # Train and evaluate on each fold
    fold_model = clone(best_model)
    fold_model.fit(X_fold_train, y_fold_train)
    y_pred = fold_model.predict(X_fold_test)

    # Calculate metrics: MAE, RMSE, R²
    ...
```

### 4. Metrics Calculation

For each fold, the following metrics are calculated:
- **MAE** (Mean Absolute Error)
- **RMSE** (Root Mean Squared Error)
- **R²** (R-squared score)

After all folds:
- **Mean ± Standard Deviation** across all folds for each metric

### 5. Final Validation

The best model (with optimized hyperparameters) is trained on the full training set and evaluated on the validation set (20%):

```python
best_model.fit(X_train, y_train)
y_val_pred = best_model.predict(X_val)

# Calculate final validation metrics
val_mae = mean_absolute_error(y_val, y_val_pred)
val_rmse = np.sqrt(mean_squared_error(y_val, y_val_pred))
val_r2 = r2_score(y_val, y_val_pred)
```

## Configuration

### MLForecaster Initialization

```python
forecaster = MLForecaster(
    max_lag=4,              # Number of lag features
    n_splits=5,             # Number of K-folds
    validation_size=0.2     # Validation set size (20%)
)
```

### Training with K-Fold CV

```python
# Enable K-Fold CV protocol
forecaster.train_models(data, use_kfold_cv=True)

# Or use legacy Time Series CV
forecaster.train_models(data, use_kfold_cv=False)
```

## Output Format

### Console Output

For each model, the system outputs:

```
RandomForest - K-Fold Cross-Validation (5 folds):
============================================================

Performing Grid Search for hyperparameter tuning...
Parameter grid: {'n_estimators': [50, 100, 150], 'max_depth': [3, 5, 7], ...}
Best hyperparameters: {'max_depth': 3, 'min_samples_split': 5, 'n_estimators': 150}
Best CV score (MAE): 1.567
Validation set MAE: 2.691

K-Fold Cross-Validation Results:
------------------------------------------------------------
Fold 1: MAE=1.192, RMSE=1.537, R²=-1.956
Fold 2: MAE=2.089, RMSE=2.588, R²=-2.323
Fold 3: MAE=2.840, RMSE=3.176, R²=0.354
Fold 4: MAE=1.307, RMSE=1.438, R²=-0.331
Fold 5: MAE=0.777, RMSE=1.038, R²=0.735

Cross-Validation Summary:
  MAE:  1.641 ± 0.735
  RMSE: 1.955 ± 0.797
  R²:   -0.704 ± 1.226

Final Validation Set Performance:
  MAE:  2.691
  RMSE: 3.431
  R²:   -0.861
============================================================
```

### Results Structure

```python
{
    'MAE': 1.641,              # Mean MAE across folds
    'RMSE': 1.955,             # Mean RMSE across folds
    'MAE_percent': 34.8,       # MAE as percentage of mean
    'MAE_std': 0.735,          # Standard deviation of MAE
    'RMSE_std': 0.797,         # Standard deviation of RMSE
    'R2_mean': -0.704,         # Mean R² across folds
    'R2_std': 1.226,           # Standard deviation of R²
    'val_MAE': 2.691,          # Validation set MAE
    'val_RMSE': 3.431,         # Validation set RMSE
    'val_R2': -0.861,          # Validation set R²
    'best_params': {           # Best hyperparameters from Grid Search
        'max_depth': 3,
        'min_samples_split': 5,
        'n_estimators': 150
    }
}
```

## Files Modified

### 1. `ml_forecaster.py`
- Added `n_splits` and `validation_size` parameters to `__init__`
- Created `_get_param_grid()` method for hyperparameter grids
- Created `_cross_validate_with_kfold()` method implementing the complete protocol
- Modified `train_models()` to support K-Fold CV with Grid Search
- Updated `get_results_summary()` to include CV metrics and best parameters
- Added imports: `KFold`, `train_test_split`, `GridSearchCV`, `r2_score`, `clone`

### 2. `app.py`
- Updated MLForecaster initialization to use `n_splits=5, validation_size=0.2`
- Added `use_kfold_cv=True` parameter to `train_models()` calls
- Updated in two endpoints:
  - `/api/ml-forecast` (line 173)
  - `/api/combined-forecast` (line 300)

### 3. `ml_deadline_forecaster.py`
- Updated MLForecaster initialization in `__init__` (line 56)
- Added `use_kfold_cv=True` to `train_models()` calls (2 locations)

## Testing

### Test Script: `test_ml_cv.py`

A comprehensive test script was created to verify the implementation:

```bash
python test_ml_cv.py
```

The test script:
- Generates synthetic throughput data
- Trains all models using K-Fold CV + Grid Search
- Displays detailed CV results for each model
- Tests forecasting functionality
- Generates ensemble statistics

## Benefits

1. **Robust Model Evaluation**: K-Fold CV provides more reliable performance estimates
2. **Hyperparameter Optimization**: Grid Search finds optimal model parameters
3. **Uncertainty Quantification**: Standard deviations show model stability
4. **Overfitting Prevention**: Separate validation set prevents data leakage
5. **Transparency**: Detailed logging shows the entire training process

## Backward Compatibility

The implementation maintains backward compatibility:
- Legacy Time Series CV is still available with `use_kfold_cv=False`
- Default behavior uses the new K-Fold CV protocol
- All existing API endpoints continue to work

## Performance Considerations

- Grid Search with K-Fold CV is more computationally intensive
- Training time increases proportionally to:
  - Number of hyperparameter combinations
  - Number of folds (K)
  - Number of models
- Recommend using `n_jobs=-1` for parallel processing
- For large datasets, consider reducing grid search space

## Future Enhancements

Potential improvements:
1. **RandomizedSearchCV**: For larger hyperparameter spaces
2. **Nested Cross-Validation**: For even more robust evaluation
3. **Time Series Specific Folds**: TimeSeriesSplit with K-Fold
4. **Early Stopping**: For gradient boosting models
5. **Custom Scoring Functions**: For domain-specific metrics

## References

- Scikit-learn K-Fold Cross-Validation: https://scikit-learn.org/stable/modules/cross_validation.html
- Grid Search CV: https://scikit-learn.org/stable/modules/grid_search.html
- Model Evaluation Metrics: https://scikit-learn.org/stable/modules/model_evaluation.html
