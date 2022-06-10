# TODO copy lwf.time_fields.py to gcnet app and adjust improts

from lwf.util.time_fields import get_utc_datetime, get_year, get_julian_day, quarter_day, half_day, year_day, \
    year_week, get_unix_timestamp

from gcnet.util.constants import Columns


# Return line_clean dictionary for GC-Net data parent class: Station in gcnet/models.py
# Keys are Station model names, values are from NEAD datbase_fields key in FIELDS section
# Values matching null_value are replaced with None
def get_gcnet_line_clean(row, date_format, null_value):
    row = {
        Columns.TIMESTAMP_ISO.value: get_utc_datetime(row['timestamp_iso'], date_format),
        Columns.TIMESTAMP.value: get_unix_timestamp(row['timestamp_iso'], date_format),
        Columns.YEAR.value: get_year(row['timestamp_iso']),
        Columns.JULIANDAY.value: get_julian_day(row['timestamp_iso'], date_format),
        Columns.QUARTERDAY.value: quarter_day(row['timestamp_iso']),
        Columns.HALFDAY.value: half_day(row['timestamp_iso']),
        Columns.DAY.value: year_day(row['timestamp_iso'], date_format),
        Columns.WEEK.value: year_week(row['timestamp_iso'], date_format),

        # TODO clarify these values: OWSR, OSWR_min, NSWR_max (for 'fields' line in NEAD file)
        Columns.SWIN.value: row['swin'], Columns.SWOUT.value: row['swout'], Columns.NETRAD.value: row['netrad'],
        Columns.AIRTEMP1.value: row['airtemp1'], Columns.AIRTEMP2.value: row['airtemp2'],
        Columns.AIRTEMP_CS500AIR1.value: row['airtemp_cs500air1'],
        Columns.AIRTEMP_CS500AIR2.value: row['airtemp_cs500air2'],
        Columns.RH1.value: row['rh1'], Columns.RH2.value: row['rh2'],
        Columns.WINDSPEED1.value: row['windspeed1'], Columns.WINDSPEED2.value: row['windspeed2'],
        Columns.WINDDIR1.value: row['winddir1'], Columns.WINDDIR2.value: row['winddir2'],
        Columns.PRESSURE.value: row['pressure'],
        Columns.SH1.value: row['sh1'], Columns.SH2.value: row['sh2'],
        Columns.BATTVOLT.value: row['battvolt'],
        Columns.SWIN_MAX.value: row['swin_maximum'], Columns.SWOUT_MIN.value: row['swout_minimum'],
        Columns.NETRAD_MAX.value: row['netrad_maximum'],
        Columns.AIRTEMP1_MAX.value: row['airtemp1_maximum'], Columns.AIRTEMP2_MAX.value: row['airtemp2_maximum'],
        Columns.AIRTEMP1_MIN.value: row['airtemp1_minimum'], Columns.AIRTEMP2_MIN.value: row['airtemp2_minimum'],
        Columns.WINDSPEED_U1_MAX.value: row['windspeed_u1_maximum'],
        Columns.WINDSPEED_U2_MAX.value: row['windspeed_u2_maximum'],
        Columns.WINDSPEED_U1_STDEV.value: row['windspeed_u1_stdev'],
        Columns.WINDSPEED_U2_STDEV.value: row['windspeed_u2_stdev'],
        Columns.REFTEMP.value: row['reftemp']
    }

    # null_value is converted to float and then back to string to compare with row values
    null_value_float = str(float(null_value))

    # Assign values to None that match null_value
    for key, value in row.items():
        if value == null_value_float:
            row[key] = None

    return row
