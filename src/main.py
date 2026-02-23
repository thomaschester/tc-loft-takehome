from .config import get_config, get_url_from_config, logger, OutputMode
from .light_control import LightController
import requests
import time
from typing import Any, Dict, Set


def get_overhead_satellites(api_url: str) -> Set[str]:
    """
    Description: Handles API GET request for overhead satellites
    Args:
        API URL
    Returns:
        Set[str]: Overhead satellite ID's
    """
    try:
        resp: Dict[str, Any] = requests.get(api_url, timeout=10).json()
        logger.debug("resp=%s", resp)
        if resp.get("error"):
            logger.error("API Error response: %s", resp["error"])
            return set()
        logger.info("%s overhead satellites found", resp["info"]["satcount"])
        return set([str(sat["satid"]) for sat in resp["above"]])
    except requests.exceptions.RequestException as e:
        logger.error("API request error: %s", str(e))
        return set()
    except (KeyError, ValueError) as e:
        logger.error("Unexpected API response format: %s", str(e))
        return set()


def run(config_sat_ids: Set[str], controller: LightController, api_url: str) -> None:
    """
    Description: Main function called every 10 seconds to get satellite data and control lights.
    Matches satellites ID's from the config with overhead satellites returned by API; commands the
    lights if a match is found.
    Args:
        Satellite ID's from the config, Light Controller singleton, API URL
    Returns:
        None, logs whether satellites were found and light command was sent
    """
    overhead_sat_ids: Set[str] = get_overhead_satellites(api_url)
    matching_sat_ids: Set[str] = config_sat_ids & overhead_sat_ids
    if len(matching_sat_ids):
        logger.info("Found matching satellite id's - sending light commands")
        controller.send_cmd(matching_sat_ids)
    else:
        logger.info("No satellites matching the config were found")


if __name__ == "__main__":
    config = get_config()

    interval: int = config["interval_seconds"]
    output_mode: OutputMode = config["output_mode"]
    satellites: Dict[str, str] = config["satellites"]
    tcp_ip: str | None = config.get("tcp_ip")
    tcp_port: str | None = config.get("tcp_port")

    satellite_ids: Set[str] = set(satellites.keys())
    light_controller: LightController = LightController(
        satellites=satellites, output_mode=output_mode, tcp_ip=tcp_ip, tcp_port=tcp_port
    )
    url: str = get_url_from_config(config)

    while True:
        run(satellite_ids, light_controller, url)
        time.sleep(interval)
