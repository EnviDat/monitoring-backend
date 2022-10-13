# Example commands:
# python manage.py csv_import -i lwf/data/test.csv -t directory -d lwf/data -a lwf -m test41
# python manage.py csv_import -i https://os.zhdk.cloud.switch.ch/envidat4lwf/p1_meteo/historical/1.csv -t web -d lwf/data -a lwf -m test41
# python manage.py csv_import -i https://os.zhdk.cloud.switch.ch/envidat4lwf/p1_meteo/1.csv -t web -d lwf/data -a lwf -m test41


# Setup logging
import logging
import os
from pathlib import Path

import requests
from django.apps import apps
from django.core.management.base import BaseCommand
from django.utils.timezone import make_aware
from generic.util.nead import write_nead_config
from generic.util.views_helpers import get_model_cl
from lwf.util.cleaners import (get_lwf_meteo_line_clean,
                               get_lwf_station_line_clean)
from postgres_copy import CopyMapping

logging.basicConfig(
    filename=Path("generic/logs/csv_import.log"),
    format="%(asctime)s  %(filename)s: %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Command(BaseCommand):
    def add_arguments(self, parser):

        parser.add_argument(
            "-i", "--inputfile", required=True, help="Path or URL to input csv file"
        )

        parser.add_argument(
            "-t",
            "--typesource",
            required=True,
            help='Type of input data source. Valid options are a file path: "directory" or a url: "web"',
        )

        parser.add_argument(
            "-d",
            "--directory",
            required=True,
            help="Path to directory which will contain temporary intermediate processing csv file "
            "and if using web option temporary downloaded file. ",
        )

        parser.add_argument(
            "-a", "--app", required=True, help="App that Django model belongs to"
        )

        parser.add_argument(
            "-m",
            "--model",
            required=True,
            help="Django Model to import input data into",
        )

    def handle(self, *args, **kwargs):

        # Assign kwargs from url to variables
        inputfile = kwargs["inputfile"]
        typesource = kwargs["typesource"]
        directory = kwargs["directory"]
        app = kwargs["app"]
        model = kwargs["model"]

        # Check if data source is from a directory or a url and assign input_file to selected option
        if typesource == "web":

            # Write content from url into csv file
            url = str(inputfile)
            logger.info(f"STARTED importing input URL: {url}")
            req = requests.get(url)
            url_content = req.content
            input_file = Path(f"{directory}/{model}_downloaded.csv")
            csv_file = open(input_file, "wb")
            csv_file.write(url_content)
            csv_file.close()
        elif typesource == "directory":
            input_file = Path(inputfile)
            logger.info(f"STARTED importing input file: {input_file}")
        else:
            logger.error(
                f'ERROR non-valid value entered for "typesource": {typesource}'
            )
            return

        # Validate app
        if not apps.is_installed(app):
            logger.error(f"ERROR app {app} not found")
            return

        # Validate model
        try:
            model_class = get_model_cl(app, model)
        except AttributeError as e:
            logger.error(f"ERROR model {model} not found, exception {e}")
            return

        # Get parent class name
        parent_class_name = model_class.__base__.__name__

        # Get line cleaner function
        try:
            line_cleaner = self.get_line_cleaner(parent_class_name)
        except Exception as e:
            logger.error(e)
            return

        # Assign other variables used to write csv_temporary
        csv_temporary = Path(f"{directory}/{model}_temporary.csv")
        input_fields = model_class.input_fields
        database_fields = [
            field.name for field in model_class._meta.fields if field.name != "id"
        ]
        date_format = model_class.date_format
        written_timestamps = []
        rows_before = 24
        rows_after = 0
        rows_buffer = []
        nead_header = []

        # Write data in input_file into csv_temporary with additional computed fields
        try:
            with open(csv_temporary, "w", newline="") as sink, open(
                input_file
            ) as source:

                sink.write(",".join(database_fields) + "\n")
                records_written = 0

                # Skip number of header lines designated in parent class header line count
                for i in range(model_class.header_line_count):
                    first_lines = source.readline()
                    nead_header.append(first_lines)
                    next(source, None)

                while True:

                    line = source.readline()

                    if not line:
                        break
                    line_array = [
                        v
                        for v in line.strip().split(model_class.delimiter)
                        if len(v) > 0
                    ]

                    # Skip header lines that start with designated parent class header symbol
                    # For example: the '#' character
                    if line.startswith(model_class.header_symbol):
                        nead_header.append(line)
                        continue

                    if len(line_array) != len(input_fields):
                        error_msg = f"ERROR: line has {len(line_array)} values, header has {len(input_fields)} columns"
                        logger.error(error_msg)
                        raise ValueError(error_msg)

                    row = {
                        input_fields[i]: line_array[i] for i in range(len(line_array))
                    }

                    # Process row and add new computed fields
                    line_clean = line_cleaner(row, date_format)

                    # Make timestamp_iso value a UTC timezone aware datetime object
                    dt_obj = line_clean["timestamp_iso"]
                    aware_dt = make_aware(dt_obj)

                    # Check if record with identical timestamp already exists in table, otherwise write record to
                    # temporary csv file after checking for record with duplicate timestamp
                    try:
                        model_class.objects.get(timestamp_iso=aware_dt)
                    except model_class.DoesNotExist:
                        if line_clean["timestamp_iso"] not in written_timestamps:
                            # keep timestamps length small
                            written_timestamps = written_timestamps[
                                (-1) * min(len(written_timestamps), 1000) :
                            ]
                            written_timestamps += [line_clean["timestamp_iso"]]

                            # slide the row buffer window
                            rows_buffer = rows_buffer[
                                (-1) * min(len(rows_buffer), rows_before + rows_after) :
                            ] + [line_clean]

                            # check values before and after
                            if len(rows_buffer) > rows_after:
                                sink.write(
                                    ",".join(
                                        [
                                            f"{v}"
                                            for v in rows_buffer[
                                                -(1 + rows_after)
                                            ].values()
                                        ]
                                    )
                                    + "\n"
                                )
                                records_written += 1

                # Write nead header configuration file if applicable
                if nead_header:
                    header_symbol = model_class.header_symbol
                    write_nead_config(
                        app, nead_header, model, parent_class_name, header_symbol
                    )

        except FileNotFoundError as e:
            logger.error(f"ERROR file not found {input_file}, exception {e}")
            return

        # Assign copy_dictionary from database_fields
        copy_dictionary = {
            database_fields[i]: database_fields[i]
            for i in range(0, len(database_fields))
        }

        # Import processed and cleaned data into Postgres database
        c = CopyMapping(
            # Assign model
            model_class,
            # Temporary CSV with input data and computed fields
            csv_temporary,
            # Dictionary mapping the model fields to CSV fields
            copy_dictionary,
        )
        # Then save it.
        c.save()

        # Log import message
        logger.info(
            f"FINISHED importing {input_file}, {records_written} new records written in {model}"
        )

        # Delete csv_temporary
        os.remove(csv_temporary)

        # If file downloaded from web delete it
        if os.path.isfile(f"{directory}/{model}_downloaded.csv"):
            os.remove(f"{directory}/{model}_downloaded.csv")

    # Check which kind of line cleaner should be used
    @staticmethod
    def get_line_cleaner(parent_class_name):

        if parent_class_name == "LWFMeteo":
            return get_lwf_meteo_line_clean

        elif parent_class_name == "LWFStation":
            return get_lwf_station_line_clean

        else:
            raise Exception(
                f"ERROR parent class {parent_class_name} does not exist "
                f"or is not specified in csv_import.py"
            )
