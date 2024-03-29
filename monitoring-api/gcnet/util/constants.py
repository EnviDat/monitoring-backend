from enum import Enum


class Columns(Enum):
    TIMESTAMP_ISO = "timestamp_iso"
    TIMESTAMP = "timestamp"
    YEAR = "year"
    JULIANDAY = "julianday"
    QUARTERDAY = "quarterday"
    HALFDAY = "halfday"
    DAY = "day"
    WEEK = "week"
    SWIN = "swin"
    SWIN_MAX = "swin_maximum"
    SWOUT = "swout"
    NETRAD = "netrad"
    AIRTEMP1 = "airtemp1"
    AIRTEMP1_MAX = "airtemp1_maximum"
    AIRTEMP1_MIN = "airtemp1_minimum"
    AIRTEMP2 = "airtemp2"
    AIRTEMP2_MAX = "airtemp2_maximum"
    AIRTEMP2_MIN = "airtemp2_minimum"
    AIRTEMP_CS500AIR1 = "airtemp_cs500air1"
    AIRTEMP_CS500AIR2 = "airtemp_cs500air2"
    RH1 = "rh1"
    RH2 = "rh2"
    WINDSPEED1 = "windspeed1"
    WINDSPEED_U1_MAX = "windspeed_u1_maximum"
    WINDSPEED_U1_STDEV = "windspeed_u1_stdev"
    WINDSPEED2 = "windspeed2"
    WINDSPEED_U2_MAX = "windspeed_u2_maximum"
    WINDSPEED_U2_STDEV = "windspeed_u2_stdev"
    WINDDIR1 = "winddir1"
    WINDDIR2 = "winddir2"
    PRESSURE = "pressure"
    SH1 = "sh1"
    SH2 = "sh2"
    BATTVOLT = "battvolt"
    REFTEMP = "reftemp"
    # SWOUT_MIN = 'swout_minimum'
    SWIN_STDEV = "swin_stdev"
    # NETRAD_MAX = 'netrad_maximum'
    NETRAD_STDEV = "netrad_stdev"

    @staticmethod
    def get_columns():
        return [name.value for name in Columns]

    @staticmethod
    def get_parameters():
        parameters = [name for name in Columns]
        time_fields = [
            Columns.TIMESTAMP_ISO,
            Columns.TIMESTAMP,
            Columns.YEAR,
            Columns.JULIANDAY,
            Columns.QUARTERDAY,
            Columns.HALFDAY,
            Columns.DAY,
            Columns.WEEK,
        ]
        parameters = [elem.value for elem in parameters if elem not in time_fields]
        return parameters
