import math
from datetime import datetime, timezone

import pytz


def dict_from_csv_line(line, header, sep=","):
    line_array = [v.strip() for v in line.strip().split(sep)]

    if len(line_array) != len(header):
        return None

    return {header[i]: line_array[i] for i in range(len(line_array))}


def get_julian_day(iso_timestamp):
    date = datetime.fromisoformat(iso_timestamp)
    return date.toordinal() + 1721424.5


def get_quarter_day(date):
    gmt_date = date.astimezone(pytz.timezone("GMT0"))
    if (gmt_date.minute == 0) and (gmt_date.hour in [0, 6, 18, 12]):
        return True
    else:
        return False


def get_half_day(date):
    gmt_date = date.astimezone(pytz.timezone("GMT0"))
    if (gmt_date.minute == 0) and (gmt_date.hour in [0, 12]):
        return True
    else:
        return False


def get_year_week(date):
    return f"{date.year}-{date.isocalendar()[1]}"


def get_year_day(date):
    return f"{date.year}-{date.timetuple().tm_yday}"


def get_linux_timestamp(date):
    linux_time = round(date.timestamp())
    return linux_time


def quarter_day(julianday):
    if float(julianday) % 0.25 == 0:
        return True
    else:
        return False


def half_day(dec_day):
    if float(dec_day) % 0.5 == 0:
        return True
    else:
        return False


def year_day(year, decday):
    day = str(math.floor(float(decday)))
    return year + "-" + day


def year_week(year, decday):
    string_year = str(year)
    float_day = math.floor(float(decday))
    day = str(float_day)

    date = string_year + "-" + day
    element = datetime.strptime(date, "%Y-%j")
    timestamp = int(element.replace(tzinfo=timezone.utc).timestamp())
    date_object = datetime.fromtimestamp(timestamp).strftime("%Y-%V")
    return str(date_object)


# Returns unix timestamp
def gcnet_utc_timestamp(year, decimal_day):
    day = math.floor(float(decimal_day))
    float_decimal_day = float(decimal_day)

    fractional_day = round((float_decimal_day - day), 4)
    fractional_time = round((fractional_day * 24), 4)

    hours = int(fractional_time)
    minutes = int((fractional_time * 60) % 60)

    # Code for generating seconds
    # seconds = str(int(time * 3600) % 60).zfill(2)

    # Round minutes and hours to nearest hour +- 3 minutes
    if 57 <= minutes <= 59 and hours != 23:
        minutes = 0
        hours += 1
    elif 1 <= minutes <= 3:
        minutes = 0

    # Format variables into padded strings for strptime
    padded_day = str(day).zfill(3)
    padded_minutes = str(minutes).zfill(2)
    padded_hours = str(hours).zfill(2)

    date = f"{year}/{padded_day}/{padded_hours}:{padded_minutes}"
    element = datetime.strptime(date, "%Y/%j/%H:%M")
    timestamp = int(element.replace(tzinfo=timezone.utc).timestamp())

    return timestamp


# Return Python datetime object
def gcnet_utc_datetime(year, decimal_day):
    timestamp = gcnet_utc_timestamp(year, decimal_day)

    dt_object = datetime.utcfromtimestamp(timestamp)
    dt_object.replace(tzinfo=timezone.utc)

    return dt_object
