# Example command:
#   python manage.py import_data -s 01_swisscamp -c gcnet/config/stations.ini -i gcnet/data/1_2019_min.csv -m swisscamp_01d
#   python manage.py import_data -s 01_swisscamp -c gcnet/config/stations.ini -i https://www.wsl.ch/gcnet/data/1_v.csv -m swisscamp_01d
#   python manage.py import_data -s 01_swisscamp -c gcnet/config/stations.ini -i gcnet/data/1_2019_min.csv  -m swisscamp_01d -l True -d gcnet/data/output
#   python manage.py import_data -s 01_swisscamp -c gcnet/config/stations.ini -i gcnet/data/1_1996_30lines.dat -m swisscamp_01d
#   python manage.py import_data -s 08_dye2 -c gcnet/config/stations.ini -i gcnet/data/8_nead_min.csv  -m dye2_08d -f 1
import argparse
import importlib
# Setup logging
import logging
from datetime import datetime
from pathlib import Path

import requests
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.core.validators import URLValidator

from .importers.csv_import import CsvImporter
from .importers.dat_import import DatImporter
from .importers.nead_import import NeadImporter

# logging.basicConfig(filename=Path('gcnet/logs/import_data.log'), format='%(asctime)s   %(filename)s: %(message)s',
# #                     datefmt='%d-%b-%y %H:%M:%S')
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "-s",
            "--station",
            required=True,
            help='Station number and name, for example "02_crawford"',
        )

        parser.add_argument(
            "-c", "--config", required=True, help="Path to stations config file"
        )

        parser.add_argument(
            "-i",
            "--inputfile",
            required=True,
            type=str,
            help="Path or URL to input csv/dat file",
        )

        parser.add_argument(
            "-l",
            "--loggeronly",
            type=bool,
            required=False,
            default=False,
            help="If set to True the csv will be validated and logged to a file in the -d directory",
        )

        parser.add_argument(
            "-d",
            "--directory",
            required=False,
            help="Path to directory which will contain output logger file when --loggeronly=True option",
        )

        parser.add_argument(
            "-m", "--model", required=True, help="Django Model to map data import to"
        )

        parser.add_argument(
            "-f",
            "--force",
            type=self.str2bool,
            required=False,
            default=False,
            help="Forces the import every valid row, skips the ones that fail. Defaults to False.",
        )

    def handle(self, *args, **kwargs):

        # Check if data source is from a directory or a url and assign input_file to selected option
        input_source = self._get_input_source(kwargs["inputfile"])
        if not input_source:
            print(
                'ERROR (import_data.py) non-valid value entered for "inputfile": {}'.format(
                    kwargs["inputfile"]
                )
            )
            return

        # Get the model
        class_name = kwargs["model"].rsplit(".", 1)[-1]
        package = importlib.import_module("gcnet.models")
        model_class = getattr(package, class_name)
        if model_class is None:
            print(
                "ERROR (import_data.py) no data found for {}".format(kwargs["station"])
            )
            return

        # call the appropriate converter depending on the extension
        file_extension = kwargs["inputfile"].rsplit(".")[-1].lower().strip()
        if file_extension == "csv":
            if self.is_nead_source(kwargs["inputfile"]):
                if kwargs["loggeronly"]:
                    print(
                        "ERROR: --loggeronly parameter not valid for NEAD import (only csv)"
                    )
                    return
                return NeadImporter().import_nead(
                    input_source,
                    kwargs["inputfile"],
                    kwargs["config"],
                    model_class,
                    force=kwargs["force"],
                )
            elif kwargs["loggeronly"]:
                if kwargs.get("directory"):
                    output_file = Path(
                        kwargs["directory"]
                        + "/"
                        + kwargs["station"]
                        + "_logger_{}.csv".format(
                            datetime.now().strftime("%Y%m%d_%H%M%S%f")
                        )
                    )
                    print(f"OUTPUT FILE: {output_file}")
                    return CsvImporter().logger_csv(
                        input_source, kwargs["inputfile"], output_file, kwargs["config"]
                    )
                else:
                    print(
                        "ERROR: --loggeronly parameter requires to specify the --directory parameter for output"
                    )
            else:
                return CsvImporter().import_csv(
                    input_source,
                    kwargs["inputfile"],
                    kwargs["config"],
                    model_class,
                    force=kwargs["force"],
                )
        elif file_extension == "dat":
            if kwargs["loggeronly"]:
                print(
                    "ERROR: --loggeronly parameter not valid for dat import (only csv)"
                )
                return
            return DatImporter().import_dat(
                input_source,
                kwargs["inputfile"],
                kwargs["config"],
                model_class,
                force=kwargs["force"],
            )
        else:
            print(
                f"WARNING (import_data.py) no available converter for extension {file_extension}"
            )
            return

    # Check if data source is from a directory or a url and assign input_file to selected option
    def _get_input_source(self, inputfile, verbose=True):
        if self.is_url(inputfile):
            # Write content from url into csv file
            url = str(inputfile)
            if verbose:
                print(f"URL: {url}")
            req = requests.get(url, stream=True)
            if req.encoding is None:
                req.encoding = "utf-8"
            return req.iter_lines(decode_unicode=True)

        else:
            try:
                input_file = Path(inputfile)
                if verbose:
                    print(f"INPUT FILE: {input_file}")
                source = open(input_file)
                return source
            except FileNotFoundError as e:
                raise FileNotFoundError(
                    f"WARNING (csv_import.py) file not found {input_file}, exception {e}"
                )

    def is_nead_source(self, inputfile):
        source = self._get_input_source(inputfile, verbose=False)
        for first_line in source:
            return first_line.startswith("#") and (first_line.upper().find("NEAD") >= 0)

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
        if v.lower() in ("yes", "true", "t", "y", "1"):
            return True
        elif v.lower() in ("no", "false", "f", "n", "0"):
            return False
        else:
            raise argparse.ArgumentTypeError("Boolean value expected.")
