# Example commands:
#   python manage.py lwf_csv_import -s leb -p LWFMeteo -i lwf/data/lebforest.csv -d lwf/data -m leb -t directory
#   python manage.py lwf_csv_import -s alb -p LWFMeteo -i lwf/data/albforest.csv -d lwf/data -m alb -t directory
#   python manage.py lwf_csv_import -s baf -p LWFMeteo -i lwf/data/baffield.csv -d lwf/data -m baf -t directory
#   python manage.py lwf_csv_import -s bab -p LWFMeteo -i lwf/data/babforest.csv -d lwf/data -m bab -t directory
#   python manage.py lwf_csv_import -s clb -p LWFMeteo -i lwf/data/clbforest.csv -d lwf/data -m clb -t directory
#   python manage.py lwf_csv_import -s clf -p LWFMeteo -i lwf/data/clffield.csv -d lwf/data -m clf -t directory
#   python manage.py lwf_csv_import -s jub -p LWFMeteo -i lwf/data/jubforest.csv -d lwf/data -m jub -t directory
#   python manage.py lwf_csv_import -s juf -p LWFMeteo -i lwf/data/juffield.csv -d lwf/data -m juf -t directory
#   python manage.py lwf_csv_import -s isb -p LWFMeteo -i lwf/data/isbforest.csv -d lwf/data -m isb -t directory
#   python manage.py lwf_csv_import -s isf -p LWFMeteo -i lwf/data/isffield.csv -d lwf/data -m isf -t directory
#   python manage.py lwf_csv_import -s btf -p LWFMeteo -i lwf/data/btffield.csv -d lwf/data -m btf -t directory
#   python manage.py lwf_csv_import -s btb -p LWFMeteo -i lwf/data/btbforest.csv -d lwf/data -m btb -t directory
#   python manage.py lwf_csv_import -s cib -p LWFMeteo -i lwf/data/cibforest.csv -d lwf/data -m cib -t directory
#   python manage.py lwf_csv_import -s cif -p LWFMeteo -i lwf/data/ciffield.csv -d lwf/data -m cif -t directory
#   python manage.py lwf_csv_import -s nab -p LWFMeteo -i lwf/data/nabforest.csv -d lwf/data -m nab -t directory
#   python manage.py lwf_csv_import -s naf -p LWFMeteo -i lwf/data/naffield.csv -d lwf/data -m naf -t directory
#   python manage.py lwf_csv_import -s vsb -p LWFMeteo -i lwf/data/vsbforest.csv -d lwf/data -m vsb -t directory
#   python manage.py lwf_csv_import -s vsf -p LWFMeteo -i lwf/data/vsffield.csv -d lwf/data -m vsf -t directory
#   python manage.py lwf_csv_import -s lab -p LWFMeteo -i lwf/data/labforest.csv -d lwf/data -m lab -t directory
#   python manage.py lwf_csv_import -s laf -p LWFMeteo -i lwf/data/laffield.csv -d lwf/data -m laf -t directory
#   python manage.py lwf_csv_import -s vob -p LWFMeteo -i lwf/data/vobforest.csv -d lwf/data -m vob -t directory
#   python manage.py lwf_csv_import -s vof -p LWFMeteo -i lwf/data/voffield.csv  -d lwf/data -m vof -t directory
#   python manage.py lwf_csv_import -s neb -p LWFMeteo -i lwf/data/nebforest.csv  -d lwf/data -m neb -t directory
#   python manage.py lwf_csv_import -s nef -p LWFMeteo -i lwf/data/neffield.csv  -d lwf/data -m nef -t directory
#   python manage.py lwf_csv_import -s nob -p LWFMeteo -i lwf/data/nobforest.csv  -d lwf/data -m nob -t directory
#   python manage.py lwf_csv_import -s nof -p LWFMeteo -i lwf/data/noffield.csv  -d lwf/data -m nof -t directory
#   python manage.py lwf_csv_import -s otb -p LWFMeteo -i lwf/data/otbforest.csv  -d lwf/data -m otb -t directory
#   python manage.py lwf_csv_import -s otf -p LWFMeteo -i lwf/data/otffield.csv  -d lwf/data -m otf -t directory
#   python manage.py lwf_csv_import -s scb -p LWFMeteo -i lwf/data/scbforest.csv  -d lwf/data -m scb -t directory
#   python manage.py lwf_csv_import -s scf -p LWFMeteo -i lwf/data/scffield.csv  -d lwf/data -m scf -t directory

#   python manage.py lwf_csv_import -s test4 -p LWFStation -i lwf/data/12.csv  -d lwf/data -m test3 -t directory
import os

from pathlib import Path
import requests
from django.core.management.base import BaseCommand
from postgres_copy import CopyMapping
import importlib
from django.utils.timezone import make_aware

# Setup logging
import logging

from lwf.util.cleaners import get_lwf_meteo_line_clean, get_lwf_station_line_clean
from lwf.util.copy_dicts import get_lwf_meteo_copy_dict, get_lwf_station_copy_dict

logging.basicConfig(filename=Path('lwf/logs/lwf_csv_import.log'), format='%(asctime)s   %(filename)s: %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '-s',
            '--station',
            required=True,
            help='Station name, for example "lens", used to name temporary csv file'
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
            logger.info('URL: {0}'.format(url))
            req = requests.get(url)
            url_content = req.content
            csv_path = str(Path(kwargs['directory'] + '/' + kwargs['inputfile']))
            csv_file = open(csv_path, 'wb')
            csv_file.write(url_content)
            csv_file.close()
            input_file = csv_path

        elif kwargs['typesource'] == 'directory':
            input_file = Path(kwargs['inputfile'])
            logger.info('INPUT FILE: {0}'.format(input_file))

        else:
            logger.info('WARNING (lwf_csv_import.py) non-valid value entered for "typesource": {0}'.format(
                kwargs['typesource']))
            return

        # Get the parent class, assumes parent class is in module within lwf/models directory
        parent_name = kwargs['parentclass'].rsplit('.', 1)[-1]
        package = importlib.import_module("lwf.models." + parent_name)
        parent_class = getattr(package, parent_name)

        csv_temporary = Path(kwargs['directory'] + '/' + kwargs['station'] + '_temporary.csv')

        csv_field_names = parent_class.input_fields

        field_names = parent_class.model_fields

        date_form = parent_class.date_format

        model_class = None

        written_timestamps = []
        rows_before = 24
        rows_after = 0
        rows_buffer = []

        # Write data in input_file into csv_temporary with additional computed fields
        try:
            with open(csv_temporary, 'w', newline='') as sink, open(input_file, 'r') as source:

                sink.write(','.join(field_names) + '\n')
                records_written = 0

                # Skip number of header lines designated in parent class header line count
                for i in range(parent_class.header_line_count):
                    next(source, None)

                while True:

                    line = source.readline()

                    if not line:
                        break
                    line_array = [v for v in line.strip().split(parent_class.delimiter) if len(v) > 0]

                    # Skip header lines that start with designated parent class header symbol
                    # For example: the '#' character
                    if line.startswith(parent_class.header_symbol):
                        continue

                    if len(line_array) != len(csv_field_names):
                        error_msg = "Line has {0} values, header {1} columns ".format(len(line_array),
                                                                                      len(csv_field_names))
                        logger.error(error_msg)
                        raise ValueError(error_msg)

                    row = {csv_field_names[i]: line_array[i] for i in range(len(line_array))}

                    # Process row and add new calculated fields
                    # Check which kind of cleaner should be applied
                    if kwargs['parentclass'] == 'LWFMeteo':
                        line_clean = get_lwf_meteo_line_clean(row, date_form)
                    elif kwargs['parentclass'] == 'LWFStation':
                        line_clean = get_lwf_station_line_clean(row, date_form)
                    else:
                        logger.info(
                            'WARNING (lwf_csv_import.py) {0} parentclass does not exist'.format(kwargs['parentclass']))
                        return

                    # Get the model
                    class_name = kwargs['model'].rsplit('.', 1)[-1]
                    package = importlib.import_module("lwf.models")
                    model_class = getattr(package, class_name)

                    # Make timestamp_iso value a UTC timezone aware datetime object
                    dt_obj = line_clean['timestamp_iso']
                    aware_dt = make_aware(dt_obj)

                    # Check if record with identical timestamp already exists in table, otherwise write record to
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
            logger.info('WARNING (lwf_csv_import.py) file not found {0}, exception {1}'.format(input_file, e))
            return

        if model_class is None:
            logger.info('WARNING (lwf_csv_import.py) no data found for {0}'.format(kwargs['station']))
            return

        # Check which kind of copy_dictionary should be applied
        if kwargs['parentclass'] == 'LWFMeteo':
            copy_dictionary = get_lwf_meteo_copy_dict()
        elif kwargs['parentclass'] == 'LWFStation':
            copy_dictionary = get_lwf_station_copy_dict()
        else:
            logger.info('WARNING (lwf_csv_import.py) {0} parentclass does not exist'.format(kwargs['parentclass']))
            return

        # Import processed and cleaned data into Postgres database
        c = CopyMapping(

            # Give it the model
            model_class,

            # Temporary CSV with input data and generated fields
            csv_temporary,

            # And a dict mapping the model fields to CSV fields
            copy_dictionary,
        )
        # Then save it.
        c.save()

        # Log import message
        logger.info('{0} successfully imported, {1} new record(s) written in {2}'.format((kwargs['inputfile']),
                                                                                         records_written,
                                                                                         (kwargs['model'])))

        # Delete csv_temporary
        os.remove(csv_temporary)
