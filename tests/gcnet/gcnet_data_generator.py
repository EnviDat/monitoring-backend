from datetime import datetime, timedelta
import random
import pytz

from gcnet.util.constants import Columns


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


class GCNetTestDataGenerator():
    start_timestamp = '2020-10-01 00:00:00.000+01:00'

    #  netrad, airtemp1, airtemp2, airtemp_cs500air1, airtemp_cs500air2, rh1, rh2, windspeed1, windspeed2, winddir1, winddir2, pressure, sh1, sh2, battvolt, swin_max, swout_max, netrad_max, airtemp1_max, airtemp2_max, airtemp1_min, airtemp2_min, windspeed_u1_max, windspeed_u2_max, windspeed_u1_stdev, windspeed_u2_stdev, reftemp
    def generateTestData(self):
        test_dataset = {}

        start_date = datetime.fromisoformat(self.start_timestamp)

        id = 1

        while id < 100:
            date = start_date + timedelta(hours=(id - 1))

            iso_timestamp = date.isoformat()
            date = datetime.fromisoformat(iso_timestamp)
            data = {'id': id, Columns.TIMESTAMP_ISO.value: iso_timestamp, Columns.TIMESTAMP.value: date.strftime("%s"),
                    Columns.YEAR.value: date.year, Columns.JULIANDAY.value: get_julian_day(iso_timestamp),
                    Columns.QUARTERDAY.value: get_quarter_day(date), Columns.HALFDAY.value: get_half_day(date),
                    Columns.DAY.value: "{0}-{1}".format(date.year, date.timetuple().tm_yday),
                    Columns.WEEK.value: "{0}-{1}".format(date.year, date.isocalendar()[1]),
                    Columns.SWIN.value: round(random.uniform(0, 5.0), 2),
                    Columns.SWOUT.value: round(random.uniform(0, 5.0), 2),
                    Columns.NETRAD.value: round(random.uniform(-10.0, 1.0), 2),
                    Columns.AIRTEMP1.value: round(random.uniform(-20.0, 5.0), 2),
                    Columns.AIRTEMP2.value: round(random.uniform(-20.0, 5.0), 2)}

            test_dataset[id] = data
            id += 1

        return test_dataset
