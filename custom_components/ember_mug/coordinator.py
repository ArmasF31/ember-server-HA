"""Coordinator for Ember Mug state polling."""

from __future__ import annotations

from asyncio import Queue
from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .bluetooth import EmberStatus, read_status
from .const import CONF_ADDRESS, CONF_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class EmberMugCoordinator(DataUpdateCoordinator[EmberStatus]):
    """Fetches data from Ember mug and fans out live updates."""

    def __init__(self, hass: HomeAssistant, entry) -> None:
        self._address: str = entry.data[CONF_ADDRESS]
        self._queues: set[Queue[dict]] = set()
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=entry.options.get(CONF_SCAN_INTERVAL, entry.data[CONF_SCAN_INTERVAL])),
        )

    def subscribe_live_updates(self) -> Queue[dict]:
        """Register live update stream subscriber."""
        queue: Queue[dict] = Queue(maxsize=1)
        self._queues.add(queue)
        return queue

    def unsubscribe_live_updates(self, queue: Queue[dict]) -> None:
        """Remove live update stream subscriber."""
        self._queues.discard(queue)

    async def _async_update_data(self) -> EmberStatus:
        try:
            status = await read_status(self._address)
        except Exception as err:  # pragma: no cover - HA handles details
            raise UpdateFailed(str(err)) from err

        payload = status.as_dict()
        for queue in self._queues:
            if queue.full():
                _ = queue.get_nowait()
            queue.put_nowait(payload)

        return status
