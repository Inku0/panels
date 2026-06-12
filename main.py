from fusion_solar import get_solar_power
import logging
import os

from shelly import Shelly
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

def main():
  logging.basicConfig(level=logging.INFO)

  cloud_server = os.getenv("CLOUD_SERVER")
  if not cloud_server:
    logger.error("CLOUD_SERVER environment variable not set")
    exit(1)

  fusion_solar_url = os.getenv("CLOUD_AUTH_KEY")
  if not fusion_solar_url:
    logger.error("CLOUD_AUTH_KEY environment variable not set")
    exit(1)

  cloud_devices = os.getenv("CLOUD_DEVICES")
  if not cloud_devices:
    logger.error("CLOUD_DEVICES environment variable not set")
    exit(1)
  else:
    devices = cloud_devices.split(",")

  fusion_solar_url = os.getenv("FUSION_SOLAR_URL")
  if not fusion_solar_url:
    logger.error("FUSION_SOLAR_URL environment variable not set")
    exit(1)

  shelly = Shelly(cloud_server, fusion_solar_url)
  # Shelly limits all API requests to 1 per second!
  shelly.add_devices(devices)

  print(get_solar_power(fusion_solar_url))

if __name__ == "__main__":
  main()