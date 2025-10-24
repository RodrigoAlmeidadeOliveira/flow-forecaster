"""
Demand forecasting service using machine learning.

Transforms raw demand arrival timestamps into aggregated series (daily/weekly)
and leverages the existing MLForecaster to project future demand.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional, Sequence

import numpy as np
import pandas as pd

from ml_forecaster import MLForecaster

# Accepted date formats when parsing user input. ISO formats are attempted first.
_KNOWN_DATE_FORMATS: Sequence[str] = (
    "%Y-%m-%d",
    "%Y-%m-%d %H:%M",
    "%Y-%m-%d %H:%M:%S",
    "%Y/%m/%d",
    "%d/%m/%Y",
    "%d/%m/%y",
    "%d-%m-%Y",
    "%d-%m-%y",
    "%d.%m.%Y",
)


@dataclass
class ForecastConfig:
    """Configuration parameters for training the ML forecaster."""

    max_lag: int
    n_splits: int
    validation_size: float
    use_kfold: bool


def _parse_timestamp(value: Any) -> datetime:
    """Parse user provided timestamp into ``datetime``."""
    if isinstance(value, datetime):
        return value

    if isinstance(value, (int, float)):
        # Assume POSIX timestamp in seconds.
        return datetime.fromtimestamp(value)

    if not isinstance(value, str):
        raise ValueError(f"Unsupported input type for date parsing: {type(value)}")

    candidate = value.strip()
    if not candidate:
        raise ValueError("Encountered empty date entry.")

    # ISO formats (including with time) are handled by fromisoformat.
    try:
        return datetime.fromisoformat(candidate)
    except ValueError:
        pass

    for fmt in _KNOWN_DATE_FORMATS:
        try:
            return datetime.strptime(candidate, fmt)
        except ValueError:
            continue

    raise ValueError(f"Date '{value}' does not match supported formats.")


def _to_native(obj: Any) -> Any:
    """
    Convert numpy/pandas objects into native Python structures for JSON serialization.
    """
    if isinstance(obj, (np.generic,)):
        return obj.item()
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, pd.Timestamp):
        return obj.strftime("%Y-%m-%d")
    if isinstance(obj, pd.Series):
        return obj.to_list()
    if isinstance(obj, pd.Index):
        return [item.strftime("%Y-%m-%d") if hasattr(item, "strftime") else item for item in obj]
    if isinstance(obj, dict):
        return {key: _to_native(value) for key, value in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_to_native(item) for item in obj]
    return obj


class DemandForecastService:
    """
    Orchestrates demand forecasting using the MLForecaster over aggregated series.
    """

    def __init__(
        self,
        raw_dates: Iterable[Any],
        *,
        exclude_weekends: bool = False,
        minimum_days: int = 30,
    ) -> None:
        self.exclude_weekends = exclude_weekends
        self._raw_dates = list(raw_dates)

        if not self._raw_dates:
            raise ValueError("Nenhuma data foi fornecida para o forecasting de demanda.")

        self._datetimes = sorted(_parse_timestamp(value) for value in self._raw_dates)
        self._dates = [dt.date() for dt in self._datetimes]

        self.daily_series = self._build_series(freq="D")
        if len(self.daily_series) < minimum_days:
            raise ValueError(
                f"Sua série histórica possui apenas {len(self.daily_series)} dias. "
                f"Informe pelo menos {minimum_days} dias de histórico para treinar o modelo."
            )

        if self.daily_series.sum() <= 0:
            raise ValueError("A série histórica de demandas está vazia após o processamento.")

        # Weekly aggregation is optional; it might have fewer points depending on data span.
        self.weekly_series = self._build_series(freq="W-MON")

    def _build_series(self, freq: str) -> pd.Series:
        """
        Aggregate raw timestamps into a regular series according to ``freq``.

        Args:
            freq: Pandas frequency string ('D' for daily, 'W-MON' for weekly starting on Monday).
        """
        index = pd.DatetimeIndex(pd.to_datetime(self._datetimes)).normalize()

        if self.exclude_weekends:
            index = index[index.weekday < 5]

        if len(index) == 0:
            raise ValueError("Todas as datas foram filtradas. Revise a configuração de exclusão.")

        series = pd.Series(1, index=index).resample(freq).sum()
        series = series.asfreq(freq, fill_value=0).sort_index()
        return series.astype(float)

    def _configure(self, length: int) -> ForecastConfig:
        """
        Determine sensible hyperparameters based on series length.
        """
        if length < 15:
            raise ValueError("Histórico insuficiente para treinar modelos de Machine Learning.")

        max_lag = max(3, min(14, length // 8))

        # Ensure at least two splits and avoid exceeding available samples.
        n_splits = max(2, min(5, length // 12))
        if n_splits >= length:
            n_splits = 2

        # Prefer the lighter legacy protocol for smaller datasets to reduce runtime.
        use_kfold = length >= 60
        validation_size = 0.2 if length >= 40 else 0.25

        return ForecastConfig(
            max_lag=max_lag,
            n_splits=n_splits,
            validation_size=validation_size,
            use_kfold=use_kfold,
        )

    def _forecast(
        self,
        series: pd.Series,
        *,
        horizon: int,
        frequency: str,
        label: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Train models and generate forecasts for the provided series.
        """
        if horizon <= 0:
            return None

        length = len(series)
        config = self._configure(length)

        values = series.to_numpy(dtype=float)

        forecaster = MLForecaster(
            max_lag=config.max_lag,
            n_splits=config.n_splits,
            validation_size=config.validation_size,
        )

        forecaster.train_models(values, use_kfold_cv=config.use_kfold)

        forecasts = forecaster.forecast(values, steps=horizon, model_name="ensemble")
        ensemble = forecaster.get_ensemble_forecast(forecasts, apply_dependency_impact=False)
        model_results = forecaster.get_results_summary()
        risk_assessment = forecaster.assess_forecast_risk(values)

        # Compute future index aligned with historical frequency.
        last_timestamp = series.index[-1]
        freq_offset = pd.tseries.frequencies.to_offset(frequency)
        future_index = pd.date_range(
            start=last_timestamp + freq_offset,
            periods=horizon,
            freq=freq_offset,
        )

        total_mean = float(np.sum(ensemble["mean"]))
        total_p10 = float(np.sum(ensemble["p10"]))
        total_p90 = float(np.sum(ensemble["p90"]))

        return {
            "label": label,
            "frequency": frequency,
            "history_points": length,
            "horizon": horizon,
            "dates": [ts.strftime("%Y-%m-%d") for ts in future_index],
            "forecasts": {name: arr.tolist() for name, arr in forecasts.items()},
            "ensemble": {key: value.tolist() for key, value in ensemble.items()},
            "model_results": model_results,
            "risk": _to_native(risk_assessment),
            "summary": {
                "total_mean": round(total_mean, 2),
                "total_p10": round(total_p10, 2),
                "total_p90": round(total_p90, 2),
                "last_observation": last_timestamp.strftime("%Y-%m-%d"),
            },
        }

    def _weekday_profile(self) -> List[Dict[str, Any]]:
        """
        Calculate simple weekday seasonality metrics using the daily series.
        """
        df = self.daily_series.to_frame(name="count")
        df["weekday"] = df.index.weekday
        df_grouped = df.groupby("weekday")["count"]

        profile: List[Dict[str, Any]] = []
        for weekday in range(7):
            if weekday in df_grouped.groups:
                values = df_grouped.get_group(weekday)
                profile.append(
                    {
                        "weekday_index": weekday,
                        "count_days": int(values.count()),
                        "total": round(float(values.sum()), 3),
                        "mean": round(float(values.mean()), 3),
                        "std": round(float(values.std(ddof=0) if len(values) > 1 else 0.0), 3),
                        "max": round(float(values.max()), 3),
                    }
                )
            else:
                profile.append(
                    {
                        "weekday_index": weekday,
                        "count_days": 0,
                        "total": 0.0,
                        "mean": 0.0,
                        "std": 0.0,
                        "max": 0.0,
                    }
                )
        return profile

    def _history_summary(self) -> Dict[str, Any]:
        """Provide descriptive statistics for the processed daily series."""
        start_date = self.daily_series.index[0]
        end_date = self.daily_series.index[-1]

        return {
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "total_events": int(self.daily_series.sum()),
            "total_days": int(len(self.daily_series)),
            "mean_per_day": round(float(self.daily_series.mean()), 3),
            "median_per_day": round(float(self.daily_series.median()), 3),
            "max_per_day": round(float(self.daily_series.max()), 3),
            "weekday_profile": self._weekday_profile(),
        }

    def generate(
        self,
        *,
        daily_horizon: int = 14,
        weekly_horizon: int = 8,
    ) -> Dict[str, Any]:
        """
        Generate forecasting payload for both daily and weekly aggregations.
        """
        results: Dict[str, Any] = {
            "history": self._history_summary(),
        }

        daily_result = self._forecast(
            self.daily_series,
            horizon=daily_horizon,
            frequency="D",
            label="Demanda diária",
        )
        if daily_result:
            results["daily_forecast"] = daily_result

        if len(self.weekly_series) >= 4 and self.weekly_series.sum() > 0:
            try:
                weekly_result = self._forecast(
                    self.weekly_series,
                    horizon=weekly_horizon,
                    frequency="W-MON",
                    label="Demanda semanal",
                )
            except ValueError:
                weekly_result = None

            if weekly_result:
                results["weekly_forecast"] = weekly_result

        return _to_native(results)
