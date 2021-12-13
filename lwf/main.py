# EXAMPLE COMMANDS to run main.py
#
#    Open terminal at project directory.
#    Make sure virtual environment is activated.
#
#    Import data from URL:
#
#       python
#       from lwf.main import main
#       main.main(['-r 10'])


import argparse
from pathlib import Path
import configparser
# import multiprocessing as mp
import time
import subprocess


import logging

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

__version__ = '0.0.1'
__author__ = u'Rebecca Kurup Buchholz'
config_path = "lwf/config/LWFStations.ini"


def get_parser():
    """
    Creates a new argument parser.
    """
    parser = argparse.ArgumentParser("LWFStationImport")
    version = '%(prog)s ' + __version__
    parser.add_argument('--version', '-v', action='version', version=version)
    parser.add_argument('--repeatInterval', '-r', help='Run continuously every <interval> minutes')

    return parser


def get_csv_import_command_list(config):

    # Initialize commands variale that will be used to contain command list
    commands = []

    # Assign base_url to url used to host LWF station files
    base_url = config.get('DEFAULT', 'base_url')

    # Loop through each station in config
    for section in config.sections():

        # Check config if station data should be imported (api = True)
        if config.get(section, 'api') == 'True':

            # Assign variables to config values
            station_url = config.get(section, 'station_url')
            model = config.get(section, 'model')

            # Assign command_string to command to run csv import for station
            command_string = f'python manage.py csv_import ' \
                             f'-i {base_url}{station_url} -t web -d lwf/data -a lwf -m {model} '

            # Append command_string to commands list
            commands.append(command_string)

    return commands


def execute_commands(commands_list):
    # Iterate through commands_list and execute each command
    for command in commands_list:
        try:
            process_result = subprocess.run(command, shell=True, check=True,
                                            stdout=subprocess.PIPE, universal_newlines=True)
            # NOTE: the line line below must be included otherwise the import commands do not work!!!
            print('RUNNING: {0}   STDOUT: {1}'.format(command, process_result.stdout))
        except subprocess.CalledProcessError:
            print('COULD NOT RUN: {0}'.format(command))
            print('')
            continue


def read_config(config_path: str):

    config_file = Path(config_path)

    # Load configuration file
    config = configparser.ConfigParser()
    config.read(config_file)

    logger.info(" Read config params file: {0}, sections: {1}".format(config_path, ', '.join(config.sections())))

    if len(config.sections()) < 1:
        logger.error(" Invalid config file, missing sections")
        return None

    return config


def main(args=None):
    """
    Main entry point for importing LWF station data
    """

    parser = get_parser()
    args = parser.parse_args(args)

    # Read the config file
    # config_path = "lwf/config/LWFStations.ini"
    config = read_config(config_path)

    if not config:
        logger.error(" Not valid config file: {0}".format(config_path))
        return -1

    # Import csv files data into Postgres database
    repeat = True
    while repeat:

        # Do not repeat if the -r argument is not present
        repeat = (args.repeatInterval is not None)

        # Assign start_time for data import iteration
        start_time = time.time()

        print("\n **************************** START DATA IMPORT ITERATION **************************** ")

        # Get the import commands
        commands = get_csv_import_command_list(config)

        # Execute the commands
        execute_commands(commands)

        # TODO potentially implement multiprocessing

        # Assign empty import_processes list
        # import_processes = []

        #     # Create list with both ARGOS and GOES commands
        #     import_commands = [goes_commands, argos_commands]
        #
        #     # Process ARGOS and GOES import commands in parallel
        #     for command_list in import_commands:
        #         process = mp.Process(target=execute_commands, args=(command_list,))
        #         import_processes.append(process)
        #         process.start()
        #
        #     for process in import_processes:
        #         process.join()
        #

        # Finish data import iteration
        exec_time = int(time.time() - start_time)
        logger.info(f' FINISHED DATA IMPORT ITERATION. That took {exec_time} seconds')

        # Do not start next iteration until wait_time as lapsed
        if repeat:
            interval = int(args.repeatInterval) * 60
            if interval > exec_time:
                wait_time = interval - exec_time
                logger.info(f' SLEEPING {wait_time} seconds before next iteration...')
                time.sleep(wait_time)

    return 0


if __name__ == '__main__':
    main()
