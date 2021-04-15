
from django.db import models
from postgres_copy import CopyManager

from lwf.fields import LWFMeteoFloatField


# Parent class that defines fields for LWF Meteo stations
class LWFStation(models.Model):
    timestamp_iso = models.DateTimeField(
        verbose_name='Timestamp ISO format',
        unique=True
    )

    year = models.IntegerField(
        verbose_name='Year',
    )

    # Unit: Day of Year [days]
    julianday = models.IntegerField(
        verbose_name='Julian Day',
    )

    # Quarter day (every 6 hours (00:00, 6:00, 12:00, 18:00))
    quarterday = models.BooleanField(
        verbose_name='Quarter Day'
    )

    # Half day (every 12 hours (0:00, 12:00))
    halfday = models.BooleanField(
        verbose_name='Half Day'
    )

    # Julian day prefixed by year and hyphen (ex. 1996-123)
    day = models.CharField(
        verbose_name='Whole Day',
        max_length=8,
    )

    # Week of year prefixed by year and hyphen (ex. 1996-27)
    week = models.CharField(
        verbose_name='Week Number',
        max_length=8,
    )

    # Air temperature [°C]
    air_temperature_10 = LWFMeteoFloatField(
        verbose_name='Air Temperature',
        null=True
    )

    # Precipitation (60 min) [mm]
    precipitation_60 = LWFMeteoFloatField(
        verbose_name='Precipitation (60 min)',
        null=True
    )

    # Precipitation (10 min) [mm]
    precipitation_10 = LWFMeteoFloatField(
        verbose_name='Precipitation (10 min)',
        null=True
    )

    # Precipitation multiple gauges (10 min) [mm]
    precipitation_10_multi = LWFMeteoFloatField(
        verbose_name='Precipitation multiple gauges (10 min)',
        null=True
    )

    # Precipitation multiple gauges (60 min) [mm]
    precipitation_60_multi = LWFMeteoFloatField(
        verbose_name='Precipitation multiple gauges (60 min)',
        null=True
    )

    # Wind speed [m/s]
    wind_speed_10 = LWFMeteoFloatField(
        verbose_name='Wind speed (10 min)',
        null=True
    )

    # Wind speed peak [m/s]
    wind_speed_max_10 = LWFMeteoFloatField(
        verbose_name='Wind speed peak',
        null=True
    )

    # Wind direction [degree wind direction]
    wind_direction_10 = LWFMeteoFloatField(
        verbose_name='Wind direction',
        null=True
    )

    # Relative air humidity (60 min) [%]
    relative_air_humidity_60 = LWFMeteoFloatField(
        verbose_name='Relative air humidity (60 min)',
        null=True
    )

    # Relative air humidity (10 min) [%]
    relative_air_humidity_10 = LWFMeteoFloatField(
        verbose_name='Relative air humidity (10 min)',
        null=True
    )

    # TODO check units
    # Global radiation [W/m2]
    global_radiation_10 = LWFMeteoFloatField(
        verbose_name='Global radiation',
        null=True
    )

    # Photosynthetic active radiation [micro-mol/ m2/sec]
    photosynthetic_active_radiation_10 = LWFMeteoFloatField(
        verbose_name='Photosynthetic active radiation',
        null=True
    )

    # UV-B radiation [mW/m2]
    uv_b_radiation_10 = LWFMeteoFloatField(
        verbose_name='UV-B radiation',
        null=True
    )

    # Vapour pressure deficit (VPD) [kPa]
    vapour_pressure_deficit_10 = LWFMeteoFloatField(
        verbose_name='Vapour pressure deficit (VPD)',
        null=True
    )

    # TODO check units for temperatures, should be degrees C
    # Dewpoint [degrees C]
    dewpoint_10 = LWFMeteoFloatField(
        verbose_name='Dewpoint',
        null=True
    )

    # TODO complete writing other fields in LWF Station parent class



    # # Relative humidity [%]
    # rh = LWFMeteoFloatField(
    #     verbose_name='Relative Humidity',
    #     null=True
    # )
    #
    # # Precipitation [mm hh^-1]
    # precip = LWFMeteoFloatField(
    #     verbose_name='Precipitation',
    #     null=True
    # )
    #
    # # PAR (photosynthetically active radiation) [W m^-2]
    # par = LWFMeteoFloatField(
    #     verbose_name='Photosynthetically Active Radiation',
    #     null=True
    # )
    #
    # # Wind speed [m s^-1]
    # ws = LWFMeteoFloatField(
    #     verbose_name='Wind Speed',
    #     null=True
    # )

    # # Create copy manager for postgres_copy
    # objects = CopyManager()
    #
    # delimiter = ';'
    #
    # header_line_count = 1
    #
    # header_symbol = '#'
    #
    # input_fields = ['timestamp', 'temp', 'rH', 'precip', 'PAR', 'ws',]
    #
    # model_fields = ['timestamp_iso', 'year', 'julianday', 'quarterday', 'halfday', 'day', 'week',
    #                    'temp', 'rh', 'precip', 'par', 'ws']
    #
    # date_format = '%Y-%m-%d %H:%M:%S'
    #
    # # Declare Station has an abstract class so it can be inherited
    # class Meta:
    #     abstract = True



# # Lens (LEB)
# class leb(LWFMeteo):
#     pass
