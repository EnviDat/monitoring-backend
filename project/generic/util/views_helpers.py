import importlib

from django.apps import apps
from datetime import datetime


# =========================================== CONSTANTS ===============================================================

# String passed in kwargs['parameters'] that is used to return all parameters
ALL_DISPLAY_VALUES_STRING = 'multiple'


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
def get_display_values(parameters, model_class):
    if parameters == ALL_DISPLAY_VALUES_STRING:
        return ALL_DISPLAY_VALUES

    return validate_display_values(parameters, model_class)
