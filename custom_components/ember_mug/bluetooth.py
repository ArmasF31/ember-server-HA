"""BLE protocol helpers for Ember Mug."""

from __future__ import annotations

from dataclasses import dataclass

from bleak import BleakClient

from .const import (
    CHAR_BATTERY,
    CHAR_CURRENT_TEMP,
    CHAR_LIQUID_LEVEL,
    CHAR_LIQUID_STATE,
    CHAR_TARGET_TEMP,
    LIQUID_STATES,
)


@dataclass(slots=True)
class EmberStatus:
    """All values exposed by the Ember mug."""

    current_temp_c: float | None
    target_temp_c: float | None
    battery_percent: int | None
    charging: bool | None
    liquid_state_code: int | None
    liquid_state: str | None
    liquid_level: int | None

    def as_dict(self) -> dict[str, float | int | bool | str | None]:
        """Dictionary representation used by API/UI code."""
        return {
            "current_temp_c": self.current_temp_c,
            "target_temp_c": self.target_temp_c,
            "battery_percent": self.battery_percent,
            "charging": self.charging,
            "liquid_state_code": self.liquid_state_code,
            "liquid_state": self.liquid_state,
            "liquid_level": self.liquid_level,
        }


async def read_status(address: str) -> EmberStatus:
    """Read all supported values from the mug over BLE."""
    async with BleakClient(address) as client:
        current_temp_raw = await client.read_gatt_char(CHAR_CURRENT_TEMP)
        target_temp_raw = await client.read_gatt_char(CHAR_TARGET_TEMP)
        battery_raw = await client.read_gatt_char(CHAR_BATTERY)
        liquid_state_raw = await client.read_gatt_char(CHAR_LIQUID_STATE)
        liquid_level_raw = await client.read_gatt_char(CHAR_LIQUID_LEVEL)

    current_temp_c = int.from_bytes(current_temp_raw, byteorder="little", signed=False) * 0.01
    target_temp_c = int.from_bytes(target_temp_raw, byteorder="little", signed=False) * 0.01

    battery_percent = battery_raw[0] if len(battery_raw) > 0 else None
    charging = bool(battery_raw[1]) if len(battery_raw) > 1 else None

    state_code = liquid_state_raw[0] if liquid_state_raw else None
    liquid_state = LIQUID_STATES.get(state_code, "unknown") if state_code is not None else None
    liquid_level = liquid_level_raw[0] if liquid_level_raw else None

    return EmberStatus(
        current_temp_c=round(current_temp_c, 2),
        target_temp_c=round(target_temp_c, 2),
        battery_percent=battery_percent,
        charging=charging,
        liquid_state_code=state_code,
        liquid_state=liquid_state,
        liquid_level=liquid_level,
    )
