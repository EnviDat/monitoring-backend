# Example command:
#   python manage.py csv_import -s test_lwf_1 -p LWFMeteoTest -i monitoring/data/jubforest.csv -d monitoring/data -m test_lwf_1 -t directory

from pathlib import Path
import requests
from django.core.management.base import BaseCommand
from postgres_copy import CopyMapping
import importlib
from django.utils.timezone import make_aware

from monitoring.helpers import get_lwf_meteo_line_clean, get_lwf_meteo_copy_dict

# Setup logging
import logging

logging.basicConfig(filename=Path('monitoring/logs/csv_import.log'), format='%(asctime)s   %(filename)s: %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '-s',
            '--station',
            required=True,
            help='Station name, for example "lens"'
        )

        parser.add_argument(
            '-p',
            '--parentclass',
            required=True,
            help='Parent class that child class (database table) inherits fields from'
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
            '-m',
            '--model',
            required=True,
            help='Django Model to map data import to'
        )

        parser.add_argument(
            '-t',
            '--typesource',
            required=True,
            help='Type of input data source. Valid options are a file path: "directory" or a url: "web"'
        )

    def handle(self, *args, **kwargs):

        # Check if data source is from a directory or a url and assign input_file to selected option
        if kwargs['typesource'] == 'web':
            # Write content from url into csv file
            url = str(kwargs['inputfile'])
            print('URL: {0}'.format(url))
            req = requests.get(url)
            url_content = req.content
            csv_path = str(Path(kwargs['directory'] + '/' + kwargs['inputfile']))
            csv_file = open(csv_path, 'wb')
            csv_file.write(url_content)
            csv_file.close()
            input_file = csv_path

        elif kwargs['typesource'] == 'directory':
            input_file = Path(kwargs['inputfile'])
            print('INPUT FILE: {0}'.format(input_file))

        else:
            print('WARNING (csv_import.py) non-valid value entered for "typesource": {0}'.format(kwargs['typesource']))
            return

        # Get the parent class, assumes parent class is in module within models directory
        parent_name = kwargs['parentclass'].rsplit('.', 1)[-1]
        package = importlib.import_module("monitoring.models." + parent_name)
        parent_class = getattr(package, parent_name)

        writer = Path(kwargs['directory'] + '/' + kwargs['station'] + '_temporary.csv')

        csv_field_names = parent_class.input_fields

        field_names = parent_class.model_fields

        date_form = parent_class.date_format

        model_class = None

        written_timestamps = []
        rows_before = 24
        rows_after = 1
        rows_buffer = []

        # Write data in input_file into writer_no_duplicates with additional fields
        try:
            with open(writer, 'w', newline='') as sink, open(input_file, 'r') as source:

                sink.write(','.join(field_names) + '\n')
                records_written = 0

                # Skip header if it exists
                if parent_class.header:
                    next(source, None)

                while True:

                    line = source.readline()

                    if not line:
                        break
                    line_array = [v for v in line.strip().split(parent_class.delimiter) if len(v) > 0]

                    if len(line_array) != len(csv_field_names):
                        error_msg = "Line has {0} values, header {1} columns ".format(len(line_array),
                                                                                      len(csv_field_names))
                        logger.error(error_msg)
                        raise ValueError(error_msg)

                    row = {csv_field_names[i]: line_array[i] for i in range(len(line_array))}

                    # Process row and add new calculated fields
                    # Check which kind of cleaner should be applied
                    if kwargs['parentclass'] == 'LWFMeteoTest':
                        line_clean = get_lwf_meteo_line_clean(row, date_form)
                    else:
                        print('WARNING (csv_import.py) {0} parentclass does not exist'.format(kwargs['parentclass']))
                        return

                    # Get the model
                    class_name = kwargs['model'].rsplit('.', 1)[-1]
                    package = importlib.import_module("monitoring.models")
                    model_class = getattr(package, class_name)

                    # Make timestamp_iso value a UTC timezone aware datetime object
                    dt_obj = line_clean['timestamp_iso']
                    aware_dt = make_aware(dt_obj)

                    # Check if record with identical timestamp already exists in database, otherwise write record to
                    # temporary csv file after checking for record with duplicate timestamp
                    try:
                        model_class.objects.get(timestamp_iso=aware_dt)
                    except model_class.DoesNotExist:
                        if line_clean['timestamp_iso'] not in written_timestamps:
                            # keep timestamps length small
                            written_timestamps = written_timestamps[(-1) * min(len(written_timestamps), 1000):]
                            written_timestamps += [line_clean['timestamp_iso']]

                            # slide the row buffer window
                            rows_buffer = rows_buffer[(-1) * min(len(rows_buffer), rows_before + rows_after):] + [
                                line_clean]

                            # check values before and after
                            if len(rows_buffer) > rows_after:
                                sink.write(
                                    ','.join(["{0}".format(v) for v in rows_buffer[-(1 + rows_after)].values()]) + '\n')
                                records_written += 1

        except FileNotFoundError as e:
            print('WARNING (csv_import.py) file not found {0}, exception {1}'.format(input_file, e))
            return

        if model_class is None:
            print('WARNING (csv_import.py) no data found for {0}'.format(kwargs['station']))
            return

        # Check which kind of copy_dictionary should be applied
        if kwargs['parentclass'] == 'LWFMeteoTest':
            copy_dictionary = get_lwf_meteo_copy_dict()
        else:
            print('WARNING (csv_import.py) {0} parentclass does not exist'.format(kwargs['parentclass']))
            return

        # Import processed and cleaned data into Postgres database
        c = CopyMapping(

            # Give it the model
            model_class,

            # CSV with timestamps and other generated fields and no duplicate records
            writer,

            # And a dict mapping the model fields to CSV headers
            copy_dictionary,
        )
        # Then save it.
        c.save()

        # Log import message
        logger.info('{0} successfully imported, {1} new record(s) written in {2}'.format((kwargs['inputfile']),
                                                                                         records_written,
                                                                                         (kwargs['model'])))
