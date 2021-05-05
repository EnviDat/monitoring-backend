# Example command:
#   python manage.py new_model -c lwf/config/test.ini


from pathlib import Path
from django.core.management.base import BaseCommand

__version__ = '0.0.1'
__author__ = u'Rebecca Buchholz'

from generic.util.commands_helpers import has_spaces, model_exists, execute_commands
from generic.util.nead import read_config

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
        database_table_name = conf.get('configuration', 'database_table_name')

        # Get app of parent_class
        try:
            app = self.get_app(parent_class)
        except Exception as e:
            logger.error(e)
            return

        # Check if 'database_table_name' in config file has no spaces
        if has_spaces(database_table_name):
            logger.error(f'ERROR database_table_name in config must have no spaces: {database_table_name}')
            return

        # Covert 'database_table_name' to lowercase
        database_table_name = database_table_name.lower()

        # Create models file path string
        try:
            model_path = self.get_model_path(parent_class)
        except Exception as e:
            logger.error(e)
            return

        # Check if model ('database_table_name' in config) already exists in corresponding models file
        try:
            # First check if model is written in corresponding models file:
            with open(model_path, 'r') as f:
                if f'class {database_table_name}' in f.read():
                    logger.error(f'ERROR table {database_table_name} already written in {model_path}')
                    return
        except FileNotFoundError as e:
            logger.error(f'ERROR file not found {model_path}, exception {e}')
            return

        # Check if table already exists in database
        if model_exists(database_table_name, app):
            logger.error(f'ERROR database_table_name already exists in database: {database_table_name}')
            return

        # If child class does not exist in corresponding models file or database
        # write it to corresponding models file and run migrations to add it to database
        comment = f'\n# {name}'
        class_string = f'\nclass {database_table_name}({parent_class}):'

        try:
            # Write new class to corresponding models file
            with open(model_path, 'a') as sink:
                sink.write('\n')
                sink.write(comment)
                sink.write(class_string)
                sink.write("\n    pass")
                sink.write("\n")

            # Update '__init__.py' with new model if '__init__.py' exists in a model directory
            models_init_path = Path(f'{app}/models/__init__.py')
            if models_init_path.exists():
                with open(models_init_path, 'a') as controller:
                    controller.write(f'\nfrom .{parent_class} import {database_table_name}\n')

            # Assign migrations_commands to contain migrations strings
            migrations_commands = [f'python manage.py makemigrations {app}',
                                   f'python manage.py migrate {app} --database={app}']

            # Call execute_commands to execute migrations commands
            execute_commands(migrations_commands)

            # Log message
            logger.info(f'FINISHED creating new model {database_table_name} in parent_class {parent_class}')

            return 0

        except Exception as e:
            logger.error(f'ERROR: {e}')

    # Check which kind of model_path should be used
    @staticmethod
    def get_model_path(parent_class):

        if parent_class in ['LWFMeteo', 'LWFStation']:
            return f'lwf/models/{parent_class}.py'

        elif parent_class in ['Station']:
            return f'gcnet/models.py'

        else:
            raise Exception(f'ERROR {parent_class} parent_class does not exist or does not have model_path specified '
                            f'in new_model.py')

    # Check which kind of app should be used
    @staticmethod
    def get_app(parent_class):

        if parent_class in ['LWFMeteo', 'LWFStation']:
            return 'lwf'

        elif parent_class in ['Station']:
            return 'gcnet'

        else:
            raise Exception(f'ERROR {parent_class} parent_class does not exist or does not have app specified in '
                            f'new_model.py')
