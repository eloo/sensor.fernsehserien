"""Fetch and parse upcoming episodes from Fernsehserien.de."""

from __future__ import annotations

import datetime as dt
import logging
import time
from typing import Any

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from pyquery import PyQuery

from .const import BASE_URL, DEFAULT_MAX_PER_SHOW, REQUEST_TIMEOUT

_LOGGER = logging.getLogger(__name__)


class FernsehserienCoordinator(DataUpdateCoordinator[dict[str, Any]]):
	"""Coordinate updates for all configured series."""

	def __init__(
		self,
		hass: HomeAssistant,
		shows: list[str],
		*,
		scan_interval: int,
		max_per_show: int,
	) -> None:
		self.shows = shows
		self.max_per_show = max_per_show
		self.session = async_get_clientsession(hass)
		super().__init__(
			hass,
			_LOGGER,
			name="Fernsehserien.de",
			update_interval=dt.timedelta(seconds=scan_interval),
		)

	async def _async_update_data(self) -> dict[str, Any]:
		"""Fetch upcoming episodes for each configured show."""
		results: list[dict[str, Any]] = []
		for show in self.shows:
			try:
				async with self.session.get(
					BASE_URL.format(show),
					timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT),
				) as response:
					response.raise_for_status()
					html = await response.text()
				results.append(
					_parse_response(
						show,
						html,
						dt.date.today() - dt.timedelta(days=1),
						self.max_per_show,
					)
				)
			except (aiohttp.ClientError, TimeoutError, ValueError, IndexError) as err:
				raise UpdateFailed(f"Fehler beim Abrufen von {show}") from err
		return {"shows": results}


def _parse_response(
	show: str,
	html: str,
	date: dt.date,
	max_per_show: int = DEFAULT_MAX_PER_SHOW,
) -> dict[str, Any]:
	"""Parse a Fernsehserien.de episode guide."""
	pq = PyQuery(html)
	logo = pq.find(".serienlogo img").eq(0)
	if not logo:
		raise ValueError(f"Serienlogo für {show} fehlt")
	title = pq("h1>a").eq(0).clone().find("span").remove().end().text().strip()
	if not title:
		title = show.replace("-", " ").title()

	result: dict[str, Any] = {
		"title": title,
		"fanart": logo.attr("src"),
		"episodes": [],
	}
	for season in pq('section[itemprop="containsSeason"]'):
		season_pq = PyQuery(season)
		for episode in season_pq('a[itemprop="episode"]'):
			try:
				cells = list(PyQuery(episode)("div").items())
				if len(cells) < 8:
					continue
				airdate_text = PyQuery(cells[7]).remove("span").text().strip()
				if not airdate_text:
					airdate_text = PyQuery(cells[6]).remove("span").text().strip()
				airdate = time.strptime(airdate_text, "%d.%m.%Y")
				episode_date = dt.date(*airdate[:3])
				if episode_date <= date:
					continue

				season_text = PyQuery(cells[3]).text().strip()
				if not season_text.endswith("."):
					season_text = PyQuery(cells[2]).text().strip()
				season_number = int(season_text.replace(".", ""))
				number_text = PyQuery(cells[4]).text().strip() or PyQuery(
					cells[3]
				).text().strip()
				episode_number = int(number_text)
				episode_title = (
					PyQuery(cells[6])('span[itemprop="name"]').text().strip()
				)
				result["episodes"].append(
					{
						"airDate": airdate,
						"seasonNumber": season_number,
						"episodeNumber": episode_number,
						"title": episode_title or "Unbekannte Folge",
					}
				)
			except (ValueError, IndexError):
				_LOGGER.debug(
					"Episode von %s konnte nicht geparst werden", show, exc_info=True
				)
	result["episodes"].sort(key=lambda episode: episode["airDate"])
	result["episodes"] = result["episodes"][:max_per_show]
	return result