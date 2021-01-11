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
import datetime
from time import mktime
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import CONF_API_KEY, CONF_HOST, CONF_PORT, CONF_SSL
from homeassistant.helpers.entity import Entity

__version__ = '0.2.0'

_LOGGER = logging.getLogger(__name__)

REQUIREMENTS = ['pyquery==1.4.1']

HOST = "https://www.fernsehserien.de"
BASE_URL = HOST + "/{0}/episodenguide"
FANART_BASE_URL = "https://bilder.fernsehserien.de/gfx/bv/{0}.jpg"

REQUEST_TIMEOUT = 20
MAX_RETRIES = 3

CONF_SHOW_NAME = 'showNames'
CONF_DAYS = 'days'
CONF_MAX = 'max'
CONF_MAX_PER_SHOW = "max_per_show"

DOMAIN = 'fernsehserien_upcoming_media'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_SHOW_NAME): cv.ensure_list,
    vol.Optional(CONF_DAYS, default=7): cv.positive_int,    
    vol.Optional(CONF_MAX, default=5): cv.positive_int,
    vol.Optional(CONF_MAX_PER_SHOW, default=3): cv.positive_int,
})


def setup_platform(hass, config, add_devices, discovery_info=None):
    add_devices([FernsehserienUpcomingMediaSensor(hass, config)], True)


class FernsehserienUpcomingMediaSensor(Entity):

    def __init__(self, hass, conf):
        from pytz import timezone
        self.host = HOST
        self.urlbase = BASE_URL
        self.days = conf.get(CONF_DAYS)
        self.showNames = conf.get(CONF_SHOW_NAME)
        self._state = None
        self.data = []
        self._tz = timezone(str(hass.config.time_zone))
        self.max_items = conf.get(CONF_MAX)
        self.max_per_show_items = conf.get(CONF_MAX_PER_SHOW)

    @property
    def name(self):
        # return 'Sonarr_Upcoming_Media_'
        return 'Fernsehserien_Upcoming_Media'

    @property
    def state(self):
        return self._state

    @property
    def device_state_attributes(self):
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
            show_episode_list = []
            for episode in show['episodes']:
                card_item = {}

                card_item['airdate'] = episode['airDate']
                card_item['aired'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', episode['airDate'])

                if 'title' in show:
                    card_item['title'] = show['title']

                card_item['episode'] = episode['title']
                if 'seasonNumber' and 'episodeNumber' in episode:
                    card_item['number'] = 'S{:02d}E{:02d}'.format(episode['seasonNumber'],
                                                        episode['episodeNumber'])
                card_item['fanart'] = show['fanart']
                show_episode_list.append(card_item)
            show_episode_list = sorted(show_episode_list, key=lambda x: x['airdate'])
            episode_list.extend(show_episode_list[:self.max_per_show_items])
        episode_list = sorted(episode_list, key=lambda x: x['airdate'])
        card_json.extend(episode_list)
        attributes['data'] = json.dumps(card_json)
        return attributes

    def update(self):
        result = []
        for showName in self.showNames:
            try:
                requests.adapters.DEFAULT_RETRIES = MAX_RETRIES
                api_response = requests.get(BASE_URL.format(showName), timeout=REQUEST_TIMEOUT)
            except OSError:
                _LOGGER.warning("Host %s is not available", self.host)
                self._state = '%s cannot be reached' % self.host
                continue

            if api_response.status_code == 200:
                self._state = 'Online'
                date = get_date()
                data = parseResponse(showName, api_response, date)

                result.append(data)
                self.data = result
            else:
                self._state = '%s cannot be reached' % self.host

def get_date():
    return datetime.date.today() - datetime.timedelta(1)

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
    except ValueError:
        ea = episode[6].remove('span').text()
        if ea == '':
            return ''
        airdate = time.strptime(ea, "%d.%m.%Y")
    return airdate


def parseResponse(show, response, date):
    from pyquery import PyQuery    
    pq = PyQuery(response.text)
    showData = {}
    showData['fanart'] = pq.find('.serienlogo').find('img')[0].attrib['src']
    show_title = pq('h1>a').filter(lambda i, this: PyQuery(this).attr['data-event-category'] == 'serientitel').remove('span').text()
    seasons = pq('tbody').filter(lambda i, this: PyQuery(this).attr['itemprop'] == 'containsSeason').items()
    showData['title'] = show_title
    
    showData['episodes'] = []
    for season in seasons:
        episodes = season('tr').filter(lambda i, this: PyQuery(this).attr['itemprop'] == 'episode').items()
        for episode in episodes:
            try:
                episodeData = {}
                episode_number_obj_list = list(episode('td>a').items())

                episodeData['airDate'] = parse_episode_airdate(episode_number_obj_list)
                if episodeData['airDate'] == '' or not is_upcoming_episode(episodeData['airDate'], date):
                    continue
                
                season_number_raw = episode_number_obj_list[3].text()
                if not season_number_raw.endswith('.'):
                    season_number_raw = episode_number_obj_list[2].text()
                season_number = season_number_raw.replace('.', '')
                episodeData['seasonNumber'] = season_number
                episode_title = episode('td>a>span').filter(lambda i, this: PyQuery(this).attr['itemprop'] == 'name').text()
                episodeData['title'] = episode_title
                if season_number == '' or episode_title == '':
                    continue
                season_number = int(season_number)
                episode_number =  parse_episode_number(episode_number_obj_list)
                episodeData['seasonNumber'] = season_number
                episodeData['airDate'] = parse_episode_airdate(episode_number_obj_list)
                if episodeData['airDate'] == '' or not is_upcoming_episode(episodeData['airDate'], date):
                    continue
                episodeData['episodeNumber'] = episode_number
                showData['episodes'].append(episodeData)
            except ValueError as e:
                _LOGGER.warning("Unexpected error during parsing episode data of: " + showData['title'] + " " + season('tr>td>h2').text())
                _LOGGER.warning(e)
    return showData

def is_upcoming_episode(airDate, date):
    air_date_object = datetime.datetime.fromtimestamp(mktime(airDate)).date()
    return air_date_object > date
