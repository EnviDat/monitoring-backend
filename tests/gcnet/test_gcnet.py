from django.test import TestCase
from django.test import Client
from django.urls import resolve
import os

from datetime import datetime, timedelta
import json
import importlib

from gcnet.management.commands.importers.csv_import import CsvImporter
from gcnet.management.commands.importers.dat_import import DatImporter
from gcnet.management.commands.importers.nead_import import NeadImporter
from gcnet.util.constants import Columns

from .gcnet_data_generator import GCNetTestDataGenerator

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
import django
django.setup()

from gcnet.models import test as StationTest


class GCNetTestCase(TestCase):
    databases = '__all__'

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
        print("Check retrieved swin is {0} = {1}".format(test1.swin, self.test_dataset[1][Columns.SWIN.value]))
        self.assertTrue(test1.swin == self.test_dataset[1][Columns.SWIN.value])

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

    def test_api_data(self):

        #http://127.0.0.1:8000/api/gcnet/summary/daily/json/test/all/1996-01-01/1996-12-31/
        start_timestamp = datetime.fromisoformat(self.test_dataset[1][Columns.TIMESTAMP_ISO.value]).strftime("%Y-%m-%d")
        end_timestamp = datetime.fromisoformat(self.test_dataset[50][Columns.TIMESTAMP_ISO.value]).strftime("%Y-%m-%d")

        path = '/api/gcnet/summary/daily/json/test/multiple/{0}/{1}/'.format(start_timestamp, end_timestamp)

        # Issue a GET request.
        response = self.client.get(path)

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)

        # Check that the response is 200 OK.
        data = json.loads(response.content)
        print("Check data is not empty,  len is {0}".format(len(data)))
        self.assertGreater(len(data), 0, "Models list should not be empty")

    def test_csv_import(self):

        local_dir = os.path.dirname(__file__)

        # source
        input_csv = "resources/test_input_01.csv"
        input_path = os.path.join(local_dir, input_csv)
        source = open(input_path, 'r')

        # config file
        test_config = "resources/stations_test.ini"
        config = os.path.join(local_dir, test_config)

        # model
        package = importlib.import_module("gcnet.models")
        model_class = StationTest # getattr(package, 'test')

        # perform import
        CsvImporter().import_csv(source, input_csv, config, model_class, verbose=False)

        # retrieve data
        start_timestamp = "2019-01-01"
        end_timestamp = "2019-12-31"

        path = '/api/gcnet/summary/daily/json/test/multiple/{0}/{1}/'.format(start_timestamp, end_timestamp)

        # Issue a GET request.
        response = self.client.get(path)

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)

        # TODO: Set option for defining id's in the import so we do not affect the sequence in the database

        # Check that the response is 200 OK.
        data = json.loads(response.content)
        print("Check 10 days data imported from CSV, got {0}".format(len(data)))
        self.assertEqual(len(data), 10, "Models list should not be empty. Ensure gcnet_test_id_seq set to 200")

    def test_dat_import(self):

        local_dir = os.path.dirname(__file__)

        # source
        input_csv = "resources/test_input_01.dat"
        input_path = os.path.join(local_dir, input_csv)
        source = open(input_path, 'r')

        # config file
        test_config = "resources/stations_test.ini"
        config = os.path.join(local_dir, test_config)

        # model
        package = importlib.import_module("gcnet.models")
        model_class = StationTest # getattr(package, 'test')

        # perform import
        DatImporter().import_dat(source, input_csv, config, model_class, verbose=False)

        # retrieve data
        start_timestamp = "1996-01-01"
        end_timestamp = "1996-12-31"

        path = '/api/gcnet/summary/daily/json/test/multiple/{0}/{1}/'.format(start_timestamp, end_timestamp)

        # Issue a GET request.
        response = self.client.get(path)

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)

        # TODO: Set option for defining id's in the import so we do not affect the sequence in the database

        # Check that the response is 200 OK.
        data = json.loads(response.content)
        print("Check 7 days data imported from DAT, got {0}".format(len(data)))
        self.assertEqual(len(data), 7, "Models list should not be empty. Ensure gcnet_test_id_seq set to 200")

    def test_nead_import(self):

        local_dir = os.path.dirname(__file__)

        # source
        input_csv = "resources/test_input_08_nead.csv"
        input_path = os.path.join(local_dir, input_csv)
        source = open(input_path, 'r')

        # config file
        test_config = "resources/stations_test.ini"
        config = os.path.join(local_dir, test_config)

        # model
        package = importlib.import_module("gcnet.models")
        model_class = getattr(package, 'test')

        # perform import
        NeadImporter().import_nead(source, input_csv, config, model_class, verbose=False)

        # retrieve data
        start_timestamp = "2014-01-01"
        end_timestamp = "2014-12-31"

        path = '/api/gcnet/summary/daily/json/test/multiple/{0}/{1}/'.format(start_timestamp, end_timestamp)

        # Issue a GET request.
        response = self.client.get(path)

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)

        # TODO: Set option for defining id's in the import so we do not affect the sequence in the database

        # Check that the response is 200 OK.
        data = json.loads(response.content)
        print("Check 6 days data imported from NEAD, got {0}".format(len(data)))
        self.assertEqual(len(data), 6, "Models list should not be empty. Ensure gcnet_test_id_seq set to 200")





