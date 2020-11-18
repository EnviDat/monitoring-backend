# ======================================   EXAMPLE COMMANDS ==========================================================

# TEST model used to test data imports
# TEST:      python manage.py import_data -s test -c config/stations.ini -i gcnet/data/01c.dat -m test

# SWISS CAMP 10m:  Unable to run, this station has a different .dat file format with a header
# SWISS CAMP:      python manage.py import_data -s 01_swisscamp -c config/stations.ini -i gcnet/data/01c.dat -m swisscamp_01d
# CRAWFORD POINT:  python manage.py import_data -s 02_crawfordpoint -c config/stations.ini -i gcnet/data/02c.dat -m crawfordpoint_02d
# NASA-U:          python manage.py import_data -s 03_nasa_u -c config/stations.ini -i gcnet/data/03c.dat -m nasa_u_03d
# GITS:            python manage.py import_data -s 04_gits -c config/stations.ini -i gcnet/data/04c.dat -m gits_04d
# HUMBOLDT:        python manage.py import_data -s 05_humboldt -c /config/stations.ini -i gcnet/data/05c.dat -m humboldt_05d
# SUMMIT:          python manage.py import_data -s 06_summit -c config/stations.ini -i gcnet/data/06c.dat -m summit_06d
# TUNU-N:          python manage.py import_data -s 07_tunu_n -c config/stations.ini -i gcnet/data/07c.dat -m tunu_n_07d
# DYE-2:           python manage.py import_data -s 08_dye2 -c config/stations.ini -i gcnet/data/08c.dat -m dye2_08d
# JAR-1:           python manage.py import_data -s 09_jar1 -c config/stations.ini -i gcnet/data/09c.dat -m jar1_09d
# SADDLE:          python manage.py import_data -s 10_saddle -c config/stations.ini -i gcnet/data/10c.dat -m saddle_10d
# SOUTHDOME:       python manage.py import_data -s 11_southdome -c config/stations.ini -i gcnet/data/11c.dat -m southdome_11d
# NASA-EAST:       python manage.py import_data -s 12_nasa_east -c config/stations.ini -i gcnet/data/12c.dat -m nasa_east_12d
# NASA-SOUTHEAST:  python manage.py import_data -s 15_nasa_southeast -c config/stations.ini -i gcnet/data/15c.dat -m nasa_southeast_15d
# PETERMANN:       python manage.py import_data -s 22_petermann -c config/stations.ini -i gcnet/data/22c.dat -m petermann_22d
# NEEM:            python manage.py import_data -s 23_neem -c config/stations.ini -i gcnet/data/23c.dat -m neem_23d
# EAST-GRIP:       python manage.py import_data -s 24_east_grip -c config/stations.ini -i gcnet/data/24c.dat -m east_grip_24d

from pathlib import Path

from django.core.management.base import BaseCommand
from django.utils.timezone import make_aware
from django.db import DatabaseError, transaction

from .datvalidator import null_checker, is_null
from gcnet.helpers import quarter_day, half_day, year_day, year_week, gcnet_utc_timestamp, gcnet_utc_datetime
from gcnet.util.constants import Columns

# Setup logging
import logging

logging.basicConfig(filename=Path('gcnet/logs/dat_import.log'), format='%(asctime)s   %(filename)s: %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class DatImporter:
    DEFAULT_HEADER = ['StationID', 'Year', 'Doyd', 'SWin', 'SWout', 'NetRad', 'AirTC1', 'AirTC2', 'AirT1',
                      'AirT2', 'RH1', 'RH2', 'WS1', 'WS2', 'WD1', 'WD2', 'press', 'Sheight1', 'Sheight2',
                      'SnowT1', 'SnowT2', 'SnowT3', 'SnowT4', 'SnowT5', 'SnowT6', 'SnowT7', 'SnowT8', 'SnowT9',
                      'SnowT10', 'BattVolt', 'SWinMax', 'SWoutMin', 'NetRadMax', 'AirTC1Max', 'AirTC2Max',
                      'AirTC1Min', 'AirTC2Min', 'WS1Max', 'WS2Max', 'WS1Std', 'WS2Std', 'TempRef',
                      # This begins 10 extra columns in .dat files
                      'WS2m', 'WS10m', 'WindHeight1', 'WindHeight2', 'Albedo', 'Zenith',
                      'QC1', 'QC2', 'QC3', 'QC4'
                      ]

    def import_dat(self, source, input_file, config, model_class, force=False, header=DEFAULT_HEADER, verbose=True):

        # Write data in input_file into writer_no_duplicates with additional fields
        records_written = 0
        line_number = 0

        rows_before = 24
        rows_after = 1
        rows_buffer = []

        written_timestamps = []

        try:
            with transaction.atomic(using='gcnet'):
                for line in source:
                    # Skip header lines that start with '#'
                    if line.startswith('#'):
                        continue

                    # Increment line_number
                    line_number += 1

                    # transform the line in a dictionary
                    row = self._dict_from_dat_line(line, header)

                    if not row:
                        error_msg = "Line {0} should have {1} columns as the header".format(line_number, len(header))
                        if force:
                            print(error_msg)
                        else:
                            raise ValueError(error_msg)

                    # map line to the model fields
                    line_clean = self._clean_dat_line(row)

                    if line_clean[Columns.TIMESTAMP.value]:

                        if line_clean['timestamp'] not in written_timestamps:

                            # keep timestamps length small
                            written_timestamps = written_timestamps[(-1) * min(len(written_timestamps), 1000):]
                            written_timestamps += [line_clean['timestamp']]

                            # slide the row buffer window
                            rows_buffer = rows_buffer[(-1) * min(len(rows_buffer), rows_before + rows_after):] + [
                                line_clean]

                            # check values before and after
                            if len(rows_buffer) > rows_after:
                                null_checker(rows_buffer, rows_before, rows_after)

                                line_to_save = rows_buffer[-(1 + rows_after)]

                                # Check if record with identical timestamp already exists in database
                                try:
                                    created = True
                                    if force:
                                        obj, created = model_class.objects.get_or_create(**line_to_save)
                                    else:
                                        model_class.objects.create(**line_to_save)
                                    if created:
                                        records_written += 1
                                except Exception as e:
                                    raise e
                # save the last line #TODO: Depending on rows after
                try:
                    created = True
                    if force:
                        obj, created = model_class.objects.get_or_create(**rows_buffer[-1])
                    else:
                        model_class.objects.create(**rows_buffer[-1])
                    if created:
                        records_written += 1
                except Exception as e:
                    raise e

            # Log import message
            logger.info('{0} successfully imported, {1} lines read, {2} new record(s) written in {3}'
                        .format(input_file, line_number, records_written, model_class))
            if verbose:
                print('{0} successfully imported, {1} lines read, {2} new record(s) written in {3}'
                      .format(input_file, line_number, records_written, model_class))

        except Exception as e:
            print("Nothing imported, ROLLING BACK: exception ({1}):{0}".format(e, type(e)))

    def _dict_from_dat_line(self, line, header):

        line_array = [v for v in line.strip().split(' ') if len(v) > 0]

        if len(line_array) != len(header):
            return None

        return {header[i]: line_array[i] for i in range(len(line_array))}

    def _clean_dat_line(self, row):
        row = {Columns.TIMESTAMP_ISO.value: make_aware(gcnet_utc_datetime(row['Year'], row['Doyd'])),
               Columns.TIMESTAMP.value: gcnet_utc_timestamp(row['Year'], row['Doyd']),
               Columns.YEAR.value: row['Year'], Columns.JULIANDAY.value: row['Doyd'],
               Columns.QUARTERDAY.value: quarter_day(row['Doyd']), Columns.HALFDAY.value: half_day(row['Doyd']),
               Columns.DAY.value: year_day(row['Year'], row['Doyd']),
               Columns.WEEK.value: year_week(row['Year'], row['Doyd']),
               Columns.SWIN.value: row['SWin'], Columns.SWOUT.value: row['SWout'],
               Columns.NETRAD.value: row['NetRad'], Columns.AIRTEMP1.value: row['AirTC1'],
               Columns.AIRTEMP2.value: row['AirTC2'],
               Columns.AIRTEMP_CS500AIR1.value: row['AirT1'], Columns.AIRTEMP_CS500AIR2.value: row['AirT2'],
               Columns.RH1.value: row['RH1'], Columns.RH2.value: row['RH2'], Columns.WINDSPEED1.value: row['WS1'],
               Columns.WINDSPEED2.value: row['WS2'], Columns.WINDDIR1.value: row['WD1'],
               Columns.WINDDIR2.value: row['WD2'], Columns.PRESSURE.value: row['press'],
               Columns.SH1.value: row['Sheight1'],
               Columns.SH2.value: row['Sheight2'], Columns.BATTVOLT.value: row['BattVolt'],
               Columns.SWIN_MAX.value: row['SWinMax'],
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

