import configparser
import os
from pathlib import Path

from gcnet.util.constants import Columns

# Code to test locally
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")

# Setup logging
import logging

logging.basicConfig(
    filename=Path("gcnet/logs/csvvalidator.log"),
    format="%(asctime)s   %(filename)s: %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
)
validator_logger = logging.getLogger(__name__)
validator_logger.setLevel(logging.DEBUG)


def check_values(
    stations_config, key, value, section, minimum, maximum, row, csv_path, line_count
):

    # Log low and high values and omit '999' values that represent missing or previously filtered data
    if (
        float(value) < float(stations_config.get(section, minimum))
        or float(value) > float(stations_config.get(section, maximum))
        and not is_null(value)
    ):
        log_message = f"STATION INPUT FILE: {csv_path}  LINE COUNT: {line_count}   UNEXPECTED VALUE for {key}: {value}   {row}"
        validator_logger.info(log_message)

    return


def csv_validator(stations_config_path, row, csv_path, line_count):

    # Set relative path to stations config file
    stations_config_file = Path(stations_config_path)

    # Load stations configuration file and assign it to stations_config
    stations_config = configparser.ConfigParser()
    stations_config.read(stations_config_file)
    if len(stations_config.sections()) < 1:
        raise FileNotFoundError(f"Cannot read config file: {stations_config_path}")

    # Iterate through some keys in the row with max or min values and call check_values()
    check_dict = {
        "SWin": {"section": "DEFAULT", "minimum": "swmin", "maximum": "swmax"},
        "SWout": {"section": "DEFAULT", "minimum": "swmin", "maximum": "swmax"},
        "AirTC1": {"section": "DEFAULT", "minimum": "tcmin", "maximum": "tcmax"},
        "AirTC2": {"section": "DEFAULT", "minimum": "tcmin", "maximum": "tcmax"},
        "AirT1": {"section": "DEFAULT", "minimum": "hmpmin", "maximum": "hmpmax"},
        "AirT2": {"section": "DEFAULT", "minimum": "hmpmin", "maximum": "hmpmax"},
        "RH1": {"section": "DEFAULT", "minimum": "rhmin", "maximum": "rhmax"},
        "RH2": {"section": "DEFAULT", "minimum": "rhmin", "maximum": "rhmax"},
        "WS1": {"section": "DEFAULT", "minimum": "wmin", "maximum": "wmax"},
        "WS2": {"section": "DEFAULT", "minimum": "wmin", "maximum": "wmax"},
        "WD1": {"section": "DEFAULT", "minimum": "wdmin", "maximum": "wdmax"},
        "WD2": {"section": "DEFAULT", "minimum": "wdmin", "maximum": "wdmax"},
        "press": {"section": "DEFAULT", "minimum": "pmin", "maximum": "pmax"},
        "Sheight1": {"section": "DEFAULT", "minimum": "shmin", "maximum": "shmax"},
        "Sheight2": {"section": "DEFAULT", "minimum": "shmin", "maximum": "shmax"},
        "BattVolt": {"section": "DEFAULT", "minimum": "battmin", "maximum": "battmax"},
    }

    for key in row:
        if key in check_dict.keys():
            check_values(
                stations_config,
                key,
                row[key],
                check_dict[key]["section"],
                check_dict[key]["minimum"],
                check_dict[key]["maximum"],
                row,
                csv_path,
                line_count,
            )


def is_null(text):
    return text in ["999", "999.0", "999.00", "999.000", "999.0000", "-999", "NaN"]


# Function to check for null (i.e. '999) values near values in source .dat files
def csv_null_checker(rows_buffer, rows_before, rows_after, csv_path, line_count):

    if len(rows_buffer) > (rows_before + rows_after):

        current_row = rows_buffer[-(rows_after + 1)]
        for key, val in current_row.items():
            if not (is_null(val)) and key not in [
                Columns.TIMESTAMP_ISO.value,
                Columns.TIMESTAMP.value,
                Columns.YEAR.value,
                Columns.JULIANDAY.value,
                Columns.QUARTERDAY.value,
                Columns.HALFDAY.value,
                Columns.DAY.value,
                Columns.WEEK.value,
            ]:
                list_not_nulls = [1 for row in rows_buffer if not is_null(row[key])]
                if len(list_not_nulls) <= 1:
                    logger_message = f"STATION INPUT FILE: {csv_path}  LINE COUNT: {line_count-1}   UNEXPECTED VALUE for {key} (probably NULL):  {current_row}"
                    validator_logger.info(logger_message)
