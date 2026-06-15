from time import sleep
from json import loads, dumps
from requests import post
from logging import getLogger


ERR_NO_DEVICES = "no devices available, try adding some with add_devices()"

# TODO: this should be refactored so that a class instance corresponds to a device, not a huge controller class

class Shelly:
  def __init__(self, server: str, key: str) -> None:
    self.server: str = server
    self.key: str = key
    self.devices: list[str] = []
    self.logger = getLogger(__name__)

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
      raise Exception(ERR_NO_DEVICES)

    data = {"ids":self.devices,"select":["status"],"pick":{"status":["sys"]}}
    r = post(
      url=f"{self.server}/v2/devices/api/get?auth_key={self.key}",
      headers={"Content-Type": "application/json"},
      data=dumps(data)
    )

    if r.status_code != 200:
      raise Exception(f"shelly returned an error: {r.text}")

    online: dict[str, bool] = {}
    for device in loads(r.text):
      online[device["id"]] = (device["online"] == 1)

    return online

  def get_active(self) -> dict[str, bool]:
    """
    Returns a dictionary where each device corresponds to an entry.
    A device's ID is the key, its active status (i.e., whether it's working) as a boolean is the value.
    """
    if not self.devices:
      raise Exception(ERR_NO_DEVICES)

    data = {"ids":self.devices,"select":["status"],"pick":{"status":["switch:1"]}}
    # switch:1 seems to control the actual power output, not sure what switch:0 is for
    r = post(
      url=f"{self.server}/v2/devices/api/get?auth_key={self.key}",
      headers={"Content-Type": "application/json"},
      data=dumps(data)
    )

    if r.status_code != 200:
      raise Exception(f"shelly returned an error: {r.text}")

    active: dict[str, bool] = {}
    for device in loads(r.text):
      active[device["id"]] = (device["status"]["switch:1"]["output"] == True)

    return active

  def set_status(self, status: bool, devices: list[str] | None = None) -> None:
    """
    Turns devices on or off.
    :param status: True or False aka on or off.
    :param devices: List of devices to turn on or off. If unset, then all added devices are turned off.
    """
    if not self.devices:
      raise Exception(ERR_NO_DEVICES)

    if not devices:
      devices = self.devices

    for device in devices:
      sleep(1) # Shelly limits all API requests to 1 per second!

      data = {"id": device, "on": status, "channel": 1}
      # i've got no idea why the channel needs to be set to 1
      # the default channel is 0, but the POST request just didn't do anything when channel = 0
      # more info: the switch seems to have two channels (0 and 1) with separate temperatures and output values
      # not sure what they represent, though
      r = post(
        url=f"{self.server}/v2/devices/api/set/switch?auth_key={self.key}",
        headers={"Content-Type": "application/json"},
        data=dumps(data)
      )
      if r.status_code != 200:
        raise Exception(f"shelly returned an error while turning {"on" if status == True else "off"} device {device}: {r.text}")

      self.logger.info(f"turned {"on" if status == True else "off"} device {device}")
