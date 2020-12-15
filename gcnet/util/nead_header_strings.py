# =================================  NEAD HEADER STRINGS ==============================================================


# Returns comma separated string that will be written in a NEAD header
# Arguments:
#   db_fields_list    list of database_fields from the NEAD config file that are compared to the keys in nead_dict
#   nead_dict         dictionary used to retrieve values whose keys match the elements in db_fields_list
def get_nead_string(db_fields_list, nead_dict):

    nead_list = []

    for item in db_fields_list:
        if item in nead_dict:
            nead_list.append(nead_dict[item])
        else:
            print('WARNING (nead_header_strings.py) "{0}" not a valid key in {1}'.format(item, nead_dict))
            return

    # Convert any numbers in nead_list into strings and assign to converted_list
    converted_list = [str(element) for element in nead_list]

    # Create comma separated string from converted_list
    nead_string = ','.join(converted_list)

    return nead_string


# Returns 'fields' comma separated string for header config by mapping 'database_fields_list' to fields_dict
def get_fields_string(database_fields_list):
    fields_dict = {
        'timestamp_iso': 'timestamp',
        'swin': 'ISWR',
        'swin_maximum': 'ISWR_max',
        'swout': 'OSWR',
        'swout_minimum': 'OSWR_min',
        'netrad': 'NSWR',
        'netrad_maximum': 'NSWR_max',
        'airtemp1': 'TA1',
        'airtemp1_maximum': 'TA1_max',
        'airtemp1_minimum': 'TA1_min',
        'airtemp2': 'TA2',
        'airtemp2_maximum': 'TA2_max',
        'airtemp2_minimum': 'TA2_min',
        'airtemp_cs500air1': 'TA3',
        'airtemp_cs500air2': 'TA4',
        'rh1': 'RH1',
        'rh2': 'RH2',
        'windspeed1': 'VW1',
        'windspeed_u1_maximum': 'VW1_max',
        'windspeed_u1_stdev': 'VW1_stdev',
        'windspeed2': 'VW2',
        'windspeed_u2_maximum': 'VW2_max',
        'windspeed_u2_stdev': 'VW2_stdev',
        'winddir1': 'DW1',
        'winddir2': 'DW2',
        'pressure': 'P',
        'sh1': 'HS1',
        'sh2': 'HS2',
        'battvolt': 'V',
        'reftemp': 'TA5'
    }

    fields_string = get_nead_string(database_fields_list, fields_dict)

    return fields_string


# Returns 'add_value' comma separated string for header config by mapping 'database_fields_list' to
# add_value_dict
def get_add_value_string(database_fields_list):
    add_value_dict = {
        'timestamp_iso': 0,
        'swin': 0,
        'swin_maximum': 0,
        'swout': 0,
        'swout_minimum': 0,
        'netrad': 0,
        'netrad_maximum': 0,
        'airtemp1': 273.15,
        'airtemp1_maximum': 273.15,
        'airtemp1_minimum': 273.15,
        'airtemp2': 273.15,
        'airtemp2_maximum': 273.15,
        'airtemp2_minimum': 273.15,
        'airtemp_cs500air1': 273.15,
        'airtemp_cs500air2': 273.15,
        'rh1': 0,
        'rh2': 0,
        'windspeed1': 0,
        'windspeed_u1_maximum': 0,
        'windspeed_u1_stdev': 0,
        'windspeed2': 0,
        'windspeed_u2_maximum': 0,
        'windspeed_u2_stdev': 0,
        'winddir1': 0,
        'winddir2': 0,
        'pressure': 0,
        'sh1': 0,
        'sh2': 0,
        'battvolt': 0,
        'reftemp': 273.15
    }

    add_value_string = get_nead_string(database_fields_list, add_value_dict)

    return add_value_string


# Returns 'scale_factor' comma separated string for header config by mapping 'database_fields_list' to
# scale_factor_dict
def get_scale_factor_string(database_fields_list):
    scale_factor_dict = {
        'timestamp_iso': 1,
        'swin': 1,
        'swin_maximum': 1,
        'swout': 1,
        'swout_minimum': 1,
        'netrad': 1,
        'netrad_maximum': 1,
        'airtemp1': 1,
        'airtemp1_maximum': 1,
        'airtemp1_minimum': 1,
        'airtemp2': 1,
        'airtemp2_maximum': 1,
        'airtemp2_minimum': 1,
        'airtemp_cs500air1': 1,
        'airtemp_cs500air2': 1,
        'rh1': 0.01,
        'rh2': 0.01,
        'windspeed1': 1,
        'windspeed_u1_maximum': 1,
        'windspeed_u1_stdev': 1,
        'windspeed2': 1,
        'windspeed_u2_maximum': 1,
        'windspeed_u2_stdev': 1,
        'winddir1': 1,
        'winddir2': 1,
        'pressure': 100,
        'sh1': 1,
        'sh2': 1,
        'battvolt': 1,
        'reftemp': 1
    }

    scale_factor_string = get_nead_string(database_fields_list, scale_factor_dict)

    return scale_factor_string


# Returns 'units' comma separated string for header config by mapping 'database_fields_list' to units_dict
def get_units_string(database_fields_list):
    units_dict = {
        'timestamp_iso': 'time',
        'swin': 'W/m2',
        'swin_maximum': 'W/m2',
        'swout': 'W/m2',
        'swout_minimum': 'W/m2',
        'netrad': 'W/m2',
        'netrad_maximum': 'W/m2',
        'airtemp1': 'Degrees C',
        'airtemp1_maximum': 'Degrees C',
        'airtemp1_minimum': 'Degrees C',
        'airtemp2': 'Degrees C',
        'airtemp2_maximum': 'Degrees C',
        'airtemp2_minimum': 'Degrees C',
        'airtemp_cs500air1': 'Degrees C',
        'airtemp_cs500air2': 'Degrees C',
        'rh1': '%',
        'rh2': '%',
        'windspeed1': 'm/s',
        'windspeed_u1_maximum': 'm/s',
        'windspeed_u1_stdev': 'm/s',
        'windspeed2': 'm/s',
        'windspeed_u2_maximum': 'm/s',
        'windspeed_u2_stdev': 'm/s',
        'winddir1': 'Degrees',
        'winddir2': 'Degrees',
        'pressure': 'mbar',
        'sh1': 'm',
        'sh2': 'm',
        'battvolt': 'V',
        'reftemp': 'Degrees C'
    }

    units_string = get_nead_string(database_fields_list, units_dict)

    return units_string


# Returns 'database_fields_data_types' comma separated string for header config by mapping 'database_fields_list' to
# database_fields_data_types_dict
def get_database_fields_data_types_string(database_fields_list):
    database_fields_data_types_dict = {
        'timestamp_iso': 'timestamp',
        'swin': 'real',
        'swin_maximum': 'real',
        'swout': 'real',
        'swout_minimum': 'real',
        'netrad': 'real',
        'netrad_maximum': 'real',
        'airtemp1': 'real',
        'airtemp1_maximum': 'real',
        'airtemp1_minimum': 'real',
        'airtemp2': 'real',
        'airtemp2_maximum': 'real',
        'airtemp2_minimum': 'real',
        'airtemp_cs500air1': 'real',
        'airtemp_cs500air2': 'real',
        'rh1': 'real',
        'rh2': 'real',
        'windspeed1': 'real',
        'windspeed_u1_maximum': 'real',
        'windspeed_u1_stdev': 'real',
        'windspeed2': 'real',
        'windspeed_u2_maximum': 'real',
        'windspeed_u2_stdev': 'real',
        'winddir1': 'real',
        'winddir2': 'real',
        'pressure': 'real',
        'sh1': 'real',
        'sh2': 'real',
        'battvolt': 'real',
        'reftemp': 'real'
    }

    display_units_string = get_nead_string(database_fields_list, database_fields_data_types_dict)

    return display_units_string


# Returns 'display_description' comma separated string for header config by mapping 'database_fields_list' to
# display_description_dict
def get_display_description(database_fields_list):
    display_description_dict = {
        'timestamp_iso': 'timestamp_iso',
        'swin': 'shortwave_incoming_radiation',
        'swin_maximum': 'shortwave_incoming_radiation_max',
        'swout': 'shortwave_outgoing_radiation',
        'swout_minimum': 'shortwave_outgoing_radiation_min',
        'netrad': 'net_radiation',
        'netrad_maximum': 'net_radiation_max',
        'airtemp1': 'air_temperature_1',
        'airtemp1_maximum': 'air_temperature_1_max',
        'airtemp1_minimum': 'air_temperature_1_min',
        'airtemp2': 'air_temperature_2',
        'airtemp2_maximum': 'air_temperature_2_max',
        'airtemp2_minimum': 'air_temperature_2_min',
        'airtemp_cs500air1': 'air_temperature_cs500_air1',
        'airtemp_cs500air2': 'air_temperature_cs500_air2',
        'rh1': 'relative_humidity_1',
        'rh2': 'relative_humidity_2',
        'windspeed1': 'wind_speed_1',
        'windspeed_u1_maximum': 'wind_speed_u1_max',
        'windspeed_u1_stdev': 'wind_speed_u1_stdev',
        'windspeed2': 'wind_speed_2',
        'windspeed_u2_maximum': 'wind_speed_u2_max',
        'windspeed_u2_stdev': 'wind_speed_u2_stdev',
        'winddir1': 'wind_from_direction_1',
        'winddir2': 'wind_from_direction_2',
        'pressure': 'air_pressure',
        'sh1': 'snow_depth_1',
        'sh2': 'snow_depth_2',
        'battvolt': 'battery_voltage',
        'reftemp': 'ref_temperature'
    }

    display_description_string = get_nead_string(database_fields_list, display_description_dict)

    return display_description_string
