from datetime import datetime, timedelta

import pytest
from demand_forecasting import DemandForecastService


def _build_sample_dates(days: int = 50) -> list[str]:
    base = datetime(2023, 1, 1)
    samples: list[str] = []
    for offset in range(days):
        day = base + timedelta(days=offset)
        repetitions = (offset % 5) + 1
        for hour in range(repetitions):
            samples.append((day + timedelta(hours=hour)).isoformat())
    return samples


def test_demand_forecast_service_generates_daily_forecast():
    dates = _build_sample_dates(50)
    service = DemandForecastService(dates)
    result = service.generate(daily_horizon=7, weekly_horizon=4)

    assert "daily_forecast" in result
    daily = result["daily_forecast"]
    assert len(daily["dates"]) == 7
    assert len(daily["ensemble"]["mean"]) == 7
    assert result["history"]["total_days"] >= 30


@pytest.mark.integration
def test_demand_forecast_api_returns_payload():
    pytest.importorskip("flask")
    from app import app  # Local import to avoid requiring Flask when test is skipped

    client = app.test_client()
    dates = _build_sample_dates(45)

    response = client.post(
        "/api/demand/forecast",
        json={
            "dates": dates,
            "forecastDays": 5,
            "forecastWeeks": 3,
        },
    )

    assert response.status_code == 200, response.json
    data = response.get_json()
    assert "daily_forecast" in data
    assert "charts" in data
