# Example command
#   python manage.py new_model -c config/test_conf.ini

from django.core.management.base import BaseCommand
import importlib

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

        # Get the database table class
        package = importlib.import_module('monitoring.models.{0}'.format(model))
        child_class = getattr(package, database_table_name)
        print(child_class)

        # Check if child class already exists for child class ('database_table_name' in config)
        try:
            child_class.objects.get(id=1)
            print('exists')

        # If child class does not exist write it to corresponding models file
        except:
            print('does not exist')

            # Create path string
            model_path = 'monitoring/models/{0}.py'.format(model)

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

            except Exception as e:
                print('WARNING (new_model.py) exception: {0}'.format(e))
