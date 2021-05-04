# Example command:
#   python manage.py new_model -c lwf/config/test.ini


from pathlib import Path
from django.core.management.base import BaseCommand

__version__ = '0.0.1'
__author__ = u'Rebecca Buchholz'

from generic.util.commands_helpers import has_spaces
from generic.util.nead import read_config
from lwf.util.new_model_helpers import execute_commands, model_exists

# Setup logging
import logging

logging.basicConfig(filename=Path('generic/logs/new_model.log'), format='%(asctime)s  %(filename)s: %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Command(BaseCommand):

    # def get_config_versions(self):
    #     return ['0.0.1']

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
        parent_class = conf.get('configuration', 'parent_class')
        name = conf.get('configuration', 'name')

        # Check if 'database_table_name' in config file is in valid format (lowercase and no spaces)
        database_table_name = conf.get('configuration', 'database_table_name')
        if has_spaces(database_table_name):
            logger.error(f'ERROR database_table_name in config must have no spaces: {database_table_name}')
            return
        if not database_table_name.islower():
            logger.error(f'ERROR database_table_name in config must be in lowercase: {database_table_name}')
            return

        # Create models file path string
        model_path = self.get_model_path(parent_class)

        # Set table_exists to False
        table_exists = False

        # Check if model ('database_table_name' in config) already exists in corresponding models file
        try:
            # First check if model is written in corresponding models file:
            with open(model_path, 'r') as f:
                if database_table_name in f.read():
                    table_exists = True
                    logger.error(f'ERROR table {database_table_name} already written in {model_path}')
                    return
        except FileNotFoundError as e:
            logger.error(f'ERROR file not found {model_path}, exception {e}')

        print(table_exists)

        # # Check if table already exists in database
        # long_db_name = 'lwf_{0}'.format(database_table_name)
        #
        # if model_exists(database_table_name):
        #     table_exists = True
        #     print('WARNING (lwf_new_model.py): Table {0} already exists in database'.format(long_db_name))
        #
        # # If child class does not exist in corresponding models file or database
        # # write it to corresponding models file and run migrations to add it to database
        # if not table_exists:
        #
        #     comment = '\n# {0}'.format(name)
        #     class_string = '\nclass {0}({1}):'.format(database_table_name, model)
        #
        #     try:
        #         # Write new class to corresponding models file
        #         with open(model_path, 'a') as sink:
        #             sink.write('\n')
        #             sink.write(comment)
        #             sink.write(class_string)
        #             sink.write("\n    pass")
        #             sink.write("\n")
        #
        #         # Update '__init__.py' with new model
        #         with open('lwf/models/__init__.py', 'a') as controller:
        #             controller.write('\nfrom .{0} import {1}\n'.format(model, database_table_name))
        #
        #         # Assign migrations_commands to contain migrations strings
        #         migrations_commands = ['python manage.py makemigrations lwf', 'python manage.py migrate lwf --database=lwf']
        #
        #         # Call execute_commands to execute migrations commands
        #         execute_commands(migrations_commands)
        #
        #         return 0
        #
        #     except Exception as e:

    # Check which kind of model_path should be used
    @staticmethod
    def get_model_path(parent_class):

        if parent_class in ['LWFMeteo', 'LWFStation']:
            return f'lwf/models/{parent_class}.py'

        elif parent_class in ['Station']:
            return f'gcnet/models.py'

        else:
            logger.error(f'ERROR {parent_class} parent class does not exist or does not have model_path specified')
            return
