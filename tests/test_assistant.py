from src.assistant import get_response
from src.config import load_commands
from src.intents import detect_intent, extract_info
from src.weather import get_weather


def test_commands_config_has_weather_and_search():
    data = load_commands()
    names = {item.get("name") for item in data.get("commands", [])}
    assert "weather" in names
    assert "search" in names


def test_weather_uses_openweather_api(monkeypatch):
    class FakeResponse:
        status_code = 200

        def json(self):
            return {
                "weather": [{"description": "broken clouds"}],
                "main": {"temp": 21.5},
            }

    def fake_get(url, params=None, timeout=None):
        assert params["q"] == "Addis Ababa"
        assert "appid" in params
        return FakeResponse()

    monkeypatch.setenv("OPENWEATHER_API_KEY", "demo-key")
    monkeypatch.setattr("src.weather.requests.get", fake_get)
    result = get_weather("Addis Ababa")
    assert "Addis Ababa" in result
    assert "21.5" in result or "broken clouds" in result


def test_hello_response():
    response = get_response("hello")
    assert response == "Hello! How can I help you?"


def test_time_response():
    response = get_response("what time is it")
    assert "time" in response.lower()


def test_date_response():
    response = get_response("what date is it")
    assert "date" in response.lower()


def test_search_response():
    response = get_response("search for FastAPI tutorials")
    assert "fastapi" in response.lower()
    assert "google" in response.lower() or "search" in response.lower()


def test_weather_response():
    response = get_response("what is the weather in Addis Ababa")
    assert "addis" in response.lower() or "weather" in response.lower()


def test_reminder_response():
    response = get_response("remind me in 5 minutes to check my email")
    assert "remind" in response.lower() or "5" in response.lower()


def test_email_response():
    response = get_response("check my email")
    assert "checking inbox" in response.lower() or "email" in response.lower()


def test_custom_command_response():
    response = get_response("open my notes")
    assert "notes" in response.lower() or "custom" in response.lower()


def test_detect_weather_intent():
    intent = detect_intent("what is the weather in Addis Ababa")
    assert intent == "weather"


def test_extract_weather_city():
    info = extract_info("what is the weather in Addis Ababa")
    assert info["city"] == "Addis Ababa"


def test_unknown_response():
    response = get_response("what time is it")
    assert "time" in response.lower()
