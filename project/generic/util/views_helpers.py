import importlib

from django.apps import apps
from django.core.exceptions import FieldDoesNotExist
from datetime import datetime

# ============================================= CONSTANT ===============================================================

# String passed in kwargs['parameters'] that is used to return all parameters
ALL_DISPLAY_VALUES_STRING = 'multiple'


# ============================================== FUNCTIONS =============================================================

# ----------------------------------------  Model Functions ------------------------------------------------------------

# Function returns a list of models in an app
def get_models_list(app):
    models = []
    for key in apps.all_models[app]:
        models.append(key)
    return models


def get_model_class(class_name, app, parent_class):
    if len(parent_class) > 0:
        package = importlib.import_module('{0}.models.{1}'.format(app, parent_class))
    else:
        package = importlib.import_module('{0}.models'.format(app))
    return getattr(package, class_name)


# -------------------------------------- Date Validators --------------------------------------------------------------

def validate_date(start, end):
    if validate_iso_format(start) and validate_iso_format(end):
        dict_ts = {'timestamp_iso__range': (start, end)}
        return dict_ts

    # elif validate_unix_timestamp(int(start)) and validate_unix_timestamp(int(end)):
    #     dict_ts = {'timestamp__range': (start, end)}
    #     return dict_ts

    else:
        # raise ValueError("Incorrect date formats, start and end dates should both be in ISO format or unix timestamp")
        raise ValueError("Incorrect date formats, start and end dates should both be in ISO format")


def validate_iso_format(date_text):
    try:
        datetime.fromisoformat(date_text)
        return True
    except:
        return False


# def validate_unix_timestamp(date_text):
#     try:
#         datetime.fromtimestamp(date_text)
#         return True
#     except:
#         return False


# --------------------------------------- Dynamic Parameters Validators -----------------------------------------------

# Get display_values by validating passed parameters
# If parameters == ALL_DISPLAY_VALUES_STRING assign display_values to values in returned_parameters
# Else validate parameter(s) passed in URL
def get_display_values(parameters, model_class, parent_class):
    if parent_class == 'LWFStation' and parameters == ALL_DISPLAY_VALUES_STRING:
        # TODO implement constants.py for all display fields
        fields = [field.name for field in model_class._meta.get_fields()]
        # Return new list without 'id' and time-related fields
        parameters = fields[8:]
        return parameters

    return validate_display_values(parameters, model_class)


# Validate parameters and return them as display_values list
# parameters are comma separated string from kwargs['parameters']
# model_class is validated model as a class
def validate_display_values(parameters, model_class):
    # Split parameters comma separated string into parameter_list
    parameters_list = convert_string_to_list(parameters)

    # Validate parameters in parameters_list and add to display_values
    display_values = []
    for parameter in parameters_list:
        try:
            model_class._meta.get_field(parameter)
            if parameter != 'id':
                display_values = display_values + [parameter]
        except FieldDoesNotExist:
            pass

    return display_values


# Returns comma delimited string as list
def convert_string_to_list(string):
    new_list = [item.strip() for item in string.split(',')]
    return new_list
