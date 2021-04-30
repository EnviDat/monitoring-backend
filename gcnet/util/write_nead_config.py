from pathlib import Path

from io import StringIO

from gcnet.util.geometry import get_gcnet_geometry
from gcnet.util.nead_header_strings import get_fields_string, get_add_value_string, get_scale_factor_string, \
    get_units_string, get_display_description, get_database_fields_data_types_string
from gcnet.util.views_helpers import read_config


# Returns path of gcnet config it is exists, otherwise returns empty string
def gcnet_nead_config(app):

    # nead_config = Path('gcnet/config/nead_header.ini')
    nead_config = Path(f'{app}/config/nead_header.ini')

    # Check if nead_config exists
    if nead_config.exists():
        return nead_config

    return ''



# Returns 'station_id' from stations config by mapping kwargs['model'] to station_id_dict
def get_station_id(model, stations_config):
    station_id_dict = {stations_config.get(s, 'model_url', fallback=''): s
                       for s in stations_config.sections() if s != 'DEFAULT'}

    try:
        station_id = station_id_dict[model]
        return station_id
    except KeyError:
        print(f'WARNING (write_nead_config.py) {model} not a valid model')
        return


def get_list_comma_delimited(string):
    comma_delimited_list = string.split(',')
    return comma_delimited_list


def write_nead_config(config_path, model, stringnull='', delimiter=',', ts_meaning='end'):
    # Try to dynamically generate NEAD config in buffer_
    try:
        # Get header config
        config = read_config(config_path)

        # Get stations confg
        stations_config = read_config('gcnet/config/stations.ini')

        # Assign station_id to model's corresponding station_id
        station_id = get_station_id(model, stations_config)

        # Set 'station_id'
        config.set('METADATA', 'station_id', str(station_id))

        # Set 'station_name'
        station_name = stations_config.get(str(station_id), 'name')
        config.set('METADATA', 'station_name', station_name)

        # Set 'nodata_value' to 'stringnull' argument passed or default value which is an empty string: ''
        config.set('METADATA', 'nodata', stringnull)

        # Set 'field_delimiter' to 'delimiter' argument passed or default value which is a comma: ','
        config.set('METADATA', 'field_delimiter', delimiter)

        # Set 'timestamp_meaning' to 'ts_meaning; argument passed or default value which is 'end'
        config.set('METADATA', 'timestamp_meaning', ts_meaning)

        # Parse 'position' from stations.ini, modify, and set 'geometry'
        position = stations_config.get(str(station_id), 'position')
        geometry = get_gcnet_geometry(position)
        config.set('METADATA', 'geometry', geometry)

        # Get database_fields as list
        database_fields = config.get('FIELDS', 'database_fields')
        database_fields_list = get_list_comma_delimited(database_fields)

        # Call get_fields_string() and set 'fields'
        fields_string = get_fields_string(database_fields_list)
        config.set('FIELDS', 'fields', fields_string)

        # Call get_units_offset_string() and set 'add_value'
        add_value_string = get_add_value_string(database_fields_list)
        config.set('FIELDS', 'add_value', add_value_string)

        # Call get_scale_factor_string() and set 'scale_factor'
        scale_factor_string = get_scale_factor_string(database_fields_list)
        config.set('FIELDS', 'scale_factor', scale_factor_string)

        # Call get_units_string() and set 'units'
        units_string = get_units_string(database_fields_list)
        config.set('FIELDS', 'units', units_string)

        # Call get_display_description() and set 'display_description'
        display_description_string = get_display_description(database_fields_list)
        config.set('FIELDS', 'display_description', display_description_string)

        # Call get_database_fields_data_types_string() and set 'database_fields_data_types'
        database_fields_data_types_string = get_database_fields_data_types_string(database_fields_list)
        config.set('FIELDS', 'database_fields_data_types', database_fields_data_types_string)

        # Dynamically write NEAD header into buffer_
        buffer_ = StringIO()
        config.write(buffer_)

        return buffer_.getvalue(), config

    except Exception as e:
        # Print error message
        print(f'WARNING (write_nead_config.py): could not write nead header config, EXCEPTION: {e}')
        return None, None


