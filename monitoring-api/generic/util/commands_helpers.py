import subprocess

from django.apps import apps

# ----------------------------------------  New Model Helpers ---------------------------------------------------------

# Returns True if string has spaces
def has_spaces(string):
    if " " in string:
        return True
    else:
        return False


# Returns True if model exists in database
def model_exists(table_name, app):

    models = apps.all_models[app]
    model_names = list(models.keys())

    if table_name in model_names:
        return True
    else:
        return False


# Execute commands list, returns True if all commands executed, else returns False if at least one command fails
def execute_commands(commands_list):
    commands_executed = True
    for command in commands_list:
        try:
            process = subprocess.run(
                command, shell=True, check=True, stdout=subprocess.PIPE, text=True
            )
            print(f"RUNNING: {command}")
            print(f"STDOUT: {process.stdout}")
        except Exception as e:
            print(f"COULD NOT RUN: {command}")
            print(f"EXCEPTION: {e}")
            print("")
            commands_executed = False
            continue
    return commands_executed
