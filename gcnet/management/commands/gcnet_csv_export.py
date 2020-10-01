# Example commands:
#   python manage.py gcnet_csv_export -d gcnet/output -n 1_swisscamp -m swisscamp_01d -c gcnet/config/nead_header.ini -l ; -s -999
#   python manage.py gcnet_csv_export -d gcnet/csv_output -n 6_summit -m summit_06d -c gcnet/config/nead_header.ini -s -999
#   python manage.py gcnet_csv_export -d gcnet/csv_output -n 8_dye2 -m dye2_08d -c gcnet/config/nead_header.ini -s -999
#   python manage.py gcnet_csv_export -d gcnet/csv_output -n 24_east_grip -m east_grip_24d -c gcnet/config/nead_header.ini -s -999
#   python manage.py gcnet_csv_export -d gcnet/csv_output -n 4_gits -m gits_04d -c gcnet/config/nead_header.ini -s -999


import importlib
from pathlib import Path
from django.core.management.base import BaseCommand

# Setup logging
import logging

from gcnet.helpers import read_config, delete_line, prepend_line, get_gcnet_geometry, get_list_comma_delimited, \
    get_fields_string, get_units_offset_string, get_units_multiplier_string, get_display_units_string, \
    get_database_fields_data_types_string, prepend_multiple_lines, get_station_id

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

        parser.add_argument(
            '-c',
            '--config',
            required=True,
            help='Path to config file containing header'
        )

        parser.add_argument(
            '-l',
            '--delimiter',
            required=False,
            help='String that will be used as a delimiter in csv. Optional. Default delimiter is comma: ","'
        )

        parser.add_argument(
            '-s',
            '--stringnull',
            required=False,
            help='String to populate exported null values with in csv. Optional. Default null string is an empty string: ""'
        )

    def handle(self, *args, **kwargs):

        # ========================================= WRITE NEAD CONFIG =================================================

        # Remove first line from header config and store in first_line
        first_line = delete_line(kwargs['config'], 0)

        # Try to dynamically generate NEAD config file
        try:
            # Get header config
            config = read_config(kwargs['config'])

            # Get stations confg
            stations_config = read_config('gcnet/config/stations.ini')

            # Assign station_id to model's corresponding station_id
            station_id = get_station_id(kwargs['model'])

            # Set 'station_id'
            config.set('HEADER', 'station_id', str(station_id))

            # Set 'station_name'
            station_name = stations_config.get(str(station_id), 'name')
            config.set('HEADER', 'station_name', station_name)

            # Check if kwargs['stringnull'] passed. Set 'nodata_value' to kwarg stringnull passed.
            # Else set 'nodata_value' in config to empty string: ''
            if kwargs['stringnull']:
                config.set('HEADER', 'nodata_value', kwargs['stringnull'])
            else:
                config.set('HEADER', 'nodata_value', '')

            # Check if kwargs['delimiter'] passed. Set 'column_delimiter' to kwarg delimiter passed.
            # Else set 'column_delimiter' in config to comma: ','
            if kwargs['delimiter']:
                config.set('HEADER', 'column_delimiter', kwargs['delimiter'])
            else:
                config.set('HEADER', 'column_delimiter', ',')

            # Parse 'position' from stations.ini, modify, and set 'geometry'
            position = stations_config.get(str(station_id), 'position')
            geometry = get_gcnet_geometry(position)
            config.set('HEADER', 'geometry', geometry)

            # Get display_description as list
            display_description = config.get('HEADER', 'display_description')
            display_description_list = get_list_comma_delimited(display_description)

            # Call get_fields_string() and set 'fields'
            fields_string = get_fields_string(display_description_list)
            config.set('HEADER', 'fields', fields_string)

            # Call get_units_offset_string() and set 'units_offset'
            units_offset_string = get_units_offset_string(display_description_list)
            config.set('HEADER', 'units_offset', units_offset_string)

            # Call get_units_multiplier_string() and set 'units_multiplier'
            units_multiplier_string = get_units_multiplier_string(display_description_list)
            config.set('HEADER', 'units_multiplier', units_multiplier_string)

            # Call get_display_units_string() and set 'display_units'
            display_units_string = get_display_units_string(display_description_list)
            config.set('HEADER', 'display_units', display_units_string)

            # Call get_database_fields_data_types_string() and set 'database_fields_data_types'
            database_fields_data_types_string = get_database_fields_data_types_string(display_description_list)
            config.set('HEADER', 'database_fields_data_types', database_fields_data_types_string)

            # Dynamically write header in config file
            with open(kwargs['config'], encoding='utf-8', mode='w', newline='\n') as config_file:
                config.write(config_file)

        except Exception as e:
            # Write first_line to first line of header conf
            prepend_line(kwargs['config'], first_line)
            # Print error message
            print('WARNING (gcnet_csv_export.py): could not write nead header config, EXCEPTION: {0}'.format(e))
            return

        # ========================================= EXPORT CSV ========================================================

        # Create output_path from arguments
        output_path = Path(kwargs['directory'] + '/' + kwargs['name'] + '.csv')

        # Get the model
        class_name = kwargs['model'].rsplit('.', 1)[-1]
        package = importlib.import_module("gcnet.models")
        model_class = getattr(package, class_name)

        # Get fields tuple from config
        fields = config.get('HEADER', 'database_fields')
        fields_tuple = tuple(fields.split(","))

        # Get column_delimiter from config
        column_delimiter = config.get('HEADER', 'column_delimiter')

        # Check if stringnull argument was passed, if so assign it to null_value.
        # Else null_value = None and will by default null values will be assigned to empty string
        if kwargs['stringnull']:
            null_value = kwargs['stringnull']
        else:
            null_value = None

        # Export database table to csv with only 'timestamp_iso' and fields from 'display_description' in config
        model_class.objects.order_by('timestamp_iso').to_csv(output_path,
                                                             *fields_tuple,
                                                             delimiter=column_delimiter,
                                                             header=False,
                                                             null=null_value
                                                             )

        # Write first_line to first line of header conf
        prepend_line(kwargs['config'], first_line)

        # Prepend header to newly created csv file
        # Get header as header_list, each element is a line in the header configuration file
        header_path = kwargs['config']
        with open(header_path, 'r', newline='\n') as sink:
            header_list = sink.read().splitlines()

        # Prepend new csv file with multiple lines from header conf
        # All newly inserted lines will begin with the '#' character
        prepend_multiple_lines(output_path, header_list)

        # Log export message
        logger.info('{0} successfully exported, written in {1}'.format(model_class, output_path))
