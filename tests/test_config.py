from src.config import (
    ConfigurationError,
    is_config_valid,
    get_config,
    get_url_from_config,
)

import pytest
from typing import Any, Dict
from unittest.mock import patch, mock_open
import json


VALID_CONFIG: Dict[str, Any] = {
    "interval_seconds": 10,
    "satellite_category_id": "0",
    "search_radius_deg": "10",
    "satellites": {
        "20344": "#3FA2C8",
        "22049": "#E74B1A",
        "23833": "#9D3FE8",
        "26486": "#2BC46A",
        "50484": "#F0A500",
        "53109": "#C23B8E",
        "20025": "#1DDFB3",
        "27847": "#FF5733",
        "26536": "#4B8EF0",
        "14129": "#A0E040",
        "10703": "#E84F4F",
        "9057": "#7B2FBE",
        "17018": "#00C9A7",
    },
    "office_position": {
        "altitude_meters": "0",
        "latitude": "37.77169633081985",
        "longitude": "-122.41352817204972",
    },
    "output_mode": 3,
    "tcp_ip": "127.0.0.1",
    "tcp_port": "5005",
}


@patch("builtins.open", mock_open(read_data=json.dumps(VALID_CONFIG)))
def test_get_config_valid() -> None:
    result: Dict[str, Any] = get_config()
    assert result == VALID_CONFIG


INVALID_CONFIG = VALID_CONFIG.copy()
INVALID_CONFIG["output_mode"] = 4


@patch("builtins.open", mock_open(read_data=json.dumps(INVALID_CONFIG)))
def test_get_config_invalid_raises() -> None:
    with pytest.raises(ConfigurationError):
        get_config()


@patch("builtins.open", side_effect=FileNotFoundError)
def test_get_config_missing_file(mock_file) -> None:
    with pytest.raises(FileNotFoundError):
        get_config()


@patch("src.config.SAT_POSITION_API_KEY", "fake_api_key")
@patch("src.config.SAT_BASE_URL", "https://api.fake.com/satellites")
def test_get_url_from_config() -> None:
    result: str = get_url_from_config(VALID_CONFIG)
    expected: str = (
        "https://api.fake.com/satellites/above/37.77169633081985/-122.41352817204972/0/10/0?apiKey=fake_api_key"
    )
    assert result == expected


VALID_CONFIG_MISSING_INPUTS = VALID_CONFIG.copy()
VALID_CONFIG_MISSING_INPUTS.pop("office_position")
VALID_CONFIG_MISSING_INPUTS.pop("satellite_category_id")
VALID_CONFIG_MISSING_INPUTS.pop("search_radius_deg")


@patch("src.config.SAT_POSITION_API_KEY", "fake_api_key")
@patch("src.config.SAT_BASE_URL", "https://api.fake.com/satellites")
def test_get_url_from_config_missing_inputs() -> None:
    result: str = get_url_from_config(VALID_CONFIG_MISSING_INPUTS)
    expected: str = (
        "https://api.fake.com/satellites/above/0.0/0.0/0/10/0?apiKey=fake_api_key"
    )
    assert result == expected


def test_is_config_valid_happy() -> None:
    assert is_config_valid(VALID_CONFIG) == True


def test_is_config_valid_missing_interval() -> None:
    VALID_CONFIG_MISSING_INTERVAL = VALID_CONFIG.copy()
    VALID_CONFIG_MISSING_INTERVAL.pop("interval_seconds")
    assert is_config_valid(VALID_CONFIG_MISSING_INTERVAL) == False


def test_is_config_valid_missing_output_mode() -> None:
    VALID_CONFIG_MISSING_OUTPUT_MODE = VALID_CONFIG.copy()
    VALID_CONFIG_MISSING_OUTPUT_MODE.pop("output_mode")
    assert is_config_valid(VALID_CONFIG_MISSING_OUTPUT_MODE) == False


def test_is_config_valid_missing_tcp_port() -> None:
    VALID_CONFIG_MISSING_TCP_PORT = VALID_CONFIG.copy()
    VALID_CONFIG_MISSING_TCP_PORT.pop("tcp_port")
    assert is_config_valid(VALID_CONFIG_MISSING_TCP_PORT) == False


def test_is_config_valid_missing_satellites() -> None:
    VALID_CONFIG_MISSING_SATS = VALID_CONFIG.copy()
    VALID_CONFIG_MISSING_SATS.pop("satellites")
    assert is_config_valid(VALID_CONFIG_MISSING_SATS) == False
