from io import StringIO
import configparser
from pathlib import Path
import pandas as pd


def read_config(config_path: str):
    config_file = Path(config_path)

    # Load configuration file
    config = configparser.RawConfigParser(inline_comment_prefixes='#', allow_no_value=True)
    config.read(config_file)

    if len(config.sections()) < 1:
        print("Invalid config file, missing sections")
        return None

    return config


# Fill hash_lines with config lines prepended with '# '
def get_hashed_lines(config):
    hash_lines = []
    for line in config.replace('\r\n', '\n').split('\n'):
        line = '# ' + line + '\n'
        hash_lines.append(line)
    return hash_lines


def write_nead(data_frame, nead_header, output_name):

    # Assign nead_output to output_name with .csv extension
    nead_output = '{0}.csv'.format(output_name)

    # Read nead_header into nead_config
    nead_config = read_config(nead_header)

    # Assign fields from nead_header 'fields'
    fields = nead_config.get('FIELDS', 'fields')
    fields_list = fields.split(',')

    # Dynamically write NEAD header into buffer
    buffer = StringIO()
    nead_config.write(buffer)

    # Assign hash_lines with nead_config lines prepended with '# '
    hash_lines = get_hashed_lines(buffer.getvalue())

    # Write hash_lines into nead_header
    with open(nead_output, 'w', newline='\n') as nead_header:
        for row in hash_lines:
            nead_header.write(row)

    # Append data to header
    with open(nead_output, 'a') as nead:
        data_frame.to_csv(nead, index=False, header=False, columns=fields_list, line_terminator='\n')


# =============================== TESTS =====================================================================
data_df = pd.read_csv('test_data.csv')
write_nead(data_df, 'gcnet/config/nead_header.ini', 'test_name')

