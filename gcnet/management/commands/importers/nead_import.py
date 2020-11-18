from django.utils.timezone import make_aware
from django.db import DatabaseError, transaction
from datetime import datetime

from pathlib import Path
from configparser import ConfigParser

from gcnet.util.constants import Columns
import gcnet.management.commands.importers.import_helpers as h

# Setup logging
import logging

logging.basicConfig(filename=Path('gcnet/logs/nead_import.log'), format='%(asctime)s   %(filename)s: %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class NeadImporter:

    def import_nead(self, source, input_file, config, model_class, force=False, verbose=True):

        nead_config = self.read_nead_header(source)
        if not nead_config:
            print("Nothing imported, cannot read NEAD config from file {0}".format(input_file))

        sep = nead_config.get('METADATA', 'field_delimiter')
        header = nead_config.get('FIELDS', 'fields').split(',')

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
                    row = h.dict_from_csv_line(line, header, sep=sep)

                    if not row:
                        error_msg = "Line {0} should have {1} columns as the header".format(line_number, len(header))
                        if force:
                            print(error_msg)
                        else:
                            raise ValueError(error_msg)

                    # Process row and add new calculated fields
                    line_clean = self._clean_nead_line(row)
                    # print(line_clean)

                    if line_clean[Columns.TIMESTAMP.value]:
                        # Check if record with identical timestamp already exists in database, otherwise write
                        # record to temporary csv file after checking for record with duplicate timestamp
                        try:
                            created = True
                            if force:
                                obj, created = model_class.objects.get_or_create(**line_clean)
                            else:
                                model_class.objects.create(**line_clean)
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

    def read_nead_header(self, source):
        config_lines = []
        for line in source:
            # Skip header lines that start with '#'
            if line.startswith('#') and (line.find('[DATA]') < 0):
                config_lines += [line[1:].strip()]
            else:
                break

        if config_lines:
            nead_config_text = u'\n'.join(config_lines[1:])
            nead_config = ConfigParser(allow_no_value=True)
            nead_config.read_string(nead_config_text)
            return nead_config
        return None

    def _clean_nead_line(self, row):

        iso_date = datetime.fromisoformat(row['timestamp'])
        return {Columns.TIMESTAMP_ISO.value: iso_date,

                Columns.TIMESTAMP.value: iso_date.strftime("%s"),
                Columns.YEAR.value: iso_date.year,
                Columns.JULIANDAY.value: h.get_julian_day(row['timestamp']),
                Columns.QUARTERDAY.value: h.get_quarter_day(iso_date),
                Columns.HALFDAY.value: h.get_half_day(iso_date),
                Columns.DAY.value: h.get_year_day(iso_date),
                Columns.WEEK.value: h.get_year_week(iso_date),

                Columns.SWIN.value: row['ISWR'], Columns.SWOUT.value: row['OSWR'],
                Columns.NETRAD.value: row['NSWR'],
                Columns.AIRTEMP1.value: row['TA1'], Columns.AIRTEMP2.value: row['TA2'],
                Columns.AIRTEMP_CS500AIR1.value: row['TA3'],
                Columns.AIRTEMP_CS500AIR2.value: row['TA4'],
                Columns.RH1.value: row['RH1'], Columns.RH2.value: row['RH2'],
                Columns.WINDSPEED1.value: row['VW1'], Columns.WINDSPEED2.value: row['VW2'],
                Columns.WINDDIR1.value: row['DW1'], Columns.WINDDIR2.value: row['DW2'],
                Columns.PRESSURE.value: row['P'],
                Columns.SH1.value: row['HS1'], Columns.SH2.value: row['HS2'],
                Columns.BATTVOLT.value: row['V'], Columns.SWIN_MAX.value: row['ISWR_max'],
                Columns.SWOUT_MIN.value: row['OSWR_min'], Columns.NETRAD_MAX.value: row['NSWR_max'],
                Columns.AIRTEMP1_MAX.value: row['TA1_max'], Columns.AIRTEMP2_MAX.value: row['TA2_max'],
                Columns.AIRTEMP1_MIN.value: row['TA1_min'], Columns.AIRTEMP2_MIN.value: row['TA2_min'],
                Columns.WINDSPEED_U1_MAX.value: row['VW1_max'],
                Columns.WINDSPEED_U2_MAX.value: row['VW2_max'],
                Columns.WINDSPEED_U1_STDEV.value: row['VW1_stdev'],
                Columns.WINDSPEED_U2_STDEV.value: row['VW2_stdev'],
                Columns.REFTEMP.value: row['TA5']
                }
