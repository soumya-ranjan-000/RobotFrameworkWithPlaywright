import json
import subprocess
import urllib.parse
from browserstack.local import Local

# Robot will treat module-level functions as keywords
ROBOT_LIBRARY_SCOPE = 'GLOBAL'

bs_local = None

desired_cap = {
    'browser_version': 'latest',
    'browserstack.username': 'soumyaranjanghad_FsCSGL',
    'browserstack.accessKey': 'cEWs6zvLtLsfdhKEN5r8',
    'project': 'BStack Project',
    'build': 'browserstack-build-1',
    'buildTag': 'Regression',
    'resolution': '1280x1024',
    'browserstack.local': 'false',
    'browserstack.localIdentifier': 'local_connection_name',
    'browserstack.playwrightVersion': '1.latest',
    'client.playwrightVersion': '1.latest',
    'browserstack.debug': 'true',
    'browserstack.console': 'info',
    'browserstack.networkLogs': 'true',
    'browserstack.networkLogsOptions': {
        'captureContent': 'true'
    }
}


def createCdpUrl(browser):
    """Create BrowserStack CDP URL for Playwright based on desired_cap and browser."""
    clientPlaywrightVersion = str(subprocess.getoutput('playwright --version')).strip().split(" ")[1]
    desired_cap['client.playwrightVersion'] = clientPlaywrightVersion
    if browser == 'chrome':
        desired_cap['os'] = 'Windows'
        desired_cap['os_version'] = '11'
        desired_cap['browser'] = 'chrome'
    elif browser == 'firefox':
        desired_cap['os'] = 'OS X'
        desired_cap['os_version'] = 'Ventura'
        desired_cap['browser'] = 'playwright-firefox'
    else:
        desired_cap['os'] = 'OS X'
        desired_cap['os_version'] = 'Ventura'
        desired_cap['browser'] = 'playwright-webkit'

    cdpUrl = 'wss://cdp.browserstack.com/playwright?caps=' + urllib.parse.quote(json.dumps(desired_cap))
    print(cdpUrl)
    return cdpUrl


def getPlatformDetails():
    """Return a readable string describing the selected platform."""
    platformDetails = (
        f"{desired_cap.get('os', '')} {desired_cap.get('os_version', '')} "
        f"{desired_cap.get('browser', '')} {desired_cap.get('browser_version', '')}"
    )
    print(platformDetails)
    return platformDetails


def startLocalTunnel():
    """Start BrowserStackLocal tunnel if not already running."""
    global bs_local
    if not bs_local:
        bs_local = Local()
        bs_local_args = {
            "key": desired_cap.get('browserstack.accessKey'),
            "localIdentifier": desired_cap.get('browserstack.localIdentifier')
        }
        bs_local.start(**bs_local_args)


def stopLocalTunnel():
    """Stop BrowserStackLocal tunnel if running."""
    global bs_local
    if bs_local:
        bs_local.stop()
        bs_local = None
