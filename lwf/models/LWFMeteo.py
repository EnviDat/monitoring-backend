
from django.db import models
from postgres_copy import CopyManager

from lwf.fields import LWFMeteoFloatField


# Parent class that defines fields for LWF Meteo stations
class LWFMeteo(models.Model):
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
    temp = LWFMeteoFloatField(
        verbose_name='Air Temperature',
        null=True
    )

    # Relative humidity [%]
    rh = LWFMeteoFloatField(
        verbose_name='Relative Humidity',
        null=True
    )

    # Precipitation [mm hh^-1]
    precip = LWFMeteoFloatField(
        verbose_name='Precipitation',
        null=True
    )

    # PAR (photosynthetically active radiation) [W m^-2]
    par = LWFMeteoFloatField(
        verbose_name='Photosynthetically Active Radiation',
        null=True
    )

    # Wind speed [m s^-1]
    ws = LWFMeteoFloatField(
        verbose_name='Wind Speed',
        null=True
    )

    # Create copy manager for postgres_copy
    objects = CopyManager()

    delimiter = ';'

    header_line_count = 1

    header_symbol = '#'

    input_fields = ['timestamp', 'temp', 'rH', 'precip', 'PAR', 'ws',]

    model_fields = ['timestamp_iso', 'year', 'julianday', 'quarterday', 'halfday', 'day', 'week',
                       'temp', 'rh', 'precip', 'par', 'ws']

    date_format = '%Y-%m-%d %H:%M:%S'

    # Declare Station has an abstract class so it can be inherited
    class Meta:
        abstract = True



# Lens (LEB)
class leb(LWFMeteo):
    pass


# Beatenberg (BAF)
class baf(LWFMeteo):
    pass


# Beatenberg (BAB)
class bab(LWFMeteo):
    pass


# Celerina (CLB)
class clb(LWFMeteo):
    pass


# Celerina (CLF)
class clf(LWFMeteo):
    pass


# Jussy (JUB)
class jub(LWFMeteo):
    pass


# Jussy (JUF)
class juf(LWFMeteo):
    pass
