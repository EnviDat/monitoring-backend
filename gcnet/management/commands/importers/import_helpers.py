from datetime import datetime, timedelta
import pytz


def dict_from_csv_line(line, header, sep=','):
    line_array = [v for v in line.strip().split(sep) if len(v) > 0]

    if len(line_array) != len(header):
        return None

    return {header[i]: line_array[i] for i in range(len(line_array))}


def get_julian_day(iso_timestamp):
    date = datetime.fromisoformat(iso_timestamp)
    return date.toordinal() + 1721424.5


def get_quarter_day(date):
    gmt_date = date.astimezone(pytz.timezone('GMT0'))
    if (gmt_date.minute == 0) and (gmt_date.hour in [0, 6, 18, 12]):
        return True
    else:
        return False


def get_half_day(date):
    gmt_date = date.astimezone(pytz.timezone('GMT0'))
    if (gmt_date.minute == 0) and (gmt_date.hour in [0, 12]):
        return True
    else:
        return False


def get_year_week(date):
    return "{0}-{1}".format(date.year, date.isocalendar()[1])


def get_year_day(date):
    return "{0}-{1}".format(date.year, date.timetuple().tm_yday)

