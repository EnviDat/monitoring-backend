from django.test import TestCase
from django.test import Client
from django.urls import resolve

from datetime import datetime, timedelta

import json

from .gcnet_data_generator import GCNetTestDataGenerator
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
import django
django.setup()

from gcnet.models import test as StationTest


class GCNetTestCase(TestCase):
    databases = '__all__'

    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.test_dataset = GCNetTestDataGenerator().generateTestData()

        for id, data in cls.test_dataset.items():
            cls.station = StationTest.objects.create(id=id, timestamp_iso=data.get('timestamp_iso'),
                                                     timestamp=data.get('timestamp'),
                                                     year=data.get('year'), julianday=data.get('julianday'),
                                                     quarterday=data.get('quarterday'), halfday=data.get('halfday'),
                                                     day=data.get('day'), week=data.get('week'),
                                                     swin=data.get('swin')
                                                     )
        pass

    def tearDown(self):
        pass

    def test_basic_query(self):
        test1 = StationTest.objects.get(id=1)
        print("Check retrieved swin is {0} = {1}".format(test1.swin, self.test_dataset[1]['swin']))
        self.assertTrue(test1.swin == self.test_dataset[1]['swin'])

    def test_api_models(self):
        path = '/api/gcnet/models/'

        # Issue a GET request.
        response = self.client.get(path)

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)

        # Check that the response is 200 OK.
        stations_list = json.loads(response.content)
        print("Check models list is not empty,  len is {0}".format(len(stations_list)))
        self.assertGreater(len(stations_list), 0, "Models list should not be empty")

    def test_api_models(self):

        #http://127.0.0.1:8000/api/gcnet/summary/daily/json/test/all/1996-01-01/1996-12-31/
        start_timestamp = datetime.fromisoformat(self.test_dataset[1]['timestamp_iso']).strftime("%Y-%m-%d")
        end_timestamp = datetime.fromisoformat(self.test_dataset[50]['timestamp_iso']).strftime("%Y-%m-%d")

        path = '/api/gcnet/summary/daily/json/test/multiple/{0}/{1}/'.format(start_timestamp, end_timestamp)

        # Issue a GET request.
        response = self.client.get(path)

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)

        # Check that the response is 200 OK.
        data = json.loads(response.content)
        print("Check data is not empty,  len is {0}".format(len(data)))
        self.assertGreater(len(data), 0, "Models list should not be empty")


