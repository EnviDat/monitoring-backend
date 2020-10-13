from gcnet.helpers import read_config, get_station_id, get_gcnet_geometry, get_list_comma_delimited, get_fields_string, \
    get_add_value_string, get_scale_factor_string, get_units_string, get_database_fields_data_types_string


def write_nead_config(config_path, model, stringnull='', delimiter=','):
    # Try to dynamically generate NEAD config file
    try:
        # Get header config
        config = read_config(config_path)

        # create map containing comment lines and their indices
        # comment_map = save_comments(config)
        # print(comment_map)

        # # put the comments back in their original indices
        # restore_comments(config_file, comment_map)

        # Get stations confg
        stations_config = read_config('config/stations.ini')

        # Assign station_id to model's corresponding station_id
        station_id = get_station_id(model)

        # Set 'station_id'
        config.set('METADATA', 'station_id', str(station_id))

        # Set 'station_name'
        station_name = stations_config.get(str(station_id), 'name')
        config.set('METADATA', 'station_name', station_name)

        # Check if 'stringnull' passed. Set 'nodata_value' to stringnull passed.
        # Else set 'nodata' in config to empty string: ''
        if stringnull:
            config.set('METADATA', 'nodata', stringnull)
        else:
            config.set('METADATA', 'nodata', '')

        # Check if 'delimiter' passed. Set 'field_delimiter' to delimiter passed.
        # Else set 'column_delimiter' in config to comma: ','
        if delimiter != ',':
            config.set('METADATA', 'field_delimiter', delimiter)
        else:
            config.set('METADATA', 'field_delimiter', ',')

        # Parse 'position' from stations.ini, modify, and set 'geometry'
        position = stations_config.get(str(station_id), 'position')
        geometry = get_gcnet_geometry(position)
        config.set('METADATA', 'geometry', geometry)

        # Get display_description as list
        display_description = config.get('FIELDS', 'display_description')
        display_description_list = get_list_comma_delimited(display_description)

        # Call get_fields_string() and set 'fields'
        fields_string = get_fields_string(display_description_list)
        config.set('FIELDS', 'fields', fields_string)

        # Call get_units_offset_string() and set 'add_value'
        add_value_string = get_add_value_string(display_description_list)
        config.set('FIELDS', 'add_value', add_value_string)

        # Call get_scale_factor_string() and set 'scale_factor'
        scale_factor_string = get_scale_factor_string(display_description_list)
        config.set('FIELDS', 'scale_factor', scale_factor_string)

        # Call get_units_string() and set 'units'
        units_string = get_units_string(display_description_list)
        config.set('FIELDS', 'units', units_string)

        # Call get_database_fields_data_types_string() and set 'database_fields_data_types'
        database_fields_data_types_string = get_database_fields_data_types_string(display_description_list)
        config.set('FIELDS', 'database_fields_data_types', database_fields_data_types_string)

        # Dynamically write header in config file
        with open(config_path, encoding='utf-8', mode='w', newline='\n') as config_file:
            config.write(config_file)

    except Exception as e:
        # Print error message
        print('WARNING (write_nead_config.py): could not write nead header config, EXCEPTION: {0}'.format(e))
        return

# write_nead_config('config/nead_header.ini', 'gits_04d', stringnull='', delimiter=',')
