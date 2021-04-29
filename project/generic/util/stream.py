import csv
from io import StringIO

from django.core.exceptions import FieldError
from django.http import StreamingHttpResponse

from gcnet.util.stream import gcnet_stream
from project.generic.util.views_helpers import get_timestamp_iso_range_day_dict


# ----------------------------------------  Streaming Helpers ---------------------------------------------------------
# Assign null_value
def get_null_value(nodata_kwarg):
    if nodata_kwarg == 'empty':
        null_value = ''
    else:
        null_value = nodata_kwarg
    return null_value


# Write row and populate null values
def write_row(writer, null_value, row):
    writer.writerow(null_value if x is None else x for x in row)


# ----------------------------------------  Data Generator ------------------------------------------------------------
# TODO handle timestamp_meaning
# Define a generator to stream GC-Net data directly to the client
def stream(nead_version, hashed_lines, model_class, display_values, timestamp_meaning, null_value, start, end, dict_fields):
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
            write_row(writer, null_value, row)

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
            write_row(writer, null_value, row)

            # Yield data (row from database)
            buffer_.seek(0)
            data = buffer_.read()
            buffer_.seek(0)
            buffer_.truncate()
            yield data

    # Elif retrieve all data currently in database table if 'display_values' passed and 'start' and 'end' are not passed
    elif len(display_values) > 0:

        queryset = model_class.objects \
            .values_list(*display_values) \
            .order_by('timestamp_iso') \
            .iterator()

        for row in queryset:
            # Call write_row
            write_row(writer, null_value, row)

            # Yield data (row from database)
            buffer_.seek(0)
            data = buffer_.read()
            buffer_.seek(0)
            buffer_.truncate()
            yield data

    else:
        raise FieldError("ERROR (stream.py) 'display_values' not passed in API call")
