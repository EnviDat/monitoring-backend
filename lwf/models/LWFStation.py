import os

from django.db import models
from postgres_copy import CopyManager

from lwf.fields import LWFStationFloatField

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
import django

django.setup()


# TODO add minutes to verbose names?
# TODO check how many decimal places and which custom field to use for float values
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
    air_temperature_10 = LWFStationFloatField(
        verbose_name='Air Temperature',
        null=True
    )

    # Precipitation (60 min) [mm]
    precipitation_60 = LWFStationFloatField(
        verbose_name='Precipitation (60 min)',
        null=True
    )

    # Precipitation (10 min) [mm]
    precipitation_10 = LWFStationFloatField(
        verbose_name='Precipitation (10 min)',
        null=True
    )

    # Precipitation multiple gauges (10 min) [mm]
    precipitation_10_multi = LWFStationFloatField(
        verbose_name='Precipitation multiple gauges (10 min)',
        null=True
    )

    # Precipitation multiple gauges (60 min) [mm]
    precipitation_60_multi = LWFStationFloatField(
        verbose_name='Precipitation multiple gauges (60 min)',
        null=True
    )

    # Wind speed [m/s]
    wind_speed_10 = LWFStationFloatField(
        verbose_name='Wind speed (10 min)',
        null=True
    )

    # Wind speed peak [m/s]
    wind_speed_max_10 = LWFStationFloatField(
        verbose_name='Wind speed peak',
        null=True
    )

    # Wind direction [degree wind direction]
    wind_direction_10 = LWFStationFloatField(
        verbose_name='Wind direction',
        null=True
    )

    # Relative air humidity (60 min) [%]
    relative_air_humidity_60 = LWFStationFloatField(
        verbose_name='Relative air humidity (60 min)',
        null=True
    )

    # Relative air humidity (10 min) [%]
    relative_air_humidity_10 = LWFStationFloatField(
        verbose_name='Relative air humidity (10 min)',
        null=True
    )

    # TODO check units
    # Global radiation [W/m2]
    global_radiation_10 = LWFStationFloatField(
        verbose_name='Global radiation',
        null=True
    )

    # Photosynthetic active radiation [micro-mol/ m2/sec]
    photosynthetic_active_radiation_10 = LWFStationFloatField(
        verbose_name='Photosynthetic active radiation',
        null=True
    )

    # UV-B radiation [mW/m2]
    uv_b_radiation_10 = LWFStationFloatField(
        verbose_name='UV-B radiation',
        null=True
    )

    # Vapour pressure deficit (VPD) [kPa]
    vapour_pressure_deficit_10 = LWFStationFloatField(
        verbose_name='Vapour pressure deficit (VPD)',
        null=True
    )

    # Dewpoint [degrees C]
    dewpoint_10 = LWFStationFloatField(
        verbose_name='Dewpoint',
        null=True
    )

    # Ozone [ppb ozone concentration]
    ozone_10 = LWFStationFloatField(
        verbose_name='Ozone',
        null=True
    )

    # Soil temperature -5 cm [degrees C]
    soil_temperature_60_5 = LWFStationFloatField(
        verbose_name='Soil temperature -5 cm',
        null=True
    )

    # Soil temperature -10 cm [degrees C]
    soil_temperature_60_10 = LWFStationFloatField(
        verbose_name='Soil temperature -10 cm',
        null=True
    )

    # Soil temperature -20 cm [degrees C]
    soil_temperature_60_20 = LWFStationFloatField(
        verbose_name='Soil temperature -20 cm',
        null=True
    )

    # Soil temperature BT -5 cm [degrees C]
    soil_temperature_10_5 = LWFStationFloatField(
        verbose_name='Soil temperature BT -5 cm',
        null=True
    )

    # Soil temperature BT -10 cm [degrees C]
    soil_temperature_10_10 = LWFStationFloatField(
        verbose_name='Soil temperature BT -10 cm',
        null=True
    )

    # Soil temperature BT -30 cm [degrees C]
    soil_temperature_10_30 = LWFStationFloatField(
        verbose_name='Soil temperature BT -30 cm',
        null=True
    )

    # Soil temperature BT -50 cm [degrees C]
    soil_temperature_10_50 = LWFStationFloatField(
        verbose_name='Soil temperature BT -50 cm',
        null=True
    )

    # Soil temperature BT -80 cm [degrees C]
    soil_temperature_10_80 = LWFStationFloatField(
        verbose_name='Soil temperature BT -80 cm',
        null=True
    )

    # Soil temperature BT -120 cm [degrees C]
    soil_temperature_10_120 = LWFStationFloatField(
        verbose_name='Soil temperature BT -120 cm',
        null=True
    )

    # Soil temperature 15 cm [degrees C]
    soil_temperature_20_15 = LWFStationFloatField(
        verbose_name='Soil temperature 15 cm',
        null=True
    )

    # Soil temperature 50 cm [degrees C]
    soil_temperature_20_50 = LWFStationFloatField(
        verbose_name='Soil temperature 50 cm',
        null=True
    )

    # Soil temperature 80 cm [degrees C]
    soil_temperature_20_80 = LWFStationFloatField(
        verbose_name='Soil temperature 80 cm',
        null=True
    )

    # Soil temperature 150 cm [degrees C]
    soil_temperature_20_150 = LWFStationFloatField(
        verbose_name='Soil temperature 150 cm',
        null=True
    )

    # TODO confirm that soil water potential should have negative depths
    # Soil water potential 15 cm [hPa]
    soil_water_potential_20_15 = LWFStationFloatField(
        verbose_name='Soil water potential 15 cm',
        null=True
    )

    # Soil water potential 50 cm [hPa]
    soil_water_potential_20_50 = LWFStationFloatField(
        verbose_name='Soil water potential 50 cm',
        null=True
    )

    # Soil water potential 80 cm [hPa]
    soil_water_potential_20_80 = LWFStationFloatField(
        verbose_name='Soil water potential 80 cm',
        null=True
    )

    # Soil water potential 150 cm [hPa]
    soil_water_potential_20_150 = LWFStationFloatField(
        verbose_name='Soil water potential 150 cm',
        null=True
    )

    # Soil water content -15 cm [m3 m-3]
    soil_water_content_60_15 = LWFStationFloatField(
        verbose_name='Soil water content -15 cm',
        null=True
    )

    # Soil water content -50 cm [m3 m-3]
    soil_water_content_60_50 = LWFStationFloatField(
        verbose_name='Soil water content -50 cm',
        null=True
    )

    # Soil water content -80 cm [m3 m-3]
    soil_water_content_60_80 = LWFStationFloatField(
        verbose_name='Soil water content -80 cm',
        null=True
    )

    # Soil water content -5 cm [m3 m-3]
    soil_water_content_60_5 = LWFStationFloatField(
        verbose_name='Soil water content -5 cm',
        null=True
    )

    # Soil water content -30 cm [m3 m-3]
    soil_water_content_60_30 = LWFStationFloatField(
        verbose_name='Soil water content -30 cm',
        null=True
    )

    # Soil water content -15 cm [m3 m-3]
    soil_water_content_10_15 = LWFStationFloatField(
        verbose_name='Soil water content -15 cm',
        null=True
    )

    # Soil water content -50 cm [m3 m-3]
    soil_water_content_10_50 = LWFStationFloatField(
        verbose_name='Soil water content -50 cm',
        null=True
    )

    # Soil water content -80 cm [m3 m-3]
    soil_water_content_10_80 = LWFStationFloatField(
        verbose_name='Soil water content -80 cm',
        null=True
    )

    # Create copy manager for postgres_copy
    objects = CopyManager()

    delimiter = ','

    header_line_count = 1

    header_symbol = '#'

    input_fields = ['timestamp_iso', 'air_temperature_10',
                    'precipitation_60', 'precipitation_10', 'precipitation_10_multi', 'precipitation_60_multi',
                    'wind_speed_10', 'wind_speed_max_10', 'wind_direction_10', 'relative_air_humidity_60',
                    'relative_air_humidity_10', 'global_radiation_10', 'photosynthetic_active_radiation_10',
                    'uv_b_radiation_10', 'vapour_pressure_deficit_10', 'dewpoint_10', 'ozone_10',
                    'soil_temperature_60_5', 'soil_temperature_60_10', 'soil_temperature_60_20',
                    'soil_temperature_10_5', 'soil_temperature_10_10', 'soil_temperature_10_30',
                    'soil_temperature_10_50', 'soil_temperature_10_80', 'soil_temperature_10_120',
                    'soil_temperature_20_15', 'soil_temperature_20_50', 'soil_temperature_20_80',
                    'soil_temperature_20_150', 'soil_water_potential_20_15', 'soil_water_potential_20_50',
                    'soil_water_potential_20_80', 'soil_water_potential_20_150', 'soil_water_content_60_15',
                    'soil_water_content_60_50', 'soil_water_content_60_80', 'soil_water_content_60_5',
                    'soil_water_content_60_30', 'soil_water_content_10_15', 'soil_water_content_10_50',
                    'soil_water_content_10_80']

    model_fields = ['timestamp_iso', 'year', 'julianday', 'quarterday', 'halfday', 'day', 'week', 'air_temperature_10',
                    'precipitation_60', 'precipitation_10', 'precipitation_10_multi', 'precipitation_60_multi',
                    'wind_speed_10', 'wind_speed_max_10', 'wind_direction_10', 'relative_air_humidity_60',
                    'relative_air_humidity_10', 'global_radiation_10', 'photosynthetic_active_radiation_10',
                    'uv_b_radiation_10', 'vapour_pressure_deficit_10', 'dewpoint_10', 'ozone_10',
                    'soil_temperature_60_5', 'soil_temperature_60_10', 'soil_temperature_60_20',
                    'soil_temperature_10_5', 'soil_temperature_10_10', 'soil_temperature_10_30',
                    'soil_temperature_10_50', 'soil_temperature_10_80', 'soil_temperature_10_120',
                    'soil_temperature_20_15', 'soil_temperature_20_50', 'soil_temperature_20_80',
                    'soil_temperature_20_150', 'soil_water_potential_20_15', 'soil_water_potential_20_50',
                    'soil_water_potential_20_80', 'soil_water_potential_20_150', 'soil_water_content_60_15',
                    'soil_water_content_60_50', 'soil_water_content_60_80', 'soil_water_content_60_5',
                    'soil_water_content_60_30', 'soil_water_content_10_15', 'soil_water_content_10_50',
                    'soil_water_content_10_80']

    date_format = '%Y-%m-%dT%H:%M:%SZ'

    # Declare Station has an abstract class so it can be inherited
    class Meta:
        abstract = True