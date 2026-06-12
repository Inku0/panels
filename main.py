from time import sleep
import sys

from fusion_solar_py.client import FusionSolarClient
import logging
import os

from shelly import Shelly
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


def get_required_env_var(name: str) -> str:
  """
  Retrieve an environment variable and exit with an error if it's missing or empty.
  """
  value = os.getenv(name)
  if not value:
    logger.error(f"Required environment variable '{name}' is not set or is empty.")
    sys.exit(1)
  return value

def main():
  logging.basicConfig(level=logging.INFO)

  cloud_server = get_required_env_var("CLOUD_SERVER")
  cloud_auth_key = get_required_env_var("CLOUD_AUTH_KEY")
  cloud_devices_raw = get_required_env_var("CLOUD_DEVICES")
  devices = cloud_devices_raw.split(",")

  fusion_solar_username = get_required_env_var("FUSION_SOLAR_USERNAME")
  fusion_solar_password = get_required_env_var("FUSION_SOLAR_PASSWORD")
  fusion_solar_subdomain = get_required_env_var("FUSION_SOLAR_SUBDOMAIN")

  solar = FusionSolarClient(fusion_solar_username, fusion_solar_password, huawei_subdomain=fusion_solar_subdomain)

  # Shelly limits all API requests to 1 per second!
  shelly = Shelly(cloud_server, cloud_auth_key)
  shelly.add_devices(devices)

  if solar.get_power_status().current_power_kw >= 7:
    shelly.set_status(True)
  elif solar.get_power_status().current_power_kw < 5:
    shelly.set_status(False)

if __name__ == "__main__":
  main()