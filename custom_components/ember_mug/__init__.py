"""Home Assistant integration for Ember Mug BLE metrics + realtime page."""

from __future__ import annotations

import asyncio
import json

from aiohttp import web
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.typing import ConfigType
from homeassistant.components.http import HomeAssistantView

from .const import DOMAIN, PLATFORMS
from .coordinator import EmberMugCoordinator


class EmberMugStatusView(HomeAssistantView):
    """Single-shot JSON view."""

    url = "/api/ember_mug/status"
    name = "api:ember_mug:status"
    requires_auth = False

    async def get(self, request: web.Request) -> web.Response:
        hass: HomeAssistant = request.app["hass"]
        coordinator: EmberMugCoordinator = hass.data[DOMAIN]["coordinator"]
        if coordinator.data is None:
            await coordinator.async_request_refresh()
        payload = coordinator.data.as_dict() if coordinator.data else {}
        return web.json_response(payload)


class EmberMugEventsView(HomeAssistantView):
    """Server-Sent Events endpoint for live status updates."""

    url = "/api/ember_mug/events"
    name = "api:ember_mug:events"
    requires_auth = False

    async def get(self, request: web.Request) -> web.StreamResponse:
        hass: HomeAssistant = request.app["hass"]
        coordinator: EmberMugCoordinator = hass.data[DOMAIN]["coordinator"]
        response = web.StreamResponse(
            status=200,
            headers={
                "Content-Type": "text/event-stream",
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            },
        )
        await response.prepare(request)

        queue = coordinator.subscribe_live_updates()

        try:
            if coordinator.data is not None:
                await response.write(f"data: {json.dumps(coordinator.data.as_dict())}\n\n".encode())

            while True:
                payload = await queue.get()
                await response.write(f"data: {json.dumps(payload)}\n\n".encode())
                await response.drain()
        except (ConnectionResetError, asyncio.CancelledError):
            pass
        finally:
            coordinator.unsubscribe_live_updates(queue)

        return response


class EmberMugPageView(HomeAssistantView):
    """Tiny realtime webpage exposing Ember values."""

    url = "/ember_mug"
    name = "api:ember_mug:page"
    requires_auth = False

    async def get(self, request: web.Request) -> web.Response:
        html = """<!doctype html>
<html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
<title>Ember Mug Live Status</title>
<style>body{font-family:system-ui,sans-serif;margin:2rem;background:#161b22;color:#e6edf3}h1{margin-bottom:1rem}ul{list-style:none;padding:0}li{padding:.5rem 0;border-bottom:1px solid #30363d}.muted{opacity:.8}.ok{color:#3fb950}</style>
</head><body>
<h1>Ember Mug Live Status</h1>
<p class='muted'>Streaming from Home Assistant integration endpoint.</p>
<ul>
<li>Current Temp: <strong id='current_temp_c'>-</strong> °C</li>
<li>Target Temp: <strong id='target_temp_c'>-</strong> °C</li>
<li>Battery Level: <strong id='battery_percent'>-</strong> %</li>
<li>Charging: <strong id='charging'>-</strong></li>
<li>Liquid State: <strong id='liquid_state'>-</strong></li>
<li>Liquid Level: <strong id='liquid_level'>-</strong></li>
</ul>
<p>Status: <span id='status' class='muted'>connecting…</span></p>
<script>
const fields = ["current_temp_c","target_temp_c","battery_percent","charging","liquid_state","liquid_level"];
function render(data){
  for(const key of fields){
    const node=document.getElementById(key); if(!node) continue;
    let value=data[key]; if(value===true) value='yes'; if(value===false) value='no';
    node.textContent=value ?? '-';
  }
}
fetch('/api/ember_mug/status').then(r=>r.json()).then(render).catch(()=>{});
const statusNode=document.getElementById('status');
const events=new EventSource('/api/ember_mug/events');
events.onopen=()=>{statusNode.textContent='connected';statusNode.className='ok';};
events.onmessage=(event)=>{render(JSON.parse(event.data));};
events.onerror=()=>{statusNode.textContent='reconnecting…';statusNode.className='muted';};
</script></body></html>"""
        return web.Response(text=html, content_type="text/html")


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up integration from YAML (unused)."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Ember Mug from a config entry."""
    coordinator = EmberMugCoordinator(hass, entry)
    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:
        raise ConfigEntryNotReady(str(err)) from err

    hass.data.setdefault(DOMAIN, {})["coordinator"] = coordinator

    if not hass.data[DOMAIN].get("views_registered"):
        hass.http.register_view(EmberMugStatusView)
        hass.http.register_view(EmberMugEventsView)
        hass.http.register_view(EmberMugPageView)
        hass.data[DOMAIN]["views_registered"] = True

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload Ember Mug config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data.get(DOMAIN, {}).pop("coordinator", None)
    return unload_ok
