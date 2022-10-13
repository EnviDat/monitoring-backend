import random
from datetime import datetime, timedelta

import gcnet.management.commands.importers.helpers.import_date_helpers as h
from gcnet.util.constants import Columns


class GCNetTestDataGenerator:
    start_timestamp = "2020-10-01 00:00:00.000+01:00"

    def generate_test_data(self):
        test_dataset = {}

        start_date = datetime.fromisoformat(self.start_timestamp)

        id = 1

        while id < 100:
            date = start_date + timedelta(hours=(id - 1))

            iso_timestamp = date.isoformat()
            date = datetime.fromisoformat(iso_timestamp)
            linux_time = h.get_linux_timestamp(date)
            data = {
                "id": id,
                Columns.TIMESTAMP_ISO.value: iso_timestamp,
                Columns.TIMESTAMP.value: linux_time,
                Columns.YEAR.value: date.year,
                Columns.JULIANDAY.value: h.get_julian_day(iso_timestamp),
                Columns.QUARTERDAY.value: h.get_quarter_day(date),
                Columns.HALFDAY.value: h.get_half_day(date),
                Columns.DAY.value: h.get_year_day(date),
                Columns.WEEK.value: h.get_year_week(date),
                Columns.SWIN.value: round(random.uniform(0, 5.0), 2),
                Columns.SWOUT.value: round(random.uniform(0, 5.0), 2),
                Columns.NETRAD.value: round(random.uniform(-10.0, 1.0), 2),
                Columns.AIRTEMP1.value: round(random.uniform(-20.0, 5.0), 2),
                Columns.AIRTEMP2.value: round(random.uniform(-20.0, 5.0), 2),
            }

            test_dataset[id] = data
            id += 1

        return test_dataset
