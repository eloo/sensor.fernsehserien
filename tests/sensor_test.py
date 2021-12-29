import unittest
import requests
from custom_components.fernsehserien import sensor

import logging
import datetime

# logging.basicConfig(level=logging.DEBUG)
sensor._LOGGER.setLevel(logging.DEBUG)
logging.getLogger().setLevel(logging.DEBUG)
logging.getLogger("custom_components.fernsehserien.sensor").setLevel(logging.DEBUG)
class TestFernsehserien(unittest.TestCase):
    """
    Test the parser
    """

    _LOGGER = logging.getLogger(sensor.__name__)
    _LOGGER.setLevel(logging.DEBUG)

    test_data = [
        'game-of-thrones',
        'vikings',
        'brooklyn-nine-nine',
        'doctor-who-2005',
        'the-big-bang-theory',
        'suits',
        'hubert-und-staller',
        'young-sheldon'
    ]

    def test_parse(self):
        test_date = datetime.date(2019, 1, 1)
        # test_date = datetime.date.today() - datetime.timedelta(1)

        print("Test date used: ", test_date)
        for show in self.test_data:
            print("Test parse for show: " + show)
            requests.adapters.DEFAULT_RETRIES = sensor.MAX_RETRIES
            api_response = requests.get(sensor.BASE_URL.format(show), timeout=sensor.REQUEST_TIMEOUT)
            show_data = sensor.parseResponse(show, api_response, test_date)
            print("Episodes found: " + str(len(show_data['episodes'])))
            self.assertIn('title', show_data, "No Show title parsed")
            self.assertIn('episodes', show_data, "No episode sparsed")
            self.assertGreater(len(show_data['seasons']), 0, "Unable to find seasons")
            self.assertGreater(len(show_data['episodes']), 0, "Unable to find episodes")

    def test_correct_data(self):
        show = 'vikings'
        print("Test correct data for: " + show)
        api_response = requests.get(sensor.BASE_URL.format(show), timeout=10)
        test_date = datetime.date(2019, 12, 1)
        show_data = sensor.parseResponse(show, api_response, test_date)

        first_episode = show_data['episodes'][0]
        self.assertEqual(first_episode['seasonNumber'], 6)
        self.assertEqual(first_episode['episodeNumber'], 1)
        
        second_episode = show_data['episodes'][1]
        self.assertEqual(second_episode['seasonNumber'], 6)
        self.assertEqual(second_episode['episodeNumber'], 2)

    def test_get_date(self):
        self.assertIsNotNone(sensor.get_date())


    def test_has_fanart(self):
        test_date = datetime.date(2019, 1, 1)
        # test_date = datetime.date.today() - datetime.timedelta(1)

        print("Test date used: ", test_date)
        for show in self.test_data:
            print("Test parse for show: " + show)
            requests.adapters.DEFAULT_RETRIES = sensor.MAX_RETRIES
            api_response = requests.get(sensor.BASE_URL.format(show), timeout=sensor.REQUEST_TIMEOUT)
            show_data = sensor.parseResponse(show, api_response, test_date)
            print(show_data['fanart'])
            api_response = requests.get(show_data['fanart'])
            self.assertEqual(api_response.status_code, 200, "Fanart not found at: '{}'".format(show_data['fanart']))

    def test_can_scrape_show_title(self):
        show = 'vikings'
        api_response = requests.get(sensor.BASE_URL.format(show), timeout=10)
        test_date = datetime.date(2019, 12, 1)
        show_data = sensor.parseResponse(show, api_response, test_date)
        self.assertEqual(show_data['title'], "Vikings")

    def test_can_scrape_show_seasons(self):
        show = 'vikings'
        api_response = requests.get(sensor.BASE_URL.format(show), timeout=10)
        test_date = datetime.date(2019, 12, 1)
        show_data = sensor.parseResponse(show, api_response, test_date)
        self.assertEqual(len(show_data['seasons']), 6)

    def test_can_scrape_show_episodes(self):
        show = 'vikings'
        api_response = requests.get(sensor.BASE_URL.format(show), timeout=10)
        test_date = datetime.date(2000, 12, 1)
        show_data = sensor.parseResponse(show, api_response, test_date)
        self.assertEqual(len(show_data['episodes']), 89)

    def test_can_scrape_filtered_show_episodes(self):
        show = 'vikings'
        api_response = requests.get(sensor.BASE_URL.format(show), timeout=10)
        test_date = datetime.date(2019, 12, 1)
        show_data = sensor.parseResponse(show, api_response, test_date)
        self.assertEqual(len(show_data['episodes']), 20)

if __name__ == '__main__':
    unittest.main()