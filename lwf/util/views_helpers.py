import os
from datetime import datetime, date
from django.db.models import Func
from django.http import HttpResponseNotFound

from generic.util.views_helpers import validate_display_values

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")

import django

django.setup()


# ============================================= CONSTANT ===============================================================

# String passed in kwargs['parameters'] that is used to return all parameters
ALL_DISPLAY_VALUES_STRING = 'multiple'


# ============================================== FUNCTIONS =============================================================

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


# Validate if date string is in year format: 'YYYY' ('2016')
def validate_year(date_string):
    try:
        datetime.strptime(date_string, '%Y')
        return True
    except:
        return False


# Validate if date string in year-week number format: '2015-00', '2015-01', …, '2015-53'
# From documentation:
# Week number of the year (Monday as the first day of the week) as a decimal number.
# All days in a new year preceding the first Monday are considered to be in week 0.
def validate_year_week(date_string):
    try:
        datetime.strptime(date_string, '%Y-%W')
        return True
    except:
        return False


# Validate if date string is in ISO timestamp format
def validate_iso_format(date_string):
    try:
        datetime.fromisoformat(date_string)
        return True
    except:
        return False


# Validate if date string is in ISO timestamp format: YYYY-MM-DD ('2019-12-04')
def validate_iso_format_date(date_string):
    try:
        date.fromisoformat(date_string)
        return True
    except:
        return False


# Return timestamp_iso dict with start and end range
# From documentation about 'range':
# Warning
# Filtering a DateTimeField with dates won’t include items on the last day, because the bounds are interpreted as
# “0am on the given date”. If pub_date was a DateTimeField, the above expression would be turned into this SQL:
# SELECT ... WHERE pub_date BETWEEN '2005-01-01 00:00:00' and '2005-03-31 00:00:00';
def get_timestamp_iso_range_dict(start, end):
    if validate_iso_format(start) and validate_iso_format(end):
        dict_ts = {'timestamp_iso__range': (start, end)}
        return dict_ts
    # else:
    #     raise ValueError("Incorrect date format, start and end dates should both be in ISO timestamp format")
    else:
        return HttpResponseNotFound("<h1>Page not found</h1>"
                                    "<h3>Incorrect date format for 'start' and/or 'end' timestamps.</h3>"
                                    "<h3>Start and end dates should both be in either ISO timestamp "
                                    "date format: YYYY-MM-DD ('2019-12-04')</h3>"
                                    )


# Return timestamp_iso dict with start and end range in whole date format: YYYY-MM-DD ('2019-12-04')
def get_timestamp_iso_range_day_dict(start, end):
    if validate_iso_format_date(start) and validate_iso_format_date(end):
        start_day = datetime.strptime(start + 'T00:00:00+00:00', '%Y-%m-%dT%H:%M:%S%z')
        start_iso = datetime.strftime(start_day, '%Y-%m-%dT%H:%M:%S%z')

        end_day = datetime.strptime(end + 'T00:00:00+00:00', '%Y-%m-%dT%H:%M:%S%z')
        end_iso = datetime.strftime(end_day, '%Y-%m-%dT%H:%M:%S%z')

        dict_ts = {'timestamp_iso__gte': start_iso, 'timestamp_iso__lt': end_iso}
        return dict_ts

    else:
        raise ValueError("Incorrect date format, start and end dates should both be in ISO timestamp date format:"
                         " YYYY-MM-DD ('2019-12-04')")


def validate_iso_format_datetime(date_text):
    try:
        datetime.fromisoformat(date_text)
        return True
    except:
        return False


# Return timestamp_iso dict with start and end range for whole weeks
# Monday is considered the first day of the week, time starts at 00:00:00
# Week number of the year (Monday as the first day of the week) as a decimal number.
# All days in a new year preceding the first Monday are considered to be in week 0.
def get_timestamp_iso_range_year_week(start, end):
    start_week = datetime.strptime(start + '-1T00:00:00+00:00', '%Y-%W-%wT%H:%M:%S%z')
    start_iso = datetime.strftime(start_week, '%Y-%m-%dT%H:%M:%S%z')

    end_week = datetime.strptime(end + '-0T23:59:59+00:00', '%Y-%W-%wT%H:%M:%S%z')
    end_iso = datetime.strftime(end_week, '%Y-%m-%dT%H:%M:%S%z')

    dict_ts = {'timestamp_iso__range': (start_iso, end_iso)}
    return dict_ts


# Return timestamp_iso dict with start and end range for whole years
def get_timestamp_iso_range_years(start, end):
    start_year = datetime.strptime(start + '-01-01T00:00:00+00:00', '%Y-%m-%dT%H:%M:%S%z')
    start_iso = datetime.strftime(start_year, '%Y-%m-%dT%H:%M:%S%z')

    end_year = datetime.strptime(end + '-12-31T23:00:00+00:00', '%Y-%m-%dT%H:%M:%S%z')
    end_iso = datetime.strftime(end_year, '%Y-%m-%dT%H:%M:%S%z')

    dict_ts = {'timestamp_iso__range': (start_iso, end_iso)}
    return dict_ts


class Round2(Func):
    function = "ROUND"
    template = "%(function)s(%(expressions)s::numeric, 2)"
