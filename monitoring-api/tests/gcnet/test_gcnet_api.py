import importlib
import json
import os
from datetime import datetime, timedelta

from django.test import Client, TestCase
from django.urls import resolve
from gcnet.management.commands.importers.csv_import import CsvImporter
from gcnet.management.commands.importers.dat_import import DatImporter
from gcnet.management.commands.importers.nead_import import NeadImporter
from gcnet.util.constants import Columns

from .gcnet_data_generator import GCNetTestDataGenerator

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")

import django

django.setup()

from gcnet.models import test as StationTest


class GCNetAPITestCase(TestCase):
    databases = "__all__"

    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.test_dataset = GCNetTestDataGenerator().generate_test_data()

        for data in cls.test_dataset.values():
            cls.station = StationTest.objects.create(**data)
        pass

    def tearDown(self):
        pass

    def test_basic_query(self):
        test1 = StationTest.objects.get(id=1)
        print(
            f"Check retrieved swin is {test1.swin} = {self.test_dataset[1][Columns.SWIN.value]}"
        )
        self.assertTrue(test1.swin == self.test_dataset[1][Columns.SWIN.value])

    def test_api_models(self):
        path = "/gcnet/models/"

        # Issue a GET request.
        response = self.client.get(path)

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)

        # Check that the response is 200 OK.
        stations_list = json.loads(response.content)
        print(f"Check models list is not empty,  len is {len(stations_list)}")
        self.assertGreater(len(stations_list), 0, "Models list should not be empty")

    def test_api_data(self):

        start_timestamp = datetime.fromisoformat(
            self.test_dataset[1][Columns.TIMESTAMP_ISO.value]
        ).strftime("%Y-%m-%d")
        end_timestamp = datetime.fromisoformat(
            self.test_dataset[50][Columns.TIMESTAMP_ISO.value]
        ).strftime("%Y-%m-%d")

        path = f"/gcnet/summary/daily/json/test/multiple/{start_timestamp}/{end_timestamp}/"

        # Issue a GET request.
        response = self.client.get(path)

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)

        # Check that the response is 200 OK.
        data = json.loads(response.content)
        print(f"Check data is not empty,  len is {len(data)}")
        self.assertGreater(len(data), 0, "Data retrieved should not be empty")
