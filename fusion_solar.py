import html
import json
import logging
import requests


logger = logging.getLogger(__name__)

def get_solar_power(url: str) -> float:
  """
  Gets a Fusion Solar panel plant's current power output in kilowatts.
  :param url: The URL where the "kiosk version" gets its data from
  :return: real-time power output in kW (currently has a noticeable delay)
  """

  # TODO these kiosk URLs have a big delay and they only last a year, a better solution would be helpful
  r = requests.get(url)
  if r.status_code != 200:
    logger.error(f"failed to get solar power: {r.text}")

  response: dict[str, str] = json.loads(r.text)
  unescaped_content = html.unescape(response["data"])
  parsed_content = json.loads(unescaped_content)

  return parsed_content["realKpi"]["realTimePower"]