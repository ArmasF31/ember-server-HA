"""Config flow for Ember Mug integration."""

from __future__ import annotations

from collections.abc import Mapping

from bleak import BleakScanner
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import (
    CONF_ADDRESS,
    CONF_DEVICE_TYPE,
    CONF_SCAN_INTERVAL,
    DEFAULT_DEVICE_TYPE,
    DEFAULT_SCAN_INTERVAL,
    DEVICE_TYPE_MUG,
    DEVICE_TYPE_TUMBLER,
    DOMAIN,
    SERVICE_UUID,
)


async def discover_ember_devices() -> list[tuple[str, str]]:
    """Return discovered Ember-like BLE devices as (address, label)."""
    devices = await BleakScanner.discover(timeout=5.0)
    found: list[tuple[str, str]] = []

    for device in devices:
        name = (device.name or "").strip()
        uuids = [u.lower() for u in (device.metadata.get("uuids") or [])]
        looks_like_ember = "ember" in name.lower() or SERVICE_UUID.lower() in uuids
        if not looks_like_ember:
            continue
        label = f"{name or 'Ember device'} ({device.address})"
        found.append((device.address, label))

    found.sort(key=lambda item: item[1].lower())
    return found


class EmberMugConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle Ember Mug setup."""

    VERSION = 2

    async def async_step_user(self, user_input: dict | None = None) -> FlowResult:
        errors: dict[str, str] = {}

        discovered = await discover_ember_devices()
        discovered_addresses = {address for address, _ in discovered}

        if user_input is not None:
            selected_address = user_input.get("discovered_device")
            manual_address = user_input.get(CONF_ADDRESS, "").strip()
            address = selected_address if selected_address and selected_address != "manual" else manual_address

            if not address:
                errors["base"] = "address_required"
            else:
                await self.async_set_unique_id(address)
                self._abort_if_unique_id_configured()

                data = {
                    CONF_ADDRESS: address,
                    CONF_SCAN_INTERVAL: user_input[CONF_SCAN_INTERVAL],
                    CONF_DEVICE_TYPE: user_input[CONF_DEVICE_TYPE],
                }
                title_type = "Tumbler" if user_input[CONF_DEVICE_TYPE] == DEVICE_TYPE_TUMBLER else "Mug"
                return self.async_create_entry(title=f"Ember {title_type} {address}", data=data)

        discovered_choices: dict[str, str] = {address: label for address, label in discovered}
        discovered_choices["manual"] = "Manual entry"

        default_discovered = next(iter(discovered_addresses), "manual")

        schema = vol.Schema(
            {
                vol.Required("discovered_device", default=default_discovered): vol.In(discovered_choices),
                vol.Optional(CONF_ADDRESS, default=""): str,
                vol.Required(CONF_DEVICE_TYPE, default=DEFAULT_DEVICE_TYPE): vol.In(
                    {
                        DEVICE_TYPE_MUG: "Mug",
                        DEVICE_TYPE_TUMBLER: "Tumbler",
                    }
                ),
                vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(
                    vol.Coerce(int), vol.Range(min=5, max=300)
                ),
            }
        )

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @staticmethod
    def async_get_options_flow(config_entry):
        return EmberMugOptionsFlow(config_entry)


class EmberMugOptionsFlow(config_entries.OptionsFlow):
    """Options flow for scan interval and type."""

    def __init__(self, config_entry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input: Mapping[str, str | int] | None = None) -> FlowResult:
        if user_input is not None:
            return self.async_create_entry(title="", data=dict(user_input))

        schema = vol.Schema(
            {
                vol.Optional(
                    CONF_SCAN_INTERVAL,
                    default=self.config_entry.options.get(
                        CONF_SCAN_INTERVAL,
                        self.config_entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
                    ),
                ): vol.All(vol.Coerce(int), vol.Range(min=5, max=300)),
                vol.Optional(
                    CONF_DEVICE_TYPE,
                    default=self.config_entry.options.get(
                        CONF_DEVICE_TYPE,
                        self.config_entry.data.get(CONF_DEVICE_TYPE, DEFAULT_DEVICE_TYPE),
                    ),
                ): vol.In({DEVICE_TYPE_MUG: "Mug", DEVICE_TYPE_TUMBLER: "Tumbler"}),
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
