# Example command:
#   python manage.py gcnet_csv_export -d gcnet/output -n 1_swisscamp -m swisscamp_01d
#   python manage.py gcnet_csv_export -d gcnet/output -n 2_crawfordpoint -m crawfordpoint_02d
#   python manage.py gcnet_csv_export -d gcnet/output -n 3_nasa_u -m nasa_u_03d

import importlib
from pathlib import Path
from django.core.management.base import BaseCommand

# Setup logging
import logging
logging.basicConfig(filename=Path('gcnet/logs/gcnet_csv_export.log'), format='%(asctime)s   %(filename)s: %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '-d',
            '--directory',
            required=True,
            help='Path to directory which will contain output csv file'
        )

        parser.add_argument(
            '-n',
            '--name',
            required=True,
            help='Name for csv file, for example "0_swisscamp"'
        )

        parser.add_argument(
            '-m',
            '--model',
            required=True,
            help='Django Model to export data from'
        )

    def handle(self, *args, **kwargs):

        # Create output_path from arguments
        output_path = Path(kwargs['directory'] + '/' + kwargs['name'] + '.csv')

        # Get the model
        class_name = kwargs['model'].rsplit('.', 1)[-1]
        package = importlib.import_module("gcnet.models")
        model_class = getattr(package, class_name)

        # Export database table to csv with only 'timestamp_iso' and parameter fields
        model_class.objects.order_by('timestamp_iso').to_csv(output_path,
                                                               'timestamp_iso',
                                                               'swin',
                                                               'swout',
                                                               'netrad',
                                                               'airtemp1',
                                                               'airtemp2',
                                                               'airtemp_cs500air1',
                                                               'airtemp_cs500air2',
                                                               'rh1',
                                                               'rh2',
                                                               'windspeed1',
                                                               'windspeed2',
                                                               'winddir1',
                                                               'winddir2',
                                                               'pressure',
                                                               'sh1',
                                                               'sh2',
                                                               'battvolt',
                                                               'swin_max',
                                                               'swout_max',
                                                               'netrad_max',
                                                               'airtemp1_max',
                                                               'airtemp2_max',
                                                               'airtemp1_min',
                                                               'airtemp2_min',
                                                               'windspeed_u1_max',
                                                               'windspeed_u2_max',
                                                               'windspeed_u1_stdev',
                                                               'windspeed_u2_stdev',
                                                               'reftemp'
                                                               )

        # Log import message
        logger.info('{0} successfully exported, written in {1}'.format(model_class, output_path))
