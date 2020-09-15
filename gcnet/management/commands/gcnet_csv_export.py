# Example command:
#   python manage.py gcnet_csv_export -s 01_swisscamp -c config/stations.ini -i gcnet/data/1.csv -d gcnet/data -m swisscamp_01d -t web

from pathlib import Path
import requests
from django.core.management.base import BaseCommand
from postgres_copy import CopyMapping
import importlib
from django.utils.timezone import make_aware

from gcnet.helpers import quarter_day, half_day, year_day, year_week, gcnet_utc_timestamp, gcnet_utc_datetime

# Setup logging
import logging

from gcnet.models import swisscamp_01d

logging.basicConfig(filename=Path('gcnet/logs/gcnet_csv_export.log'), format='%(asctime)s   %(filename)s: %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Command(BaseCommand):

    # def add_arguments(self, parser):
    #     parser.add_argument(
    #         '-s',
    #         '--station',
    #         required=True,
    #         help='Station number and name, for example "02_crawford"'
    #     )
    #
    #     parser.add_argument(
    #         '-c',
    #         '--config',
    #         required=True,
    #         help='Path to stations config file'
    #     )
    #
    #     parser.add_argument(
    #         '-i',
    #         '--inputfile',
    #         required=True,
    #         help='Path or URL to input csv file'
    #     )
    #
    #     parser.add_argument(
    #         '-d',
    #         '--directory',
    #         required=True,
    #         help='Path to directory which will contain intermediate processing csv file'
    #     )
    #
    #     parser.add_argument(
    #         '-m',
    #         '--model',
    #         required=True,
    #         help='Django Model to map data import to'
    #     )
    #
    #     parser.add_argument(
    #         '-t',
    #         '--typesource',
    #         required=True,
    #         help='Type of data source. Valid options are a file path: "directory" or a url: "web"'
    #     )

    def handle(self, *args, **kwargs):

        swisscamp_01d.objects.order_by('timestamp_iso').to_csv('gcnet/output/0_swisscamp.csv',
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