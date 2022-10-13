# Legacy fortran processor used prior to March 2022

import logging
import subprocess
import urllib.request
import warnings
# import requests
from pathlib import Path

import numpy as np

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class FortranProcessor:
    def __init__(
        self,
        station_type: str,
        output_file_name: str,
        data_url: str,
        raw_path: str,
        command: str,
        dat_path: str,
        start_year: str,
    ):
        self.station_type = station_type
        self.output_file_name = output_file_name

        self.data_url = data_url
        self.raw_path = raw_path
        self.command = command

        self.dat_path = dat_path

        self.start_year = start_year

    def process(self, dat_file_path=None):
        if dat_file_path:
            logger.info(
                f"Skipping raw file processing, reading dat file from {dat_file_path}"
            )
        else:
            # TODO fix SSL certification issue, verify=False should not remain
            # # Download ARGOS data and write 'LATEST_<station_type>.raw' to raw_path directory
            # r = requests.get(self.data_url, allow_redirects=True, verify=False)
            # open(self.raw_path, 'wb').write(r.content)
            # Download RAW data and write 'LATEST_<station_type>.raw' to raw_path directory

            with urllib.request.urlopen(self.data_url) as response:
                data = response.read()
            open(self.raw_path, "wb").write(data)

            logger.info(f"Wrote {self.station_type} raw file")

            try:
                # Write <station>_decoded.dat file using Fortran code to dat_path directory
                process_result = subprocess.run(
                    self.command,
                    cwd=Path(self.dat_path),
                    shell=True,
                    check=True,
                    stdout=subprocess.PIPE,
                    text=True,
                )

                logger.debug(f"Processing Raw file stdout = {process_result.stdout}")
                logger.info(f"Wrote {self.station_type} .dat file")
            except:
                # TODO refine exceptions and print them properly
                logger.error(f"Could NOT run {self.station_type} executable")
                return None

            dat_file_path = self.dat_path + self.output_file_name

        # Try to open and return new .dat file
        try:
            dat_file = open(dat_file_path)
            # TEST
            # dat_file = open('gcnet/management/commands/importers/processor/exec/goes_decoded.dat', "r")
            with warnings.catch_warnings():
                warnings.simplefilter(
                    "ignore"
                )  # ignores warnings about lines with incorrect columns
                # (some columns are corrupt and missing values)
                data_array = np.genfromtxt(
                    dat_file,
                    missing_values=(
                        "*******",
                        "******",
                        "*****",
                        "****",
                        "***",
                        "**",
                        "*",
                    ),
                    filling_values=999,
                    invalid_raise=False,
                )
            gmat = np.array(data_array)

            try:
                if self.start_year and int(self.start_year) > 0:
                    return self._filter_by_year(gmat)
            except Exception as e:
                logger.error(
                    f"ERROR: wrong defined start year, skipping filtering, exception: {e}"
                )

            return gmat

        # TODO refine exceptions and print them properly
        except Exception as e:
            logger.error(
                "Could not load {0} input file {1}, exception {3}".format(
                    self.station_type, dat_file_path, e
                )
            )
            return None

    def _filter_by_year(self, np_array):
        return np_array


class ArgosFortranProcessor(FortranProcessor):
    """process ARGOS data"""

    def __init__(
        self, data_url: str, raw_path: str, command: str, dat_path: str, start_year: str
    ):
        FortranProcessor.__init__(
            self,
            station_type="ARGOS",
            output_file_name="argos_decoded.dat",
            data_url=data_url,
            raw_path=raw_path,
            command=command,
            dat_path=dat_path,
            start_year=start_year,
        )

    def _filter_by_year(self, np_array):
        logger.info(f"Filtering outputs from year {self.start_year}")
        np_array_filtered = np_array[np.where(np_array[:, 0] >= float(self.start_year))]
        logger.info(
            "Removed {} records older than year {} (originally {})".format(
                len(np_array) - len(np_array_filtered), self.start_year, len(np_array)
            )
        )
        return np_array_filtered


class GoesFortranProcessor(FortranProcessor):
    """process GOES data"""

    def __init__(
        self, data_url: str, raw_path: str, command: str, dat_path: str, start_year: str
    ):
        FortranProcessor.__init__(
            self,
            station_type="GOES",
            output_file_name="goes_decoded.dat",
            data_url=data_url,
            raw_path=raw_path,
            command=command,
            dat_path=dat_path,
            start_year=start_year,
        )

    def _filter_by_year(self, np_array):
        logger.info(f"Filtering outputs from year {self.start_year}")
        np_array_filtered = np_array[np.where(np_array[:, 2] >= float(self.start_year))]
        logger.info(
            "Removed {} records older than year {} (originally {})".format(
                len(np_array) - len(np_array_filtered), self.start_year, len(np_array)
            )
        )
        return np_array_filtered


class FortranProcessorFactory:
    @staticmethod
    def get_processor(
        station_type,
        data_url: str,
        raw_path: str,
        command: str,
        dat_path: str,
        start_year: str,
    ):
        if station_type == "argos":
            return ArgosFortranProcessor(
                data_url=data_url,
                raw_path=raw_path,
                command=command,
                dat_path=dat_path,
                start_year=start_year,
            )
        elif station_type == "goes":
            return GoesFortranProcessor(
                data_url=data_url,
                raw_path=raw_path,
                command=command,
                dat_path=dat_path,
                start_year=start_year,
            )
        else:
            logger.error(f"No processor for station type '{station_type}'")
            return None
