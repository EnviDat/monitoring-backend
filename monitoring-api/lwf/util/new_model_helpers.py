import configparser
import subprocess
from pathlib import Path

from django.apps import apps


def read_config(config_path: str):
    config_file = Path(config_path)

    # Load configuration file
    config = configparser.ConfigParser()
    config.read(config_file)

    print(
        "Read config params file: {}, sections: {}".format(
            config_path, ", ".join(config.sections())
        )
    )

    if len(config.sections()) < 1:
        print("Invalid config file, has 0 sections")
        return None

    return config


def execute_commands(commands_list):
    # Iterate through migrations_list and execute each command
    for command in commands_list:
        try:
            process = subprocess.run(
                command, shell=True, check=True, stdout=subprocess.PIPE, text=True
            )
            print(f"RUNNING: {command}")
            print(f"STDOUT: {process.stdout}")
        except subprocess.CalledProcessError:
            print(f"COULD NOT RUN: {command}")
            print("")
            continue


def model_exists(table_name):
    models = [model.__name__ for model in apps.get_models()]
    if table_name in models:
        return True
    else:
        return False


# Returns True if string has spaces
def has_spaces(string):
    if " " in string:
        return True
    else:
        return False
