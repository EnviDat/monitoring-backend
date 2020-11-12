# Example command:
#   python manage.py import_data -s 01_swisscamp -c gcnet/config/stations.ini -i gcnet/data/1_2019_min.csv -m swisscamp_01d -t file
#   python manage.py import_data -s 01_swisscamp -c gcnet/config/stations.ini -i https://www.wsl.ch/gcnet/data/1_v.csv -m swisscamp_01d -t web

from pathlib import Path
import requests
from django.core.management.base import BaseCommand
import importlib

from .impl.csv_import import CsvImporter

# Setup logging
import logging

logging.basicConfig(filename=Path('gcnet/logs/import_data.log'), format='%(asctime)s   %(filename)s: %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '-s',
            '--station',
            required=True,
            help='Station number and name, for example "02_crawford"'
        )

        parser.add_argument(
            '-c',
            '--config',
            required=True,
            help='Path to stations config file'
        )

        parser.add_argument(
            '-i',
            '--inputfile',
            required=True,
            help='Path or URL to input csv file'
        )

        parser.add_argument(
            '-m',
            '--model',
            required=True,
            help='Django Model to map data import to'
        )

        parser.add_argument(
            '-t',
            '--typesource',
            required=True,
            help='Type of data source. Valid options are a file path: "file" or a url: "web"'
        )

    def handle(self, *args, **kwargs):

        # Check if data source is from a directory or a url and assign input_file to selected option
        input_source = self._get_input_source(kwargs['typesource'], kwargs['inputfile'])
        if not input_source:
            print('WARNING (import_data.py) non-valid value entered for "typesource": {0}'.format(kwargs['typesource']))
            return

        # Get the model
        class_name = kwargs['model'].rsplit('.', 1)[-1]
        package = importlib.import_module("gcnet.models")
        model_class = getattr(package, class_name)
        if model_class is None:
            print('WARNING (import_data.py) no data found for {0}'.format(kwargs['station']))
            return

        # call the appropriate converter depending on the extension
        file_extension = kwargs['inputfile'].rsplit('.')[-1].lower().strip()
        if file_extension == "csv":
            return CsvImporter().import_csv(input_source, kwargs['inputfile'], kwargs['config'], model_class)
        else:
            print('WARNING (import_data.py) no avaliable converter for extension {0}'.format(file_extension))
            return

    # Check if data source is from a directory or a url and assign input_file to selected option
    def _get_input_source(self, typesource, inputfile):
        if typesource == 'web':
            # Write content from url into csv file
            url = str(inputfile)
            print('URL: {0}'.format(url))
            req = requests.get(url, stream=True)
            if req.encoding is None:
                req.encoding = 'utf-8'
            return req.iter_lines(decode_unicode=True)

        elif typesource == 'file':
            try:
                input_file = Path(inputfile)
                print('INPUT FILE: {0}'.format(input_file))
                source = open(input_file, 'r')
                return source
            except FileNotFoundError as e:
                raise FileNotFoundError(
                    'WARNING (csv_import.py) file not found {0}, exception {1}'.format(input_file, e))

        return None
