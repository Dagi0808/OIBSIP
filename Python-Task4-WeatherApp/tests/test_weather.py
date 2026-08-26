"""Tests for the weather app — API layer and utilities."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from unittest.mock import patch, MagicMock

from weather import get_current_weather, get_forecast, detect_city_from_ip
from utils import (
    celsius_to_fahrenheit,
    fahrenheit_to_celsius,
    format_temp,
    format_wind,
    parse_current,
    parse_hourly,
    parse_daily,
    epoch_to_time,
    epoch_to_day,
)


# ── Unit conversion tests ────────────────────────────────────────────────────

def test_celsius_to_fahrenheit():
    assert celsius_to_fahrenheit(0) == 32.0
    assert celsius_to_fahrenheit(100) == 212.0
    assert round(celsius_to_fahrenheit(20), 1) == 68.0


def test_fahrenheit_to_celsius():
    assert fahrenheit_to_celsius(32) == 0.0
    assert fahrenheit_to_celsius(212) == 100.0
    assert round(fahrenheit_to_celsius(68), 1) == 20.0


def test_format_temp_metric():
    assert format_temp(20.5, "metric") == "20.5°C"


def test_format_temp_imperial():
    assert format_temp(68.9, "imperial") == "68.9°F"


def test_format_wind_metric():
    assert format_wind(3.5, "metric") == "3.5 m/s"


def test_format_wind_imperial():
    assert format_wind(7.8, "imperial") == "7.8 mph"


# ── Parse utilities ──────────────────────────────────────────────────────────

SAMPLE_CURRENT = {
    "name": "Addis Ababa",
    "sys": {"country": "ET", "sunrise": 1700000000, "sunset": 1700043600},
    "main": {
        "temp": 20.0, "feels_like": 19.0,
        "temp_min": 18.0, "temp_max": 22.0, "humidity": 55,
    },
    "weather": [{"description": "light rain", "icon": "10d"}],
    "wind": {"speed": 3.0, "deg": 180},
    "visibility": 10000,
}

SAMPLE_FORECAST = {
    "list": [
        {
            "dt": 1700010000 + i * 10800,
            "main": {"temp": 20.0 + i, "temp_min": 18.0, "temp_max": 22.0},
            "weather": [{"description": "clear sky", "icon": "01d"}],
        }
        for i in range(20)
    ]
}


def test_parse_current():
    result = parse_current(SAMPLE_CURRENT, "metric")
    assert result["city"] == "Addis Ababa"
    assert result["country"] == "ET"
    assert result["temp"] == 20.0
    assert result["humidity"] == 55
    assert result["description"] == "Light Rain"
    assert result["icon"] == "10d"
    assert result["unit"] == "metric"


def test_parse_hourly_count():
    result = parse_hourly(SAMPLE_FORECAST, 6)
    assert len(result) == 6


def test_parse_hourly_fields():
    result = parse_hourly(SAMPLE_FORECAST, 1)
    item = result[0]
    assert "time" in item
    assert "temp" in item
    assert "icon" in item
    assert "description" in item


def test_parse_daily_count():
    result = parse_daily(SAMPLE_FORECAST)
    assert 1 <= len(result) <= 5


def test_parse_daily_fields():
    result = parse_daily(SAMPLE_FORECAST)
    item = result[0]
    assert "day" in item
    assert "date" in item
    assert "temp_max" in item
    assert "temp_min" in item
    assert "icon" in item


# ── API layer tests (mocked) ─────────────────────────────────────────────────

def test_get_current_weather_empty_city():
    with pytest.raises(ValueError, match="empty"):
        get_current_weather("", "metric")


def test_get_current_weather_city_not_found(monkeypatch):
    mock_resp = MagicMock()
    mock_resp.status_code = 404
    monkeypatch.setenv("OPENWEATHER_API_KEY", "test-key")
    with patch("weather.requests.get", return_value=mock_resp):
        with pytest.raises(ValueError, match="not found"):
            get_current_weather("xyzxyz123", "metric")


def test_get_current_weather_invalid_key(monkeypatch):
    mock_resp = MagicMock()
    mock_resp.status_code = 401
    monkeypatch.setenv("OPENWEATHER_API_KEY", "bad-key")
    with patch("weather.requests.get", return_value=mock_resp):
        with pytest.raises(ValueError, match="Invalid API key"):
            get_current_weather("London", "metric")


def test_get_current_weather_success(monkeypatch):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = SAMPLE_CURRENT
    monkeypatch.setenv("OPENWEATHER_API_KEY", "test-key")
    with patch("weather.requests.get", return_value=mock_resp):
        result = get_current_weather("Addis Ababa", "metric")
        assert result["name"] == "Addis Ababa"


def test_get_forecast_success(monkeypatch):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = SAMPLE_FORECAST
    monkeypatch.setenv("OPENWEATHER_API_KEY", "test-key")
    with patch("weather.requests.get", return_value=mock_resp):
        result = get_forecast("Addis Ababa", "metric")
        assert "list" in result


def test_detect_city_from_ip_success():
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"city": "Addis Ababa"}
    with patch("weather.requests.get", return_value=mock_resp):
        city = detect_city_from_ip()
        assert city == "Addis Ababa"


def test_detect_city_from_ip_failure():
    import requests as req
    with patch("weather.requests.get", side_effect=req.exceptions.RequestException("Network error")):
        city = detect_city_from_ip()
        assert city == ""
