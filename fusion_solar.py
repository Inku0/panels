from datetime import datetime
from json import loads
from logging import getLogger
from time import time
from requests import get

from playwright.sync_api import Playwright, expect


logger = getLogger(__name__)


def get_session(playwright: Playwright, url: str, username: str, password: str) -> str:
  """
  Gets the "dp-session" cookie from the management panel.
  :param playwright: A Playwright instance
  :param url: The URL which provides the login page
  :param username: Username for logging in
  :param password: Password for logging in
  :return: The "dp-session" cookie's value
  """
  browser = playwright.chromium.launch(headless=True)
  context = browser.new_context()
  page = context.new_page()
  page.goto(url=url)
  page.get_by_role("textbox", name="Username/Email").click()
  page.get_by_role("textbox", name="Username/Email").fill(username)
  page.get_by_role("textbox", name="Password").click()
  page.get_by_role("textbox", name="Password").fill(password)
  page.locator("#submitDataverify").click()
  expect(page.locator("canvas").nth(1)).to_be_visible(timeout=30000)
  cookies = context.cookies()
  # params = context.
  context.close()
  browser.close()

  for cookie in cookies:
    if cookie["name"] == "dp-session":
      return cookie["value"]

  raise Exception(f"failed to get session cookie from {cookies}")

def get_current_usage(session_cookie: str, station_dn: str, time_dim: str, time_zone: str, subdomain: str) -> float:
  """
  Gets the current energy usage in kilowatts.
  :param session_cookie: The "dp-session" cookie's value
  :param station_dn: Not sure what this controls, perhaps it's the plant's ID?
  :param time_dim: Seems to be the UTC timezone offset as a float
  :param time_zone: Timezone as Country/City
  :param subdomain: Management URL's subdomain, usually something like uni023eu5
  :return: Current energy usage in kilowatts
  """
  cookies = {
    'dp-session': session_cookie,
  }

  headers = {
    'Accept': 'application/json',
    'Connection': 'keep-alive',
  }

  now: int = round(time())
  params = {
    #
    'stationDn': station_dn,
    'timeDim': time_dim,
    'timeZone': time_zone,
    'queryTime': now,
    'dateStr': datetime.now().strftime("%Y-%m-%d") + " 00:00:00",
    '_': now + 53403377, # not sure what this controls, a request i captured was set to this
  }

  r = get(
    f'https://{subdomain}.fusionsolar.huawei.com/rest/pvms/web/station/v3/overview/energy-balance',
    params=params,
    cookies=cookies,
    headers=headers,
  )

  parsed = loads(r.text)
  usages: list[str] = parsed["data"]["usePower"]

  boundary: int = usages.index("--")
  if boundary - 1 < 0:
    raise Exception("no power usage data")

  return float(usages[boundary - 1])