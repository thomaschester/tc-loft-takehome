from src.main import get_overhead_satellites, run

import requests
from unittest.mock import patch, MagicMock


API_URL = "https://api.fake.com/satellites"


@patch("src.main.requests.get")
def test_get_overhead_satellites_happy(mock_get) -> None:
    mock_get.return_value.json.return_value = {
        "info": {"satcount": 2},
        "above": [{"satid": 123}, {"satid": 456}],
    }
    assert get_overhead_satellites(API_URL) == {"123", "456"}


@patch("src.main.requests.get")
def test_get_overhead_satellites_api_error(mock_get) -> None:
    mock_get.return_value.json.return_value = {"error": "something went wrong"}
    assert get_overhead_satellites(API_URL) == set()


@patch("src.main.requests.get")
def test_get_overhead_satellites_requests_timeout(mock_get) -> None:
    mock_get.side_effect = requests.exceptions.RequestException("timeout")
    assert get_overhead_satellites(API_URL) == set()


@patch("src.main.requests.get")
def test_get_overhead_satellites_bad_resp(mock_get) -> None:
    mock_get.return_value.json.return_value = {"unexpected": "format"}
    assert get_overhead_satellites(API_URL) == set()


@patch("src.main.get_overhead_satellites")
def test_run_sends_command(mock_get_overhead) -> None:
    mock_get_overhead.return_value = {"123", "456"}

    controller: MagicMock = MagicMock()
    run({"123"}, controller, "https://api.fake.com/satellites")

    controller.send_cmd.assert_called_once_with({"123"})


@patch("src.main.get_overhead_satellites")
def test_run_skips_command(mock_get_overhead) -> None:
    mock_get_overhead.return_value = {"456", "789"}

    controller: MagicMock = MagicMock()
    run({"123"}, controller, "https://api.fake.com/satellites")

    controller.send_cmd.assert_not_called()
