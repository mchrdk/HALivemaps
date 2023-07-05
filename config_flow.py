from homeassistant import config_entries, core
import voluptuous as vol
from . import DOMAIN

class InvalidAuth(Exception):
    """Raise when the authentication credentials are invalid."""
    pass

async def validate_input(hass: core.HomeAssistant, data):
    # Validate the user input (optional, could also be done in the form itself)
    if "username" not in data or "password" not in data or "url" not in data:
        raise InvalidAuth

class LiveMapsFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            try:
                await validate_input(self.hass, user_input)
                return self.async_create_entry(title="LiveMaps", data=user_input)
            except InvalidAuth:
                errors["base"] = "invalid_auth"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("username"): str,
                    vol.Required("password"): str,
                    vol.Required("url"): str,
                    vol.Required("connection_type"): vol.In(["https", "file"]),
                }
            ),
            errors=errors,
        )
