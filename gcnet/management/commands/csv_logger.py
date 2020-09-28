# Example commands:
#   python manage.py csv_logger -s 06_summit -c config/stations.ini -i gcnet/csv_output/6_summit.csv -d gcnet/data -t directory
#   python manage.py csv_logger -s 08_dye2 -c config/stations.ini -i gcnet/csv_output/8_dye2.csv -d gcnet/data -t directory
#   python manage.py csv_logger -s 24_east_grip -c config/stations.ini -i gcnet/csv_output/24_east_grip.csv -d gcnet/data -t directory


from pathlib import Path
import requests
from django.core.management.base import BaseCommand

from gcnet.csvvalidator import csv_validator, csv_null_checker

# Setup logging
import logging

logging.basicConfig(filename=Path('gcnet/csv_logs/east_grip.log'), format='%(asctime)s   %(filename)s: %(message)s',
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
            '-d',
            '--directory',
            required=True,
            help='Path to directory which will contain intermediate processing csv file'
        )

        parser.add_argument(
            '-t',
            '--typesource',
            required=True,
            help='Type of data source. Valid options are a file path: "directory" or a url: "web"'
        )

    def handle(self, *args, **kwargs):

        # Check if data source is from a directory or a url and assign input_file to selected option
        if kwargs['typesource'] == 'web':
            # Write content from url into csv file
            url = str(kwargs['inputfile'])
            print('URL: {0}'.format(url))
            req = requests.get(url)
            url_content = req.content
            csv_path = str(Path(kwargs['directory'] + '/' + kwargs['station'] + '_v.csv'))
            csv_file = open(csv_path, 'wb')
            csv_file.write(url_content)
            csv_file.close()
            input_file = csv_path

        elif kwargs['typesource'] == 'directory':
            input_file = Path(kwargs['inputfile'])
            print('INPUT FILE: {0}'.format(input_file))

        else:
            print('WARNING (csv_logger.py) non-valid value entered for "typesource": {0}'.format(kwargs['typesource']))
            return

        writer_no_duplicates = Path(kwargs['directory'] + '/' + kwargs['station'] + '_temporary.csv')

        csv_field_names = ['timestamp_iso', 'short_wave_incoming_radiation', 'short_wave_outgoing_radiation',
                           'net_radiation', 'air_temperature_1', 'air_temperature_2', 'relative_humidity_1',
                           'relative_humidity_2', 'wind_speed_1', 'wind_speed_2', 'wind_direction_1',
                           'wind_direction_2', 'atmospheric_pressure', 'snow_height_1', 'snow_height_2',
                           'battery_voltage']

        field_names = ['timestamp_iso', 'swin', 'swout', 'netrad', 'airtemp1', 'airtemp2',
                       'rh1', 'rh2', 'windspeed1', 'windspeed2', 'winddir1',
                       'winddir2', 'pressure', 'sh1', 'sh2',
                       'battvolt']

        # Write data in input_file into writer_no_duplicates with additional fields
        try:
            with open(writer_no_duplicates, 'w', newline='') as sink, open(input_file, 'r') as source:

                sink.write(','.join(field_names) + '\n')

                rows_before = 24
                rows_after = 1
                rows_buffer = []
                written_timestamps = []
                line_number = 0

                while True:

                    # Increment line_number
                    line_number += 1

                    line = source.readline()

                    # Skip header lines that start with '#'
                    if line.startswith('#'):
                        continue

                    if not line:
                        break

                    line_array = [v for v in line.strip().split(',') if len(v) > 0]

                    if len(line_array) != len(csv_field_names):
                        error_msg = "Line has {0} values, header {1} columns ".format(len(line_array),
                                                                                      len(csv_field_names))
                        # logger.error(error_msg)
                        raise ValueError(error_msg)

                    row = {csv_field_names[i]: line_array[i] for i in range(len(line_array))}

                    # Call csv_validator and log unexpected values
                    csv_validator(kwargs['config'], row, kwargs['inputfile'], line_number)

                    if row['timestamp_iso'] not in written_timestamps:

                        # keep timestamps length small
                        written_timestamps = written_timestamps[(-1) * min(len(written_timestamps), 1000):]
                        written_timestamps += row['timestamp_iso']

                        # slide the row buffer window
                        rows_buffer = rows_buffer[(-1) * min(len(rows_buffer), rows_before + rows_after):] + [row]

                        # check values before and after
                        if len(rows_buffer) > rows_after:
                            csv_null_checker(rows_buffer, rows_before, rows_after, kwargs['inputfile'], line_number)
                            sink.write(
                                ','.join(["{0}".format(v) for v in rows_buffer[-(1 + rows_after)].values()]) + '\n')

        except FileNotFoundError as e:
            print('WARNING (csv_logger.py) file not found {0}, exception {1}'.format(input_file, e))
            return
