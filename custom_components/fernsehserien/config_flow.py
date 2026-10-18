"""Config flow for Fernsehserien.de."""

from __future__ import annotations

import re

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import CONF_SHOWS, DOMAIN

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
                    title="Fernsehserien.de", data={CONF_SHOWS: shows}
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_SHOWS): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT, multiline=True
                        )
                    )
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
            title="Fernsehserien.de", data={CONF_SHOWS: shows}
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
                return self.async_create_entry(title="", data={CONF_SHOWS: shows})

        existing = self.config_entry.options.get(
            CONF_SHOWS, self.config_entry.data.get(CONF_SHOWS, [])
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
                    )
                }
            ),
            errors=errors,
        )