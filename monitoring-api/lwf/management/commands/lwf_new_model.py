# Example command
#   python manage.py lwf_new_model -c lwf/config/test.ini

from django.core.management.base import BaseCommand

__version__ = "0.0.1"
__author__ = "Rebecca Buchholz"

from lwf.util.new_model_helpers import (execute_commands, has_spaces,
                                        model_exists, read_config)


class Command(BaseCommand):

    # def get_config_versions(self):
    #     return ['0.0.1']

    def add_arguments(self, parser):

        parser.add_argument("-c", "--config", required=True, help="Path to config file")

    def handle(self, *args, **kwargs):

        # Read configuration file and assign variables for configuration values
        conf = read_config(kwargs["config"])
        parent_class = conf.get("configuration", "parent_class")
        name = conf.get("configuration", "name")

        # Check if 'database_table_name' in config file is in valid format (no spaces)
        database_table_name = conf.get("configuration", "database_table_name").lower()
        if has_spaces(database_table_name):
            print(
                'WARNING (lwf_new_model.py): {} "database_table_name" setting "{}" is in invalid format. This '
                "value must not contain spaces.".format(
                    kwargs["config"], database_table_name
                )
            )
            return

        # Create models file path string
        parent_class_path = f"lwf/models/{parent_class}.py"

        # Set table_exists to False
        table_exists = False

        # Check if child class ('database_table_name' in config) already exists in corresponding models file
        try:
            # First check if model is written in corresponding models file:
            with open(parent_class_path) as f:
                if database_table_name in f.read():
                    table_exists = True
                    print(
                        "WARNING (lwf_new_model.py): Table {} already written in {}".format(
                            database_table_name, parent_class_path
                        )
                    )
                    return
        except FileNotFoundError as e:
            print(
                f"WARNING (lwf_new_model.py): File not found {parent_class_path}, exception {e}"
            )

        # Check if table already exists in database
        long_db_name = f"lwf_{database_table_name}"

        if model_exists(database_table_name):
            table_exists = True
            print(
                f"WARNING (lwf_new_parent_class.py): Table {long_db_name} already exists in database"
            )

        # If child class does not exist in corresponding parent_classs file or database
        # write it to corresponding models file and run migrations to add it to database
        if not table_exists:

            comment = f"\n# {name}"
            class_string = f"\nclass {database_table_name}({parent_class}):"

            try:
                # Write new class to corresponding models file
                with open(parent_class_path, "a") as sink:
                    sink.write("\n")
                    sink.write(comment)
                    sink.write(class_string)
                    sink.write("\n    pass")
                    sink.write("\n")

                # Update '__init__.py' with new model
                with open("lwf/models/__init__.py", "a") as controller:
                    controller.write(
                        f"\nfrom .{parent_class} import {database_table_name}\n"
                    )

                # Assign migrations_commands to contain migrations strings
                migrations_commands = [
                    "python manage.py makemigrations lwf",
                    "python manage.py migrate lwf --database=lwf",
                ]

                # Call execute_commands to execute migrations commands
                execute_commands(migrations_commands)

                return 0

            except Exception as e:
                print(f"WARNING (lwf_new_model.py) exception: {e}")
