
from lwf.util.time_fields import get_utc_datetime, get_year, get_julian_day, quarter_day, half_day, year_day, year_week


# Return line_clean dictionary for lwf_csv_import.py for LWFStation data
def get_lwf_station_line_clean(row, date_format):
    return {
        'timestamp_iso': get_utc_datetime(row['timestamp_iso'], date_format),
        'year': get_year(row['timestamp_iso']),
        'julianday': get_julian_day(row['timestamp_iso'], date_format),
        'quarterday': quarter_day(row['timestamp_iso']),
        'halfday': half_day(row['timestamp_iso']),
        'day': year_day(row['timestamp_iso'], date_format),
        'week': year_week(row['timestamp_iso'], date_format),
        'air_temperature_10': row['air_temperature_10'],
        'precipitation_60': row['precipitation_60'],
        'precipitation_10': row['precipitation_10'],
        'precipitation_10_multi': row['precipitation_10_multi'],
        'precipitation_60_multi': row['precipitation_60_multi'],
        'wind_speed_10': row['wind_speed_10'],
        'wind_speed_max_10': row['wind_speed_max_10'],
        'wind_direction_10': row['wind_direction_10'],
        'relative_air_humidity_60': row['relative_air_humidity_60'],
        'relative_air_humidity_10': row['relative_air_humidity_10'],
        'global_radiation_10': row['global_radiation_10'],
        'photosynthetic_active_radiation_10': row['photosynthetic_active_radiation_10'],
        'uv_b_radiation_10': row['uv_b_radiation_10'],
        'vapour_pressure_deficit_10': row['vapour_pressure_deficit_10'],
        'dewpoint_10': row['dewpoint_10'],
        'ozone_10': row['ozone_10'],
        'soil_temperature_60_5': row['soil_temperature_60_5'],
        'soil_temperature_60_10': row['soil_temperature_60_10'],
        'soil_temperature_60_20': row['soil_temperature_60_20'],
        'soil_temperature_10_5': row['soil_temperature_10_5'],
        'soil_temperature_10_10': row['soil_temperature_10_10'],
        'soil_temperature_10_30': row['soil_temperature_10_30'],
        'soil_temperature_10_50': row['soil_temperature_10_50'],
        'soil_temperature_10_80': row['soil_temperature_10_80'],
        'soil_temperature_10_120': row['soil_temperature_10_120'],
        'soil_temperature_20_15': row['soil_temperature_20_15'],
        'soil_temperature_20_50': row['soil_temperature_20_50'],
        'soil_temperature_20_80': row['soil_temperature_20_80'],
        'soil_temperature_20_150': row['soil_temperature_20_150'],
        'soil_water_potential_20_15': row['soil_water_potential_20_15'],
        'soil_water_potential_20_50': row['soil_water_potential_20_50'],
        'soil_water_potential_20_80': row['soil_water_potential_20_80'],
        'soil_water_potential_20_150': row['soil_water_potential_20_150'],
        'soil_water_content_60_15': row['soil_water_content_60_15'],
        'soil_water_content_60_50': row['soil_water_content_60_50'],
        'soil_water_content_60_80': row['soil_water_content_60_80'],
        'soil_water_content_60_5': row['soil_water_content_60_5'],
        'soil_water_content_60_30': row['soil_water_content_60_30'],
        'soil_water_content_10_15': row['soil_water_content_10_15'],
        'soil_water_content_10_50': row['soil_water_content_10_50'],
        'soil_water_content_10_80': row['soil_water_content_10_80']
    }


# Return line_clean dictionary for csv_import.py for LWF Meteo data
def get_lwf_meteo_line_clean(row, date_format):
    return {
        'timestamp_iso': get_utc_datetime(row['timestamp'], date_format),
        'year': get_year(row['timestamp']),
        'julianday': get_julian_day(row['timestamp'], date_format),
        'quarterday': quarter_day(row['timestamp']),
        'halfday': half_day(row['timestamp']),
        'day': year_day(row['timestamp'], date_format),
        'week': year_week(row['timestamp'], date_format),
        'temp': row['temp'],
        'rh': row['rH'],
        'precip': row['precip'],
        'par': row['PAR'],
        'ws': row['ws']
    }
