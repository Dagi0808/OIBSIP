# Python Weather App

**Dagmawit Dagne — OIBSIP Python Programming — Task 4 (Advanced)**

---

## Overview

A Python desktop weather application that fetches and displays real-time weather data using the OpenWeatherMap API. Built with tkinter for the GUI, it supports current conditions, hourly and 5-day forecasts, unit toggling, dark/light themes, and automatic location detection.

---

## Features

- Auto-detects your city from your IP address on startup
- Current weather: temperature, feels like, high/low, humidity, wind speed, visibility, sunrise/sunset
- Weather icons from OpenWeatherMap
- Hourly forecast: next 6 hours with icons and temperatures
- 5-day daily forecast with high/low temperatures
- Celsius / Fahrenheit toggle
- Dark and light theme toggle
- Full error handling: empty input, city not found, network timeout, invalid API key
- Input validation: rejects empty city names
- Scrollable results panel

---

## Tech Stack

| Component | Technology |
|---|---|
| Language | Python 3.8+ |
| GUI | tkinter (built-in) |
| Icons | Pillow (PIL) |
| Weather API | OpenWeatherMap (free tier) |
| IP Location | ipinfo.io (free, no key needed) |
| HTTP | requests |
| Config | python-dotenv |
| Tests | pytest |

---

## Installation

```bash
# 1. Navigate to the project folder
cd OIBSIP/Python-Task4-WeatherApp

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up your API key
cp .env.example .env
# Edit .env and add your OpenWeatherMap API key
```

---

## Environment Variables

```env
OPENWEATHER_API_KEY=your_openweathermap_api_key_here
```

Get a free API key at [openweathermap.org](https://openweathermap.org/api).

> Never commit your real `.env` file. It is excluded by `.gitignore`.

---

## Usage

```bash
source .venv/bin/activate
python main.py
```

The app opens, auto-detects your city, and loads the weather immediately. You can also type any city name and press Enter or click **Get Weather**.

---

## Supported Features by Tier

### Beginner Tier ✅
- City name input
- API call + JSON parsing
- Temperature (°C and °F), humidity, condition, wind speed
- Graceful error handling
- Input validation

### Advanced Tier ✅
- GUI window with input field, button, and results panel
- Weather icons
- Hourly forecast (next 6 hours)
- 5-day daily forecast
- °C/°F unit toggle
- Automatic location detection via ipinfo.io (bonus)
- Error messages inside the GUI

---

## Project Structure

```
Python-Task4-WeatherApp/
├── main.py          # Entry point
├── gui.py           # tkinter GUI — all UI components
├── weather.py       # API layer — current weather, forecast, IP detection
├── utils.py         # Helpers — parsing, formatting, icon loading
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── assets/
│   └── icons/       # Cached weather icons (gitignored)
├── screenshots/
└── tests/
    └── test_weather.py
```

---

## Screenshots

> Screenshots will be added after the demo recording.

---

## Demo

> Demo video will be linked here after recording.

---

## Privacy Considerations

- Your OpenWeatherMap API key is stored only in the local `.env` file, which is excluded from version control.
- IP-based location uses ipinfo.io with no personal data sent beyond your IP address.
- No user data is stored or transmitted beyond the API calls needed for weather data.

---

## Future Improvements

- Add weather alerts and severe weather warnings
- Add precipitation probability to forecasts
- Support searching by ZIP code
- Add a favorites/history list for recent cities
- Package as a standalone desktop app (.deb or AppImage)
