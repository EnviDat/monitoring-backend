"""
EXAMPLE COMMANDS to run main.py

   Open terminal at project directory.
   Make sure virtual environment is activated.

   Import data from URL:

      python
      from lwf import main
      main.main(['-r 10'])

Author: Rebecca Kurup Buchholz, Swiss Federal Research Institute WSL
Date last modified: January, 6, 2022
"""

import argparse
import configparser
import logging
import os
import subprocess
import sys
import time
from pathlib import Path

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", default="DEBUG"),
    format=(
        "%(asctime)s.%(msecs)03d [%(levelname)s] "
        "%(name)s | %(funcName)s:%(lineno)d | %(message)s"
    ),
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stdout,
)
log = logging.getLogger(__name__)


# ============================================ MAIN SUPPORTING FUNCTIONS===============================================


def get_parser():
    """
    Creates a new argument parser.
    """
    parser = argparse.ArgumentParser("LWFStationImport")
    parser.add_argument(
        "--repeatInterval", "-r", help="Run continuously every <interval> minutes"
    )

    return parser


def get_csv_import_command_list(config):

    # Initialize commands variale that will be used to contain command list
    commands = []

    # Assign base_url to url used to host LWF station files
    base_url = config.get("DEFAULT", "base_url")

    # Assign size_limit to maximum size (in mb) of files that can be downloaded
    size_limit = config.get("DEFAULT", "download_limit_mb")

    # Loop through each station in config
    for section in config.sections():

        # Check config if station data should be imported (api = True)
        if config.get(section, "api") == "True":

            # Assign variables to config values
            station_url = config.get(section, "station_url")
            model = config.get(section, "model")

            # Assign command_string to command to run csv import for station
            command_string = (
                f"python manage.py lwf_main_import "
                f"-i {base_url}{station_url} -t web -d lwf/data -a lwf -m {model} -s {size_limit}"
            )

            # Append command_string to commands list
            commands.append(command_string)

    return commands


def execute_commands(commands_list):
    # Iterate through commands_list and execute each command
    for command in commands_list:
        try:
            log.info(f" Running: {command}")
            subprocess.run(
                command, shell=True, check=True, stdout=subprocess.PIPE, text=True
            )
        except subprocess.CalledProcessError:
            log.error(f" ERROR could not run: {command}")
            continue


def read_config(conf_path: str):

    config_file = Path(conf_path)

    # Load configuration file
    config = configparser.ConfigParser()
    config.read(config_file)

    # Uncomment line below to log config read and config sections
    # log.info(' Read config params file: {0}, sections: {1}'.format(conf_path, ', '.join(config.sections())))

    if len(config.sections()) < 1:
        log.error(" ERROR: invalid config file, missing sections")
        return None

    return config


# ============================================ MAIN ===================================================================


def main(args=None):
    """
    Main entry point for importing LWF station data
    """

    parser = get_parser()
    args = parser.parse_args(args)

    # Read the config file
    config_path = "lwf/config/LWFStations.ini"
    config = read_config(config_path)

    if not config:
        log.error(f" ERROR not valid config file: {config_path}")
        return -1

    # Import csv files data into Postgres database
    repeat = True
    while repeat:

        # Do not repeat loop if the -r argument is not present
        repeat = args.repeatInterval is not None

        # Assign start_time for data import iteration
        start_time = time.time()

        print("\n")
        log.info(
            " ************************************************* START DATA IMPORT ITERATION"
            " *************************************************"
        )

        # Get the import commands
        commands = get_csv_import_command_list(config)

        # Execute the commands
        execute_commands(commands)

        # Finish data import iteration
        exec_time = int(time.time() - start_time)
        log.info(f" FINISHED data import iteration, that took {exec_time} seconds")

        # Do not start next iteration until wait_time has lapsed
        if repeat:
            interval = int(args.repeatInterval) * 60
            if interval > exec_time:
                wait_time = interval - exec_time
                log.info(f" SLEEPING {wait_time} seconds before next iteration...")
                time.sleep(wait_time)

    return 0


if __name__ == "__main__":
    main()
