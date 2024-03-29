from datetime import datetime, timezone

import dateutil.parser as date_parser


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


# Returns Julian day, assumes input string in UTC
def get_julian_day(date_string, date_format):
    dt_object = get_utc_datetime(date_string, date_format)
    dt_object = dt_object.timetuple()
    julian_day = dt_object.tm_yday

    return julian_day


# Returns hour from date string
def get_hour(date_string):
    return date_parser.parse(date_string).hour


# Returns minute from date string
def get_minute(date_string):
    return date_parser.parse(date_string).minute


# Returns week as string from date string, assumes date in UTC time
# Assumes all days in a new year preceding the first Sunday are considered to be in week 0
def get_week(date_string, date_format):
    dt_object = get_utc_datetime(date_string, date_format)
    week = dt_object.strftime("%U")

    return week


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
