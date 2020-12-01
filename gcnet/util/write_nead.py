import argparse

from gcnet.util.helpers import get_null_value, get_model
from gcnet.util.write_nead_config import write_nead_config


def get_parser():
    """
    Creates a new argument parser.
    """
    parser = argparse.ArgumentParser("NEADWriter")
    parser.add_argument('--station', '-s', required=True, help='Name of station. Must be station from the list at this'
                                                               'website: https://www.envidat.ch/data-api/gcnet/models/')
    return parser


def write_nead(args=None):
    parser = get_parser()
    args = parser.parse_args(args)

    # ===================================== ASSIGN VARIABLES ========================================================
    # Assign version
    version = "# NEAD 1.0 UTF-8\n"

    # Assign nead_config
    nead_config = 'gcnet/config/nead_header.ini'

    # Assign station_model
    station_model = args.station

    # Assign NEAD output csv
    output_nead = station_model + '.csv'

    # # Assign null_value
    # null_value = get_null_value(kwargs['nodata'])

    # # Assign timestamp_meaning
    # timestamp_meaning = kwargs['timestamp_meaning']

    # ================================  VALIDATE VARIABLES =========================================================
    # Get and validate the model_class
    try:
        model_class = get_model(station_model.strip())
        print(station_model + 'VALIDATED')
    except Exception as e:
        raise Exception("{1}\nWARNING (write_nead.py): Invalid station:{0}".format(station_model, e))

    # # Check if timestamp_meaning is valid
    # if timestamp_meaning not in ['end', 'beginning']:
    #     return timestamp_meaning_http_error(timestamp_meaning)
    #
    # # Validate 'start' and 'end' if they are passed
    # if len(start) > 0 and len(end) > 0:
    #     # Check if timestamps are in whole date format: YYYY-MM-DD ('2019-12-04')
    #     try:
    #         get_timestamp_iso_range_day_dict(start, end)
    #     except ValueError:
    #         return HttpResponseNotFound("<h1>Page not found</h1>"
    #                                     "<h3>Incorrect date format for 'start' and/or 'end' timestamps.</h3>"
    #                                     "<h3>Start and end dates should both be in ISO timestamp "
    #                                     "date format: YYYY-MM-DD ('2019-12-04')</h3>")
    #
    # # =============================== PROCESS NEAD HEADER ===========================================================
    # Get NEAD header
    # config_buffer, nead_config_parser = write_nead_config(config_path=nead_config, model=station_model,
    #                                                       stringnull=null_value, delimiter=',',
    #                                                       ts_meaning=timestamp_meaning)
    # #
    # # Check if config_buffer or nead_config_parser are None
    # if nead_config_parser is None or config_buffer is None:
    #     return HttpResponseNotFound("<h1>Page not found</h1>"
    #                                 "<h3>Check that valid 'model' (station) entered in URL: {0}</h3>"
    #                                 .format(kwargs['model']))
    #
    # # Fill hash_lines with config_buffer lines prepended with '# '
    # hash_lines = get_hashed_lines(config_buffer)
    #
    # # Assign display_values from database_fields in nead_config_parser
    # database_fields = nead_config_parser.get('FIELDS', 'database_fields')
    # display_values = list(database_fields.split(','))
    #
    # # ===================================  STREAM NEAD DATA ===========================================================
    # # Create the streaming response object and output csv
    # response = StreamingHttpResponse(stream(version, hash_lines, model_class, display_values, timestamp_meaning,
    #                                         null_value, start, end, dict_fields={}), content_type='text/csv')
    # response['Content-Disposition'] = 'attachment; filename=' + output_csv
    #
    # return response


if __name__ == '__write_nead__':
    write_nead()
