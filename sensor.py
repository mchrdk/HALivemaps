import json
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.entity import Entity
import logging
from bs4 import BeautifulSoup
import requests
import json
from requests_ntlm import HttpNtlmAuth


_LOGGER = logging.getLogger(__name__)

DOMAIN = 'livemaps'

def get_alerts(url, username, password):
    """This function will run in the executor pool and not block the event loop."""
    session = requests.Session()
    session.auth = HttpNtlmAuth(username, password)
    response = session.get(url)
    decoded_content = response.content.decode('utf-16le')
    soup = BeautifulSoup(decoded_content, 'html.parser')
    table = soup.find('table', attrs={'id': 't02'})
    headers = [header.get_text() for header in table.find_all('th')]
    rows = table.find_all('tr')
    data = []

    for row in rows:
        cols = row.find_all('td')
        cols_text = [col.get_text().strip() for col in cols]
        if cols_text:
            data.append(dict(zip(headers, cols_text)))
    return data

async def async_setup_entry(hass, entry, async_add_devices):
    """Set up the LiveMaps sensor platform."""
    config = entry.data
    async_add_devices([LiveMapsSensor(config, hass)])


def setup(hass, config):
    """Set up the LiveMaps integration."""
    hass.data.setdefault(DOMAIN, {})
    hass.async_create_task(
        hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": config_entries.SOURCE_IMPORT},
            data={},
        )
    )
    return True

class LiveMapsSensor(Entity):
    def __init__(self, config, hass):
        self._state = "ok"
        self._alerts = []
        self._config = config
        self._hass = hass
        self._unique_id = f"{DOMAIN}_livemaps"

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._unique_id

    @property
    def name(self):
        return "livemaps"

    @property
    def state(self):
        return self._state

    @property
    def device_state_attributes(self):
        return {"alerts": self._alerts}

    async def async_update(self):
        url = self._config["url"]
        username = self._config["username"]
        password = self._config["password"]
        connection_type = self._config["connection_type"]
        _LOGGER.debug(username)

        self._alerts = []
        self._state = "ok"
        _LOGGER.debug(connection_type)

        if connection_type == "https":
            try:
                data = await self._hass.async_add_executor_job(get_alerts, url, username, password)
            except Exception as e:
                _LOGGER.debug(f"HTTPS call failed, Caught an exception: {e}")
                return
                    
        elif connection_type == "file":
            try:
                with open("data.json") as f:
                    data = json.load(f)
            except FileNotFoundError:
                _LOGGER.debug('data.json not found')
                return

        for alert in data:
            if alert["Priority"] == "P1":
                self._state = "critical"
            elif alert["Priority"] == "P2" and self._state != "critical":
                self._state = "warning"

            self._alerts.append(alert)
