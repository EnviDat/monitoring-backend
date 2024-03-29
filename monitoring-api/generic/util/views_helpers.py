import importlib
from datetime import datetime

from django.apps import apps
from django.core.exceptions import FieldDoesNotExist

# from django.db.models import Func, Min, Max, Avg, Sum
from django.db.models import Avg, Func, Max, Min

# ----------------------------------------  Model Helpers -------------------------------------------------------------

# Function returns a list of models in an app, if parent_class passed returns only models from that parent class
def get_models_list(app, parent_class=""):

    models = []

    for key in apps.all_models[app]:

        model_class = get_model_cl(app, key)
        parent_class_name = model_class.__base__.__name__

        if parent_class:
            if parent_class == parent_class_name:
                models.append(key)
        else:
            models.append(key)

    return models


# Returns model class without parent_class kwarg
def get_model_cl(app, model):
    package = importlib.import_module(f"{app}.models")
    return getattr(package, model)


# Returns model class with parent_class kwarg
def get_model_class(app, **kwargs):
    model = kwargs["model"]
    parent_class = kwargs["parent_class"]
    package = importlib.import_module(f"{app}.models.{parent_class}")
    return getattr(package, model)


# -------------------------------------- Date Validators --------------------------------------------------------------


def validate_date(start, end):
    if validate_iso_format(start) and validate_iso_format(end):
        dict_ts = {"timestamp_iso__range": (start, end)}
        return dict_ts

    # elif validate_unix_timestamp(int(start)) and validate_unix_timestamp(int(end)):
    #     dict_ts = {'timestamp__range': (start, end)}
    #     return dict_ts

    else:
        # raise ValueError("Incorrect date formats, start and end dates should both be in ISO format or unix timestamp")
        raise ValueError(
            "Incorrect date formats, start and end dates should both be in ISO format"
        )


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


# Return timestamp_iso dict with start and end range in whole date format: YYYY-MM-DD ('2019-12-04')
def get_timestamp_iso_range_day_dict(start, end):
    if validate_iso_format(start) and validate_iso_format(end):
        start_day = datetime.strptime(start + "T00:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
        start_iso = datetime.strftime(start_day, "%Y-%m-%dT%H:%M:%S%z")

        end_day = datetime.strptime(end + "T00:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
        end_iso = datetime.strftime(end_day, "%Y-%m-%dT%H:%M:%S%z")

        dict_ts = {"timestamp_iso__gte": start_iso, "timestamp_iso__lt": end_iso}
        return dict_ts

    else:
        raise ValueError(
            "Incorrect date format, start and end dates should both be in ISO timestamp date format:"
            " YYYY-MM-DD ('2019-12-04')"
        )


# --------------------------------------- Dynamic Parameters Validator -------------------------------------------------

# Validate parameters and return them as display_values list
# If 'multiple' passed returns all parameters (except 'id' and time related fields)
# parameters are comma separated string from kwargs['parameters']
# model_class is validated model as a class
def validate_display_values(parameters, model_class):

    display_values = []

    # If parameters == 'multiple' return all parameters (except 'id' and time related fields)
    if parameters == "multiple":
        fields_excluded = [
            "id",
            "timestamp_iso",
            "timestamp",
            "year",
            "julianday",
            "quarterday",
            "halfday",
            "day",
            "week",
        ]
        display_values = [
            field.name
            for field in model_class._meta.get_fields()
            if field.name not in fields_excluded
        ]
        return display_values

    # Split parameters comma separated string into parameter_list
    parameters_list = convert_string_to_list(parameters)

    # Validate parameters in parameters_list and add to display_values
    for parameter in parameters_list:
        try:
            model_class._meta.get_field(parameter)
            if parameter != "id":
                display_values = display_values + [parameter]
        except FieldDoesNotExist:
            pass

    return display_values


# Returns comma delimited string as list
def convert_string_to_list(string):
    new_list = [item.strip() for item in string.split(",")]
    return new_list


# --------------------------------------- Aggregate View Helpers ------------------------------------------------------


class Round3(Func):
    function = "ROUND"
    template = "%(function)s(%(expressions)s::numeric, 3)"


# Get 'dict_fields' for aggregate views
def get_dict_fields(display_values):
    dict_fields = {
        "timestamp_first": Min("timestamp_iso"),
        "timestamp_last": Max("timestamp_iso"),
    }

    for parameter in display_values:
        dict_fields[parameter + "_min"] = Round3(Min(parameter))
        dict_fields[parameter + "_max"] = Round3(Max(parameter))
        dict_fields[parameter + "_avg"] = Round3(Avg(parameter))
        # dict_fields[parameter + '_sum'] = Round3(Sum(parameter))

    return dict_fields


# --------------------------------------- Metadata View Helper --------------------------------------------------------

# Get dict_timestamps for metadata view
def get_dict_timestamps():
    dict_timestamps = {
        "timestamp_iso_earliest": Min("timestamp_iso"),
        "timestamp_iso_latest": Max("timestamp_iso"),
    }
    return dict_timestamps
