"""Tests for Fernsehserien config and options flows."""

import pytest
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.fernsehserien.config_flow import _validate_shows
from custom_components.fernsehserien.const import (
    CONF_MAX_PER_SHOW,
    CONF_SCAN_INTERVAL,
    DOMAIN,
)


def test_validate_shows_normalizes_and_deduplicates() -> None:
    """Newline and comma-separated slugs are normalized."""
    assert _validate_shows("Breaking-Bad\nbreaking-bad, dark") == (
        ["breaking-bad", "dark"],
        None,
    )


def test_validate_shows_rejects_invalid_slug() -> None:
    """URLs and invalid characters are rejected."""
    shows, error = _validate_shows("https://fernsehserien.de/dark")
    assert shows == []
    assert error == "invalid_show"


@pytest.mark.asyncio
async def test_user_flow_creates_entry(
    hass: HomeAssistant, enable_custom_integrations
) -> None:
    """Initial UI flow creates an entry with one or more slugs."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == "form"
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={
            "shows": "dark\nbreaking-bad",
            CONF_SCAN_INTERVAL: 1800,
            CONF_MAX_PER_SHOW: 4,
        },
    )
    assert result["type"] == "create_entry"
    assert result["data"] == {
        "shows": ["dark", "breaking-bad"],
        CONF_SCAN_INTERVAL: 1800,
        CONF_MAX_PER_SHOW: 4,
    }


@pytest.mark.asyncio
async def test_options_allow_removing_all_shows(
    hass: HomeAssistant, enable_custom_integrations
) -> None:
    """Options allow deleting all current series from the list."""
    entry = MockConfigEntry(domain=DOMAIN, data={"shows": ["dark"]})
    entry.add_to_hass(hass)
    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            "shows": "",
            CONF_SCAN_INTERVAL: 21600,
            CONF_MAX_PER_SHOW: 2,
        },
    )
    assert result["type"] == "create_entry"
    assert result["data"] == {
        "shows": [],
        CONF_SCAN_INTERVAL: 21600,
        CONF_MAX_PER_SHOW: 2,
    }


@pytest.mark.asyncio
async def test_options_update_interval_and_episode_limit(
    hass: HomeAssistant, enable_custom_integrations
) -> None:
    """Options flow stores polling interval and per-show episode limit."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            "shows": ["dark"],
            CONF_SCAN_INTERVAL: 21600,
            CONF_MAX_PER_SHOW: 2,
        },
    )
    entry.add_to_hass(hass)
    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            "shows": "dark",
            CONF_SCAN_INTERVAL: 1800,
            CONF_MAX_PER_SHOW: 5,
        },
    )
    assert result["type"] == "create_entry"
    assert result["data"] == {
        "shows": ["dark"],
        CONF_SCAN_INTERVAL: 1800,
        CONF_MAX_PER_SHOW: 5,
    }