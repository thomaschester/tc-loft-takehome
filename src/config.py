from dotenv import load_dotenv
from enum import Enum
import json
import logging
from os import environ
from typing import Any, Dict


class OutputMode(Enum):
    STDOUT = 1
    FILE = 2
    TCP = 3


class ConfigurationError(Exception):
    pass


def is_config_valid(config: Dict[str, Any]) -> bool:
    """
    Description: Passes or fails the provided config.json file. Some inputs are skipped and defaults used if they're missing.
    Args:
        config dictionary, loaded from config.json
    Returns:
        bool: Pass/fail flag.
    """
    if not config.get("interval_seconds"):
        logger.error("'interval_seconds: int' is a required config.json parameter")
        return False

    mode = config.get("output_mode")
    if not mode or mode not in [1, 2, 3]:
        logger.error(
            "'output_mode: int' is a required config.json parameter. 'output_mode' must be either 1 (STDOUT), 2 (FILE), or 3 (TCP)"
        )
        return False
    if OutputMode(mode) == OutputMode.TCP and (
        not config.get("tcp_ip") or not config.get("tcp_port")
    ):
        logger.error(
            "'tcp_ip: str' and 'tcp_port: str' are required config.json parameters when 'output_mode' is set to 3 (TCP)"
        )
        return False

    if not config.get("satellites"):
        logger.error(
            "'satellites: Dict[str, str]' is a required config.json parameter. key/value pair in 'satellites' must follow the convention: {'NORAD_SAT_ID': 'HEX_COLOR_CODE'}"
        )
        return False

    return True


def get_url_from_config(config: Dict[str, Any]) -> str:
    """
    Description: Returns a url from the config dictionary inputs. Default values are used for missing inputs.
    Args:
        config dictionary, loaded from config.json
    Returns:
        str: Third-party API path url with the API key as a url param
    """
    altitude: str = config.get("office_position", {}).get("altitude_meters", "0")
    category_id: str = config.get("satellite_category_id", "0")
    latitude: str = config.get("office_position", {}).get("latitude", "0.0")
    longitude: str = config.get("office_position", {}).get("longitude", "0.0")
    search_radius: str = config.get("search_radius_deg", "10")

    return f"{SAT_BASE_URL}/above/{latitude}/{longitude}/{altitude}/{search_radius}/{category_id}?apiKey={SAT_POSITION_API_KEY}"


def get_config() -> Dict[str, Any]:
    """
    Description: Validates config.json and returns the config
    Returns:
        Dict[str, Any]: config parameters
    """
    logger.info("Loading and validating config.json")

    config: Dict[str, Any] = {}
    with open("config.json", "r", encoding="utf-8") as file:
        config = json.load(file)

    if not is_config_valid(config):
        raise ConfigurationError("Invalid configuration")

    return config


load_dotenv()

DEBUG = environ.get("DEBUG", "0") == "1"
logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

SAT_BASE_URL = "https://api.n2yo.com/rest/v1/satellite/"
SAT_POSITION_API_KEY = environ.get("SAT_POSITION_API_KEY")
if not SAT_POSITION_API_KEY:
    raise ConfigurationError("SAT_POSITION_API_KEY missing from .env file")
