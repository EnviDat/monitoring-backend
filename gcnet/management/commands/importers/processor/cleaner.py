import sys

from pathlib import Path
import numpy as np
import configparser
from datetime import datetime

from gcnet.util.writer import Writer

import logging

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Cleaner(object):

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
    def _filter_values_calibrate(self, unfiltered_values, sect, minimum, maximum, calibration,
                                 no_data_min, no_data_max):

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

    def clean(self, input_data: np.ndarray):
        # Function to process ARGOS np array fom a dat file

        # Iterate through each station and write json and csv file
        for section in self.stations_config.sections():

            # Assign station config variables
            station_type = self.stations_config.get(section, "type")
            is_active = self.stations_config.get(section, "active")

            # Process Argos stations
            if station_type == 'argos' and is_active == 'True':

                # Assign station ID
                sid = int(section)

                # Assign station number
                snum = int(self.stations_config.get(section, "station_num"))

                logger.info("ArgosCleaner: Processing {0} Station #{1}...".format(self.station_type, snum))

                if input_data.size != 0:

                    usdata = np.array(input_data[input_data[:, 7] == sid, :])  # find data associated with each

                    if len(usdata) != 0:

                        u, IA = np.unique(usdata[:, 8:], axis=0, return_index=True)  # find rows with unique data
                        #     % after column 8 because data may repeat with different time signature
                        usdata = usdata[np.sort(IA), :]

                        inds = np.argwhere(
                            (usdata[:, 0] == usdata[:, 9]) & (np.ceil(usdata[:, 10]) == np.floor(usdata[:, 10])) & (
                                    usdata[:, 10] > 0) & (usdata[:, 10] < 367))  # find lines that are first
                        # part of the two piece table and have integer Julian day (records with
                        # decimal julian day are erroneous) and have realistic (positive and
                        # less than 367 day, leap year will have 366 days)

                        lastp2v = np.argwhere(
                            (usdata[:, 0] != usdata[:, 9]) & (usdata[:, 9] <= 360))  # second parts of table
                        # column 10 of 2nd table is wind direction, realistic values will be less than 360 deg

                        lastp2 = lastp2v[-1:]  # last second part
                        inds = inds[inds < lastp2]  # make sure last record
                        # has a second piece of the table
                        numrecs = len(inds)  # number of total records
                        adata = np.ones((numrecs, 43)) * 999
                        # indexes (columns) to be assigned in data vector
                        aind = np.concatenate(
                            (
                                np.arange(0, 20), np.arange(30, 33), np.arange(34, 38), np.array([38]),
                                np.array([39])))
                        # indexes (columns) in table 1 raw
                        usind1 = np.concatenate((np.array([0]), np.array([10]), np.array([3]), np.arange(12, 23)))
                        # indexes (columns) in table 2 raw
                        usind2 = np.concatenate((np.arange(9, 14), np.array([22]), np.arange(14, 22)))

                        for j in range(numrecs):  # loop through records
                            ind2v = np.argwhere(usdata[inds[j]:, 0] != usdata[inds[j]:, 9])  # find second
                            # table parts occurring after associated first part
                            ind1 = inds[j]
                            ind2 = inds[j] + ind2v[0]  # take the closest 2nd table line
                            adata[j, aind] = np.concatenate(
                                (np.array([snum]), usdata[ind1, usind1], usdata[ind2, usind2]))
                        gdata = adata[
                                (adata[:, 1] > 1990) & (adata[:, 1] < 2050) & (adata[:, 2] >= 0) & (
                                        adata[:, 2] < 367),
                                :]  # filter realistic time

                        if len(gdata) != 0:
                            # (positive and less than 367 JD, leap year will have 366 days)
                            # and sensible year
                            gdata[gdata == -8190] = self.no_data
                            gdata[gdata == 2080] = self.no_data
                            yr = gdata[:, 1]  # get year data
                            jday = gdata[:, 2] + gdata[:, 3] / 24  # calculate fractional julian day
                            datenum = yr * 1.e3 + jday  # number that is ascending in time
                            numraw = int(len(datenum))  # number of total datasets before duplicate filtering
                            udatenum, unind = np.unique(datenum, axis=0,
                                                        return_index=True)  # find only unique time stamps
                            gdata = gdata[unind, :]  # need to reassign datenum to unique values
                            yr = gdata[:, 1]  # get year data
                            jday = gdata[:, 2] + gdata[:, 3] / 24  # calculate fractional julian day
                            datenum = yr * 1.e3 + jday  # number that is ascending in time

                            if len(unind) < numraw:
                                numduptime = numraw - len(unind)
                                logger.warning(
                                    "ArgosCleaner: Warning: Removed " + str(numduptime) + " entries out of: " + str(
                                        numraw) + " good pts from station ID: " + str(
                                        sid) + " Reason: duplicate time tags")
                            tind = np.argsort(
                                udatenum)  # find indexes of a sort of unique datetime values along time
                            gdata = gdata[tind, :]  # crop data array to unique times
                            jday = jday[tind]  # crop jday vector to unique times
                            yr = yr[tind]
                            datenum = datenum[tind]  # leave only unique and sorted datenums
                            stnum = gdata[:, 0]  # get station number vector

                            # assign and calibrate incoming shortwave
                            swin = self._filter_values_calibrate(gdata[:, 4], section, "swmin", "swmax", "swin",
                                                                 self.no_data, self.no_data)

                            # assign and calibrate outgoing shortwave
                            swout = self._filter_values_calibrate(gdata[:, 5], section, "swmin", "swmax", "swout",
                                                                  self.no_data, self.no_data)

                            # #assign and calibrate net shortwave, negative and positive values
                            # have different calibration coefficients according to QC code
                            swnet = 999 * np.ones(np.size(swout, 0))
                            swnet[gdata[:, 6] >= 0] = gdata[gdata[:, 6] >= 0, 6] * float(
                                self.stations_config.get(section, "swnet_pos"))
                            swnet[gdata[:, 6] < 0] = gdata[gdata[:, 6] < 0, 6] * float(
                                self.stations_config.get(section, "swnet_neg"))

                            swnet[
                                swnet < -float(self.stations_config.get(section, "swmax"))] = self.no_data  # filter low
                            swnet[
                                swnet > float(self.stations_config.get(section, "swmax"))] = self.no_data  # filter high

                            tc1 = self._filter_values(gdata[:, 7], section, "tcmin", "tcmax")  # thermocouple 1

                            tc2 = self._filter_values(gdata[:, 8], section, "tcmin", "tcmax")  # thermocouple 2

                            hmp1 = self._filter_values(gdata[:, 9], section, "hmpmin", "hmpmax")  # hmp1 temp

                            hmp2 = self._filter_values(gdata[:, 10], section, "hmpmin", "hmpmax")  # hmp2 temp

                            rh1 = gdata[:, 11]  # HMP relative humidity 1
                            rh1[rh1 < float(self.stations_config.get(section, "rhmin"))] = self.no_data  # filter low
                            rh1[rh1 > float(self.stations_config.get(section, "rhmax"))] = self.no_data  # filter high
                            # Assign values greater than 100 and less than rhmax to 100
                            rh1[(rh1 > 100) & (
                                    rh1 < float(self.stations_config.get(section, "rhmax")))] = 100

                            rh2 = gdata[:, 12]  # HMP relative humidity 2
                            rh2[rh2 < float(self.stations_config.get(section, "rhmin"))] = self.no_data  # filter low
                            rh2[rh2 > float(self.stations_config.get(section, "rhmax"))] = self.no_data  # filter high
                            # Assign values greater than 100 and less than rhmax to 100
                            rh2[(rh2 > 100) & (
                                    rh2 < float(self.stations_config.get(section, "rhmax")))] = 100

                            ws1 = self._filter_values(gdata[:, 13], section, "wmin", "wmax")  # wind speed 1

                            ws2 = self._filter_values(gdata[:, 14], section, "wmin", "wmax")  # wind speed 2

                            wd1 = self._filter_values(gdata[:, 15], section, "wdmin", "wdmax")  # wind direction 1

                            wd2 = self._filter_values(gdata[:, 16], section, "wdmin", "wdmax")  # wind direction 2

                            pres = gdata[:, 17] + float(
                                self.stations_config.get(section, "pressure_offset"))  # barometric pressure
                            pres[pres < float(self.stations_config.get(section, "pmin"))] = self.no_data  # filter low
                            pres[pres > float(self.stations_config.get(section, "pmax"))] = self.no_data  # filter low
                            presd = np.diff(pres)  # find difference of subsequent pressure meas
                            hrdif = np.diff(jday) * 24.  # time diff in hrs
                            mb_per_hr = np.absolute(
                                np.divide(presd, hrdif, out=np.zeros_like(presd), where=hrdif != 0))
                            pjumps = np.argwhere(mb_per_hr > 10)  # find jumps > 10mb/hr (quite unnatural)
                            pres[pjumps + 1] = self.no_data  # eliminate these single point jumps

                            sh1 = self._filter_values(gdata[:, 18], section, "shmin", "shmax")  # height above snow 1

                            sh2 = self._filter_values(gdata[:, 19], section, "shmin", "shmax")  # height above snow 2

                            # 10m snow temperature (many of these are non functional or not connected)
                            snow_temp10 = gdata[:, 20:30]

                            volts = self._filter_values(gdata[:, 30], section, "battmin", "battmax")  # battery voltage

                            s_winmax = self._filter_values_calibrate(gdata[:, 31], section, "swmin", "swmax", "swin",
                                                                     self.no_data, self.no_data)

                            s_woutmax = self._filter_values_calibrate(gdata[:, 32], section, "swmin", "swmax", "swout",
                                                                      0.00, self.no_data)

                            s_wnetmax = 999 * np.ones_like(s_woutmax)
                            s_wnetmax[gdata[:, 33] >= 0] = gdata[gdata[:, 33] >= 0, 33] * float(
                                self.stations_config.get(section, "swnet_pos"))  # net radiation max
                            s_wnetmax[gdata[:, 33] < 0] = gdata[gdata[:, 33] < 0, 33] * float(
                                self.stations_config.get(section, "swnet_neg"))
                            s_wnetmax[s_wnetmax < -(
                                float(self.stations_config.get(section, "swmax")))] = self.no_data  # filter low
                            s_wnetmax[
                                s_wnetmax > float(
                                    self.stations_config.get(section, "swmax"))] = self.no_data  # filter high

                            tc1max = self._filter_values(gdata[:, 34], section, "tcmin", "tcmax")

                            tc2max = self._filter_values(gdata[:, 35], section, "tcmin", "tcmax")

                            tc1min = self._filter_values(gdata[:, 36], section, "tcmin", "tcmax")

                            tc2min = self._filter_values(gdata[:, 37], section, "tcmin", "tcmax")

                            ws1max = gdata[:, 38]  # stats
                            ws2max = gdata[:, 39]
                            ws1std = gdata[:, 40]
                            ws2std = gdata[:, 41]
                            tref = gdata[:, 42]

                            # # note this code does not currently calculate the 2 and 10 m winds
                            # # and albedo, so this is column 1-42 of the Level C data
                            wdata = np.column_stack(
                                (stnum, yr, jday, swin, swout, swnet, tc1, tc2, hmp1, hmp2, rh1, rh2, ws1,
                                 ws2, wd1, wd2, pres, sh1, sh2, snow_temp10, volts, s_winmax, s_woutmax,
                                 s_wnetmax, tc1max, tc2max, tc1min, tc2min, ws1max, ws2max, ws1std, ws2std,
                                 tref))  # assemble data into final level C standard form
                            today = datetime.now()
                            day_of_year = (today - datetime(today.year, 1, 1)).days + 1
                            theyear = today.year
                            todayjday = day_of_year + today.hour / 24  # calculate fractional julian day
                            nowdatenum = theyear * 1e3 + todayjday
                            wdata = wdata[datenum < nowdatenum, :]  # only take entries in the past
                            numfuturepts = len(np.argwhere(datenum > nowdatenum))

                            if numfuturepts > 0:
                                logger.warning(
                                    "ArgosCleaner: Warning: Removed " + str(numfuturepts) + " entries out of: " + str(
                                        len(wdata[:, 1]) + numfuturepts) + " good pts from station ID: " + str(
                                        sid) + " Reason: time tags in future")

                            # Call write_csv function to write csv file with processed data
                            # TODO test write_csv with convertingself.no_data value to null
                            self.writer.write_csv(wdata, snum, yr, jday, datenum)

                            # Call write_json function to write json long-term and shor-term files with processed data
                            self.writer.write_json(wdata, snum, self.no_data)

                        else:  # if gdata is empty after removing bad dates
                            wdata = np.array([])
                            logger.warning("\t{0} Station  #{1} does not have usable data".format(self.station_type,
                                                                                                  snum))

                else:
                    logger.warning("\t{0} Station  #{1} does not have usable data".format(self.station_type, snum))


# TEST refactoring of ArgosCleaner()
class ArgosCleanerV2(Cleaner):

    def __init__(self, init_file_path: str, writer: Writer):
        Cleaner.__init__(self, init_file_path, "ARGOS", writer)

    # Function to process ARGOS numpy array fom a dat file
    def clean(self, input_data: np.ndarray):

        np.set_printoptions(threshold=sys.maxsize)

        # Assign constants for column indices in input numpy array
        INPUT_YEAR1_COL = 0
        INPUT_STATION_ID_COL = 7
        INPUT_STATION_NUM_COL = 8
        INPUT_YEAR2_COL = 9
        INPUT_JULIAN_DAY_COL = 10
        INPUT_WIND_DIRECTION_COL = 9

        # Assign constants for column indices and other constants in combined_array
        COMBINED_YEAR_COL = 1
        COMBINED_YEAR_MIN = 1990
        COMBINED_YEAR_MAX = 2050
        COMBINED_JULIAN_DAY_COL = 2

        # Assign constants for column indices and other constants used in station_array processing
        STATION_NO_DATA1 = -8190
        STATION_NO_DATA2 = 2080
        STATION_NUMBER_COL = 0
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
        MAX_DAYS_YEAR = 367
        MAX_DEGREES_WIND = 360
        HOURS_IN_DAY = 24
        MAX_HUMIDITY = 100
        INITIALIZER_VAL = 999

        # Iterate through each station and write json and csv file
        for section in self.stations_config.sections():

            # Assign station config variables
            station_type = self.stations_config.get(section, "type")
            is_active = self.stations_config.get(section, "active")

            # Process Argos stations
            if station_type == 'argos' and is_active == 'True':

                # Assign station_id
                station_id = int(section)

                # Assign station_num
                station_num = int(self.stations_config.get(section, "station_num"))

                logger.info(f'ArgosCleaner: Processing {self.station_type} Station #{station_num}...')

                if input_data.size != 0:

                    # Assign station_data to data assoicated with each station
                    station_data = np.array(input_data[input_data[:, INPUT_STATION_ID_COL] == station_id, :])

                    if len(station_data) != 0:

                        # Assign unique_array to unique_rows after INPUT_STATION_NUM_COL
                        # Assign unique_indices to indices of unique rows after INPUT_STATION_NUM_COL
                        # because data may repeat with different time signature
                        unique_array, unique_indices = np.unique(station_data[:, INPUT_STATION_NUM_COL:],
                                                                 axis=0, return_index=True)

                        # Assign station_data to station_data sorted by unique_indcies
                        station_data = station_data[np.sort(unique_indices), :]

                        # Assign table_1_indices to indices of rows that are the first part of the two part table
                        # and have integer Julian day (records with decimal julian day are erroneous)
                        # and have a realistic Julian day (positive and less than 367 day, leap year will have 366 days)
                        table_1_indices = np.argwhere(
                            (station_data[:, INPUT_YEAR1_COL] == station_data[:, INPUT_YEAR2_COL]) &
                            (np.ceil(station_data[:, INPUT_JULIAN_DAY_COL]) ==
                             np.floor(station_data[:, INPUT_JULIAN_DAY_COL])) &
                            (station_data[:, INPUT_JULIAN_DAY_COL] > 0) &
                            (station_data[:, INPUT_JULIAN_DAY_COL] < MAX_DAYS_YEAR))

                        # Assign table_2_indices to indices of rows that are the second part of the two part table
                        # column 10 of 2nd table is wind direction, realistic values will be less than 360 degrees
                        table_2_indices = np.argwhere(
                            (station_data[:, INPUT_YEAR1_COL] != station_data[:, INPUT_WIND_DIRECTION_COL]) &
                            (station_data[:, INPUT_WIND_DIRECTION_COL] <= MAX_DEGREES_WIND))

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
                            (np.arange(0, 20), np.arange(30, 33), np.arange(34, 38), np.array([38]), np.array([39])))

                        # Assign table_1_columns to columns in table 1 raw
                        table_1_columns = np.concatenate(
                            (np.array([0]), np.array([10]), np.array([3]), np.arange(12, 23)))

                        # Assign table_2_columns to columns in table 2 raw
                        table_2_columns = np.concatenate((np.arange(9, 14), np.array([22]), np.arange(14, 22)))

                        # Loop through records
                        for j in range(num_records):
                            # Find second table parts occurring after associated first part
                            table_2_current_indices = np.argwhere(
                                station_data[table_1_indices[j]:, 0] != station_data[table_1_indices[j]:, 9])

                            table_1_index = table_1_indices[j]

                            # Assign table_2_index to the closest table 2 line
                            table_2_index = table_1_indices[j] + table_2_current_indices[INPUT_YEAR1_COL]

                            # Combine corresponding parts of table 1 and table 2 into an array within combined_array
                            combined_array[j, combined_array_columns] = np.concatenate(
                                (np.array([station_num]),
                                 station_data[table_1_index, table_1_columns],
                                 station_data[table_2_index, table_2_columns]))

                        # Assign station_array to combined_array filtered for realistic years and Julian days
                        station_array = combined_array[(combined_array[:, COMBINED_YEAR_COL] > COMBINED_YEAR_MIN) &
                                                       (combined_array[:, COMBINED_YEAR_COL] < COMBINED_YEAR_MAX) &
                                                       (combined_array[:, COMBINED_JULIAN_DAY_COL] >= 0) &
                                                       (combined_array[:, COMBINED_JULIAN_DAY_COL] < MAX_DAYS_YEAR), :]

                        # Filter and process station_array
                        # Assign variables used to create new array that will be used to write csv files and json files
                        if len(station_array) != 0:

                            # Assign no_data values to self.no_data
                            station_array[station_array == STATION_NO_DATA1] = self.no_data
                            station_array[station_array == STATION_NO_DATA2] = self.no_data

                            # Assign year to year data
                            year = station_array[:, STATION_NUMBER_COL]

                            # Assign julian_day to julian day plus fractional julian day
                            julian_day = station_array[:, STATION_JULIAN_DAY_COL] \
                                         + station_array[:, STATION_HOUR_COL] / HOURS_IN_DAY

                            # Assign date_number to year * 1000 + julian_day
                            date_num = year * 1.e3 + julian_day

                            # Assign raw_num to number of records before duplicate filtering
                            raw_num = int(len(date_num))

                            # Find only unique timestamps and their indices from date_num
                            unique_date_num_array, unique_date_num_indices = np.unique(date_num, axis=0,
                                                                                       return_index=True)

                            # Reassign station_array to records with unique timestamps
                            station_array = station_array[unique_date_num_indices, :]

                            # Reassign year to year data
                            year = station_array[:, STATION_YEAR_COL]

                            # Reassign julian_day to julian day plus fractional julian day
                            julian_day = station_array[:, STATION_JULIAN_DAY_COL] \
                                         + station_array[:, STATION_HOUR_COL] / HOURS_IN_DAY

                            # Reassign date_number to year * 1000 + julian_day
                            date_num = year * 1.e3 + julian_day

                            # Log how many records removed because of duplicate time stamps
                            if len(unique_date_num_indices) < raw_num:
                                duplicate_timestamps_num = raw_num - len(unique_date_num_indices)
                                logger.warning(f'ArgosCleaner: Warning: Removed {duplicate_timestamps_num} entries out'
                                               f' of: {raw_num} records from station ID: {station_id} '
                                               f'Reason: duplicate time tags')

                            # Assign unique_timestamp_indices to indices of a sort of unique datetime values along time
                            unique_timestamp_indices = np.argsort(unique_date_num_array)

                            # Crop data array to unique times
                            station_array = station_array[unique_timestamp_indices, :]
                            julian_day = julian_day[unique_timestamp_indices]  # crop julian_day vector to unique times
                            year = year[unique_timestamp_indices]
                            date_num = date_num[unique_timestamp_indices]  # leave only unique and sorted date_nums

                            # Assign station_number
                            station_number = station_array[:, STATION_YEAR_COL]

                            # Assign and calibrate incoming shortwave
                            swin = self._filter_values_calibrate(station_array[:, STATION_SWIN_COL], section,
                                                                 "swmin", "swmax", "swin",
                                                                 self.no_data, self.no_data)

                            # Assign and calibrate outgoing shortwave
                            swout = self._filter_values_calibrate(station_array[:, STATION_SWOUT_COL], section,
                                                                  "swmin", "swmax", "swout",
                                                                  self.no_data, self.no_data)

                            # Assign and calibrate net shortwave, negative and positive values
                            # Different stations have different calibration coefficients according to QC code
                            swnet = INITIALIZER_VAL * np.ones(np.size(swout, 0))
                            swnet[station_array[:, STATION_SWNET_COL] >= 0] = \
                                station_array[station_array[:, STATION_SWNET_COL] >= 0, STATION_SWNET_COL] \
                                * float(self.stations_config.get(section, "swnet_pos"))
                            swnet[station_array[:, STATION_SWNET_COL] < 0] = \
                                station_array[station_array[:, STATION_SWNET_COL] < 0, STATION_SWNET_COL] \
                                * float(self.stations_config.get(section, "swnet_neg"))

                            # Filter low net shortwave
                            swnet[swnet < -float(self.stations_config.get(section, "swmax"))] = self.no_data

                            # Filter high net shortwave
                            swnet[swnet > float(self.stations_config.get(section, "swmax"))] = self.no_data

                            # Filter thermocouple 1
                            tc1 = self._filter_values(station_array[:, STATION_TC1_COL], section, "tcmin", "tcmax")

                            # Filter thermocouple 2
                            tc2 = self._filter_values(station_array[:, STATION_TC2_COL], section, "tcmin", "tcmax")

                            # Filter hmp1 temp
                            hmp1 = self._filter_values(station_array[:, STATION_HMP1_COL], section, "hmpmin", "hmpmax")

                            # Filter hmp2 temp
                            hmp2 = self._filter_values(station_array[:, STATION_HMP2_COL], section, "hmpmin", "hmpmax")

                            # Assign and calibrate relative humidity 1
                            rh1 = station_array[:, STATION_RH1_COL]
                            rh1[rh1 < float(self.stations_config.get(section, "rhmin"))] = self.no_data  # filter low
                            rh1[rh1 > float(self.stations_config.get(section, "rhmax"))] = self.no_data  # filter high
                            # Assign values greater than MAX_HUMIDITY and less than rhmax to MAX_HUMIDITY
                            rh1[(rh1 > MAX_HUMIDITY) & (rh1 < float(self.stations_config.get(section, "rhmax")))] \
                                = MAX_HUMIDITY

                            # Assign and calibrate relative humidity 2
                            rh2 = station_array[:, STATION_RH2_COL]
                            rh2[rh2 < float(self.stations_config.get(section, "rhmin"))] = self.no_data  # filter low
                            rh2[rh2 > float(self.stations_config.get(section, "rhmax"))] = self.no_data  # filter high
                            # Assign values greater than MAX_HUMIDITY and less than rhmax to MAX_HUMIDITY
                            rh2[(rh2 > MAX_HUMIDITY) & (
                                    rh2 < float(self.stations_config.get(section, "rhmax")))] = MAX_HUMIDITY

                            # Filter wind speed 1
                            ws1 = self._filter_values(station_array[:, STATION_WS1_COL], section, "wmin", "wmax")

                            # Filter wind speed 2
                            ws2 = self._filter_values(station_array[:, STATION_WS2_COL], section, "wmin", "wmax")

                            # Filter wind direction 1
                            wd1 = self._filter_values(station_array[:, STATION_WD1_COL], section, "wdmin", "wdmax")

                            # Filter wind direction 2
                            wd2 = self._filter_values(station_array[:, STATION_WD2_COL], section, "wdmin", "wdmax")

                            # Assign and calibrate barometric pressure
                            pres = station_array[:, STATION_PRESSURE_COL] \
                                   + float(self.stations_config.get(section, "pressure_offset"))
                            pres[pres < float(self.stations_config.get(section, "pmin"))] = self.no_data  # filter low
                            pres[pres > float(self.stations_config.get(section, "pmax"))] = self.no_data  # filter low
                            pres_diff = np.diff(pres)  # Find difference of subsequent pressure measurements
                            hr_diff = np.diff(julian_day) * 24.  # Time difference in hours
                            mb_per_hr = np.absolute(
                                np.divide(pres_diff, hr_diff, out=np.zeros_like(pres_diff), where=hr_diff != 0)
                            )
                            press_jumps = np.argwhere(mb_per_hr > 10)  # Find jumps > 10mb/hr (quite unnatural)
                            pres[press_jumps + 1] = self.no_data  # Eliminate these single point jumps

                            # Filter height above snow 1
                            sh1 = self._filter_values(station_array[:, STATION_SH1_COL], section, "shmin", "shmax")

                            # Filter height above snow 2
                            sh2 = self._filter_values(station_array[:, STATION_SH2_COL], section, "shmin", "shmax")

                            # 10m snow temperature (many of these are non functional or not connected)
                            snow_temp10 = station_array[:, 20:30]

                            # Filter battery voltage
                            volts = self._filter_values(station_array[:, STATION_VOLTS_COL], section,
                                                        "battmin", "battmax")

                            s_winmax = self._filter_values_calibrate(station_array[:, STATION_S_WINMAX_COL], section,
                                                                     "swmin", "swmax", "swin",
                                                                     self.no_data, self.no_data)

                            s_woutmax = self._filter_values_calibrate(station_array[:, STATION_S_WOUTMAX_COL], section,
                                                                      "swmin", "swmax", "swout", 0.00, self.no_data)

                            # Assign and calibrate net radiation max
                            s_wnetmax = INITIALIZER_VAL * np.ones_like(s_woutmax)
                            s_wnetmax[station_array[:, STATION_S_WNETMAX_COL] >= 0] \
                                = station_array[station_array[:, STATION_S_WNETMAX_COL] >= 0, STATION_S_WNETMAX_COL] \
                                  * float(self.stations_config.get(section, "swnet_pos"))
                            s_wnetmax[station_array[:, STATION_S_WNETMAX_COL] < 0] \
                                = station_array[station_array[:, STATION_S_WNETMAX_COL] < 0, STATION_S_WNETMAX_COL] \
                                  * float(self.stations_config.get(section, "swnet_neg"))
                            # Filter low
                            s_wnetmax[s_wnetmax < -(float(self.stations_config.get(section, "swmax")))] = self.no_data
                            # Filter high
                            s_wnetmax[s_wnetmax > float(self.stations_config.get(section, "swmax"))] = self.no_data

                            # Filter other measurements
                            tc1max = self._filter_values(station_array[:, STATION_TC1MAX_COL], section,
                                                         "tcmin", "tcmax")

                            tc2max = self._filter_values(station_array[:, STATION_TC2MAX_COL], section,
                                                         "tcmin", "tcmax")

                            tc1min = self._filter_values(station_array[:, STATION_TC1MIN_COL], section,
                                                         "tcmin", "tcmax")

                            tc2min = self._filter_values(station_array[:, STATION_TC2MIN_COL], section,
                                                         "tcmin", "tcmax")

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
                                (station_number, year, julian_day, swin, swout, swnet, tc1, tc2, hmp1, hmp2, rh1, rh2,
                                 ws1, ws2, wd1, wd2, pres, sh1, sh2, snow_temp10, volts, s_winmax, s_woutmax,
                                 s_wnetmax, tc1max, tc2max, tc1min, tc2min, ws1max, ws2max, ws1std, ws2std, tref)
                            )

                            # Get current date number
                            current_date_num = self._get_date_num()

                            # Only take entries in the past
                            wdata = wdata[date_num < current_date_num, :]
                            future_reports_num = len(np.argwhere(date_num > current_date_num))

                            if future_reports_num > 0:
                                logger.warning(f'ArgosCleaner: Warning: Removed {str(future_reports_num)} entries out '
                                               f'of: {str(len(wdata[:, 1]) + future_reports_num)} records from station '
                                               f'ID: {str(station_id)} Reason: time tags in future')

                            # Call write_csv function to write csv file with processed data
                            self.writer.write_csv(wdata, station_num, year, julian_day, date_num)

                            # Call write_json function to write json long-term and short-term files with processed data
                            self.writer.write_json(wdata, station_num, self.no_data)

                        # Else station_array is empty after removing bad dates
                        else:
                            # wdata = np.array([])
                            logger.warning(f'\t{self.station_type} Station #{station_num} does not have usable data')

                else:
                    logger.warning(f'\t{self.station_type} Station #{station_num} does not have usable data')


class GoesCleaner(Cleaner):

    def __init__(self, init_file_path: str, writer: Writer):
        Cleaner.__init__(self, init_file_path, "GOES", writer)

    def clean(self, input_data: np.ndarray):
        # Iterate through each station and write json and csv file
        for section in self.stations_config.sections():

            # Assign station config values
            station_type = self.stations_config.get(section, "type")
            is_active = self.stations_config.get(section, "active")

            # Process Goes stations
            if station_type == 'goes' and is_active == 'True':

                # Assign station ID
                sid = section

                # Assign station number
                snum = int(self.stations_config.get(section, "station_num"))

                logger.info("GoesCleaner: Processing {0} Station #{1}...".format(self.station_type, snum))

                if input_data.size > 0:

                    adata = np.array(input_data[input_data[:, 1] == snum, :])  # find data associated with each

                    logger.info("GoesCleaner: Data size {0} for Station #{1}...".format(adata.size, snum))
                    # if adata.size <= 0:
                    #     logger.warning("Skipping cleaning of {0} for Station #{1}, NO DATA".format(adata.size, snum))
                    # continue

                    u, ia = np.unique(adata[:, 5:], axis=0, return_index=True)  # find rows with unique data
                    #     % after column 5 because data may repeat with different time signature
                    adata = adata[np.sort(ia), :]
                    adata = adata[
                            (adata[:, 2] > 1990) & (adata[:, 2] < 2050) & (adata[:, 3] >= 0) & (adata[:, 3] < 367),
                            :]  # filter realistic time
                    # #(positive and less than 367 JD, leap year will have 366 days)
                    # # and sensible year

                    logger.info("GoesCleaner: Clean data size {0} for Station #{1}...".format(adata.size, snum))
                    # if adata.size <= 0:
                    #     logger.warning("Skipping cleaning of {0} for Station #{1}, NO DATA after cleaning"
                    #                    .format(adata.size, snum))
                    #     continue

                    if snum == 0:  # if 10 meter tower
                        gdata = np.ones((np.size(adata, 0), 43)) * 999
                        gind = np.concatenate((np.arange(0, 7), np.arange(8, 20), np.array([30, 34, 35, 38, 39])))
                        aind = np.concatenate((np.arange(1, 8), np.arange(8, 20), np.array([24]), np.arange(20, 24)))
                        gdata[:, gind] = adata[:, aind]  # format is
                    elif snum == 24:  # if East GRIP
                        gdata = np.ones((np.size(adata, 0), 43)) * 999
                        gind = np.concatenate((np.arange(0, 7), np.arange(8, 20), np.array([30]), np.arange(34, 43)))
                        aind = np.concatenate((np.arange(1, 8), np.arange(8, 20), np.array([31]), np.arange(22, 31)))
                        gdata[:, gind] = adata[:, aind]  # format is
                        # different for this station: no snow temp, only 2 radiation
                        # statistic measurements
                    elif snum == 30:  # if PE Blue
                        gdata = np.ones((np.size(adata, 0), 43)) * 999
                        gind = np.concatenate((np.arange(0, 20), np.array([30, 31, 32]), np.arange(34, 40)))
                        aind = np.concatenate((np.arange(1, 21), np.array([29]), np.arange(21, 29)))
                        # gdata(:,[1:20,31,32,33,35:40])=adata(:,[1:20,29,21:28]); %format is
                        gdata[:, gind] = adata[:, aind]
                        # different for this station: no snow temp, only 2 radiation
                        # statistic measurements
                    else:  # if normal station
                        # this vector is made from looking at C-level columns and find index of raw data that matches
                        aind = np.concatenate(
                            (np.arange(1, 8), np.arange(18, 31), np.arange(8, 18), np.array([43]), np.arange(31, 43)))
                        # rawindex = [1:7,18:30,8:17,43,31:42];
                        # gdata=adata(:,rawindex); %put data into pseudo C-level format!
                        gdata = np.array(adata[:, aind])
                    gdata[gdata == -8190] = self.no_data
                    gdata[gdata == 2080] = self.no_data

                    yr = gdata[:, 1]  # get year data
                    jday = gdata[:, 2] + gdata[:, 3] / 24  # calculate fractional julian day
                    datenum = yr * 1e3 + jday  # number that is ascending in time
                    numraw = int(len(datenum))  # number of total datasets before duplicate filtering
                    udatenum, unind = np.unique(datenum, axis=0, return_index=True)  # find only unique time stamps
                    gdata = gdata[unind, :]  # need to reassign datenum to unique values
                    yr = gdata[:, 1]  # get year data of unique values only
                    jday = gdata[:, 2] + gdata[:, 3] / 24  # calculate fractional julian day of unique values
                    datenum = yr * 1.e3 + jday  # number that is ascending in time of unique values
                    if len(unind) < numraw:
                        numduptime = numraw - len(unind)
                        logger.warning("GoesCleaner: Warning: Removed " + str(numduptime) + " entries out of: " + str(
                            numraw) + " good pts from station ID: " + str(sid) + " Reason: duplicate time tags")
                    tind = np.argsort(udatenum)  # find indices of a sort of unique values along time
                    gdata = gdata[tind, :]  # crop data array to unique times
                    jday = jday[tind]  # crop jday vector to unique times
                    yr = yr[tind]
                    datenum = datenum[tind]  # leave only unique and sorted datenums
                    stnum = gdata[:, 0]  # get station number vector

                    swin = self._filter_values_calibrate(gdata[:, 4], section, "swmin", "swmax", "swin",
                                                         self.no_data, self.no_data)

                    swout = self._filter_values_calibrate(gdata[:, 5], section, "swmin", "swmax", "swout",
                                                          self.no_data, self.no_data)

                    # #assign and calibrate net shortwave, negative and positive values
                    # #have different calibration coefficients according to QC code
                    swnet = 999 * np.ones(np.size(swout, 0))
                    swnet[gdata[:, 6] >= 0] = gdata[gdata[:, 6] >= 0, 6] * float(self.stations_config.get(section,
                                                                                                          "swnet_pos"))
                    swnet[gdata[:, 6] < 0] = gdata[gdata[:, 6] < 0, 6] * float(self.stations_config.get(section,
                                                                                                        "swnet_neg"))
                    swnet[swnet < -(float(self.stations_config.get(section, "swmax")))] = self.no_data  # filter low
                    swnet[swnet > float(self.stations_config.get(section, "swmax"))] = self.no_data  # filter high

                    pres = gdata[:, 17] + float(self.stations_config.get(section,
                                                                         "pressure_offset"))  # barometeric pressure
                    pres[pres < float(self.stations_config.get(section, "pmin"))] = self.no_data  # filter low
                    pres[pres > float(self.stations_config.get(section, "pmax"))] = self.no_data  # filter high
                    presd = np.diff(pres)  # find difference of subsequent pressure meas
                    hrdif = np.diff(jday) * 24.  # time diff in hrs
                    mb_per_hr = np.absolute(np.divide(presd, hrdif, out=np.zeros_like(presd), where=hrdif != 0))
                    pjumps = np.argwhere(mb_per_hr > 10)  # find jumps > 10mb/hr (quite unnatural)
                    pres[pjumps + 1] = self.no_data  # eliminate these single point jumps

                    s_winmax = self._filter_values_calibrate(gdata[:, 31], section, "swmin", "swmax", "swin",
                                                             self.no_data, self.no_data)

                    s_woutmax = self._filter_values_calibrate(gdata[:, 32], section, "swmin", "swmax", "swout",
                                                              0.00, self.no_data)

                    s_wnetmax = 999 * np.ones_like(s_woutmax)
                    # net radiation max
                    s_wnetmax[gdata[:, 33] >= 0] = gdata[gdata[:, 33] >= 0, 33] * float(
                        self.stations_config.get(section, "swnet_pos"))
                    s_wnetmax[gdata[:, 33] < 0] = gdata[gdata[:, 33] < 0, 33] * float(
                        self.stations_config.get(section, "swnet_neg"))
                    s_wnetmax[
                        s_wnetmax < -(float(self.stations_config.get(section, "swmax")))] = self.no_data  # filter low
                    s_wnetmax[
                        s_wnetmax > float(self.stations_config.get(section, "swmax"))] = self.no_data  # filter high

                    tc1 = self._filter_values(gdata[:, 7], section, "tcmin", "tcmax")  # thermocouple 1

                    tc2 = self._filter_values(gdata[:, 8], section, "tcmin", "tcmax")  # thermocouple 2

                    hmp1 = self._filter_values(gdata[:, 9], section, "hmpmin", "hmpmax")  # hmp1 temp

                    hmp2 = self._filter_values(gdata[:, 10], section, "hmpmin", "hmpmax")  # hmp2 temp

                    rh1 = gdata[:, 11]  # HMP relative humidity 1
                    rh1[rh1 < float(self.stations_config.get(section, "rhmin"))] = self.no_data  # filter low
                    rh1[rh1 > float(self.stations_config.get(section, "rhmax"))] = self.no_data  # filter high
                    rh1[(rh1 > 100) & (
                            rh1 < float(
                        self.stations_config.get(section, "rhmax")))] = 100  # Assign values greater than
                    # 100 and less than rhmax to 100
                    rh2 = gdata[:, 12]  # HMP relative humidity 2
                    rh2[rh2 < float(self.stations_config.get(section, "rhmin"))] = self.no_data  # filter low
                    rh2[rh2 > float(self.stations_config.get(section, "rhmax"))] = self.no_data  # filter high
                    rh2[(rh2 > 100) & (
                            rh2 < float(
                        self.stations_config.get(section, "rhmax")))] = 100  # Assign values greater than
                    # 100 and less than rhmax to 100

                    ws1 = self._filter_values(gdata[:, 13], section, "wmin", "wmax")  # wind speed 1

                    ws2 = self._filter_values(gdata[:, 14], section, "wmin", "wmax")  # wind speed 2

                    wd1 = self._filter_values(gdata[:, 15], section, "wdmin", "wdmax")  # wind direction 1

                    wd2 = self._filter_values(gdata[:, 16], section, "wdmin", "wdmax")  # wind direction 2

                    sh1 = self._filter_values(gdata[:, 18], section, "shmin", "shmax")  # height above snow 1

                    sh2 = self._filter_values(gdata[:, 19], section, "shmin", "shmax")  # height above snow 2

                    snow_temp10 = gdata[:,
                                  20:30]  # 10m snow temperature (many of these are non functional or not connected)

                    volts = self._filter_values(gdata[:, 30], section, "battmin", "battmax")  # battery voltage

                    tc1max = self._filter_values(gdata[:, 34], section, "tcmin", "tcmax")

                    tc2max = self._filter_values(gdata[:, 35], section, "tcmin", "tcmax")

                    tc1min = self._filter_values(gdata[:, 36], section, "tcmin", "tcmax")

                    tc2min = self._filter_values(gdata[:, 37], section, "tcmin", "tcmax")

                    ws1max = gdata[:, 38]  # stats
                    ws2max = gdata[:, 39]
                    ws1std = gdata[:, 40]
                    ws2std = gdata[:, 41]
                    tref = gdata[:, 42]

                    # # note this code does not currently calculate the 2 and 10 m winds
                    # # and albedo, so these are columns 1-42 of the Level C data
                    wdata = np.column_stack(
                        (stnum, yr, jday, swin, swout, swnet, tc1, tc2, hmp1, hmp2, rh1, rh2, ws1, ws2, wd1,
                         wd2, pres, sh1, sh2, snow_temp10, volts, s_winmax, s_woutmax, s_wnetmax, tc1max,
                         tc2max, tc1min, tc2min, ws1max, ws2max, ws1std, ws2std,
                         tref))  # assemble data into final level C standard form
                    today = datetime.now()
                    day_of_year = (today - datetime(today.year, 1, 1)).days + 1
                    theyear = today.year
                    todayjday = day_of_year + today.hour / 24  # calculate fractional julian day
                    nowdatenum = theyear * 1e3 + todayjday
                    wdata = wdata[datenum < nowdatenum, :]  # only take entries in the past
                    numfuturepts = len(np.argwhere(datenum > nowdatenum))

                    if numfuturepts > 0:
                        logger.warning("GoesCleaner: Warning: Removed " + str(numfuturepts) + " entries out of: " + str(
                            len(wdata[:, 1]) + numfuturepts) + " good pts from station ID: " + str(
                            sid) + " Reason: time tags in future")

                    # Call write_csv function to write csv files with processed data
                    # TODO test write_csv with convertingself.no_data value to null
                    self.writer.write_csv(wdata, snum, yr, jday, datenum)

                    # Call write_json function to write long-term and short-term json files with processed data
                    self.writer.write_json(wdata, snum, self.no_data)

                else:  # if no data in adata still output empty wdata array so empty file is created
                    wdata = np.array([])
                    logger.warning("\t{0} Station  #{1} does not have usable data".format(self.station_type, snum))


class CleanerFactory(object):

    @staticmethod
    def get_cleaner(station_type, init_file_path: str, writer: Writer):
        # TODO test that ArgosCleanerV2() returns same output as ArgosCleaner()
        if station_type == 'argos':
            # return ArgosCleaner(init_file_path=init_file_path, writer=writer)
            # TEST
            return ArgosCleanerV2(init_file_path=init_file_path, writer=writer)
        elif station_type == 'goes':
            return GoesCleaner(init_file_path=init_file_path, writer=writer)
        else:
            logger.error("No cleaner for station type '{0}'".format(station_type))
            return None
