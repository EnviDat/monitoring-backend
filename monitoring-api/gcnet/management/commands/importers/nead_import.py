import logging
from configparser import ConfigParser
from datetime import datetime
from pathlib import Path

import gcnet.management.commands.importers.helpers.import_date_helpers as h
from django.db import transaction
from gcnet.util.constants import Columns

log = logging.getLogger(__name__)


class NeadImporter:
    def import_nead(
        self, source, input_file, config, model_class, force=False, verbose=True
    ):

        nead_config = self.read_nead_header(source)
        if not nead_config:
            print(f"Nothing imported, cannot read NEAD config from file {input_file}")

        sep = nead_config.get("METADATA", "field_delimiter", fallback=",")
        null_value = nead_config.get("METADATA", "nodata", fallback="")
        header = nead_config.get("FIELDS", "fields").split(sep)

        # Write data in input_file into writer_no_duplicates with additional fields
        records_written = 0
        line_number = 0

        try:
            with transaction.atomic(using="gcnet"):
                for line in source:
                    # Skip header lines that start with '#'
                    if line.startswith("#") or (len(line.strip()) == 0):
                        continue

                    # Increment line_number
                    line_number += 1

                    # transform the line in a dictionary
                    row = h.dict_from_csv_line(line, header, sep=sep)

                    if not row:
                        error_msg = f"Line {line_number} should have {len(header)} columns as the header"
                        if force:
                            print(error_msg)
                        else:
                            raise ValueError(error_msg)

                    # Process row and add new calculated fields
                    line_clean = self._clean_nead_line(row, null_value)
                    # print(line_clean)

                    if line_clean[Columns.TIMESTAMP.value]:
                        # Check if record with identical timestamp already exists in database, otherwise write
                        # record to temporary csv file after checking for record with duplicate timestamp
                        try:
                            created = True
                            if force:
                                key_dict = {
                                    Columns.TIMESTAMP.value: line_clean[
                                        Columns.TIMESTAMP.value
                                    ],
                                    Columns.TIMESTAMP_ISO.value: line_clean[
                                        Columns.TIMESTAMP_ISO.value
                                    ],
                                }
                                obj, created = model_class.objects.get_or_create(
                                    **key_dict, defaults=line_clean
                                )
                            else:
                                model_class.objects.create(**line_clean)
                            if created:
                                records_written += 1
                        except Exception as e:
                            raise e

            # Log import message
            log.info(
                "{} successfully imported, {} lines read, {} new record(s) written in {}".format(
                    input_file, line_number, records_written, model_class
                )
            )
            if verbose:
                print(
                    "{} successfully imported, {} lines read, {} new record(s) written in {}".format(
                        input_file, line_number, records_written, model_class
                    )
                )

        except Exception as e:
            records_written = 0
            print(f"Nothing imported, ROLLING BACK: exception ({type(e)}):{e}")

        return str(records_written)

    def read_nead_header(self, source):
        config_lines = []
        for line in source:
            # Skip header lines that start with '#'
            if line.startswith("#") and (line.find("[DATA]") < 0):
                config_lines += [line[1:].strip()]
            elif len(line.strip()) == 0:
                continue
            else:
                break

        if config_lines:
            nead_config_text = "\n".join(config_lines[1:])
            nead_config = ConfigParser(allow_no_value=True)
            nead_config.read_string(nead_config_text)
            return nead_config
        return None

    def _clean_nead_line(self, row, null_value):

        iso_date = datetime.fromisoformat(row["timestamp"])
        row = {
            Columns.TIMESTAMP_ISO.value: iso_date,
            Columns.TIMESTAMP.value: h.get_linux_timestamp(iso_date),
            Columns.YEAR.value: iso_date.year,
            Columns.JULIANDAY.value: h.get_julian_day(row["timestamp"]),
            Columns.QUARTERDAY.value: h.get_quarter_day(iso_date),
            Columns.HALFDAY.value: h.get_half_day(iso_date),
            Columns.DAY.value: h.get_year_day(iso_date),
            Columns.WEEK.value: h.get_year_week(iso_date),
            Columns.SWIN.value: row["ISWR"],
            Columns.SWOUT.value: row["OSWR"],
            Columns.NETRAD.value: row["NSWR"],
            Columns.AIRTEMP1.value: row["TA1"],
            Columns.AIRTEMP2.value: row["TA2"],
            Columns.AIRTEMP_CS500AIR1.value: row["TA3"],
            Columns.AIRTEMP_CS500AIR2.value: row["TA4"],
            Columns.RH1.value: row["RH1"],
            Columns.RH2.value: row["RH2"],
            Columns.WINDSPEED1.value: row["VW1"],
            Columns.WINDSPEED2.value: row["VW2"],
            Columns.WINDDIR1.value: row["DW1"],
            Columns.WINDDIR2.value: row["DW2"],
            Columns.PRESSURE.value: row["P"],
            Columns.SH1.value: row["HS1"],
            Columns.SH2.value: row["HS2"],
            Columns.BATTVOLT.value: row["V"],
            Columns.SWIN_MAX.value: row["ISWR_max"],
            Columns.SWOUT_MIN.value: row["OSWR_min"],
            Columns.NETRAD_MAX.value: row["NSWR_max"],
            Columns.AIRTEMP1_MAX.value: row["TA1_max"],
            Columns.AIRTEMP2_MAX.value: row["TA2_max"],
            Columns.AIRTEMP1_MIN.value: row["TA1_min"],
            Columns.AIRTEMP2_MIN.value: row["TA2_min"],
            Columns.WINDSPEED_U1_MAX.value: row["VW1_max"],
            Columns.WINDSPEED_U2_MAX.value: row["VW2_max"],
            Columns.WINDSPEED_U1_STDEV.value: row["VW1_stdev"],
            Columns.WINDSPEED_U2_STDEV.value: row["VW2_stdev"],
            Columns.REFTEMP.value: row["TA5"],
        }

        for k, v in row.items():
            if v == null_value:
                row[k] = None
        return row
