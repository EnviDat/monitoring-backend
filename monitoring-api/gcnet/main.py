"""
Purpose: Read, decode, and clean ARGOS and GOES satellite raw data. Also imports data
into Postgres database.
Output: Writes csv and json files with the decoded data.

Contributing Authors : Rebecca Buchholz, V.Trotsiuk and Lucia de Espona,
Orgnization: Swiss Federal Research Institute WSL
Date Last Modified: October 13, 2022

Example commands to run main() (make sure virtual environment is activated):
  python
  from gcnet.main import main

Then call main and pass arguments as needed.

No arguments:
  main()

repeatInterval:
  main(['-r 10'])

repeatInterval and localInput:
  main(['-r 10', '-l True'])
"""


import argparse
import configparser
import logging
import multiprocessing
import subprocess
import time
from datetime import datetime
from pathlib import Path
from urllib import request

from gcnet.management.commands.importers.processor.cleaner import \
    CleanerFactory
from gcnet.management.commands.importers.processor.process_argos import (
    decode_argos, read_argos)
from gcnet.management.commands.importers.processor.process_goes import \
    decode_goes
from gcnet.util.writer import Writer

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def get_parser():
    parser = argparse.ArgumentParser("GCNetProcessing")
    parser.add_argument(
        "--repeatInterval", "-r", help="Run continuously every <interval> minutes"
    )
    parser.add_argument(
        "--localInput",
        "-l",
        help="Any string used in this argument will load local input files "
        "designated in config and skip downloading files from web",
    )
    return parser


def read_config(config_path: str):

    config_file = Path(config_path)
    config = configparser.ConfigParser()
    config.read(config_file)
    logger.info(f" Read configuration file: {config_path}")

    if len(config.sections()) < 1:
        logger.error(" Invalid config file, missing sections")
        raise ValueError("Invalid config file, missing sections")

    return config


def get_writer_config_dict(config_parser: configparser):
    config_dict = dict(config_parser.items("file"))
    config_dict["columns"] = dict(config_parser.items("columns"))
    return config_dict


def get_input_data(config_dict: dict, local_input):

    # If command line localInput argument passed (with any string) assign data_file to
    # 'data_local' from config
    if local_input:
        data_file = config_dict["data_local"]
        logger.info(f" Skipping downloading input data, using local file: {data_file}")

    # Else assign data_file to file downloaded from data_url
    else:
        data_url = config_dict["data_url"]
        data_file = config_dict["data_url_file"]

        # Download data from URL
        logger.debug(f"Attempting to download URL: {data_url}")
        with request.urlopen(data_url) as data:
            content = data.read()

        # Save data to data_file
        with open(data_file, "wb") as download_file:
            download_file.write(content)

        logger.info(f" Downloaded input data from URL and wrote file: {data_file}")

    return data_file


def get_csv_import_command_list(config_parser: configparser, station_type: str):

    # Load stations configuration file and assign it to stations_config
    stations_config = config_parser

    # Assign variable to contain command list
    commands = []

    # Assign variables to stations_config values and loop through each station in
    # stations_config, create list of command strings to run csv imports
    # for each station
    for section in stations_config.sections():

        # Check config key 'active' if data for station should be processed
        # A value of 'True' means that station data will be processed
        # Any other value means that station data will not be processed
        if (
            stations_config.get(section, "active") == "True"
            and stations_config.get(section, "type") == station_type
        ):

            csv_input = stations_config.get(section, "csv_input")
            model = stations_config.get(section, "model")
            csv_data = stations_config.get(section, "csv_data_dir")
            source = stations_config.get(section, "source")

            # Management command 'import_csv' will be used to import processed
            # station data stored locally or served at a URL
            # into corresponding database model
            command_string = ""
            if source == "local":
                command_string = (
                    f"python manage.py import_csv -s {source} "
                    f"-i {csv_data}/{csv_input} -a gcnet -m {model}"
                )
            elif source == "url":
                source_url = stations_config.get(section, "source_url")
                command_string = (
                    f"python manage.py import_csv -s {source} "
                    f"-i {source_url}/{csv_input} -a gcnet -m {model}"
                )

            if len(command_string) > 0:
                commands.append(command_string)

    return commands


def execute_commands(commands_list):
    # Iterate through commands_list and execute each command
    for station_command in commands_list:
        try:
            subprocess.run(
                station_command,
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                text=True,
            )
        except subprocess.CalledProcessError:
            logger.error(f"Could not run command: {station_command}")
            continue


def process_data(station_type: str, config_dict: dict, local_input=None):

    # Get input data
    data = get_input_data(config_dict, local_input)

    # Get writer configured for the cleaner output
    writer = Writer.new_from_dict(config_dict["writer"])

    # Decode ARGOS data
    if station_type == "argos":
        data_raw = read_argos(data, nrows=None)
        data_decode = decode_argos(data_raw, remove_duplicate=True, sort=True)

    # Decode GOES data
    elif station_type == "goes":
        data_decode = decode_goes(data)

    else:
        logger.error(f" Invalid station type: {station_type}")
        raise ValueError(f"Invalid station type: {station_type}")

    # Convert decoded data pandas dataframe to Numpy array
    data_array = data_decode.to_numpy()

    # Clean data and write csv and json files
    stations_config_path = "gcnet/config/stations.ini"
    cleaner = CleanerFactory.get_cleaner(station_type, stations_config_path, writer)

    if not cleaner:
        logger.error(f"No cleaner exists for station type: {station_type}")
        raise ValueError(f"No cleaner exists for station type: {station_type}")

    # Clean Numpy array data by applying basic filters
    # Cleaner also writes csv and json files
    cleaner.clean(data_array)

    return


def main(args=None):
    """
    Main entry point for processing ARGOS and GOES satellite transmissions.
    """

    # Access arguments passed in command line
    parser = get_parser()
    args = parser.parse_args(args)

    # Read config file
    metadata_path = "gcnet/config/gcnet_metadata.ini"
    config = read_config(metadata_path)

    if not config:
        logger.error(f"Not valid config file: {metadata_path}")
        return -1

    # Process and clean input data, write csv and json files, import csv files data
    # into Postgres database
    repeat = True
    while repeat:

        # Do not repeat if the -r argument is not present
        repeat = args.repeatInterval is not None

        start_time = time.time()

        logger.info(
            " **************************** START DATA PROCESSING ITERATION"
            " (start time: {}) "
            "**************************** ".format(
                datetime.fromtimestamp(start_time).strftime("%Y-%m-%d %H:%M:%S")
            )
        )

        # Assign empty processes list
        processes = []

        # Start process
        for station_type in ["argos", "goes"]:

            # Get config_dict configured for station_type
            config_dict = dict(config.items(station_type))
            config_dict["writer"] = get_writer_config_dict(config)

            local_input = None
            # Assign local_input if commandline option localInput is passed
            if args.localInput:
                local_input = args.localInput

            # Process data from each station_type concurrently using multiprocessing
            process = multiprocessing.Process(
                target=process_data, args=(station_type, config_dict, local_input)
            )
            processes.append(process)
            process.start()

        for process in processes:
            process.join()

        # Write short-term csv files
        station_array = list((config.get("file", "stations")).split(","))
        csv_short_days = int(config.get("file", "short_term_days"))
        csv_writer_config = get_writer_config_dict(config)
        csv_writer = Writer.new_from_dict(csv_writer_config)
        csv_writer.write_csv_short_term(station_array, csv_short_days)

        # Read the stations config file
        stations_path = "gcnet/config/stations.ini"
        stations_config = read_config(stations_path)

        # Check if stations_config exists
        if not stations_config:
            logger.error(f"Non-valid config file: {stations_path}")
            return -1

        # Import csv files into Postgres database so that data are available for API
        logger.info(
            " **************************** START DATA IMPORT ITERATION ****************"
            "************ "
        )

        # Assign empty import_processes list
        import_processes = []

        # Get the import commands
        goes_commands = get_csv_import_command_list(stations_config, "goes")
        argos_commands = get_csv_import_command_list(stations_config, "argos")

        # Create list with both ARGOS and GOES commands
        import_commands = [goes_commands, argos_commands]

        # Process ARGOS and GOES import commands in parallel
        for command_list in import_commands:
            process = multiprocessing.Process(
                target=execute_commands, args=(command_list,)
            )
            import_processes.append(process)
            process.start()

        for process in import_processes:
            process.join()

        exec_time = int(time.time() - start_time)
        logger.info(
            f" FINISHED data processing and data import iteration, "
            f"that took {exec_time} seconds"
        )

        if repeat:
            interval = int(args.repeatInterval) * 60
            if interval > exec_time:
                wait_time = interval - exec_time
                logger.info(f" SLEEPING {wait_time} seconds before next iteration...\n")
                time.sleep(wait_time)

    return 0


if __name__ == "__main__":
    main()
