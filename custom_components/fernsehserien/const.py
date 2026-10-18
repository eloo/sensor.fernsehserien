"""Constants for the Fernsehserien.de integration."""

from datetime import timedelta

DOMAIN = "fernsehserien"
PLATFORMS = ("sensor",)

CONF_SHOWS = "shows"
CONF_SHOW_NAME = "showNames"  # Legacy YAML key.
DEFAULT_SCAN_INTERVAL = timedelta(hours=6)
HOST = "https://www.fernsehserien.de"
BASE_URL = f"{HOST}/{{}}/episodenguide"
REQUEST_TIMEOUT = 20
MAX_PER_SHOW = 3