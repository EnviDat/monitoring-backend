import os
import subprocess
from pathlib import Path
import configparser

from django.db import connection

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "monitoring.settings")

import django
django.setup()

from monitoring.models.LWFMeteoTest import LWFMeteoTest


def read_config(config_path: str):

    config_file = Path(config_path)

    # Load configuration file
    config = configparser.ConfigParser()
    config.read(config_file)

    print("Read config params file: {0}, sections: {1}".format(config_path, ', '.join(config.sections())))

    if len(config.sections()) < 1:
        print("Invalid config file, has 0 sections")
        return None

    return config


def db_table_exists(table_name):
    return table_name in [t.lower() for t in connection.introspection.table_names()]


def execute_commands(commands_list):
    # Iterate through migrations_list and execute each command
    for command in commands_list:
        try:
            process = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE,
                                     universal_newlines=True)
            print('RUNNING: {0}'.format(command))
            print('STDOUT: {0}'.format(process.stdout))
        except subprocess.CalledProcessError:
            print('COULD NOT RUN: {0}'.format(command))
            print('')
            continue


def retrieve_attribute():
    a = LWFMeteoTest.test_attribute
    return a

print(retrieve_attribute())