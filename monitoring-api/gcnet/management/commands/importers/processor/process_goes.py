#
# # GOES satellite data processing functions
#

import logging

import pandas

log = logging.getLogger(__name__)


def get_converted_line(line):
    """
    Support function to decode each line of the GOES data to the standard output.
    :param line: a line to be decoded
    :return: an array with the converted values for a line
    """

    # Get the station information and split the string into each character
    station = line[0:8]
    chain = list(line[38:176])

    # Initliaze empty list for the output array
    converted_line = [None] * 46

    # Find the minimum length of the string and either take it (if <= 46) or take 46 (number of output columns)
    chain_n = min(int(len(chain) / 3), 46)

    # Loop through each string in the vector
    for i in range(chain_n):

        converted_line[i] = 0
        SF = 1

        # Convert the bits
        A = ord(chain[3 * i]) & 15
        B = ord(chain[3 * i + 1]) & 63
        C = ord(chain[3 * i + 2]) & 63

        # Further conversion
        if ((A * 64) + B) >= 1008:
            converted_line[i] = (B - 48) * 64 + C + 9000
        else:
            if (A & 8) != 0:
                SF = -1
            if (A & 4) != 0:
                SF = SF * 0.01
            if (A & 2) != 0:
                SF = SF * 0.1
            if (A & 1) != 0:
                converted_line[i] = 4096
            converted_line[i] = (converted_line[i] + ((B & 63) * 64) + (C & 63)) * SF

    # Add a station to the list
    converted_line.insert(0, station)

    return converted_line


def decode_goes(file):
    """
    Translate the existing FORTRAN code to process the satellite transmitted data into array format.
    Developed and tested by V.Trotsiuk[volodymyr.trotsiuk@wsl.ch], 2021.11.24

    Updated by Rebecca Kurup Buchholz (WSL), 2022.02.08

    :param file: path to the Goes raw file
    :return: a Pandas DataFrame [N,47], where each row corresponds to one entry, and column to Station[1]
    and variables
    """

    log.debug(f"Decoding GOES raw data {file}...")

    with open(file, encoding="ASCII") as goes_input:

        # For the testing purposes we take only last X lines, later we will do the full
        # goes_lines = goes_input.readlines()[-100000:]

        goes_lines = goes_input.readlines()

        data_out = []

        for line in goes_lines:

            converted_line = get_converted_line(line)

            # Replace None values with 999
            conv_line = [999 if item is None else item for item in converted_line]

            data_out.append(conv_line)

    try:
        # Convert data to Pandas DataFrame
        df = pandas.DataFrame(data_out)
    except Exception as e:
        log.error(e)
        log.error("Failed to read GOES into dataframe")
        raise ValueError("Failed to read GOES into dataframe")

    log.debug(f"GOES file read and decoded successfully into dataframe")

    return df
