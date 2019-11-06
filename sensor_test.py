import unittest
import requests
import custom_components.fernsehserien.sensor as sensor

class TestFernsehserien(unittest.TestCase):
    """
    Test the parser
    """

    test_data = [
        'brooklyn-nine-nine',
        'doctor-who-2005',
        'the-big-bang-theory',
        'suits',
        'vikings',
        'hubert-ohne-staller',
        'game-of-thrones',
        'young-sheldon',
        'gomorrha-die-serie'
    ]

    def test_parse(self):
        """
        The actual test.
        Any method which starts with ``test_`` will considered as a test case.
        """
        for show in self.test_data:
            print("Test show: " + show)
            api_response = requests.get(sensor.BASE_URL.format(show), timeout=10)
            show_data = sensor.parseResponse(api_response)
            print(show_data)
            self.assertIn('fanart', show_data)
            self.assertIn('title', show_data)
            self.assertIn('episodes', show_data)
            self.assertGreater(len(show_data['episodes']), 0)

if __name__ == '__main__':
    unittest.main()