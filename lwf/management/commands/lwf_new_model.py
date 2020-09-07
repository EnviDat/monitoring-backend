# Example command
#   python manage.py lwf_new_model -c lwf/config/test_conf.ini

from django.core.management.base import BaseCommand

__version__ = '0.0.1'
__author__ = u'Rebecca Kurup Buchholz'

from lwf.helpers import read_config, db_table_exists, execute_commands


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
        # TODO make lower case, replace space with _ (report error)
        database_table_name = conf.get('configuration', 'database_table_name').lower()

        # Create models file path string
        model_path = 'lwf/models/{0}.py'.format(model)

        # Set table_exists to False
        table_exists = False

        # Check if child class ('database_table_name' in config) already exists in corresponding models file
        try:
            # First check if model is written in corresponding models file:
            with open(model_path, 'r') as f:
                if database_table_name in f.read():
                    table_exists = True
                    print('WARNING (lwf_new_model.py): Table {0} already written in {1}'.format(database_table_name,
                                                                                            model_path))
                    return
        except FileNotFoundError as e:
            print('WARNING (lwf_new_model.py): File not found {0}, exception {1}'.format(model_path, e))

        # Check if table already exists in database
        long_db_name = 'lwf_{0}'.format(database_table_name)

        if db_table_exists(database_table_name):
            table_exists = True
            print('WARNING (lwf_new_model.py): Table {0} already exists in monitoring database'.format(long_db_name))

        # If child class does not exist in corresponding models file or database
        # write it to corresponding models file and run migrations to add it to database
        if not table_exists:

            comment = '\n# {0}'.format(name)
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
                with open('lwf/models/__init__.py', 'a') as controller:
                    controller.write('\nfrom .{0} import {1}\n'.format(model, database_table_name))

                # Assign migrations_commands to contain migrations strings
                migrations_commands = ['python manage.py makemigrations lwf', 'python manage.py migrate --database=lwf']

                # Call execute_commands to execute migrations commands
                execute_commands(migrations_commands)

                return 0

            except Exception as e:
                print('WARNING (lwf_new_model.py) exception: {0}'.format(e))
