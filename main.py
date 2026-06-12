from time import sleep
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

  cloud_auth_key = os.getenv("CLOUD_AUTH_KEY")
  if not cloud_auth_key:
    logger.error("CLOUD_AUTH_KEY environment variable not set")
    exit(1)

  cloud_devices = os.getenv("CLOUD_DEVICES")
  if not cloud_devices:
    logger.error("CLOUD_DEVICES environment variable not set")
    exit(1)
  else:
    devices = cloud_devices.split(",")

  shelly = Shelly(cloud_server, cloud_auth_key)

  # Shelly limits all API requests to 1 per second!

  shelly.add_devices(devices)
  print(shelly.get_online())
  shelly.set_offline()

if __name__ == "__main__":
  main()