import unittest
import requests
import custom_components.fernsehserien.sensor as sensor
import datetime 
from datetime import date

class TestFernsehserien(unittest.TestCase):
    """
    Test the parser
    """

    test_data = [
        'game-of-thrones',
        'vikings',
        'brooklyn-nine-nine',
        'doctor-who-2005',
        'the-big-bang-theory',
        'suits',
        'hubert-ohne-staller',
        'young-sheldon',
        'gomorrha-die-serie'
    ]

    def test_parse(self):
        """
        The actual test.
        Any method which starts with ``test_`` will considered as a test case.
        """
        for show in self.test_data:
            print("Test parse for show: " + show)
            api_response = requests.get(sensor.BASE_URL.format(show), timeout=10)
            show_data = sensor.parseResponse(api_response)
            print("Episodes found: " + str(len(show_data['episodes'])))
            self.assertIn('title', show_data)
            self.assertIn('episodes', show_data)
            self.assertGreater(len(show_data['episodes']), 0)

    def test_filter_upcoming(self):
        show = self.test_data[0]
        print("Test filter for show: " + show)

        api_response = requests.get(sensor.BASE_URL.format(show), timeout=10)
        show_data = sensor.parseResponse(api_response)
        test_date = datetime.date(2019, 1, 1)

        show_data['episodes'] = sensor.filter_upcoming(show_data['episodes'], show, test_date)
        self.assertEqual(len(show_data['episodes']), 6)


if __name__ == '__main__':
    unittest.main()