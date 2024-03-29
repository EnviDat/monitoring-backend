from datetime import datetime, timezone

import dateutil.parser as date_parser
from gcnet.util.constants import Columns


# Returns dictionary for timestamped record in GC-Net data parent class: Station in gcnet/models.py
# Keys are Station model names, values are from NEAD database_fields key in FIELDS section
# If database_field does not exist in NEAD input file then assigns value to None for that key
# Values matching null_value are replaced with None
def get_gcnet_record_clean(row, date_format, null_value):

    # Computed time fields
    time_fields = {
        Columns.TIMESTAMP_ISO.value: get_utc_datetime(
            row["timestamp_iso"], date_format
        ),
        Columns.TIMESTAMP.value: get_unix_timestamp(row["timestamp_iso"], date_format),
        Columns.YEAR.value: get_year(row["timestamp_iso"]),
        Columns.JULIANDAY.value: get_julian_day(row["timestamp_iso"], date_format),
        Columns.QUARTERDAY.value: quarter_day(row["timestamp_iso"]),
        Columns.HALFDAY.value: half_day(row["timestamp_iso"]),
        Columns.DAY.value: year_day(row["timestamp_iso"], date_format),
        Columns.WEEK.value: year_week(row["timestamp_iso"], date_format),
    }

    # Values directly from input file
    # If value does not exist then assign to None
    columns = Columns.get_parameters()
    parameters = {}
    for col in columns:
        try:
            val = float(row[col])
        except KeyError:
            val = None
        parameters[col] = val

    # Assemble record
    record = {**time_fields, **parameters}

    # null_value is converted to float to compare with record values
    null_value_float = float(null_value)

    # Assign values to None that match null_value
    for key, value in record.items():
        if value == null_value_float:
            record[key] = None

    return record


# Return line_clean dictionary for GC-Net data parent class: Station in gcnet/models.py
# Keys are Station model names, values are from NEAD datbase_fields key in FIELDS section
# Values matching null_value are replaced with None
def get_gcnet_line_clean(row, date_format, null_value):
    row = {
        # Computed time fields
        Columns.TIMESTAMP_ISO.value: get_utc_datetime(
            row["timestamp_iso"], date_format
        ),
        Columns.TIMESTAMP.value: get_unix_timestamp(row["timestamp_iso"], date_format),
        Columns.YEAR.value: get_year(row["timestamp_iso"]),
        Columns.JULIANDAY.value: get_julian_day(row["timestamp_iso"], date_format),
        Columns.QUARTERDAY.value: quarter_day(row["timestamp_iso"]),
        Columns.HALFDAY.value: half_day(row["timestamp_iso"]),
        Columns.DAY.value: year_day(row["timestamp_iso"], date_format),
        Columns.WEEK.value: year_week(row["timestamp_iso"], date_format),
        # Fields directly read from input data, convert input string values to float values
        Columns.SWIN.value: float(row["swin"]),
        Columns.SWOUT.value: float(row["swout"]),
        Columns.NETRAD.value: float(row["netrad"]),
        Columns.AIRTEMP1.value: float(row["airtemp1"]),
        Columns.AIRTEMP2.value: float(row["airtemp2"]),
        Columns.AIRTEMP_CS500AIR1.value: float(row["airtemp_cs500air1"]),
        Columns.AIRTEMP_CS500AIR2.value: float(row["airtemp_cs500air2"]),
        Columns.RH1.value: float(row["rh1"]),
        Columns.RH2.value: float(row["rh2"]),
        Columns.WINDSPEED1.value: float(row["windspeed1"]),
        Columns.WINDSPEED2.value: float(row["windspeed2"]),
        Columns.WINDDIR1.value: float(row["winddir1"]),
        Columns.WINDDIR2.value: float(row["winddir2"]),
        Columns.PRESSURE.value: float(row["pressure"]),
        Columns.SH1.value: float(row["sh1"]),
        Columns.SH2.value: float(row["sh2"]),
        Columns.BATTVOLT.value: float(row["battvolt"]),
        Columns.SWIN_MAX.value: float(row["swin_maximum"]),
        Columns.SWIN_STDEV.value: float(row["swin_stdev"]),
        Columns.NETRAD_STDEV.value: float(row["netrad_stdev"]),
        Columns.AIRTEMP1_MAX.value: float(row["airtemp1_maximum"]),
        Columns.AIRTEMP2_MAX.value: float(row["airtemp2_maximum"]),
        Columns.AIRTEMP1_MIN.value: float(row["airtemp1_minimum"]),
        Columns.AIRTEMP2_MIN.value: float(row["airtemp2_minimum"]),
        Columns.WINDSPEED_U1_MAX.value: float(row["windspeed_u1_maximum"]),
        Columns.WINDSPEED_U2_MAX.value: float(row["windspeed_u2_maximum"]),
        Columns.WINDSPEED_U1_STDEV.value: float(row["windspeed_u1_stdev"]),
        Columns.WINDSPEED_U2_STDEV.value: float(row["windspeed_u2_stdev"]),
        Columns.REFTEMP.value: float(row["reftemp"]),
    }

    # null_value is converted to float to compare with row values
    null_value_float = float(null_value)

    # Assign values to None that match null_value
    for key, value in row.items():
        if value == null_value_float:
            row[key] = None

    return row


# Returns a datetime object for date strings (assumes date_string is in UTC timezone)
# Example format used in LWF Meteo data: "1998-05-20 11:00:00","%Y-%m-%d %H:%M:%S"
def get_utc_datetime(date_string, date_format):
    dt_object = datetime.strptime(date_string, date_format)
    dt_object.replace(tzinfo=timezone.utc)
    return dt_object


# Return unix timestamp (assumes date_string is in UTC timezone)
def get_unix_timestamp(date_string, date_format):
    dt_object = get_utc_datetime(date_string, date_format)
    return int(datetime.timestamp(dt_object.replace(tzinfo=timezone.utc)))


# Returns year from date string
def get_year(date_string):
    return date_parser.parse(date_string).year


# Returns week as string from date string, assumes date in UTC time
# Assumes all days in a new year preceding the first Sunday are considered to be in week 0
def get_week(date_string, date_format):
    dt_object = get_utc_datetime(date_string, date_format)
    week = dt_object.strftime("%U")
    return week


# Returns Julian day, assumes input string in UTC
def get_julian_day(date_string, date_format):
    dt_object = get_utc_datetime(date_string, date_format)
    dt_object = dt_object.timetuple()
    julian_day = dt_object.tm_yday
    return float(julian_day)


# Returns hour from date string
def get_hour(date_string):
    return date_parser.parse(date_string).hour


# Returns minute from date string
def get_minute(date_string):
    return date_parser.parse(date_string).minute


# Returns True if time is "quarterday" (every 6 hours 00:00, 6:00, 12:00, 18:00)
def quarter_day(date_string):
    hour = get_hour(date_string)
    minute = get_minute(date_string)

    if minute == 0 and (hour == 0 or hour % 6 == 0):
        return True
    else:
        return False


# Returns True if time is "halfday" (every 12 hours 00:00 or 12:00)
def half_day(date_string):
    hour = get_hour(date_string)
    minute = get_minute(date_string)

    if minute == 0 and (hour == 0 or hour == 12):
        return True
    else:
        return False


# Return Julian day prefixed by year and hyphen (ex. 1996-123)
def year_day(date_string, date_format):
    year = get_year(date_string)
    julian_day = get_julian_day(date_string, date_format)
    return f"{year}-{julian_day}"


# Return week of year prefixed by year and hyphen (ex. 1996-27)
def year_week(date_string, date_format):
    year = get_year(date_string)
    week = get_week(date_string, date_format)
    return f"{year}-{week}"
