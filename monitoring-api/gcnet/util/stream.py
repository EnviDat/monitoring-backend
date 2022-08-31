# =================================  GC-NET DATA GENERATOR =========================================================

import csv
from io import StringIO
from django.core.exceptions import FieldError
from django.http import HttpResponseNotFound
from datetime import datetime, timedelta

from generic.util.views_helpers import get_timestamp_iso_range_day_dict


# Define a generator to stream GC-Net data directly to the client
def gcnet_stream(nead_version, hashed_lines, model_class, display_values, null_value, start, end, dict_fields,
                 **kwargs):

    timestamp_meaning = kwargs['timestamp_meaning']

    # If kwargs 'start' and 'end' passed in URL validate and assign to dict_timestamps
    dict_timestamps = {}
    if '' not in [start, end]:
        dict_timestamps = get_timestamp_iso_range_day_dict(start, end)

    # Create buffer_ and writer objects
    buffer_ = StringIO()
    writer = csv.writer(buffer_, lineterminator="\n")

    # Check if values passed for 'nead_version' and 'hashed_lines'
    # If True: Write version and hash_lines to buffer_
    if len(nead_version) > 0 and len(hashed_lines) > 0:
        buffer_.writelines(nead_version)
        buffer_.writelines(hashed_lines)
    # Else: Write 'display_values' to buffer_
    else:
        buffer_.writelines(','.join(display_values) + '\n')

    # Generator expressions to write each row in the queryset by calculating each row as needed and not all at once
    # Write values that are null in database as the value assigned to 'null_value'
    # Check if 'dict_fields' passed, if so stream aggregate daily data
    if len(dict_fields) > 0:

        queryset = model_class.objects \
            .values_list('day') \
            .annotate(**dict_fields) \
            .filter(**dict_timestamps) \
            .order_by('timestamp_first') \
            .iterator()

        for row in queryset:
            # Call write_row
            write_row(timestamp_meaning, writer, null_value, row)

            # Yield data (row from database)
            buffer_.seek(0)
            data = buffer_.read()
            buffer_.seek(0)
            buffer_.truncate()
            yield data

    # Elif kwargs 'start' and 'end' passed then apply timestamps filter
    elif len(dict_timestamps) > 0:

        queryset = model_class.objects \
            .values_list(*display_values) \
            .filter(**dict_timestamps) \
            .order_by('timestamp_iso') \
            .iterator()

        for row in queryset:
            # Call write_row
            write_row(timestamp_meaning, writer, null_value, row)

            # Yield data (row from database)
            buffer_.seek(0)
            data = buffer_.read()
            buffer_.seek(0)
            buffer_.truncate()
            yield data

    # Elif retrieve all data currently in database table if 'display_values' passed
    elif len(display_values) > 0:

        queryset = model_class.objects \
            .values_list(*display_values) \
            .order_by('timestamp_iso') \
            .iterator()

        for row in queryset:
            # Call write_row
            write_row(timestamp_meaning, writer, null_value, row)

            # Yield data (row from database)
            buffer_.seek(0)
            data = buffer_.read()
            buffer_.seek(0)
            buffer_.truncate()
            yield data

    else:
        raise FieldError("WARNING 'display_values' not passed")


# Write row and adjust timestamp_meaning
def write_row(timestamp_meaning, writer, null_value, row):
    # Write timestamps as they are in database if 'timestamp_meaning' == 'end'
    if timestamp_meaning == 'end':
        writer.writerow(null_value if x is None else x for x in row)

    # Write timestamps one hour behind how they are in database if 'timestamp_meaning' == 'beginning'
    elif timestamp_meaning == 'beginning':
        writer.writerow(get_nead_queryset_value(x, null_value) for x in row)

    else:
        return HttpResponseNotFound("<h1>WARNING non-valid 'timestamp_meaning' kwarg. Must be either 'beginning' or "
                                    "'end'</h3>")


def get_nead_queryset_value(x, null_value):
    if type(x) is datetime:
        x = dt_minus_hour(x)
    if x is None:
        x = null_value
    return x


def dt_minus_hour(dt_obj):
    dt_obj_minus_hour = dt_obj - timedelta(hours=1)
    return dt_obj_minus_hour
