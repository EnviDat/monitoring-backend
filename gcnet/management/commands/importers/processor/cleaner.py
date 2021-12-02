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


# class ArgosCleaner(Cleaner):
#
#     def __init__(self, init_file_path: str, writer: Writer):
#         Cleaner.__init__(self, init_file_path, "ARGOS", writer)
#
#     def clean(self, input_data: np.ndarray):
#         # Function to process ARGOS np array fom a dat file
#
#         # Iterate through each station and write json and csv file
#         for section in self.stations_config.sections():
#
#             # Assign station config variables
#             station_type = self.stations_config.get(section, "type")
#             is_active = self.stations_config.get(section, "active")
#
#             # Process Argos stations
#             if station_type == 'argos' and is_active == 'True':
#
#                 # Assign station ID
#                 sid = int(section)
#
#                 # Assign station number
#                 snum = int(self.stations_config.get(section, "station_num"))
#
#                 logger.info("ArgosCleaner: Processing {0} Station #{1}...".format(self.station_type, snum))
#
#                 if input_data.size != 0:
#
#                     usdata = np.array(input_data[input_data[:, 7] == sid, :])  # find data associated with each
#
#                     if len(usdata) != 0:
#
#                         u, IA = np.unique(usdata[:, 8:], axis=0, return_index=True)  # find rows with unique data
#                         #     % after column 8 because data may repeat with different time signature
#                         usdata = usdata[np.sort(IA), :]
#                         inds = np.argwhere(
#                             (usdata[:, 0] == usdata[:, 9]) & (np.ceil(usdata[:, 10]) == np.floor(usdata[:, 10])) & (
#                                     usdata[:, 10] > 0) & (usdata[:, 10] < 367))  # find lines that are first
#                         # part of the two piece table and have integer Julian day (records with
#                         # decimal julian day are erroneous) and have realistic (positive and
#                         # less than 367 day, leap year will have 366 days)
#                         lastp2v = np.argwhere(
#                             (usdata[:, 0] != usdata[:, 9]) & (usdata[:, 9] <= 360))  # second parts of table
#                         # column 10 of 2nd table is wind direction, realistic values will be less than 360 deg
#                         lastp2 = lastp2v[-1:]  # last second part
#                         inds = inds[inds < lastp2]  # make sure last record
#                         # has a second piece of the table
#                         numrecs = len(inds)  # number of total records
#                         adata = np.ones((numrecs, 43)) * 999
#                         # indexes (columns) to be assigned in data vector
#                         aind = np.concatenate(
#                             (
#                                 np.arange(0, 20), np.arange(30, 33), np.arange(34, 38), np.array([38]),
#                                 np.array([39])))
#                         # indexes (columns) in table 1 raw
#                         usind1 = np.concatenate((np.array([0]), np.array([10]), np.array([3]), np.arange(12, 23)))
#                         # indexes (columns) in table 2 raw
#                         usind2 = np.concatenate((np.arange(9, 14), np.array([22]), np.arange(14, 22)))
#
#                         for j in range(numrecs):  # loop through records
#                             ind2v = np.argwhere(usdata[inds[j]:, 0] != usdata[inds[j]:, 9])  # find second
#                             # table parts occurring after associated first part
#                             ind1 = inds[j]
#                             ind2 = inds[j] + ind2v[0]  # take the closest 2nd table line
#                             adata[j, aind] = np.concatenate(
#                                 (np.array([snum]), usdata[ind1, usind1], usdata[ind2, usind2]))
#                         gdata = adata[
#                                 (adata[:, 1] > 1990) & (adata[:, 1] < 2050) & (adata[:, 2] >= 0) & (
#                                         adata[:, 2] < 367),
#                                 :]  # filter realistic time
#
#                         if len(gdata) != 0:
#                             # (positive and less than 367 JD, leap year will have 366 days)
#                             # and sensible year
#                             gdata[gdata == -8190] = self.no_data
#                             gdata[gdata == 2080] = self.no_data
#                             yr = gdata[:, 1]  # get year data
#                             jday = gdata[:, 2] + gdata[:, 3] / 24  # calculate fractional julian day
#                             datenum = yr * 1.e3 + jday  # number that is ascending in time
#                             numraw = int(len(datenum))  # number of total datasets before duplicate filtering
#                             udatenum, unind = np.unique(datenum, axis=0,
#                                                         return_index=True)  # find only unique time stamps
#                             gdata = gdata[unind, :]  # need to reassign datenum to unique values
#                             yr = gdata[:, 1]  # get year data
#                             jday = gdata[:, 2] + gdata[:, 3] / 24  # calculate fractional julian day
#                             datenum = yr * 1.e3 + jday  # number that is ascending in time
#
#                             if len(unind) < numraw:
#                                 numduptime = numraw - len(unind)
#                                 logger.warning(
#                                     "ArgosCleaner: Warning: Removed " + str(numduptime) + " entries out of: " + str(
#                                         numraw) + " good pts from station ID: " + str(
#                                         sid) + " Reason: duplicate time tags")
#                             tind = np.argsort(
#                                 udatenum)  # find indexes of a sort of unique datetime values along time
#                             gdata = gdata[tind, :]  # crop data array to unique times
#                             jday = jday[tind]  # crop jday vector to unique times
#                             yr = yr[tind]
#                             datenum = datenum[tind]  # leave only unique and sorted datenums
#                             stnum = gdata[:, 0]  # get station number vector
#
#                             # assign and calibrate incoming shortwave
#                             swin = self._filter_values_calibrate(gdata[:, 4], section, "swmin", "swmax", "swin",
#                                                                  self.no_data, self.no_data)
#
#                             # assign and calibrate outgoing shortwave
#                             swout = self._filter_values_calibrate(gdata[:, 5], section, "swmin", "swmax", "swout",
#                                                                   self.no_data, self.no_data)
#
#                             # #assign and calibrate net shortwave, negative and positive values
#                             # have different calibration coefficients according to QC code
#                             swnet = 999 * np.ones(np.size(swout, 0))
#                             swnet[gdata[:, 6] >= 0] = gdata[gdata[:, 6] >= 0, 6] * float(
#                                 self.stations_config.get(section, "swnet_pos"))
#                             swnet[gdata[:, 6] < 0] = gdata[gdata[:, 6] < 0, 6] * float(
#                                 self.stations_config.get(section, "swnet_neg"))
#
#                             swnet[
#                                 swnet < -float(self.stations_config.get(section, "swmax"))] = self.no_data  # filter low
#                             swnet[
#                                 swnet > float(self.stations_config.get(section, "swmax"))] = self.no_data  # filter high
#
#                             tc1 = self._filter_values(gdata[:, 7], section, "tcmin", "tcmax")  # thermocouple 1
#
#                             tc2 = self._filter_values(gdata[:, 8], section, "tcmin", "tcmax")  # thermocouple 2
#
#                             hmp1 = self._filter_values(gdata[:, 9], section, "hmpmin", "hmpmax")  # hmp1 temp
#
#                             hmp2 = self._filter_values(gdata[:, 10], section, "hmpmin", "hmpmax")  # hmp2 temp
#
#                             rh1 = gdata[:, 11]  # HMP relative humidity 1
#                             rh1[rh1 < float(self.stations_config.get(section, "rhmin"))] = self.no_data  # filter low
#                             rh1[rh1 > float(self.stations_config.get(section, "rhmax"))] = self.no_data  # filter high
#                             # Assign values greater than 100 and less than rhmax to 100
#                             rh1[(rh1 > 100) & (
#                                     rh1 < float(self.stations_config.get(section, "rhmax")))] = 100
#
#                             rh2 = gdata[:, 12]  # HMP relative humidity 2
#                             rh2[rh2 < float(self.stations_config.get(section, "rhmin"))] = self.no_data  # filter low
#                             rh2[rh2 > float(self.stations_config.get(section, "rhmax"))] = self.no_data  # filter high
#                             # Assign values greater than 100 and less than rhmax to 100
#                             rh2[(rh2 > 100) & (
#                                     rh2 < float(self.stations_config.get(section, "rhmax")))] = 100
#
#                             ws1 = self._filter_values(gdata[:, 13], section, "wmin", "wmax")  # wind speed 1
#
#                             ws2 = self._filter_values(gdata[:, 14], section, "wmin", "wmax")  # wind speed 2
#
#                             wd1 = self._filter_values(gdata[:, 15], section, "wdmin", "wdmax")  # wind direction 1
#
#                             wd2 = self._filter_values(gdata[:, 16], section, "wdmin", "wdmax")  # wind direction 2
#
#                             pres = gdata[:, 17] + float(
#                                 self.stations_config.get(section, "pressure_offset"))  # barometric pressure
#                             pres[pres < float(self.stations_config.get(section, "pmin"))] = self.no_data  # filter low
#                             pres[pres > float(self.stations_config.get(section, "pmax"))] = self.no_data  # filter low
#                             presd = np.diff(pres)  # find difference of subsequent pressure meas
#                             hrdif = np.diff(jday) * 24.  # time diff in hrs
#                             mb_per_hr = np.absolute(
#                                 np.divide(presd, hrdif, out=np.zeros_like(presd), where=hrdif != 0))
#                             pjumps = np.argwhere(mb_per_hr > 10)  # find jumps > 10mb/hr (quite unnatural)
#                             pres[pjumps + 1] = self.no_data  # eliminate these single point jumps
#
#                             sh1 = self._filter_values(gdata[:, 18], section, "shmin", "shmax")  # height above snow 1
#
#                             sh2 = self._filter_values(gdata[:, 19], section, "shmin", "shmax")  # height above snow 2
#
#                             # 10m snow temperature (many of these are non functional or not connected)
#                             snow_temp10 = gdata[:, 20:30]
#
#                             volts = self._filter_values(gdata[:, 30], section, "battmin", "battmax")  # battery voltage
#
#                             s_winmax = self._filter_values_calibrate(gdata[:, 31], section, "swmin", "swmax", "swin",
#                                                                      self.no_data, self.no_data)
#
#                             s_woutmax = self._filter_values_calibrate(gdata[:, 32], section, "swmin", "swmax", "swout",
#                                                                       0.00, self.no_data)
#
#                             s_wnetmax = 999 * np.ones_like(s_woutmax)
#                             s_wnetmax[gdata[:, 33] >= 0] = gdata[gdata[:, 33] >= 0, 33] * float(
#                                 self.stations_config.get(section, "swnet_pos"))  # net radiation max
#                             s_wnetmax[gdata[:, 33] < 0] = gdata[gdata[:, 33] < 0, 33] * float(
#                                 self.stations_config.get(section, "swnet_neg"))
#                             s_wnetmax[s_wnetmax < -(
#                                 float(self.stations_config.get(section, "swmax")))] = self.no_data  # filter low
#                             s_wnetmax[
#                                 s_wnetmax > float(
#                                     self.stations_config.get(section, "swmax"))] = self.no_data  # filter high
#
#                             tc1max = self._filter_values(gdata[:, 34], section, "tcmin", "tcmax")
#
#                             tc2max = self._filter_values(gdata[:, 35], section, "tcmin", "tcmax")
#
#                             tc1min = self._filter_values(gdata[:, 36], section, "tcmin", "tcmax")
#
#                             tc2min = self._filter_values(gdata[:, 37], section, "tcmin", "tcmax")
#
#                             ws1max = gdata[:, 38]  # stats
#                             ws2max = gdata[:, 39]
#                             ws1std = gdata[:, 40]
#                             ws2std = gdata[:, 41]
#                             tref = gdata[:, 42]
#
#                             # # note this code does not currently calculate the 2 and 10 m winds
#                             # # and albedo, so this is column 1-42 of the Level C data
#                             wdata = np.column_stack(
#                                 (stnum, yr, jday, swin, swout, swnet, tc1, tc2, hmp1, hmp2, rh1, rh2, ws1,
#                                  ws2, wd1, wd2, pres, sh1, sh2, snow_temp10, volts, s_winmax, s_woutmax,
#                                  s_wnetmax, tc1max, tc2max, tc1min, tc2min, ws1max, ws2max, ws1std, ws2std,
#                                  tref))  # assemble data into final level C standard form
#                             today = datetime.now()
#                             day_of_year = (today - datetime(today.year, 1, 1)).days + 1
#                             theyear = today.year
#                             todayjday = day_of_year + today.hour / 24  # calculate fractional julian day
#                             nowdatenum = theyear * 1e3 + todayjday
#                             wdata = wdata[datenum < nowdatenum, :]  # only take entries in the past
#                             numfuturepts = len(np.argwhere(datenum > nowdatenum))
#
#                             if numfuturepts > 0:
#                                 logger.warning(
#                                     "ArgosCleaner: Warning: Removed " + str(numfuturepts) + " entries out of: " + str(
#                                         len(wdata[:, 1]) + numfuturepts) + " good pts from station ID: " + str(
#                                         sid) + " Reason: time tags in future")
#
#                             # Call write_csv function to write csv file with processed data
#                             # TODO test write_csv with convertingself.no_data value to null
#                             self.writer.write_csv(wdata, snum, yr, jday, datenum)
#
#                             # Call write_json function to write json long-term and shor-term files with processed data
#                             self.writer.write_json(wdata, snum, self.no_data)
#
#                         else:  # if gdata is empty after removing bad dates
#                             wdata = np.array([])
#                             logger.warning("\t{0} Station  #{1} does not have usable data".format(self.station_type,
#                                                                                                   snum))
#
#                 else:
#                     logger.warning("\t{0} Station  #{1} does not have usable data".format(self.station_type, snum))


# TEST refactoring of ArgosCleaner()
class ArgosCleaner(Cleaner):

    def __init__(self, init_file_path: str, writer: Writer):
        Cleaner.__init__(self, init_file_path, "ARGOS", writer)

    # Function to process ARGOS np array fom a dat file
    def clean(self, input_data: np.ndarray):

        # print(np.ndarray)

        np.set_printoptions(threshold=1)
        # print(np.nparray)

        # print(input_data)

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

                logger.info("ArgosCleaner: Processing {0} Station #{1}...".format(self.station_type, station_num))

                if input_data.size != 0:

                    # Assign station_data to data associated with each station
                    station_data = np.array(input_data[input_data[:, 7] == station_id, :])

                    # print(station_data)

                    if len(station_data) != 0:

                        u, IA = np.unique(station_data[:, 8:], axis=0, return_index=True)  # find rows with unique data
                        #     % after column 8 because data may repeat with different time signature

                        print(u)
                        print(IA)

                        station_data = station_data[np.sort(IA), :]
                        inds = np.argwhere(
                            (station_data[:, 0] == station_data[:, 9]) & (np.ceil(station_data[:, 10]) == np.floor(station_data[:, 10])) & (
                                    station_data[:, 10] > 0) & (station_data[:, 10] < 367))  # find lines that are first
                        # part of the two piece table and have integer Julian day (records with
                        # decimal julian day are erroneous) and have realistic (positive and
                        # less than 367 day, leap year will have 366 days)
                        lastp2v = np.argwhere(
                            (station_data[:, 0] != station_data[:, 9]) & (station_data[:, 9] <= 360))  # second parts of table
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
                            ind2v = np.argwhere(station_data[inds[j]:, 0] != station_data[inds[j]:, 9])  # find second
                            # table parts occurring after associated first part
                            ind1 = inds[j]
                            ind2 = inds[j] + ind2v[0]  # take the closest 2nd table line
                            adata[j, aind] = np.concatenate(
                                (np.array([station_num]), station_data[ind1, usind1], station_data[ind2, usind2]))
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
                                        station_id) + " Reason: duplicate time tags")
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
                                        station_id) + " Reason: time tags in future")

                            # Call write_csv function to write csv file with processed data
                            # TODO test write_csv with convertingself.no_data value to null
                            self.writer.write_csv(wdata, station_num, yr, jday, datenum)

                            # Call write_json function to write json long-term and shor-term files with processed data
                            self.writer.write_json(wdata, station_num, self.no_data)

                        else:  # if gdata is empty after removing bad dates
                            wdata = np.array([])
                            logger.warning("\t{0} Station  #{1} does not have usable data".format(self.station_type,
                                                                                                  station_num))

                else:
                    logger.warning("\t{0} Station  #{1} does not have usable data".format(self.station_type, station_num))


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
        if station_type == 'argos':
            return ArgosCleaner(init_file_path=init_file_path, writer=writer)
        elif station_type == 'goes':
            return GoesCleaner(init_file_path=init_file_path, writer=writer)
        else:
            logger.error("No cleaner for station type '{0}'".format(station_type))
            return None
