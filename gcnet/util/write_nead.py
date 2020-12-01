import pandas as pd
import argparse

from gcnet.util.helpers import get_model, get_hashed_lines
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
    station_model = args.station.strip()

    # Assign NEAD output csv
    output_nead = 'gcnet/output/nead/' + station_model + '.csv'

    # # Assign null_value
    # null_value = get_null_value(kwargs['nodata'])
    # TODO fix this
    null_value = '-999'

    # # Assign timestamp_meaning
    # timestamp_meaning = kwargs['timestamp_meaning']
    # TODO fix this
    timestamp_meaning = 'end'

    # ================================  VALIDATE STATION MODEL =======================================================
    # Validate station_model
    try:
        model_class = get_model(station_model)
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

    # =============================== PROCESS NEAD HEADER ===========================================================
    # Get NEAD header
    config_buffer, nead_config_parser = write_nead_config(config_path=nead_config, model=station_model,
                                                          stringnull=null_value, delimiter=',',
                                                          ts_meaning=timestamp_meaning)

    # Fill hash_lines with config_buffer lines prepended with '# '
    hash_lines = get_hashed_lines(config_buffer)

    # ===================================  WRITE NEAD ===========================================================
    # TODO fix this to read Pandas data frame data
    # TODO determine if data need to be processed: null values changed
    data_df = pd.read_csv('test_data.csv')
    # # Read csv data
    # with open('test_data.csv', 'r') as nead_data:
    #     data = nead_data.read()

    # Write nead_header into NEAD file
    with open(output_nead, 'w', newline='\n') as nead_header:
        for row in hash_lines:
            nead_header.write(row)

    # Append data to header
    with open(output_nead, 'a') as nead:
        #nead.write(data)
        data_df.to_csv(nead, index=False, line_terminator='\n')


if __name__ == '__write_nead__':
    write_nead()
