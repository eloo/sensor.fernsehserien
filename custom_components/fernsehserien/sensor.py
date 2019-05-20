"""
Home Assistant component to feed the Upcoming Media Lovelace card with
Fernsehserien.de upcoming releases.

https://github.com/custom-components/sensor.fernsehserien_upcoming_media

https://github.com/custom-cards/upcoming-media-card

"""
import logging
import json 

import time
import requests
import re
from datetime import date, datetime
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import CONF_API_KEY, CONF_HOST, CONF_PORT, CONF_SSL
from homeassistant.helpers.entity import Entity

__version__ = '0.1.0'

_LOGGER = logging.getLogger(__name__)

REQUIREMENTS = ['pyquery==1.4.0']

BASE_URL = "https://www.fernsehserien.de/{0}/episodenguide"
CONF_SHOW_NAME = 'showNames'
CONF_DAYS = 'days'
CONF_MAX = 'max'

DOMAIN = 'fernsehserien_upcoming_media'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_SHOW_NAME): cv.ensure_list,
    vol.Optional(CONF_DAYS, default='7'): cv.string,    
    vol.Optional(CONF_MAX, default=5): cv.string,
})


def setup_platform(hass, config, add_devices, discovery_info=None):
    add_devices([FernsehserienUpcomingMediaSensor(hass, config)], True)


class FernsehserienUpcomingMediaSensor(Entity):

    def __init__(self, hass, conf):
        from pytz import timezone
        self.urlbase = BASE_URL
        self.days = int(conf.get(CONF_DAYS))
        self.showNames = conf.get(CONF_SHOW_NAME)
        self._state = None
        self.data = []
        self._tz = timezone(str(hass.config.time_zone))
        self.max_items = int(conf.get(CONF_MAX))

    @property
    def name(self):
        # return 'Sonarr_Upcoming_Media_'
        return 'Fernsehserien_Upcoming_Media'

    @property
    def state(self):
        return self._state

    @property
    def device_state_attributes(self):
        # import re
        # """Return JSON for the sensor."""
        attributes = {}
        default = {}
        card_json = []
        default['title_default'] = '$title'
        default['line1_default'] = '$episode'
        default['line2_default'] = '$number'
        default['line3_default'] = '$aired'
        default['line4_default'] = ''
        default['icon'] = 'mdi:arrow-down-bold'
        card_json.append(default)
        episode_list = []
        for show in self.data:
            for episode in show['episodes']:
                card_item = {}
        #     if 'series' not in show:
        #         continue
                card_item['airdate'] = episode['airDate']
                card_item['aired'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', episode['airDate'])
        #     if days_until(show['airDateUtc'], self._tz) <= 7:
        #         card_item['release'] = '$day, $time'
        #     else:
        #         card_item['release'] = '$day, $date $time'
        #     card_item['flag'] = show.get('hasFile', False)
                if 'title' in show:
                    card_item['title'] = show['title']
        #     else:
        #         continue
                card_item['episode'] = episode['title']
                if 'seasonNumber' and 'episodeNumber' in episode:
                    card_item['number'] = 'S{:02d}E{:02d}'.format(episode['seasonNumber'],
                                                        episode['episodeNumber'])
                card_item['fanart'] = show['fanart']
                episode_list.append(card_item)
        episode_list = sorted(episode_list, key=lambda x: x['airdate'])
        card_json.extend(episode_list)
        attributes['data'] = json.dumps(card_json)
        return attributes

    def update(self):
        start = get_date(self._tz)
        end = get_date(self._tz, self.days)
        result = []
        for showName in self.showNames:
            try:
                api_response = requests.get(BASE_URL.format(showName), timeout=10)

            except OSError:
                _LOGGER.warning("Host %s is not available", self.host)
                self._state = '%s cannot be reached' % self.host
                continue

            if api_response.status_code == 200:
                self._state = 'Online'
                data = parseResponse(api_response)
                # data = list(filter(lambda x: x['airDate'] > time.gmtime(), data))
                result.append(data)
                self.data = result
            else:
                self._state = '%s cannot be reached' % self.host

def parse_episode_number(episode):
    number = episode[4].text()
    if not number:
        number = episode[3].text()
    episode_number =  int(number)
    return episode_number

def parse_episode_airdate(episode):
    ea = episode[7].remove('span').text()
    airdate = ''
    try:
        airdate = time.strptime(ea, "%d.%m.%Y")
    except ValueError as e:
        ea = episode[6].remove('span').text()
        airdate = time.strptime(ea, "%d.%m.%Y")
    return airdate


def parseResponse(response):
    from pyquery import PyQuery    
    pq = PyQuery(response.text)
    show_title = pq('h1>a').filter(lambda i, this: PyQuery(this).attr['data-event-category'] == 'serientitel').remove('span').text()
    seasons = pq('tbody').filter(lambda i, this: PyQuery(this).attr['itemprop'] == 'season').items()
    showData = {}
    fanartUrl = pq('div>a>img').attr['src']
    showData['fanart'] = fanartUrl
    showData['title'] = show_title
    showData['episodes'] = []
    for season in seasons:
        episodes = season('tr').filter(lambda i, this: PyQuery(this).attr['itemprop'] == 'episode').items()
        for episode in episodes:
            try:
                episodeData = {}
                episode_number_obj_list = list(episode('td>a').items())
                season_number = episode_number_obj_list[3].text().replace('.', '')
                episodeData['seasonNumber'] = season_number
                episode_title = episode('td>a>span').filter(lambda i, this: PyQuery(this).attr['itemprop'] == 'name').text()
                episodeData['title'] = episode_title
                if season_number is '' or episode_title is '':
                    continue
                season_number = int(season_number)
                episode_number =  parse_episode_number(episode_number_obj_list)
                episodeData['seasonNumber'] = season_number
                episodeData['airDate'] = parse_episode_airdate(episode_number_obj_list)
                episodeData['episodeNumber'] = episode_number
                if episodeData['airDate'] < time.gmtime()[:3]:
                    continue
                showData['episodes'].append(episodeData)
            except ValueError as e:
                _LOGGER.warning("Unexpected error during parsing episode data of: " + showData['title'] + " " + season('tr>td>h2').text())
    return showData

def get_date(zone, offset=0):
    """Get date based on timezone and offset of days."""
    return datetime.date(datetime.fromtimestamp(
        time.time() + 86400 * offset, tz=zone))
        
def days_until(date, tz):
    from pytz import utc
    date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ')
    date = str(date.replace(tzinfo=utc).astimezone(tz))[:10]
    date = time.strptime(date, '%Y-%m-%d')
    date = time.mktime(date)
    now = datetime.now().strftime('%Y-%m-%d')
    now = time.strptime(now, '%Y-%m-%d')
    now = time.mktime(now)
    return int((date - now) / 86400)
