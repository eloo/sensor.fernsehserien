"""Constants for the Fernsehserien.de integration."""

from datetime import timedelta

DOMAIN = "fernsehserien"
PLATFORMS = ("sensor",)

CONF_SHOWS = "shows"
CONF_SHOW_NAME = "showNames"  # Legacy YAML key.
CONF_SCAN_INTERVAL = "scan_interval"
CONF_MAX_PER_SHOW = "max_per_show"
DEFAULT_SCAN_INTERVAL = timedelta(seconds=21600)
DEFAULT_MAX_PER_SHOW = 2
HOST = "https://www.fernsehserien.de"
BASE_URL = f"{HOST}/{{}}/episodenguide"
REQUEST_TIMEOUT = 20
MAX_PER_SHOW = 3