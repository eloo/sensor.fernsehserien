"""Diagnostics for Fernsehserien.de."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return redacted integration diagnostics."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    return {
        "entry": {"title": entry.title, "version": entry.version},
        "configured_shows": entry.options.get(
            "shows", entry.data.get("shows", [])
        ),
        "last_update_success": coordinator.last_update_success,
        "show_count": len(coordinator.data.get("shows", [])),
    }