
import requests
from datetime import date
import os
import sys
import inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 

from custom_components.fernsehserien import sensor

show = 'the-mandalorian'

requests.adapters.DEFAULT_RETRIES = sensor.MAX_RETRIES
api_response = requests.get(sensor.BASE_URL.format(show), timeout=sensor.REQUEST_TIMEOUT)
show_data = sensor.parseResponse(show, api_response, date.today())
print("Episodes found: " + str(len(show_data['episodes'])))