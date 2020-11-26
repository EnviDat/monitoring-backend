from django.test import TestCase
from django.test import Client
from django.db import connection
import os

import json

from gcnet.management.commands.importers.csv_import import CsvImporter
from gcnet.management.commands.importers.dat_import import DatImporter
from gcnet.management.commands.importers.nead_import import NeadImporter

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")

import django
django.setup()

from gcnet.models import test as station_test


class GCNetImportTestCase(TestCase):
    databases = '__all__'

    @classmethod
    def setUp(cls):
        cls.client = Client()

    def tearDown(self):
        # reset sequence and clean db
        with connection.cursor() as c:
            c.execute("DELETE FROM gcnet.gcnet_test;")
            c.execute("SELECT setval('gcnet.gcnet_test_id_seq', 1, true);")
        pass

    def test_csv_import(self):

        local_dir = os.path.dirname(__file__)

        # set input path
        input_csv = "resources/test_input_01.csv"
        input_path = os.path.join(local_dir, input_csv)

        # get source
        source = open(input_path, 'r')

        # config file
        test_config = "resources/stations_test.ini"
        config = os.path.join(local_dir, test_config)

        # model
        model_class = station_test

        # perform import
        written_rows = CsvImporter().import_csv(source, input_csv, config, model_class, verbose=False)

        # assert all rows were imported
        num_lines = self._count_input_lines(input_path)
        self.assertEqual(num_lines, int(written_rows), "Should retrieve {0} written rows, got {1}."
                         .format(num_lines, written_rows))

        # retrieve data
        start_timestamp = "2019-01-01"
        end_timestamp = "2019-12-31"

        path = '/api/gcnet/summary/daily/json/test/multiple/{0}/{1}/'.format(start_timestamp, end_timestamp)

        # Issue a GET request.
        response = self.client.get(path)

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)

        # Check that the response is 200 OK.
        data = json.loads(response.content)
        print("Check 10 days data imported from CSV, got {0}".format(len(data)))
        self.assertEqual(len(data), 10, "Should retrieve 10 imported rows.")

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
        model_class = station_test

        # perform import
        written_rows = DatImporter().import_dat(source, input_csv, config, model_class, verbose=False)

        # assert all rows were imported
        num_lines = self._count_input_lines(input_path)
        self.assertEqual(num_lines, int(written_rows), "Should retrieve {0} written rows, got {1}."
                         .format(num_lines, written_rows))

        # retrieve data
        start_timestamp = "1996-01-01"
        end_timestamp = "1996-12-31"

        path = '/api/gcnet/summary/daily/json/test/multiple/{0}/{1}/'.format(start_timestamp, end_timestamp)

        # Issue a GET request.
        response = self.client.get(path)

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)

        # Check that the response is 200 OK.
        data = json.loads(response.content)
        print("Check 7 days data imported from DAT, got {0}".format(len(data)))
        self.assertEqual(len(data), 7, "Should retrieve 7 imported rows.")

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
        model_class = station_test

        # perform import
        written_rows = NeadImporter().import_nead(source, input_csv, config, model_class, verbose=False)

        # assert all rows were imported
        num_lines = self._count_input_lines(input_path)
        self.assertEqual(num_lines, int(written_rows), "Should retrieve {0} written rows, got {1}."
                         .format(num_lines, written_rows))

        # retrieve data
        start_timestamp = "2014-01-01"
        end_timestamp = "2014-12-31"

        path = '/api/gcnet/summary/daily/json/test/multiple/{0}/{1}/'.format(start_timestamp, end_timestamp)

        # Issue a GET request.
        response = self.client.get(path)

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)

        # Check that the response is 200 OK.
        data = json.loads(response.content)
        print("Check 6 days data imported from NEAD, got {0}".format(len(data)))
        self.assertEqual(len(data), 6, "Should retrieve 6 imported rows.")

    @staticmethod
    def _count_input_lines(input_path):
        with open(input_path) as f:
            num_lines = sum(1 for l in f if not (l.startswith('#')) and (len(l.strip()) > 0))
        return num_lines
