from django.utils.timezone import make_aware
from django.db import transaction

from pathlib import Path

from gcnet.management.commands.importers.helpers.csvvalidator import csv_validator, csv_null_checker, is_null
from gcnet.management.commands.importers.helpers.import_date_helpers import dict_from_csv_line
from gcnet.util.helpers import quarter_day, half_day, year_day, year_week, gcnet_utc_timestamp, gcnet_utc_datetime
from gcnet.util.constants import Columns

# Setup logging
import logging

logging.basicConfig(filename=Path('gcnet/logs/csv_import.log'), format='%(asctime)s   %(filename)s: %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class CsvImporter:

    DEFAULT_HEADER = ['StationID', 'Year', 'Doyd', 'SWin', 'SWout', 'NetRad', 'AirTC1', 'AirTC2', 'AirT1',
                      'AirT2', 'RH1', 'RH2', 'WS1', 'WS2', 'WD1', 'WD2', 'press', 'Sheight1', 'Sheight2',
                      'SnowT1', 'SnowT2', 'SnowT3', 'SnowT4', 'SnowT5', 'SnowT6', 'SnowT7', 'SnowT8', 'SnowT9',
                      'SnowT10', 'BattVolt', 'SWinMax', 'SWoutMin', 'NetRadMax', 'AirTC1Max', 'AirTC2Max',
                      'AirTC1Min', 'AirTC2Min', 'WS1Max', 'WS2Max', 'WS1Std', 'WS2Std', 'TempRef']

    def import_csv(self, source, input_file, config, model_class, force=False, header=DEFAULT_HEADER, verbose=True):

        # Write data in input_file into writer_no_duplicates with additional fields
        records_written = 0
        line_number = 0

        try:
            with transaction.atomic(using='gcnet'):
                for line in source:
                    # Skip header lines that start with '#'
                    if line.startswith('#') or (len(line.strip()) == 0):
                        continue

                    # Increment line_number
                    line_number += 1

                    # transform the line in a dictionary
                    row = dict_from_csv_line(line, header)

                    if not row:
                        error_msg = "Line {0} should have {1} columns as the header".format(line_number, len(header))
                        if force:
                            print(error_msg)
                        else:
                            raise ValueError(error_msg)

                    # Call csv_validator and log unexpected values
                    csv_validator(config, row, input_file, line_number)

                    # Check if doyd is greater than or equal to 367 or less than 1. Do not process row if it
                    # contains a doyd out of the normal range of days of a leap year (1 to 366).
                    if 367 > float(row['Doyd']) >= 1:
                        # Process row and add new calculated fields
                        line_clean = self._clean_csv_line(row)
                        # print(line_clean)

                        if line_clean[Columns.TIMESTAMP.value]:
                            # Check if record with identical timestamp already exists in database, otherwise write
                            # record to temporary csv file after checking for record with duplicate timestamp
                            created = True
                            if force:
                                key_dict = {Columns.TIMESTAMP.value: line_clean[Columns.TIMESTAMP.value]}
                                obj, created = model_class.objects.get_or_create(**key_dict, defaults=line_clean)
                            else:
                                model_class.objects.create(**line_clean)
                            if created:
                                records_written += 1

            # Log import message
            logger.info('{0} successfully imported, {1} lines read, {2} new record(s) written in {3}'
                        .format(input_file, line_number, records_written, model_class))
            if verbose:
                print('{0} successfully imported, {1} lines read, {2} new record(s) written in {3}'
                      .format(input_file, line_number, records_written, model_class))

        except Exception as e:
            records_written = 0
            print("Nothing imported, ROLLING BACK: exception ({1}):{0}".format(e, type(e)))

        return str(records_written)

    def logger_csv(self, source, input_file, output_file, config, header=DEFAULT_HEADER):

        # Write data in input_file into writer_no_duplicates with additional fields
        with open(output_file, 'w', newline='') as sink:

            sink.write(','.join(Columns.get_columns()) + '\n')

            rows_before = 24
            rows_after = 1
            rows_buffer = []
            written_timestamps = []

            line_number = 0

            for line in source:

                # Increment line_number
                line_number += 1

                # Skip header lines that start with '#'
                if line.startswith('#'):
                    continue

                row = dict_from_csv_line(line, header)

                # Call csv_validator and log unexpected values
                csv_validator(config, row, input_file, line_number)

                line_clean = self._clean_csv_line(row)

                if line_clean[Columns.TIMESTAMP_ISO.value] not in written_timestamps:

                    # keep timestamps length small
                    written_timestamps = written_timestamps[(-1) * min(len(written_timestamps), 1000):]
                    written_timestamps += [line_clean[Columns.TIMESTAMP_ISO.value]]

                    # slide the row buffer window
                    rows_buffer = rows_buffer[(-1) * min(len(rows_buffer), rows_before + rows_after):] + [line_clean]

                    # check null values before and after
                    if len(rows_buffer) > rows_after:
                        csv_null_checker(rows_buffer, rows_before, rows_after, input_file, line_number)
                        sink.write(','.join(["{0}".format(v) for v in rows_buffer[-(1 + rows_after)].values()]) + '\n')
            # save the last line #TODO: Depending on rows after
            sink.write(','.join(["{0}".format(v) for v in rows_buffer[-1].values()]) + '\n')

    def _clean_csv_line(self, row):
        row = {Columns.TIMESTAMP_ISO.value: make_aware(gcnet_utc_datetime(row['Year'], row['Doyd'])),
               Columns.TIMESTAMP.value: gcnet_utc_timestamp(row['Year'], row['Doyd']),
               Columns.YEAR.value: row['Year'],
               Columns.JULIANDAY.value: row['Doyd'],
               Columns.QUARTERDAY.value: quarter_day(row['Doyd']),
               Columns.HALFDAY.value: half_day(row['Doyd']),
               Columns.DAY.value: year_day(row['Year'], row['Doyd']),
               Columns.WEEK.value: year_week(row['Year'], row['Doyd']),
               Columns.SWIN.value: row['SWin'], Columns.SWOUT.value: row['SWout'],
               Columns.NETRAD.value: row['NetRad'],
               Columns.AIRTEMP1.value: row['AirTC1'], Columns.AIRTEMP2.value: row['AirTC2'],
               Columns.AIRTEMP_CS500AIR1.value: row['AirT1'],
               Columns.AIRTEMP_CS500AIR2.value: row['AirT2'],
               Columns.RH1.value: row['RH1'], Columns.RH2.value: row['RH2'],
               Columns.WINDSPEED1.value: row['WS1'], Columns.WINDSPEED2.value: row['WS2'],
               Columns.WINDDIR1.value: row['WD1'], Columns.WINDDIR2.value: row['WD2'],
               Columns.PRESSURE.value: row['press'],
               Columns.SH1.value: row['Sheight1'], Columns.SH2.value: row['Sheight2'],
               Columns.BATTVOLT.value: row['BattVolt'], Columns.SWIN_MAX.value: row['SWinMax'],
               Columns.SWOUT_MIN.value: row['SWoutMin'], Columns.NETRAD_MAX.value: row['NetRadMax'],
               Columns.AIRTEMP1_MAX.value: row['AirTC1Max'], Columns.AIRTEMP2_MAX.value: row['AirTC2Max'],
               Columns.AIRTEMP1_MIN.value: row['AirTC1Min'], Columns.AIRTEMP2_MIN.value: row['AirTC2Min'],
               Columns.WINDSPEED_U1_MAX.value: row['WS1Max'],
               Columns.WINDSPEED_U2_MAX.value: row['WS2Max'],
               Columns.WINDSPEED_U1_STDEV.value: row['WS1Std'],
               Columns.WINDSPEED_U2_STDEV.value: row['WS2Std'],
               Columns.REFTEMP.value: row['TempRef']
               }
        for k, v in row.items():
            if is_null(v):
                row[k] = None
        return row
