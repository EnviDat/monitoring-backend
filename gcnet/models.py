from django.db import models
from django.db.models import Subquery, Max, Min

from gcnet.fields import CustomFloatField
from postgres_copy import CopyManager


# This class used for metadata endpoint development and testing and may not be deployed
class MetadataSet(models.QuerySet):

    def metadata(self, parameter):

        filter_dict = {f'{parameter}__isnull': False}

        dict_timestamps = {'timestamp_iso_latest': Max('timestamp_iso'),
                           'timestamp_latest': Max('timestamp'),
                           'timestamp_iso_earliest': Min('timestamp_iso'),
                           'timestamp_earliest': Min('timestamp')}

        return self.filter(**filter_dict).values(parameter).aggregate(**dict_timestamps)


# Parent class that defines fields for each station's model
class Station(models.Model):
    timestamp_iso = models.DateTimeField(
        verbose_name='Timestamp ISO format',
        unique=True
    )

    timestamp = models.IntegerField(
        verbose_name='Unix-Timestamp',
        unique=True
    )

    year = models.IntegerField(
        verbose_name='Year',
    )

    # Unit: Day of Year.hour/24 [days]
    julianday = models.FloatField(
        verbose_name='Decimal Julian Day',
    )

    # Quarter day (every 6 hours (00:00, 6:00, 12:00, 18:00))
    quarterday = models.BooleanField(
        verbose_name='Quarter Day'
    )

    # Half day (every 12 hours (0:00,. 12:00))
    halfday = models.BooleanField(
        verbose_name='Half Day'
    )

    # Julian day truncated to whole day (i.e. 1.25 to 1) prefixed by year and hyphen (ex. 1996-123)
    day = models.CharField(
        verbose_name='Whole Day',
        max_length=10,
    )

    # Week of year prefixed by year and hyphen (ex. 1996-27)
    week = models.CharField(
        verbose_name='Week Number',
        max_length=10,
    )

    # Unit:  SW_down [W m-2]
    swin = CustomFloatField(
        verbose_name='SWin',
        null=True,
        db_column='swin',
        help_text='W m^-2'
    )

    # Unit: SW_up [W m-2]
    swout = CustomFloatField(
        verbose_name='SWout',
        null=True,
        help_text='W m^-2'
    )

    # Unit: Net Radiation F [W m-2]
    netrad = CustomFloatField(
        verbose_name='Net Radiation',
        null=True,
        help_text='W m^-2'
    )

    # Unit: TC Air 1 G Air Temperature [degC]
    airtemp1 = CustomFloatField(
        verbose_name='Air Temperature-TC Air 1',
        null=True,
        help_text='°C',
    )

    # Unit: TC Air 2 H Air Temperature [degC]
    airtemp2 = CustomFloatField(
        verbose_name='Air Temperature-TC Air 2',
        null=True,
        help_text='°C',
    )

    # Unit:  CS500 T Air 1 I Air Temperature [degC]
    airtemp_cs500air1 = CustomFloatField(
        verbose_name='Air Temperature-CS500 T Air 1',
        null=True,
        help_text='°C',
    )

    # Unit: CS500 T Air 2 J Air Temperature [degC]
    airtemp_cs500air2 = CustomFloatField(
        verbose_name='Air Temperature-CS500 T Air 2',
        null=True,
        help_text='°C',
    )

    # Unit: RH 1 K Relative Humidity [%]
    rh1 = CustomFloatField(
        verbose_name='Relative Humidity-RH 1',
        null=True,
        help_text='%',
    )

    # Unit: RH 2 L Relative Humidity [%]
    rh2 = CustomFloatField(
        verbose_name='Relative Humidity-RH 2',
        null=True,
        help_text='%',
    )

    # Unit: U1 M Wind Speed [m/s]
    windspeed1 = CustomFloatField(
        verbose_name='Windspeed-U1',
        null=True,
    )

    # Unit: U2 N Wind Speed [m/s]
    windspeed2 = CustomFloatField(
        verbose_name='Windspeed-U2',
        null=True,
    )

    # Unit: U Dir 1 O [deg]
    winddir1 = CustomFloatField(
        verbose_name='Wind Direction-U Dir 1',
        null=True,
    )

    # Unit: U Dir 2 P [deg]
    winddir2 = CustomFloatField(
        verbose_name='Wind Direction-U Dir 2',
        null=True,
    )

    # Unit: Atmos Pressure Q [mbar]
    pressure = CustomFloatField(
        verbose_name='Atmos Pressure',
        null=True,
    )

    # Unit: Snow Height 1 R [m]
    sh1 = CustomFloatField(
        verbose_name='Snow Height 1',
        null=True,
    )

    # Unit: Snow Height 2 S [m]
    sh2 = CustomFloatField(
        verbose_name='Snow Height 2',
        null=True,
    )

    # Unit: Battery Voltage [V]
    battvolt = CustomFloatField(
        verbose_name='Battery Voltage',
        null=True,
    )

    # Unit: SW Incoming Radiation Maximum [W m-2]
    swin_maximum = CustomFloatField(
        verbose_name='SWinMax',
        null=True,
    )

    # Unit: [W m-2]
    swout_minimum = CustomFloatField(
        verbose_name='SWoutMin',
        null=True,
    )

    # Unit: NetRadMax[W m-2]
    netrad_maximum = CustomFloatField(
        verbose_name='NetRadMax',
        null=True,
    )

    # Unit: Max Air Temperature1 (TC) [degC]
    airtemp1_maximum = CustomFloatField(
        verbose_name='Max Air Temperature1 (TC)',
        null=True,
    )

    # Unit: Max Air Temperature2 (TC)[degC]
    airtemp2_maximum = CustomFloatField(
        verbose_name='Max Air Temperature2 (TC)',
        null=True,
    )

    # Unit: Min Air Temperature1 (TC)[degC]
    airtemp1_minimum = CustomFloatField(
        verbose_name='Min Air Temperature1 (TC)',
        null=True,
    )

    # Unit: Min Air Temperature2 (TC) [degC]
    airtemp2_minimum = CustomFloatField(
        verbose_name='Min Air Temperature2 (TC)',
        null=True,
    )

    # Unit: Max Windspeed-U1 [m/s]
    windspeed_u1_maximum = CustomFloatField(
        verbose_name='Max Windspeed-U1',
        null=True,
    )

    # Unit: Max Windspeed-U2 [m/s]
    windspeed_u2_maximum = CustomFloatField(
        verbose_name='Max Windspeed-U2',
        null=True,
    )

    # Unit: StdDev Windspeed-U1 [m/s]
    windspeed_u1_stdev = CustomFloatField(
        verbose_name='StdDev Windspeed-U1',
        null=True,
    )

    # Unit: StdDev Windspeed-U2 [m/s]
    windspeed_u2_stdev = CustomFloatField(
        verbose_name='StdDev Windspeed-U2',
        null=True,
    )

    # Unit: Ref Temperature [degC]
    reftemp = CustomFloatField(
        verbose_name='Ref Temperature',
        null=True,
    )

    objects = MetadataSet.as_manager()

    # Create copy manager for postgres_copy
    # objects = CopyManager()

    # Declare Station has an abstract class so it can be inherited
    class Meta:
        abstract = True


# Create models for each Station
# FUTURE VERSION: implement Stations 30-34 (Antarctic), possibly with a different parent class

# ===========================================   GOES STATIONS and ID Numbers  =========================================

# Test class to use for testing data imports
class test(Station):
    pass


# Test class 2 to use for testing data imports
class test2(Station):
    pass


# Swiss Camp 10 Meter Tower 00
class swisscamp_10m_tower_00d(Station):
    pass


# Swiss Camp 01
class swisscamp_01d(Station):
    pass


# Crawford Point 02
class crawfordpoint_02d(Station):
    pass


# NASA-U 03
class nasa_u_03d(Station):
    pass


# Summit Station 06
class summit_06d(Station):
    pass


# DYE-II 08
class dye2_08d(Station):
    pass


# JAR-1 09
class jar1_09d(Station):
    pass


# Saddle 10
class saddle_10d(Station):
    pass


# South Dome 11
class southdome_11d(Station):
    pass


# NASA East 12
class nasa_east_12d(Station):
    pass


# NASA South-East 15
class nasa_southeast_15d(Station):
    pass


# NEEM 23
class neem_23d(Station):
    pass


# East GRIP 24
class east_grip_24d(Station):
    pass


# ===========================================   ARGOS STATIONS and ID Numbers  =======================================

# GITS 04
class gits_04d(Station):
    pass


# Humboldt Glacier 05
class humboldt_05d(Station):
    pass


# Tunu N Glacier 07
class tunu_n_07d(Station):
    pass


# Petermann Glacier 22
class petermann_22d(Station):
    pass


# test3
class test3(Station):
    pass
