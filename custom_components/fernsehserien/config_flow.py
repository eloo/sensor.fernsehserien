"""Config flow for Fernsehserien.de."""

from __future__ import annotations

import re

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import (
    CONF_MAX_PER_SHOW,
    CONF_SCAN_INTERVAL,
    CONF_SHOWS,
    DEFAULT_MAX_PER_SHOW,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)

_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def _parse_shows(value: str) -> list[str]:
    """Parse newline- or comma-separated Fernsehserien.de slugs."""
    return list(
        dict.fromkeys(
            slug.strip().lower()
            for slug in re.split(r"[\n,]+", value)
            if slug.strip()
        )
    )


def _validate_shows(
    value: str, *, allow_empty: bool = False
) -> tuple[list[str], str | None]:
    """Validate and normalize a submitted list of show slugs."""
    shows = _parse_shows(value)
    if not shows and not allow_empty:
        return [], "no_shows"
    if any(not _SLUG_RE.fullmatch(show) for show in shows):
        return [], "invalid_show"
    return shows, None


class FernsehserienConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Fernsehserien.de."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, str] | None = None
    ) -> FlowResult:
        """Set up the initial show list."""
        errors: dict[str, str] = {}
        if user_input is not None:
            shows, error = _validate_shows(user_input[CONF_SHOWS])
            if error:
                errors[CONF_SHOWS] = error
            else:
                await self.async_set_unique_id(DOMAIN)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title="Fernsehserien.de",
                    data={
                        CONF_SHOWS: shows,
                        CONF_SCAN_INTERVAL: int(user_input[CONF_SCAN_INTERVAL]),
                        CONF_MAX_PER_SHOW: int(user_input[CONF_MAX_PER_SHOW]),
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_SHOWS): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT, multiline=True
                        )
                    ),
                    vol.Required(
                        CONF_SCAN_INTERVAL,
                        default=int(DEFAULT_SCAN_INTERVAL.total_seconds()),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=60,
                            max=604800,
                            step=60,
                            mode=selector.NumberSelectorMode.BOX,
                            unit_of_measurement="s",
                        )
                    ),
                    vol.Required(
                        CONF_MAX_PER_SHOW, default=DEFAULT_MAX_PER_SHOW
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=1,
                            max=50,
                            step=1,
                            mode=selector.NumberSelectorMode.BOX,
                        )
                    ),
                }
            ),
            errors=errors,
        )

    async def async_step_import(self, import_config: dict) -> FlowResult:
        """Import legacy YAML settings when explicitly handed to the flow."""
        legacy_shows = import_config.get(CONF_SHOWS) or import_config.get(
            "showNames", []
        )
        shows = [
            str(show).strip().lower() for show in legacy_shows if str(show).strip()
        ]
        shows, error = _validate_shows("\n".join(shows))
        if error:
            return self.async_abort(reason="invalid_import")
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()
        return self.async_create_entry(
            title="Fernsehserien.de",
            data={
                CONF_SHOWS: shows,
                CONF_SCAN_INTERVAL: int(
                    import_config.get(
                        CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL.total_seconds()
                    )
                ),
                CONF_MAX_PER_SHOW: int(
                    import_config.get(CONF_MAX_PER_SHOW, DEFAULT_MAX_PER_SHOW)
                ),
            },
        )

    @staticmethod
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> FernsehserienOptionsFlow:
        """Return the options flow handler."""
        return FernsehserienOptionsFlow()


class FernsehserienOptionsFlow(config_entries.OptionsFlow):
    """Manage the configured series list."""

    async def async_step_init(
        self, user_input: dict[str, str] | None = None
    ) -> FlowResult:
        """Add or remove shows by editing the complete list."""
        errors: dict[str, str] = {}
        if user_input is not None:
            shows, error = _validate_shows(user_input[CONF_SHOWS], allow_empty=True)
            if error:
                errors[CONF_SHOWS] = error
            else:
                return self.async_create_entry(
                    title="",
                    data={
                        CONF_SHOWS: shows,
                        CONF_SCAN_INTERVAL: int(user_input[CONF_SCAN_INTERVAL]),
                        CONF_MAX_PER_SHOW: int(user_input[CONF_MAX_PER_SHOW]),
                    },
                )

        existing = self.config_entry.options.get(
            CONF_SHOWS, self.config_entry.data.get(CONF_SHOWS, [])
        )
        scan_interval = self.config_entry.options.get(
            CONF_SCAN_INTERVAL,
            self.config_entry.data.get(
                CONF_SCAN_INTERVAL, int(DEFAULT_SCAN_INTERVAL.total_seconds())
            ),
        )
        max_per_show = self.config_entry.options.get(
            CONF_MAX_PER_SHOW,
            self.config_entry.data.get(CONF_MAX_PER_SHOW, DEFAULT_MAX_PER_SHOW),
        )
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_SHOWS, default="\n".join(existing)
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT, multiline=True
                        )
                    ),
                    vol.Required(
                        CONF_SCAN_INTERVAL, default=scan_interval
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=60,
                            max=604800,
                            step=60,
                            mode=selector.NumberSelectorMode.BOX,
                            unit_of_measurement="s",
                        )
                    ),
                    vol.Required(
                        CONF_MAX_PER_SHOW, default=max_per_show
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=1,
                            max=50,
                            step=1,
                            mode=selector.NumberSelectorMode.BOX,
                        )
                    ),
                }
            ),
            errors=errors,
        )