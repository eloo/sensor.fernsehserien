"""Sensors for Fernsehserien.de."""

from __future__ import annotations

import json
import time
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import FernsehserienCoordinator


class FernsehserienUpcomingMediaSensor(
    CoordinatorEntity[FernsehserienCoordinator], SensorEntity
):
    """Expose upcoming episodes in Upcoming Media Card format."""

    _attr_name = "Fernsehserien Upcoming Media"
    _attr_unique_id = "fernsehserien_upcoming_media"
    _attr_icon = "mdi:television-play"
    _attr_has_entity_name = True

    @property
    def device_info(self) -> DeviceInfo:
        """Return device registry information."""
        return DeviceInfo(
            identifiers={(DOMAIN, "upcoming_media")},
            name="Fernsehserien.de",
            manufacturer="Fernsehserien.de",
        )

    @property
    def native_value(self) -> str:
        """Return the coordinator status."""
        return "Online" if self.coordinator.last_update_success else "Offline"

    @property
    def extra_state_attributes(self) -> dict[str, str]:
        """Return episode data for Upcoming Media Card."""
        data: list[dict[str, Any]] = [
            {
                "title_default": "$title",
                "line1_default": "$episode",
                "line2_default": "$number",
                "line3_default": "$aired",
                "line4_default": "",
                "icon": "mdi:arrow-down-bold",
            }
        ]
        for show in self.coordinator.data.get("shows", []):
            for episode in show["episodes"]:
                airdate = episode["airDate"]
                data.append(
                    {
                        "airdate": int(time.mktime(airdate)),
                        "aired": time.strftime("%Y-%m-%dT%H:%M:%SZ", airdate),
                        "title": show["title"],
                        "episode": episode["title"],
                        "number": "S{:02d}E{:02d}".format(
                            episode["seasonNumber"], episode["episodeNumber"]
                        ),
                        "fanart": show["fanart"],
                    }
                )
        data[1:] = sorted(data[1:], key=lambda item: item["airdate"])
        return {"data": json.dumps(data)}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities,
) -> None:
    """Set up the configured series sensor."""
    coordinator = hass.data["fernsehserien"][entry.entry_id]
    async_add_entities([FernsehserienUpcomingMediaSensor(coordinator)])