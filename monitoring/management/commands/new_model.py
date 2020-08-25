# Example command
#   python manage.py new_model -c config/test_conf.ini

from django.core.management.base import BaseCommand
import importlib
import subprocess

__version__ = '0.0.1'
__author__ = u'Rebecca Kurup Buchholz'

from monitoring.helpers import read_config


class Command(BaseCommand):

    def add_arguments(self, parser):

        parser.add_argument(
            '-c',
            '--config',
            required=True,
            help='Path to config file'
        )

    def handle(self, *args, **kwargs):

        # Read configuration file and assign variables for configuration values
        conf = read_config(kwargs['config'])
        model = conf.get('configuration', 'model')
        name = conf.get('configuration', 'name')
        database_table_name = conf.get('configuration', 'database_table_name')

        # Create models file path string
        model_path = 'monitoring/models/{0}.py'.format(model)

        # Check if child class already exists for child class ('database_table_name' in config)
        try:
            # First check if model is written in corresponding models file:
            with open(model_path, 'r') as f:
                if database_table_name in f.read():
                    print('WARNING (new_model.py): Table {0} already written in {1}'.format(database_table_name,
                                                                                            model_path))
                    return

            # Get the database table class
            package = importlib.import_module('monitoring.models.{0}'.format(model))
            child_class = getattr(package, database_table_name)
            print(child_class)
            # Check if model exists in database (with at least one record)
            child_class.objects.get(id=1)
            print('WARNING (new_model.py): Table {0} already exists in database'.format(database_table_name))
            return

        # If child class does not exist in database write it to corresponding models file and run migrations to add it
        # to database
        except:

            # Create comment string
            comment = '\n# {0}'.format(name)

            # Create class_string
            class_string = '\nclass {0}({1}):'.format(database_table_name, model)

            try:
                # Write new class to corresponding models file
                with open(model_path, 'a') as sink:
                    sink.write('\n')
                    sink.write(comment)
                    sink.write(class_string)
                    sink.write("\n    pass")
                    sink.write("\n")

                # Update '__init__.py' with new model
                with open('monitoring/models/__init__.py', 'a') as controller:
                    controller.write('\nfrom .{0} import {1}\n'.format(model, database_table_name))

                # Create migrations strings
                makemigrations = 'python manage.py makemigrations monitoring'
                migrations = 'python manage.py migrate'

                # Assign migrations_commands to contain migrations strings
                migrations_commands = []
                migrations_commands.append(makemigrations)
                migrations_commands.append(migrations)

                # Iterate through migrations_list and execute each command
                for command in migrations_commands:
                    try:
                        process = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE,
                                                 universal_newlines=True)
                        # NOTE: the line line below must be included otherwise the import commands do not work!!!
                        print('RUNNING: {0}   STDOUT: {1}'.format(command, process.stdout))
                    except subprocess.CalledProcessError:
                        print('COULD NOT RUN: {0}'.format(command))
                        print('')
                        continue

            except Exception as e:
                print('WARNING (new_model.py) exception: {0}'.format(e))
