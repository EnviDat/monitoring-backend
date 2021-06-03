import os

from generic.util.views_helpers import validate_display_values

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")

import django

django.setup()


# ============================================= CONSTANT ==============================================================

# String passed in kwargs['parameters'] that is used to return all parameters
ALL_DISPLAY_VALUES_STRING = 'multiple'


# ============================================== FUNCTION =============================================================

# Get display_values by validating passed parameters
# If parameters == ALL_DISPLAY_VALUES_STRING assign display_values to values in returned_parameters
# Else validate parameter(s) passed in URL
def get_display_values(parameters, model_class):

    if parameters == ALL_DISPLAY_VALUES_STRING:
        fields = [field.name for field in model_class._meta.get_fields()]
        # Return new list without 'id' and time-related fields
        parameters = fields[8:]
        return parameters

    return validate_display_values(parameters, model_class)


def get_documentation_context(model_class):

    params_dict = {}
    for field in model_class._meta.get_fields():
        params_dict[field.name] = {'param': field.name, 'long_name': field.verbose_name, 'units': field.help_text}

    keys_to_remove = ['id', 'timestamp_iso', 'year', 'julianday', 'quarterday', 'halfday', 'day', 'week']
    for key in keys_to_remove:
        params_dict.pop(key)

    context = {'parameters': params_dict}

    return context
