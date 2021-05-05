from django.apps import apps
import subprocess


# ----------------------------------------  New Model Helpers ---------------------------------------------------------

# Returns True if string has spaces
def has_spaces(string):
    if ' ' in string:
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


# Execute commands list
def execute_commands(commands_list):
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
