from zoneinfo import ZoneInfo
from datetime import datetime
from os import getenv
import logging

from playwright.sync_api import sync_playwright
from suntime.suntime import Sun
from fusion_solar_py.client import FusionSolarClient
from shelly import Shelly
from dotenv import load_dotenv

from fusion_solar import get_session, get_current_usage

logger = logging.getLogger(__name__)

def get_required_env_var(name: str) -> str:
  """
  Retrieve an environment variable and exit with an error if it's missing or empty.
  :return: the value of the given variable
  """
  value = getenv(name)
  if not value:
    raise Exception(f"Required environment variable '{name}' is not set or is empty.")

  return value

def sun_check():
  """
  Checks if the Sun is up.
  :return: True if the Sun is up, False otherwise.
  """
  latitude: str = get_required_env_var("LATITUDE")
  longitude: str = get_required_env_var("LONGITUDE")
  timezone: str = get_required_env_var("TIMEZONE")

  tz = ZoneInfo(timezone)
  sun = Sun(float(latitude), float(longitude))

  sun_up: datetime = sun.get_sunrise_time(time_zone=tz)
  now: datetime = datetime.now(tz=tz)

  logger.debug(f"Right now: {now}, Sun rises: {sun_up}")
  return sun_up <= now

def production_usage_delta():
  """
  Calculates the difference between energy production and usage.
  :return: energy_production - energy_usage
  """
  fusion_solar_username: str = get_required_env_var("FUSION_SOLAR_USERNAME")
  fusion_solar_password: str = get_required_env_var("FUSION_SOLAR_PASSWORD")
  fusion_solar_url: str = get_required_env_var("FUSION_SOLAR_URL")
  fusion_solar_subdomain: str = get_required_env_var("FUSION_SOLAR_SUBDOMAIN")
  station_dn: str = get_required_env_var("STATION_DN")
  time_dim: str = get_required_env_var("TIME_DIM")
  time_zone: str = get_required_env_var("TIME_ZONE")

  solar = FusionSolarClient(
    username=fusion_solar_username,
    password=fusion_solar_password,
    huawei_subdomain=fusion_solar_subdomain
  )

  current_production: float = solar.get_power_status().current_power_kw

  session_cookie: str = ""
  with sync_playwright() as playwright:
    session_cookie: str = get_session(
      playwright=playwright,
      url=fusion_solar_url,
      username=fusion_solar_username,
      password=fusion_solar_password
    )

  if not session_cookie:
    raise Exception("Session cookie is empty.")

  current_usage: float = get_current_usage(
    session_cookie=session_cookie,
    station_dn=station_dn,
    time_dim=time_dim,
    time_zone=time_zone,
    subdomain=fusion_solar_subdomain
  )

  logger.debug(f"Current production: {current_production}, current usage: {current_usage}")
  return current_production - current_usage

def main():
  load_dotenv()
  logging.basicConfig(level=logging.INFO)

  if not sun_check():
    logger.info("The Sun isn't up. Skipping poll.")
    return

  cloud_server: str = get_required_env_var("CLOUD_SERVER")
  cloud_auth_key: str = get_required_env_var("CLOUD_AUTH_KEY")
  cloud_devices_raw: str = get_required_env_var("CLOUD_DEVICES")
  devices: list[str] = cloud_devices_raw.split(",")

  # Shelly limits all API requests to 1 per second!
  shelly = Shelly(cloud_server, cloud_auth_key)
  shelly.add_devices(devices)

  delta = production_usage_delta()

  if delta >= 0:
    all_devices: dict[str, bool] = shelly.get_active()
    inactive_devices: list[str] = []

    for device in all_devices.keys():
      # TODO better version?
      if not all_devices[device]:
        inactive_devices.append(device)

    if len(inactive_devices) == 0:
      logger.debug(f"all devices in {all_devices} are already active.")
      return

    shelly.set_status(status=True, devices=inactive_devices)

  else:
    all_devices: dict[str, bool] = shelly.get_active()
    active_devices: list[str] = []

    for device in all_devices.keys():
      # TODO better version?
      if all_devices[device]:
        active_devices.append(device)

    if len(active_devices) == 0:
      logger.debug(f"all devices in {all_devices} are already inactive.")
      return

    shelly.set_status(status=False, devices=active_devices)

if __name__ == "__main__":
  main()