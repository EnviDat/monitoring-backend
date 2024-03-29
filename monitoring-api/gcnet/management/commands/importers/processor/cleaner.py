import configparser
import logging
from datetime import datetime
from pathlib import Path

import numpy as np
from gcnet.util.writer import Writer

log = logging.getLogger(__name__)


class Cleaner:
    def __init__(self, init_file_path: str, station_type: str, writer: Writer):
        self.init_file_path = init_file_path
        self.stations_config = self._get_config()
        self.no_data = float(self.stations_config.get("DEFAULT", "no_data"))
        self.station_type = station_type
        self.writer = writer

    def _get_config(self):
        # Set relative path to stations config file
        stations_config_file = Path(self.init_file_path)

        # Load stations configuration file and assign it to self.stations_config
        stations_config = configparser.ConfigParser()
        stations_config.read(stations_config_file)

        return stations_config

    # Function to filter values
    def _filter_values(self, unfiltered_values, sect, minimum, maximum):
        # Filter out low and high values
        array = unfiltered_values
        array[array < float(self.stations_config.get(sect, minimum))] = self.no_data
        array[array > float(self.stations_config.get(sect, maximum))] = self.no_data

        return array

    # Function to filter values with calibration factor
    def _filter_values_calibrate(
        self,
        unfiltered_values,
        sect,
        minimum,
        maximum,
        calibration,
        no_data_min,
        no_data_max,
    ):
        # Multiply values by calibration factor, filter out low and high values
        array = unfiltered_values * float(self.stations_config.get(sect, calibration))
        array[array < float(self.stations_config.get(sect, minimum))] = no_data_min
        array[array > float(self.stations_config.get(sect, maximum))] = no_data_max

        return array

        # Function to return current date number

    @staticmethod
    def _get_date_num():
        # Get current date
        today = datetime.now()
        day_of_year = (today - datetime(today.year, 1, 1)).days + 1
        current_year = today.year

        # Calculate fractional julian day
        current_julian_day = day_of_year + today.hour / 24

        current_date_num = current_year * 1e3 + current_julian_day

        return current_date_num


class ArgosCleaner(Cleaner):
    def __init__(self, init_file_path: str, writer: Writer):
        Cleaner.__init__(self, init_file_path, "ARGOS", writer)

    # Function to process ARGOS numpy array generated from a decoded csv file
    def clean(self, input_data: np.ndarray):

        # TODO test if input_data numpy array generates same outputs
        #  as numpy array created from Fortran generated .dat file

        # Assign constant for column index in input numpy array
        INPUT_STATION_ID_COL = 7

        # Assign constants for column indices and other constants used in station_array processing
        STATION_NO_DATA1 = -8190
        STATION_NO_DATA2 = 2080
        STATION_NUM_COL = 0
        STATION_YEAR_COL = 1
        STATION_JULIAN_DAY_COL = 2
        STATION_HOUR_COL = 3
        STATION_SWIN_COL = 4
        STATION_SWOUT_COL = 5
        STATION_SWNET_COL = 6
        STATION_TC1_COL = 7
        STATION_TC2_COL = 8
        STATION_HMP1_COL = 9
        STATION_HMP2_COL = 10
        STATION_RH1_COL = 11
        STATION_RH2_COL = 12
        STATION_WS1_COL = 13
        STATION_WS2_COL = 14
        STATION_WD1_COL = 15
        STATION_WD2_COL = 16
        STATION_PRESSURE_COL = 17
        STATION_SH1_COL = 18
        STATION_SH2_COL = 19
        STATION_VOLTS_COL = 30
        STATION_S_WINMAX_COL = 31
        STATION_S_WOUTMAX_COL = 32
        STATION_S_WNETMAX_COL = 33
        STATION_TC1MAX_COL = 34
        STATION_TC2MAX_COL = 35
        STATION_TC1MIN_COL = 36
        STATION_TC2MIN_COL = 37
        STATION_WS1MAX_COL = 38
        STATION_WS2MAX_COL = 39
        STATION_WS1STD_COL = 40
        STATION_WS2STD_COL = 41
        STATION_TREF_COL = 42

        # Assign other constants
        HOURS_IN_DAY = 24
        MAX_HUMIDITY = 100
        INITIALIZER_VAL = 999

        # Iterate through each station and write json and csv file
        for section in self.stations_config.sections():

            # Assign station config variables
            station_type = self.stations_config.get(section, "type")
            is_active = self.stations_config.get(section, "active")

            # Process Argos stations
            if station_type == "argos" and is_active == "True":

                # Assign station_id
                station_id = int(section)

                # Assign station_num
                station_num = int(self.stations_config.get(section, "station_num"))

                log.info(
                    f"ArgosCleaner: Cleaning {self.station_type} Station {station_num}..."
                )

                if input_data.size != 0:

                    # Assign station_data to data assciated with each station
                    station_data = np.array(
                        input_data[input_data[:, INPUT_STATION_ID_COL] == station_id, :]
                    )

                    if len(station_data) != 0:

                        # Assign station_array to array returns from get_station_array()
                        station_array = self.get_station_array(
                            station_data, station_num
                        )

                        # Filter and process station_array
                        # Assign variables used to create new array that will be used to write csv files and json files
                        if len(station_array) != 0:

                            # Assign no_data values to self.no_data
                            station_array[
                                station_array == STATION_NO_DATA1
                            ] = self.no_data
                            station_array[
                                station_array == STATION_NO_DATA2
                            ] = self.no_data

                            # Assign year to year data
                            year = station_array[:, STATION_YEAR_COL]

                            # Assign julian_day to julian day plus fractional julian day
                            julian_day = (
                                station_array[:, STATION_JULIAN_DAY_COL]
                                + station_array[:, STATION_HOUR_COL] / HOURS_IN_DAY
                            )

                            # Assign date_number to year * 1000 + julian_day
                            date_num = year * 1.0e3 + julian_day

                            # Assign raw_num to number of records before duplicate filtering
                            raw_num = int(len(date_num))

                            # Find only unique timestamps and their indices from date_num
                            unique_date_num_array, unique_date_num_indices = np.unique(
                                date_num, axis=0, return_index=True
                            )

                            # Reassign station_array to records with unique timestamps
                            station_array = station_array[unique_date_num_indices, :]

                            # Reassign year data
                            year = station_array[:, STATION_YEAR_COL]

                            # Reassign julian_day to julian day plus fractional julian day
                            julian_day = (
                                station_array[:, STATION_JULIAN_DAY_COL]
                                + station_array[:, STATION_HOUR_COL] / HOURS_IN_DAY
                            )

                            # Reassign date_number to year * 1000 + julian_day
                            date_num = year * 1.0e3 + julian_day

                            # Log how many records removed because of duplicate time stamps
                            if len(unique_date_num_indices) < raw_num:
                                duplicate_timestamps_num = raw_num - len(
                                    unique_date_num_indices
                                )
                                log.warning(
                                    f"ArgosCleaner: Removed {duplicate_timestamps_num} entries out of:"
                                    f" {raw_num} records from Station {station_num} "
                                    f"because of duplicate time tags"
                                )

                            # Assign unique_timestamp_indices to indices of a sort of unique datetime values along time
                            unique_timestamp_indices = np.argsort(unique_date_num_array)

                            # Crop data array to unique times
                            station_array = station_array[unique_timestamp_indices, :]
                            julian_day = julian_day[
                                unique_timestamp_indices
                            ]  # crop julian_day vector to unique times
                            year = year[unique_timestamp_indices]
                            date_num = date_num[
                                unique_timestamp_indices
                            ]  # leave only unique and sorted date_nums

                            # Assign station_number
                            station_number = station_array[:, STATION_NUM_COL]

                            # Assign and calibrate incoming shortwave
                            swin = self._filter_values_calibrate(
                                station_array[:, STATION_SWIN_COL],
                                section,
                                "swmin",
                                "swmax",
                                "swin",
                                self.no_data,
                                self.no_data,
                            )

                            # Assign and calibrate outgoing shortwave
                            swout = self._filter_values_calibrate(
                                station_array[:, STATION_SWOUT_COL],
                                section,
                                "swmin",
                                "swmax",
                                "swout",
                                self.no_data,
                                self.no_data,
                            )

                            # Assign and calibrate net shortwave, negative and positive values
                            # Different stations have different calibration coefficients according to QC code
                            swnet = INITIALIZER_VAL * np.ones(np.size(swout, 0))
                            swnet[
                                station_array[:, STATION_SWNET_COL] >= 0
                            ] = station_array[
                                station_array[:, STATION_SWNET_COL] >= 0,
                                STATION_SWNET_COL,
                            ] * float(
                                self.stations_config.get(section, "swnet_pos")
                            )
                            swnet[
                                station_array[:, STATION_SWNET_COL] < 0
                            ] = station_array[
                                station_array[:, STATION_SWNET_COL] < 0,
                                STATION_SWNET_COL,
                            ] * float(
                                self.stations_config.get(section, "swnet_neg")
                            )

                            # Filter low net shortwave
                            swnet[
                                swnet
                                < -float(self.stations_config.get(section, "swmax"))
                            ] = self.no_data

                            # Filter high net shortwave
                            swnet[
                                swnet
                                > float(self.stations_config.get(section, "swmax"))
                            ] = self.no_data

                            # Filter thermocouple 1
                            tc1 = self._filter_values(
                                station_array[:, STATION_TC1_COL],
                                section,
                                "tcmin",
                                "tcmax",
                            )

                            # Filter thermocouple 2
                            tc2 = self._filter_values(
                                station_array[:, STATION_TC2_COL],
                                section,
                                "tcmin",
                                "tcmax",
                            )

                            # Filter hmp1 temp
                            hmp1 = self._filter_values(
                                station_array[:, STATION_HMP1_COL],
                                section,
                                "hmpmin",
                                "hmpmax",
                            )

                            # Filter hmp2 temp
                            hmp2 = self._filter_values(
                                station_array[:, STATION_HMP2_COL],
                                section,
                                "hmpmin",
                                "hmpmax",
                            )

                            # Assign and calibrate relative humidity 1
                            rh1 = station_array[:, STATION_RH1_COL]
                            rh1[
                                rh1 < float(self.stations_config.get(section, "rhmin"))
                            ] = self.no_data  # filter low
                            rh1[
                                rh1 > float(self.stations_config.get(section, "rhmax"))
                            ] = self.no_data  # filter high
                            # Assign values greater than MAX_HUMIDITY and less than rhmax to MAX_HUMIDITY
                            rh1[
                                (rh1 > MAX_HUMIDITY)
                                & (
                                    rh1
                                    < float(self.stations_config.get(section, "rhmax"))
                                )
                            ] = MAX_HUMIDITY

                            # Assign and calibrate relative humidity 2
                            rh2 = station_array[:, STATION_RH2_COL]
                            rh2[
                                rh2 < float(self.stations_config.get(section, "rhmin"))
                            ] = self.no_data  # filter low
                            rh2[
                                rh2 > float(self.stations_config.get(section, "rhmax"))
                            ] = self.no_data  # filter high
                            # Assign values greater than MAX_HUMIDITY and less than rhmax to MAX_HUMIDITY
                            rh2[
                                (rh2 > MAX_HUMIDITY)
                                & (
                                    rh2
                                    < float(self.stations_config.get(section, "rhmax"))
                                )
                            ] = MAX_HUMIDITY

                            # Filter wind speed 1
                            ws1 = self._filter_values(
                                station_array[:, STATION_WS1_COL],
                                section,
                                "wmin",
                                "wmax",
                            )

                            # Filter wind speed 2
                            ws2 = self._filter_values(
                                station_array[:, STATION_WS2_COL],
                                section,
                                "wmin",
                                "wmax",
                            )

                            # Filter wind direction 1
                            wd1 = self._filter_values(
                                station_array[:, STATION_WD1_COL],
                                section,
                                "wdmin",
                                "wdmax",
                            )

                            # Filter wind direction 2
                            wd2 = self._filter_values(
                                station_array[:, STATION_WD2_COL],
                                section,
                                "wdmin",
                                "wdmax",
                            )

                            # Assign and calibrate barometric pressure
                            pres = station_array[:, STATION_PRESSURE_COL] + float(
                                self.stations_config.get(section, "pressure_offset")
                            )
                            pres[
                                pres < float(self.stations_config.get(section, "pmin"))
                            ] = self.no_data  # filter low
                            pres[
                                pres > float(self.stations_config.get(section, "pmax"))
                            ] = self.no_data  # filter low
                            pres_diff = np.diff(
                                pres
                            )  # Find difference of subsequent pressure measurements
                            hr_diff = (
                                np.diff(julian_day) * 24.0
                            )  # Time difference in hours
                            mb_per_hr = np.absolute(
                                np.divide(
                                    pres_diff,
                                    hr_diff,
                                    out=np.zeros_like(pres_diff),
                                    where=hr_diff != 0,
                                )
                            )
                            press_jumps = np.argwhere(
                                mb_per_hr > 10
                            )  # Find jumps > 10mb/hr (quite unnatural)
                            pres[
                                press_jumps + 1
                            ] = self.no_data  # Eliminate these single point jumps

                            # Filter height above snow 1
                            sh1 = self._filter_values(
                                station_array[:, STATION_SH1_COL],
                                section,
                                "shmin",
                                "shmax",
                            )

                            # Filter height above snow 2
                            sh2 = self._filter_values(
                                station_array[:, STATION_SH2_COL],
                                section,
                                "shmin",
                                "shmax",
                            )

                            # 10m snow temperature (many of these are non functional or not connected)
                            snow_temp10 = station_array[:, 20:30]

                            # Filter battery voltage
                            volts = self._filter_values(
                                station_array[:, STATION_VOLTS_COL],
                                section,
                                "battmin",
                                "battmax",
                            )

                            s_winmax = self._filter_values_calibrate(
                                station_array[:, STATION_S_WINMAX_COL],
                                section,
                                "swmin",
                                "swmax",
                                "swin",
                                self.no_data,
                                self.no_data,
                            )

                            s_woutmax = self._filter_values_calibrate(
                                station_array[:, STATION_S_WOUTMAX_COL],
                                section,
                                "swmin",
                                "swmax",
                                "swout",
                                0.00,
                                self.no_data,
                            )

                            # Assign and calibrate net radiation max
                            s_wnetmax = INITIALIZER_VAL * np.ones_like(s_woutmax)
                            s_wnetmax[
                                station_array[:, STATION_S_WNETMAX_COL] >= 0
                            ] = station_array[
                                station_array[:, STATION_S_WNETMAX_COL] >= 0,
                                STATION_S_WNETMAX_COL,
                            ] * float(
                                self.stations_config.get(section, "swnet_pos")
                            )
                            s_wnetmax[
                                station_array[:, STATION_S_WNETMAX_COL] < 0
                            ] = station_array[
                                station_array[:, STATION_S_WNETMAX_COL] < 0,
                                STATION_S_WNETMAX_COL,
                            ] * float(
                                self.stations_config.get(section, "swnet_neg")
                            )
                            # Filter low
                            s_wnetmax[
                                s_wnetmax
                                < -(float(self.stations_config.get(section, "swmax")))
                            ] = self.no_data
                            # Filter high
                            s_wnetmax[
                                s_wnetmax
                                > float(self.stations_config.get(section, "swmax"))
                            ] = self.no_data

                            # Filter other measurements
                            tc1max = self._filter_values(
                                station_array[:, STATION_TC1MAX_COL],
                                section,
                                "tcmin",
                                "tcmax",
                            )

                            tc2max = self._filter_values(
                                station_array[:, STATION_TC2MAX_COL],
                                section,
                                "tcmin",
                                "tcmax",
                            )

                            tc1min = self._filter_values(
                                station_array[:, STATION_TC1MIN_COL],
                                section,
                                "tcmin",
                                "tcmax",
                            )

                            tc2min = self._filter_values(
                                station_array[:, STATION_TC2MIN_COL],
                                section,
                                "tcmin",
                                "tcmax",
                            )

                            # Assign statistics
                            ws1max = station_array[:, STATION_WS1MAX_COL]
                            ws2max = station_array[:, STATION_WS2MAX_COL]
                            ws1std = station_array[:, STATION_WS1STD_COL]
                            ws2std = station_array[:, STATION_WS2STD_COL]
                            tref = station_array[:, STATION_TREF_COL]

                            # Note this code does not currently calculate the 2 and 10 m winds and albedo,
                            # so these are columns 1-42 of the Level C data
                            # Assemble data into final level C standard form
                            wdata = np.column_stack(
                                (
                                    station_number,
                                    year,
                                    julian_day,
                                    swin,
                                    swout,
                                    swnet,
                                    tc1,
                                    tc2,
                                    hmp1,
                                    hmp2,
                                    rh1,
                                    rh2,
                                    ws1,
                                    ws2,
                                    wd1,
                                    wd2,
                                    pres,
                                    sh1,
                                    sh2,
                                    snow_temp10,
                                    volts,
                                    s_winmax,
                                    s_woutmax,
                                    s_wnetmax,
                                    tc1max,
                                    tc2max,
                                    tc1min,
                                    tc2min,
                                    ws1max,
                                    ws2max,
                                    ws1std,
                                    ws2std,
                                    tref,
                                )
                            )

                            # Get current date number
                            current_date_num = self._get_date_num()

                            # Only take entries in the past
                            wdata = wdata[date_num < current_date_num, :]
                            future_reports_num = len(
                                np.argwhere(date_num > current_date_num)
                            )

                            if future_reports_num > 0:
                                log.warning(
                                    f"ArgosCleaner: Warning: Removed {str(future_reports_num)} entries out "
                                    f"of: {str(len(wdata[:, 1]) + future_reports_num)} records from station "
                                    f"ID: {str(station_id)} Reason: time tags in future"
                                )

                            # Call write_csv function to write csv file with processed data
                            self.writer.write_csv(
                                wdata, station_num, year, julian_day, date_num
                            )

                            # Call write_json function to write json long-term and short-term files with processed data
                            self.writer.write_json(wdata, station_num, self.no_data)

                        # Else station_array is empty after removing bad dates
                        else:
                            log.warning(
                                f"\t{self.station_type} Station #{station_num} does not have usable data"
                            )

                else:
                    log.warning(
                        f"\t{self.station_type} Station #{station_num} does not have usable data"
                    )

    # Function returns station_array which is the array for the data from each station
    # created from the combined first and second parts of the input table
    @staticmethod
    def get_station_array(station_data, station_num):

        # Assign constants for column indices in input numpy array
        INPUT_YEAR1_COL = 0
        INPUT_STATION_NUM_COL = 8
        INPUT_YEAR2_COL = 9
        INPUT_JULIAN_DAY_COL = 10
        INPUT_WIND_DIRECTION_COL = 9

        # Assign constants for column indices and other constants in combined_array
        COMBINED_YEAR_COL = 1
        COMBINED_YEAR_MIN = 1990
        COMBINED_YEAR_MAX = 2050
        COMBINED_JULIAN_DAY_COL = 2

        # Assign other constants
        MAX_DAYS_YEAR = 367
        MAX_DEGREES_WIND = 360
        INITIALIZER_VAL = 999

        # Assign unique_array to unique_rows after INPUT_STATION_NUM_COL
        # Assign unique_indices to indices of unique rows after INPUT_STATION_NUM_COL
        # because data may repeat with different time signature
        unique_array, unique_indices = np.unique(
            station_data[:, INPUT_STATION_NUM_COL:], axis=0, return_index=True
        )

        # Assign station_data to station_data sorted by unique_indcies
        station_data = station_data[np.sort(unique_indices), :]

        # Assign table_1_indices to indices of rows that are the first part of the two part table
        # and have integer Julian day (records with decimal julian day are erroneous)
        # and have a realistic Julian day (positive and less than 367 day, leap year will have 366 days)
        table_1_indices = np.argwhere(
            (station_data[:, INPUT_YEAR1_COL] == station_data[:, INPUT_YEAR2_COL])
            & (
                np.ceil(station_data[:, INPUT_JULIAN_DAY_COL])
                == np.floor(station_data[:, INPUT_JULIAN_DAY_COL])
            )
            & (station_data[:, INPUT_JULIAN_DAY_COL] > 0)
            & (station_data[:, INPUT_JULIAN_DAY_COL] < MAX_DAYS_YEAR)
        )

        # Assign table_2_indices to indices of rows that are the second part of the two part table
        # column 9 of 2nd table is wind direction, realistic values will be less than 360 degrees
        table_2_indices = np.argwhere(
            (
                station_data[:, INPUT_YEAR1_COL]
                != station_data[:, INPUT_WIND_DIRECTION_COL]
            )
            & (station_data[:, INPUT_WIND_DIRECTION_COL] <= MAX_DEGREES_WIND)
        )

        # Assign table_2_indices_last_item to last item in table_2_indices
        table_2_indices_last_item = table_2_indices[-1:]

        # Make sure last record in table 1 has a second piece of the table
        table_1_indices = table_1_indices[table_1_indices < table_2_indices_last_item]

        # Assign num_records to length of table_1_indices
        num_records = len(table_1_indices)

        # Assign combined_array as an array that will be used to
        # combine data from table 1 and table 2, inialize all values as INITIALIZER_VAL
        combined_array = np.ones((num_records, 43)) * INITIALIZER_VAL

        # Assign combined_array_columns to columns to be used in combined_array
        combined_array_columns = np.concatenate(
            (
                np.arange(0, 20),
                np.arange(30, 33),
                np.arange(34, 38),
                np.array([38]),
                np.array([39]),
            )
        )

        # Assign table_1_columns to columns in table 1 raw
        table_1_columns = np.concatenate(
            (np.array([0]), np.array([10]), np.array([3]), np.arange(12, 23))
        )

        # Assign table_2_columns to columns in table 2 raw
        table_2_columns = np.concatenate(
            (np.arange(9, 14), np.array([22]), np.arange(14, 22))
        )

        # Loop through records
        for j in range(num_records):
            # Find second table parts occurring after associated first part
            table_2_current_indices = np.argwhere(
                station_data[table_1_indices[j] :, 0]
                != station_data[table_1_indices[j] :, 9]
            )

            table_1_index = table_1_indices[j]

            # Assign table_2_index to the closest table 2 line
            table_2_index = (
                table_1_indices[j] + table_2_current_indices[INPUT_YEAR1_COL]
            )

            # Combine corresponding parts of table 1 and table 2 into an array within combined_array
            combined_array[j, combined_array_columns] = np.concatenate(
                (
                    np.array([station_num]),
                    station_data[table_1_index, table_1_columns],
                    station_data[table_2_index, table_2_columns],
                )
            )

        # Assign station_array to combined_array filtered for realistic years and Julian days
        station_array = combined_array[
            (combined_array[:, COMBINED_YEAR_COL] > COMBINED_YEAR_MIN)
            & (combined_array[:, COMBINED_YEAR_COL] < COMBINED_YEAR_MAX)
            & (combined_array[:, COMBINED_JULIAN_DAY_COL] >= 0)
            & (combined_array[:, COMBINED_JULIAN_DAY_COL] < MAX_DAYS_YEAR),
            :,
        ]

        return station_array


class GoesCleaner(Cleaner):
    def __init__(self, init_file_path: str, writer: Writer):
        Cleaner.__init__(self, init_file_path, "GOES", writer)

    def clean(self, input_data: np.ndarray):

        # Assign constant for column index in input numpy array
        INPUT_STATION_NUM_COL = 1

        # Assign constants for column indices and other constants used in station_array processing
        STATION_YEAR_COL = 2
        STATION_JULIAN_DAY_COL = 3
        STATION_YEAR_MIN = 1990
        STATION_YEAR_MAX = 2050

        # Assign constants for column indices used in gdata processing
        GDATA_STATION_NUM_COL = 0
        GDATA_YEAR_COL = 1
        GDATA_JULIAN_DAY_COL = 2
        GDATA_HOUR_COL = 3
        GDATA_SWIN_COL = 4
        GDATA_SWOUT_COL = 5
        GDATA_SWNET_COL = 6
        GDATA_TC1_COL = 7
        GDATA_TC2_COL = 8
        GDATA_HMP1_COL = 9
        GDATA_HMP2_COL = 10
        GDATA_RH1_COL = 11
        GDATA_RH2_COL = 12
        GDATA_WS1_COL = 13
        GDATA_WS2_COL = 14
        GDATA_WD1_COL = 15
        GDATA_WD2_COL = 16
        GDATA_PRES_COL = 17
        GDATA_SH1_COL = 18
        GDATA_SH2_COL = 19
        GDATA_VOLTS_COL = 30
        GDATA_S_WINMAX_COL = 31
        GDATA_S_WOUTMAX_COL = 32
        GDATA_S_WNETMAX_COL = 33
        GDATA_TC1MAX_COL = 34
        GDATA_TC2MAX_COL = 35
        GDATA_TC1MIN_COL = 36
        GDATA_TC2MIN_COL = 37
        GDATA_WS1MAX_COL = 38
        GDATA_WS2MAX_COL = 39
        GDATA_WS1STD_COL = 40
        GDATA_WS2STD_COL = 41
        GDATA_TREF_COL = 42

        # Assign other constants
        INITIALIZER_VAL = 999
        NO_DATA1 = -8190
        NO_DATA2 = 2080
        HOURS_IN_DAY = 24
        MAX_HUMIDITY = 100

        # Iterate through each station and write json and csv file
        for section in self.stations_config.sections():

            # Assign station config values
            station_type = self.stations_config.get(section, "type")
            is_active = self.stations_config.get(section, "active")

            # Process Goes stations
            if station_type == "goes" and is_active == "True":

                # Assign station ID
                station_id = section

                # Assign station number
                station_num = int(self.stations_config.get(section, "station_num"))

                log.info(
                    f"GoesCleaner: Cleaning {self.station_type} Station #{station_num}..."
                )

                if input_data.size > 0:

                    # Assign station_array to data associated with each station
                    station_array = np.array(
                        input_data[
                            input_data[:, INPUT_STATION_NUM_COL] == station_num, :
                        ]
                    )

                    log.info(
                        f"GoesCleaner: Data size {station_array.size} for Station #{station_num}..."
                    )

                    # Assign unique_array unique rows after column 5
                    # Assign unique_indices to indices of unique rows after column 5
                    # because data may repeat with different time signature
                    # TEST commenting out
                    # unique_array, unique_indices = np.unique(station_array[:, 5:], axis=0, return_index=True)
                    # station_array = station_array[np.sort(unique_indices), :]

                    # Assign station_array to station_array filtered for realistic years and Julian days,
                    # (positive and less than 367 JD, leap year will have 366 days)
                    station_array = station_array[
                        (station_array[:, STATION_YEAR_COL] > STATION_YEAR_MIN)
                        & (station_array[:, STATION_YEAR_COL] < STATION_YEAR_MAX)
                        & (station_array[:, STATION_JULIAN_DAY_COL] >= 0)
                        & (station_array[:, STATION_JULIAN_DAY_COL] < 367),
                        :,
                    ]

                    log.info(
                        f"GoesCleaner: Clean data size {station_array.size} for Station {station_num}..."
                    )
                    if station_array.size <= 0:
                        log.warning(
                            f"Skipping cleaning of {station_array.size} for Station #{station_num},"
                            f" NO DATA after cleaning"
                        )
                        continue

                    # Assign gdata to array returned by get_gdata_array(), arrays vary by station_num
                    gdata = self.get_gdata_array(station_num, station_array)

                    # Assign no_data values
                    gdata[gdata == NO_DATA1] = self.no_data
                    gdata[gdata == NO_DATA2] = self.no_data

                    # Assign year to year data
                    year = gdata[:, GDATA_YEAR_COL]

                    # Assign julian_day to julian day plus fractional hours
                    julian_day = (
                        gdata[:, GDATA_JULIAN_DAY_COL]
                        + gdata[:, GDATA_HOUR_COL] / HOURS_IN_DAY
                    )

                    # Assign date_num to year plus julian_day
                    date_num = year * 1e3 + julian_day

                    # Assign unique_date_num to unique time stamps
                    # Assign unique_date_num_indices to indicies of unique time stamps
                    # TEST comment out
                    # unique_date_num, unique_date_num_indices = np.unique(date_num, axis=0, return_index=True)
                    #
                    # # Reassign gdata values with unique time stamps
                    # gdata = gdata[unique_date_num_indices, :]

                    # Reassign year to years of unique rows only
                    year = gdata[:, GDATA_YEAR_COL]

                    # Reassign julian_day to julian day plus fractional hours of unique rows only
                    julian_day = (
                        gdata[:, GDATA_JULIAN_DAY_COL]
                        + gdata[:, GDATA_HOUR_COL] / HOURS_IN_DAY
                    )

                    # Ressign date_num to year plus julian_day of unique rows only
                    date_num = year * 1.0e3 + julian_day

                    # Log how many duplicate rows removed
                    # if len(unique_date_num_indices) < raw_num:
                    #     duplicates_num = raw_num - len(unique_date_num_indices)
                    #     log.warning(f'GoesCleaner: Removed {duplicates_num} entries out of {raw_num} records'
                    #                    f' Station {station_num} because of duplicate time tags')

                    # # Assign time_indices to indices that would sort unique rows along time
                    # time_indices = np.argsort(unique_date_num)
                    #
                    # # Crop gdata array to unique times
                    # gdata = gdata[time_indices, :]
                    #
                    # # Crop time related variables by time_indices
                    # julian_day = julian_day[time_indices]
                    # year = year[time_indices]
                    #
                    # # Leave only unique and sorted date_nums
                    # date_num = date_num[time_indices]

                    # Assign station_number to station numbers
                    station_number = gdata[:, GDATA_STATION_NUM_COL]

                    # ======== Assign scientific measurements ==========

                    # Assign swin
                    swin = self._filter_values_calibrate(
                        gdata[:, GDATA_SWIN_COL],
                        section,
                        "swmin",
                        "swmax",
                        "swin",
                        self.no_data,
                        self.no_data,
                    )

                    # Assign swout
                    swout = self._filter_values_calibrate(
                        gdata[:, GDATA_SWOUT_COL],
                        section,
                        "swmin",
                        "swmax",
                        "swout",
                        self.no_data,
                        self.no_data,
                    )

                    # Assign and calibrate net shortwave, negative and positive values
                    # Stations have different calibration coefficients according to QC code
                    swnet = INITIALIZER_VAL * np.ones(np.size(swout, 0))
                    swnet[gdata[:, GDATA_SWNET_COL] >= 0] = gdata[
                        gdata[:, GDATA_SWNET_COL] >= 0, GDATA_SWNET_COL
                    ] * float(self.stations_config.get(section, "swnet_pos"))
                    swnet[gdata[:, GDATA_SWNET_COL] < 0] = gdata[
                        gdata[:, GDATA_SWNET_COL] < 0, GDATA_SWNET_COL
                    ] * float(self.stations_config.get(section, "swnet_neg"))
                    swnet[
                        swnet < -(float(self.stations_config.get(section, "swmax")))
                    ] = self.no_data  # Filter low
                    swnet[
                        swnet > float(self.stations_config.get(section, "swmax"))
                    ] = self.no_data  # Filter high

                    # Assign and filter other values
                    tc1 = self._filter_values(
                        gdata[:, GDATA_TC1_COL], section, "tcmin", "tcmax"
                    )  # Thermocouple 1
                    tc2 = self._filter_values(
                        gdata[:, GDATA_TC2_COL], section, "tcmin", "tcmax"
                    )  # Thermocouple 2
                    hmp1 = self._filter_values(
                        gdata[:, GDATA_HMP1_COL], section, "hmpmin", "hmpmax"
                    )  # hmp1 temp
                    hmp2 = self._filter_values(
                        gdata[:, GDATA_HMP2_COL], section, "hmpmin", "hmpmax"
                    )  # hmp2 temp

                    # Assign relative humidity 1
                    rh1 = gdata[:, GDATA_RH1_COL]
                    rh1[
                        rh1 < float(self.stations_config.get(section, "rhmin"))
                    ] = self.no_data  # Filter low
                    rh1[
                        rh1 > float(self.stations_config.get(section, "rhmax"))
                    ] = self.no_data  # Filter high
                    # Assign values greater than MAX_HUMIDITY and less than rhmax to MAX_HUMIDITY
                    rh1[
                        (rh1 > MAX_HUMIDITY)
                        & (rh1 < float(self.stations_config.get(section, "rhmax")))
                    ] = MAX_HUMIDITY

                    # Assign relative humidity 2
                    rh2 = gdata[:, GDATA_RH2_COL]
                    rh2[
                        rh2 < float(self.stations_config.get(section, "rhmin"))
                    ] = self.no_data  # Filter low
                    rh2[
                        rh2 > float(self.stations_config.get(section, "rhmax"))
                    ] = self.no_data  # Filter high
                    # Assign values greater than MAX_HUMIDITY and less than rhmax to MAX_HUMIDITY
                    rh2[
                        (rh2 > MAX_HUMIDITY)
                        & (rh2 < float(self.stations_config.get(section, "rhmax")))
                    ] = MAX_HUMIDITY

                    # Assign and filter other values
                    ws1 = self._filter_values(
                        gdata[:, GDATA_WS1_COL], section, "wmin", "wmax"
                    )  # Wind speed 1
                    ws2 = self._filter_values(
                        gdata[:, GDATA_WS2_COL], section, "wmin", "wmax"
                    )  # Wind speed 2
                    wd1 = self._filter_values(
                        gdata[:, GDATA_WD1_COL], section, "wdmin", "wdmax"
                    )  # Wind direction 1
                    wd2 = self._filter_values(
                        gdata[:, GDATA_WD2_COL], section, "wdmin", "wdmax"
                    )  # Wind direction 2

                    # Assign  barometeric pressure
                    pres = gdata[:, GDATA_PRES_COL] + float(
                        self.stations_config.get(section, "pressure_offset")
                    )
                    pres[
                        pres < float(self.stations_config.get(section, "pmin"))
                    ] = self.no_data  # Filter low
                    pres[
                        pres > float(self.stations_config.get(section, "pmax"))
                    ] = self.no_data  # Filter high
                    pressure_difference = np.diff(
                        pres
                    )  # Find difference of subsequent pressure measurement
                    hour_difference = (
                        np.diff(julian_day) * 24.0
                    )  # Time difference in hours
                    mb_per_hr = np.absolute(
                        np.divide(
                            pressure_difference,
                            hour_difference,
                            out=np.zeros_like(pressure_difference),
                            where=hour_difference != 0,
                        )
                    )
                    pressure_jumps = np.argwhere(
                        mb_per_hr > 10
                    )  # Find jumps > 10mb/hr (quite unnatural)
                    pres[
                        pressure_jumps + 1
                    ] = self.no_data  # Eliminate these single point jumps

                    # Assign snow heights
                    sh1 = self._filter_values(
                        gdata[:, GDATA_SH1_COL], section, "shmin", "shmax"
                    )  # Height above snow 1
                    sh2 = self._filter_values(
                        gdata[:, GDATA_SH2_COL], section, "shmin", "shmax"
                    )  # Height above snow 2

                    # Assign 10m snow temperature (many of these are non functional or not connected)
                    snow_temp10 = gdata[:, 20:30]

                    # Assign battery voltage
                    volts = self._filter_values(
                        gdata[:, GDATA_VOLTS_COL], section, "battmin", "battmax"
                    )

                    # Assign and calibrate s_swinmax
                    s_winmax = self._filter_values_calibrate(
                        gdata[:, GDATA_S_WINMAX_COL],
                        section,
                        "swmin",
                        "swmax",
                        "swin",
                        self.no_data,
                        self.no_data,
                    )

                    # Assign and calibrate s_woutmax
                    s_woutmax = self._filter_values_calibrate(
                        gdata[:, GDATA_S_WOUTMAX_COL],
                        section,
                        "swmin",
                        "swmax",
                        "swout",
                        0.00,
                        self.no_data,
                    )

                    # Assign net radiation max
                    s_wnetmax = INITIALIZER_VAL * np.ones_like(s_woutmax)
                    s_wnetmax[gdata[:, GDATA_S_WNETMAX_COL] >= 0] = gdata[
                        gdata[:, GDATA_S_WNETMAX_COL] >= 0, GDATA_S_WNETMAX_COL
                    ] * float(self.stations_config.get(section, "swnet_pos"))
                    s_wnetmax[gdata[:, GDATA_S_WNETMAX_COL] < 0] = gdata[
                        gdata[:, GDATA_S_WNETMAX_COL] < 0, GDATA_S_WNETMAX_COL
                    ] * float(self.stations_config.get(section, "swnet_neg"))
                    # Filter low
                    s_wnetmax[
                        s_wnetmax < -(float(self.stations_config.get(section, "swmax")))
                    ] = self.no_data
                    # Filter high
                    s_wnetmax[
                        s_wnetmax > float(self.stations_config.get(section, "swmax"))
                    ] = self.no_data

                    # Assign and filter other values
                    tc1max = self._filter_values(
                        gdata[:, GDATA_TC1MAX_COL], section, "tcmin", "tcmax"
                    )
                    tc2max = self._filter_values(
                        gdata[:, GDATA_TC2MAX_COL], section, "tcmin", "tcmax"
                    )
                    tc1min = self._filter_values(
                        gdata[:, GDATA_TC1MIN_COL], section, "tcmin", "tcmax"
                    )
                    tc2min = self._filter_values(
                        gdata[:, GDATA_TC2MIN_COL], section, "tcmin", "tcmax"
                    )

                    # Assign other values
                    ws1max = gdata[:, GDATA_WS1MAX_COL]
                    ws2max = gdata[:, GDATA_WS2MAX_COL]
                    ws1std = gdata[:, GDATA_WS1STD_COL]
                    ws2std = gdata[:, GDATA_WS2STD_COL]
                    tref = gdata[:, GDATA_TREF_COL]

                    # Assign wdata, note this code does not currently calculate the 2 and 10 m winds and albedo,
                    # so these are columns 1-42 of the Level C data
                    # Assemble data into final level C standard form
                    wdata = np.column_stack(
                        (
                            station_number,
                            year,
                            julian_day,
                            swin,
                            swout,
                            swnet,
                            tc1,
                            tc2,
                            hmp1,
                            hmp2,
                            rh1,
                            rh2,
                            ws1,
                            ws2,
                            wd1,
                            wd2,
                            pres,
                            sh1,
                            sh2,
                            snow_temp10,
                            volts,
                            s_winmax,
                            s_woutmax,
                            s_wnetmax,
                            tc1max,
                            tc2max,
                            tc1min,
                            tc2min,
                            ws1max,
                            ws2max,
                            ws1std,
                            ws2std,
                            tref,
                        )
                    )

                    # Get current date number
                    current_date_num = self._get_date_num()

                    # Assign wdata only to entries in the past
                    wdata = wdata[date_num < current_date_num, :]

                    # Assign future_reports_num
                    future_reports_num = len(np.argwhere(date_num > current_date_num))

                    if future_reports_num > 0:
                        log.warning(
                            f"GoesCleaner: Removed {future_reports_num} entries out of: "
                            f"{len(wdata[:, 1]) + future_reports_num} good records from station ID: "
                            f"{station_id} Reason: time tags in future"
                        )

                    # Call write_csv function to write csv files with processed data
                    self.writer.write_csv(
                        wdata, station_num, year, julian_day, date_num
                    )

                    # Call write_json function to write long-term and short-term json files with processed data
                    self.writer.write_json(wdata, station_num, self.no_data)

                # Else station does not have usable data
                else:
                    log.warning(
                        f"{self.station_type} Station  #{station_num} does not have usable data"
                    )

    # Function returns gdata array depending on station_num, station_array formats vary by station
    @staticmethod
    def get_gdata_array(station_num, station_array):

        # Assign constant to initialize values
        INITIALIZER_VAL = 999

        # If station number 0 (10 meter tower)
        if station_num == 0:
            gdata = np.ones((np.size(station_array, 0), 43)) * INITIALIZER_VAL
            gind = np.concatenate(
                (np.arange(0, 7), np.arange(8, 20), np.array([30, 34, 35, 38, 39]))
            )
            aind = np.concatenate(
                (np.arange(1, 8), np.arange(8, 20), np.array([24]), np.arange(20, 24))
            )
            gdata[:, gind] = station_array[:, aind]
            return gdata

        # Else if station number 24 (East Grip)
        # Format is different for this station: no snow temp, only 2 radiation statistic measurements
        elif station_num == 24:
            gdata = np.ones((np.size(station_array, 0), 43)) * INITIALIZER_VAL
            gind = np.concatenate(
                (np.arange(0, 7), np.arange(8, 20), np.array([30]), np.arange(34, 43))
            )
            aind = np.concatenate(
                (np.arange(1, 8), np.arange(8, 20), np.array([31]), np.arange(22, 31))
            )
            gdata[:, gind] = station_array[:, aind]
            return gdata

        # Else if station number is 30 (PE Blue)
        # Format is different for this station: no snow temp, only 2 radiation statistic measurements
        elif station_num == 30:
            gdata = np.ones((np.size(station_array, 0), 43)) * INITIALIZER_VAL
            gind = np.concatenate(
                (np.arange(0, 20), np.array([30, 31, 32]), np.arange(34, 40))
            )
            aind = np.concatenate((np.arange(1, 21), np.array([29]), np.arange(21, 29)))
            # gdata(:,[1:20,31,32,33,35:40])=station_array(:,[1:20,29,21:28]);
            gdata[:, gind] = station_array[:, aind]
            return gdata

        # Else (all other stations)
        else:
            # Vector is made from looking at C-level columns and find index of raw data that matches
            aind = np.concatenate(
                (
                    np.arange(1, 8),
                    np.arange(18, 31),
                    np.arange(8, 18),
                    np.array([43]),
                    np.arange(31, 43),
                )
            )
            # rawindex = [1:7,18:30,8:17,43,31:42];
            # gdata=station_array(:,rawindex); %put data into pseudo C-level format!
            gdata = np.array(station_array[:, aind])
            return gdata


class CleanerFactory:
    @staticmethod
    def get_cleaner(station_type, init_file_path: str, writer: Writer):
        if station_type == "argos":
            return ArgosCleaner(init_file_path=init_file_path, writer=writer)
        elif station_type == "goes":
            return GoesCleaner(init_file_path=init_file_path, writer=writer)
        else:
            log.error(f"No cleaner for station type: {station_type}")
            return None
