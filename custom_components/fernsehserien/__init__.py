"""Fernsehserien.de integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import (
    CONF_MAX_PER_SHOW,
    CONF_SCAN_INTERVAL,
    CONF_SHOWS,
    DEFAULT_MAX_PER_SHOW,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)
from .coordinator import FernsehserienCoordinator

PLATFORMS = (Platform.SENSOR,)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the integration from a config entry only."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Fernsehserien.de from a config entry."""
    settings = {**entry.data, **entry.options}
    coordinator = FernsehserienCoordinator(
        hass,
        settings.get(CONF_SHOWS, []),
        scan_interval=settings.get(
            CONF_SCAN_INTERVAL, int(DEFAULT_SCAN_INTERVAL.total_seconds())
        ),
        max_per_show=settings.get(CONF_MAX_PER_SHOW, DEFAULT_MAX_PER_SHOW),
    )
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload after options change."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if not await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        return False
    hass.data[DOMAIN].pop(entry.entry_id)
    return True