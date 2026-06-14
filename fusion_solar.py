from datetime import datetime
import html
import json
import logging
import time

import requests
from playwright.sync_api import Playwright, expect


logger = logging.getLogger(__name__)


def get_session(playwright: Playwright, url: str, username: str, password: str) -> str:
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

  logger.error(f"failed to get session cookie from {cookies}")
  return ""

def get_current_usage(session_cookie: str, station_dn: str, time_dim: str, time_zone: str, subdomain: str) -> float:
  cookies = {
    'dp-session': session_cookie,
  }

  headers = {
    'Accept': 'application/json',
    'Connection': 'keep-alive',
  }

  now = round(time.time())
  params = {
    #
    'stationDn': station_dn,
    'timeDim': time_dim,
    'timeZone': time_zone,
    'queryTime': now,
    'dateStr': datetime.now().strftime("%Y-%m-%d") + " 00:00:00",
    '_': now + 53403377, # not sure what this controls, a request i captured was set to this
  }

  r = requests.get(
    f'https://{subdomain}.fusionsolar.huawei.com/rest/pvms/web/station/v3/overview/energy-balance',
    params=params,
    cookies=cookies,
    headers=headers,
  )

  parsed = json.loads(r.text)
  usages: list[str] = parsed["data"]["usePower"]

  boundary = usages.index("--")
  if boundary - 1 < 0:
    raise Exception("no power usage data")

  return float(usages[boundary - 1])

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