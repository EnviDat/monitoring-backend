# Legacy main.py used prior to March 2022

# EXAMPLE COMMANDS TO RUN main.py
#    Import data from URL:         main.main(['-r 15', '-i url']) or main(['-r 15', '-i url'])
#    Import data from directory:   main.main(['-r 15', '-i path'])

import argparse
import configparser
import logging
import multiprocessing as mp
import subprocess
import time
from datetime import datetime
from pathlib import Path

# from gcnet.management.commands.importers.processor.fortranprocessor import FortranProcessorFactory
from gcnet.legacy.cleaner_legacy import CleanerFactory
from gcnet.legacy.fortranprocessor import FortranProcessorFactory
# from gcnet.management.commands.importers.processor.cleaner import CleanerFactory
from gcnet.util.writer import Writer

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

__version__ = "0.0.1"
__author__ = "Lucia de Espona, Rebecca Kurup Buchholz, Matthias Haeni, Ionut Iosifescu, Derek Houtz, WSL"


def get_parser():
    """
    Creates a new argument parser.
    """
    parser = argparse.ArgumentParser("GCNetDataProcessing")
    version = "%(prog)s " + __version__
    parser.add_argument("--version", "-v", action="version", version=version)
    parser.add_argument(
        "--localFolder",
        "-l",
        help="Load local .dat files from folder and skip processing",
    )
    parser.add_argument(
        "--repeatInterval", "-r", help="Run continuously every <interval> minutes"
    )
    parser.add_argument(
        "--inputType",
        "-i",
        required=True,
        help="Input data source read from stations config. "
        '"path" = directory path (csv_data_dir)'
        '"url" = url address hosting files (csv_data_url)',
    )
    return parser


def read_config(config_path: str):
    config_file = Path(config_path)

    # Load gcnet configuration file
    gc_config = configparser.ConfigParser()
    gc_config.read(config_file)

    logger.info(
        "Read config params file: {}, sections: {}".format(
            config_path, ", ".join(gc_config.sections())
        )
    )

    if len(gc_config.sections()) < 1:
        logger.error("Invalid config file, missing sections")
        return None

    return gc_config


def get_writer_config_dict(config_parser: configparser):
    config_dict = dict(config_parser.items("file"))
    config_dict["columns"] = dict(config_parser.items("columns"))
    return config_dict


# Function to retrieve and process data
def execute_process(station_type: str, config_dict: dict, local_dat_file: str):
    raw_file = config_dict["raw_file"]
    data_url = config_dict["data_url"]
    start_year = config_dict["start_year"]
    process_command = config_dict["process_command"]

    # get writer configured for the cleaner output
    writer = Writer.new_from_dict(config_dict["writer"])

    # Assign input to data returned from raw_to_dat call
    processor = FortranProcessorFactory.get_processor(
        station_type=station_type,
        data_url=data_url,
        raw_path=raw_file,
        command=process_command,
        # dat_path="gcnet/management/commands/importers/processor/exec/",
        dat_path="gcnet/legacy/exec/",
        start_year=start_year,
    )
    if not processor:
        logger.error(f"No processor for station type '{station_type}'")
        return -1

    # process the data
    output_data = processor.process(local_dat_file)
    if output_data is None:
        logger.error(f"Failed processing for station type '{station_type}' (NO DATA)")
        return -1

    # Call cleaner to process ARGOS input data and write json and csv output files
    stations_config_path = "gcnet/config/stations.ini"
    cleaner = CleanerFactory.get_cleaner(station_type, stations_config_path, writer)
    if not cleaner:
        logger.error(f"No cleaner for station type '{station_type}'")
        return -1

    cleaner.clean(output_data)

    return 0


def get_csv_import_command_list(
    config_parser: configparser, station_type: str, input_type: str
):
    # Load stations configuration file and assign it to stations_config
    stations_config = config_parser

    # Assign variable to contain command list
    commands = []

    # Assign variables to stations_config values and loop through each station in stations_config, create list of
    # command strings to run csv imports for each station
    for section in stations_config.sections():

        # Check config if station data should be processed (active=True') for station
        # and if 'type' is current station_type being processed (either ARGOS or GOES)
        if (
            stations_config.get(section, "active") == "True"
            and stations_config.get(section, "type") == station_type
        ):

            csv_temporary = stations_config.get(section, "csv_temporary")
            csv_input = stations_config.get(section, "csv_input")
            model = stations_config.get(section, "model")

            # Check to read either url or stations config file
            if input_type == " file":
                csv_data = stations_config.get(section, "csv_data_dir")
            elif input_type == " url":
                csv_data = stations_config.get(section, "csv_data_url")
            else:
                print(
                    'WARNING (import_data.py) invalid argument "{}" entered for input_type. Must enter'
                    '"file" or "url"'.format(input_type)
                )
                return

            command_string = (
                "python manage.py import_data -s {} -c gcnet/config/stations.ini "
                "-i {}/{} -m {} -f True".format(
                    csv_temporary, csv_data, csv_input, model
                )
            )
            commands.append(command_string)

    return commands


def execute_commands(commands_list):
    # Iterate through commands_list and execute each command
    for station_command in commands_list:
        try:
            process_result = subprocess.run(
                station_command,
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                text=True,
            )
            # NOTE: the line line below must be included otherwise the import commands do not work!!!
            print(f"RUNNING: {station_command}   STDOUT: {process_result.stdout}")
        except subprocess.CalledProcessError:
            print(f"COULD NOT RUN: {station_command}")
            print("")
            continue


def main(args=None):
    """
    Main entry point.
    """

    parser = get_parser()
    args = parser.parse_args(args)

    # read the config file
    gc_metadata_path = "gcnet/config/gcnet_metadata.ini"
    gc_config = read_config(gc_metadata_path)

    if not gc_config:
        logger.error(f"Not valid config file: {gc_metadata_path}")
        return -1

    # Process and clean input data, write csv and json files, import csv files data into Postgres database
    repeat = True
    while repeat:

        # Do not repeat if the -r argument is not present
        repeat = args.repeatInterval is not None

        start_time = time.time()

        logger.info(
            "\n **************************** START DATA PROCESSING ITERATION (start time: {}) "
            "**************************** ".format(
                datetime.fromtimestamp(start_time).strftime("%Y-%m-%d %H:%M:%S")
            )
        )

        # Assign empty processes list
        processes = []

        # Start process
        for station_type in ["argos", "goes"]:
            # Assign and start process
            config_dict = dict(gc_config.items(station_type))
            config_dict["writer"] = get_writer_config_dict(gc_config)
            config_dict["start_year"] = gc_config.get("file", "start_year")

            # Add local if commandline option selected
            local_dat = None
            if args.localFolder:
                local_dat = f"{station_type}_decoded.dat"
                # local_dat = "{0}/{1}_decoded.dat".format(args.localFolder, station_type)
                # local_dat.strip()

            # Execute processing
            process = mp.Process(
                target=execute_process, args=(station_type, config_dict, local_dat)
            )
            processes.append(process)
            process.start()

        for process in processes:
            process.join()

        # Write short-term csv files
        station_array = list((gc_config.get("file", "stations")).split(","))
        csv_short_days = int(gc_config.get("file", "short_term_days"))
        csv_writer_config = get_writer_config_dict(gc_config)
        csv_writer = Writer.new_from_dict(csv_writer_config)
        csv_writer.write_csv_short_term(station_array, csv_short_days)

        # Read the stations config file
        stations_path = "gcnet/config/stations.ini"
        stations_config = read_config(stations_path)

        # Check if stations_config exists
        if not stations_config:
            print(f"WARNING non-valid config file: {stations_path}")
            return -1

        # Import csv files into Postgres database so that data are available for API
        print(
            "\n **************************** START DATA IMPORT ITERATION **************************** "
        )

        # Assign empty import_processes list
        import_processes = []

        # Get input type
        input_type = args.inputType

        # Get the import commands
        goes_commands = get_csv_import_command_list(stations_config, "goes", input_type)
        argos_commands = get_csv_import_command_list(
            stations_config, "argos", input_type
        )

        # Create list with both ARGOS and GOES commands
        import_commands = [goes_commands, argos_commands]

        # Process ARGOS and GOES import commands in parallel
        for command_list in import_commands:
            process = mp.Process(target=execute_commands, args=(command_list,))
            import_processes.append(process)
            process.start()

        for process in import_processes:
            process.join()

        exec_time = int(time.time() - start_time)
        logger.info(
            f"FINISHED DATA PROCESSING AND DATA IMPORT ITERATION. That took {exec_time} seconds"
        )

        if repeat:
            interval = int(args.repeatInterval) * 60
            if interval > exec_time:
                wait_time = interval - exec_time
                logger.info(f"SLEEPING {wait_time} seconds before next iteration...")
                time.sleep(wait_time)

    return 0


if __name__ == "__main__":
    main()
