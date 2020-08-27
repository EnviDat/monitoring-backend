import os

from django.db import models
from postgres_copy import CopyManager

from monitoring.fields import LWFMeteoFloatField


# Parent class that defines fields for LWF Meteo stations
class LWFMeteoTest(models.Model):
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

    # Half day (every 12 hours (0:00,. 12:00))
    halfday = models.BooleanField(
        verbose_name='Half Day'
    )

    # Julian day prefixed by year and hyphen (ex. 1996-123)
    day = models.CharField(
        verbose_name='Whole Day',
        max_length=10,
    )

    # Week of year prefixed by year and hyphen (ex. 1996-27)
    week = models.CharField(
        verbose_name='Week Number',
        max_length=10,
    )

    # Air temperature [°C]
    temp = LWFMeteoFloatField(
        verbose_name='Air Temperature'
    )

    # Relative humidity [%]
    rh = LWFMeteoFloatField(
        verbose_name='Relative Humidity'
    )

    # Precipitation [mm hh^-1]
    precip = LWFMeteoFloatField(
        verbose_name='Precipitation'
    )

    # PAR (photosynthetically active radiation) [W m^-2]
    par = LWFMeteoFloatField(
        verbose_name='Photosynthetically Active Radiation'
    )

    # Wind speed [m s^-1]
    ws = LWFMeteoFloatField(
        verbose_name='Wind Speed'
    )

    # Create copy manager for postgres_copy
    objects = CopyManager()

    test_attribute = 222

    input_fields = ['timestamp', 'temp', 'rH', 'precip', 'PAR', 'ws',]

    model_fields = ['timestamp_iso', 'year', 'julianday', 'quarterday', 'halfday', 'day', 'week',
                       'temp', 'rh', 'precip', 'par', 'ws']

    # Declare Station has an abstract class so it can be inherited
    class Meta:
        abstract = True





# Test Station Name
class test_lwf_1(LWFMeteoTest):
    pass
