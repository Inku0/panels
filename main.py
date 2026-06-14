from playwright.sync_api import sync_playwright

from fusion_solar import get_session, get_current_usage
import zoneinfo
from datetime import datetime
from suntime.suntime import Sun
import sys

from fusion_solar_py.client import FusionSolarClient
import logging
import os

from shelly import Shelly
from dotenv import load_dotenv

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
  load_dotenv()
  logging.basicConfig(level=logging.INFO)

  latitude = get_required_env_var("LATITUDE")
  longitude = get_required_env_var("LONGITUDE")
  timezone = get_required_env_var("TIMEZONE")
  tz = zoneinfo.ZoneInfo(timezone)
  sun = Sun(float(latitude), float(longitude))
  sun_up: datetime = sun.get_sunrise_time(time_zone=tz)

  now = datetime.now(tz=tz)
  is_sun_up = sun_up <= now

  if not is_sun_up:
    logger.info("Sun hasn't risen or has set. Skipping poll.")
    sys.exit(0)

  cloud_server = get_required_env_var("CLOUD_SERVER")
  cloud_auth_key = get_required_env_var("CLOUD_AUTH_KEY")
  cloud_devices_raw = get_required_env_var("CLOUD_DEVICES")
  devices = cloud_devices_raw.split(",")

  fusion_solar_username = get_required_env_var("FUSION_SOLAR_USERNAME")
  fusion_solar_password = get_required_env_var("FUSION_SOLAR_PASSWORD")
  fusion_solar_url = get_required_env_var("FUSION_SOLAR_URL")
  fusion_solar_subdomain = get_required_env_var("FUSION_SOLAR_SUBDOMAIN")
  station_dn = get_required_env_var("STATION_DN")
  time_dim = get_required_env_var("TIME_DIM")
  time_zone = get_required_env_var("TIME_ZONE")

  solar = FusionSolarClient(fusion_solar_username, fusion_solar_password, huawei_subdomain=fusion_solar_subdomain)

  session_cookie = ""
  with sync_playwright() as playwright:
    session_cookie = get_session(playwright, url=fusion_solar_url, username=fusion_solar_username, password=fusion_solar_password)
  if not session_cookie:
    logger.error("Session cookie is empty")
    sys.exit(1)

  current_usage = get_current_usage(session_cookie=session_cookie, station_dn=station_dn, time_dim=time_dim, time_zone=time_zone, subdomain=fusion_solar_subdomain)

  # Shelly limits all API requests to 1 per second!
  shelly = Shelly(cloud_server, cloud_auth_key)
  shelly.add_devices(devices)
  current_production: float = solar.get_power_status().current_power_kw

  if current_production >= current_usage:
    all_devices = shelly.get_active()
    inactive_devices: list[str] = []
    for device in all_devices.keys():
      # TODO better version?
      if not all_devices[device]:
        inactive_devices.append(device)
    if len(inactive_devices) == 0:
      return
    shelly.set_status(status=True, devices=inactive_devices)
  else:
    all_devices = shelly.get_active()
    active_devices: list[str] = []
    for device in all_devices.keys():
      # TODO better version?
      if all_devices[device]:
        active_devices.append(device)
    if len(active_devices) == 0:
      return
    shelly.set_status(status=False, devices=active_devices)

if __name__ == "__main__":
  main()