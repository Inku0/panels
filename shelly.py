from time import sleep
import logging
import requests
import json


ERR_NO_DEVICES = "no devices available, try adding some with add_devices()"

class Shelly():
  def __init__(self, server: str, key: str) -> None:
    self.server: str = server
    self.key: str = key
    self.devices: list[str] = []
    self.logger = logging.getLogger(__name__)

  def add_devices(self, devices: list[str]) -> None:
    """
    Adds every device ID in the list to the class instance for use in other methods.
    """
    for device in devices:
      self.devices.append(device)

  def get_online(self) -> dict[str, bool]:
    """
    Returns a dictionary where each device corresponds to an entry.
    A device's ID is the key, its online status as a boolean is the value.
    """
    if not self.devices:
      self.logger.error(ERR_NO_DEVICES)
      return {}

    data = {"ids":self.devices,"select":["status"],"pick":{"status":["sys"]}}
    r = requests.post(
      url=f"{self.server}/v2/devices/api/get?auth_key={self.key}",
      headers={"Content-Type": "application/json"},
      data=json.dumps(data)
    )

    if r.status_code != 200:
      self.logger.error(f"shelly returned an error: {r.text}")
      return {}

    online: dict[str, bool] = {}
    for device in json.loads(r.text):
      online[device["id"]] = (device["online"] == 1)

    return online

  def set_offline(self, devices: list[str] | None = None) -> None:
    """
    Turns devices off.
    :param devices: List of devices to turn off. If unset, then all added devices are turned off.
    """
    if not self.devices:
      self.logger.error(ERR_NO_DEVICES)
      return

    if not devices:
      devices = self.devices

    for device in devices:
      sleep(1) # Shelly limits all API requests to 1 per second!

      data = {"id": device, "on": False, "channel": 1}
      # i've got no idea why the channel needs to be set to 1
      # the default channel is 0, but the POST request just didn't do anything when channel = 0
      r = requests.post(
        url=f"{self.server}/v2/devices/api/set/switch?auth_key={self.key}",
        headers={"Content-Type": "application/json"},
        data=json.dumps(data)
      )
      if r.status_code != 200:
        self.logger.error(f"shelly returned an error while turning off device {device}: {r.text}")
        return
      self.logger.info(f"turned off device {device}")
