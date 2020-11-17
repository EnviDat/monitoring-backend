# Example command:
#   python manage.py import_data -s 01_swisscamp -c gcnet/config/stations.ini -i gcnet/data/1_2019_min.csv -m swisscamp_01d -t file
#   python manage.py import_data -s 01_swisscamp -c gcnet/config/stations.ini -i https://www.wsl.ch/gcnet/data/1_v.csv -m swisscamp_01d -t web

#   python manage.py import_data -s 01_swisscamp -c gcnet/config/stations.ini -i gcnet/data/1_2019_min.csv  -m swisscamp_01d -l True -d gcnet/data/output -t file

from pathlib import Path
import requests
from django.core.management.base import BaseCommand
import importlib
from datetime import datetime
from .importers.csv_import import CsvImporter

from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

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
            required=True, type=str,
            help='Path or URL to input csv/dat file'
        )

        parser.add_argument(
            '-l',
            '--loggeronly', type=bool,
            required=False, default=False,
            help='If set to True the csv will be validated and logged to a file in the -d directory'
        )

        parser.add_argument(
            '-d',
            '--directory',
            required=False,
            help='Path to directory which will contain output logger file when --loggeronly=True option'
        )

        parser.add_argument(
            '-m',
            '--model',
            required=True,
            help='Django Model to map data import to'
        )

        parser.add_argument(
            '-f',
            '--force', type=self.str2bool,
            required=False, default=False,
            help='Forces the import every valid row, skips the ones that fail. Defaults to False.'
        )

    def handle(self, *args, **kwargs):

        # Check if data source is from a directory or a url and assign input_file to selected option
        input_source = self._get_input_source(kwargs['inputfile'])
        if not input_source:
            print('WARNING (import_data.py) non-valid value entered for "inputfile": {0}'.format(kwargs['inputfile']))
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
            if kwargs['loggeronly']:
                if kwargs.get('directory'):
                    output_file = Path(kwargs['directory'] + '/' + kwargs['station'] + '_logger_{0}.csv'
                                       .format(datetime.now().strftime("%Y%m%d_%H%M%S%f")))
                    print('OUTPUT FILE: {0}'.format(output_file))
                    return CsvImporter().logger_csv(input_source, kwargs['inputfile'], output_file, kwargs['config'])
                else:
                    print("ERROR: --loggeronly parameter requires to specify the --directory parameter for output")
            else:
                return CsvImporter().import_csv(input_source, kwargs['inputfile'], kwargs['config'],
                                                model_class, force=kwargs['force'])
        else:
            print('WARNING (import_data.py) no available converter for extension {0}'.format(file_extension))
            return

    # Check if data source is from a directory or a url and assign input_file to selected option
    def _get_input_source(self, inputfile):
        if self.is_url(inputfile):
            # Write content from url into csv file
            url = str(inputfile)
            print('URL: {0}'.format(url))
            req = requests.get(url, stream=True)
            if req.encoding is None:
                req.encoding = 'utf-8'
            return req.iter_lines(decode_unicode=True)

        else:
            try:
                input_file = Path(inputfile)
                print('INPUT FILE: {0}'.format(input_file))
                source = open(input_file, 'r')
                return source
            except FileNotFoundError as e:
                raise FileNotFoundError(
                    'WARNING (csv_import.py) file not found {0}, exception {1}'.format(input_file, e))

    @staticmethod
    def is_url(text):
        try:
            URLValidator()(text)
            return True
        except ValidationError:
            pass
        return False

    @staticmethod
    def str2bool(v):
        if isinstance(v, bool):
            return v
        if v.lower() in ('yes', 'true', 't', 'y', '1'):
            return True
        elif v.lower() in ('no', 'false', 'f', 'n', '0'):
            return False
        else:
            raise argparse.ArgumentTypeError('Boolean value expected.')
