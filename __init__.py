from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant import config_entries


DOMAIN = 'livemaps'


async def async_setup(hass, config):
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data[DOMAIN][entry.entry_id] = LiveMapsSensor(entry.data)
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )
    return True


class LiveMapsSensor:
    def __init__(self, config):
        self.config = config
