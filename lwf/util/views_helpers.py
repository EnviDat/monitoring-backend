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
