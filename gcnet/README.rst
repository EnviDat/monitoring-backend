GC-Net Data Processing and API
===============================

Python software package that processes, filters and calibrate meteorological station data and serves the data
with a Django API.

GC-Net (Greenland Climate Network) transmits data from several  meteorological stations via satellite.
The stations are equipped with communication satellite transmitters that enable near real-time monitoring of weather conditions on the
Greenland ice sheet. Data are periodically manually retrieved from station data loggers in Greenland.

The GC-Net API is a Django project that imports meteorological
station data, processes and copies the data into a Postgres database, and serves the data
in an API.


---------------------
Documentation Topics
---------------------
    * `In Honor of Prof. Dr. Konrad Steffen`_
    * `Application  Overview Diagram`_
    * `Authors and Contact Information`_
    * `Configuration file: gcnet_metadata.ini`_
    * `Configuration file: stations.ini`_
    * `Create/Modify Database`_
    * `Data Import Commands`_
    * `Continuous Data Processing and Import`_
    * `Development Server`_
    * `NGINX Configuration`_
    * `API`_
    * API documentation website: https://www.envidat.ch/data-api/gcnet/


-------------------------------------
In Honor of Prof. Dr. Konrad Steffen
-------------------------------------

Prof. Dr. Konrad Steffen was the principal investigator of GC-Net and tragically died during a research expedition
in Greenland on August 8, 2020 in an accident.
His dedication made GC-Net possible and he encouraged the developers of this API to ensure
that the application was robust to guarantee access to the meteorological data.
Prof. Dr. Steffen was a committed scientist and generous friend and is deeply missed.


------------------------------
Application  Overview Diagram
------------------------------

.. image:: ./gc_net_overview.jpg


---------------------------------------------
Authors and Contact Information
---------------------------------------------

    * *Organization*: `Swiss Federal Research Institute WSL <https://www.wsl.ch>`_
    * *Authors*: Rebecca Buchholz, V.Trotsiuk, Lucia de Espona, Ionut Iosifescu, Derek Houtz
    * *Contact Email*: envidat(at)wsl.ch
    * *Date last modified*: March 1, 2022

---------------------------------------
Configuration file: gcnet_metadata.ini
---------------------------------------

Please note that quotation marks are used in the documentation
for clarity purposes and should NOT be included in the actual configuration files.

Configuration files are in the directory "gcnet/config".

The "gcnet_metadata.ini" configuration file contains the general application execution parameters such as *newloadflag, short_term_days, etc*.

The paths for *json_fileloc* and *csv_fileloc* can be expressed forward or backward slashes,
the software will translate them into the
proper format for the current OS. Both absolute and relative paths are accepted.

**[file] section**


The [file] section is usually the ONLY section that may need to be edited to run this application.

    * *newload_flag* is usually set to "0", if it is set to "1" then existing files will be overwritten.
    * *short_term_days* are the number of days that the short-term csv files suffixed with "_v" will be written. A value of "14" means that the most recent 14 days of data will be written in the short-term files.
    * *json_fileloc* should be set to existing paths in the system and end in a slash, for example "gcnet/output/". Output json files will be stored here.
    * *csv_fileloc* should be set to existing paths in the system and end in a slash, for example "gcnet/output/". Output csv files will be stored here.
    * *stations* are the station numbers
    * *groups* are the names that of the measurement groups used in csv and json output files

Example [file] section configuration::

    newloadflag=0
    short_term_days=14
    json_fileloc=gcnet/output/
    csv_fileloc=gcnet/output/
    stations=4,5,7,22,31,32,33,0,1,2,3,6,8,9,10,11,12,15,23,24,30
    groups=temp,rh,rad,sheight,stemp,ws,wd,press,battvolt


**[argos] and [goes] sections**

The [goes] and [argos] sections contain the parameters related to the raw data files retrieval and processing.

  * *data_url* is the URL to download the raw data from, for example "https://envidatrepo.wsl.ch/uploads/gcnet/data/LATEST_ARGOS.raw"
  * *data_url_file* is the file path to store the downloaded raw data, for example, "gcnet/input/LATEST_ARGOS.raw"
  * *data_local* is the file path where the raw data is stored, this key is used if the input data will be directly read from a file rather than downloaded from a URL using the "localInput" option in gcnet/main.py, please see `Continuous Data Processing and Import`_

Example [argos] and [goes] configuration::

    [argos]
    data_url=https://envidatrepo.wsl.ch/uploads/gcnet/data/LATEST_ARGOS.raw
    data_url_file=gcnet/input/LATEST_ARGOS.raw
    data_local=gcnet/input/LATEST_ARGOS.raw

    [goes]
    data_url=https://envidatrepo.wsl.ch/uploads/gcnet/data/LATEST_GOES.raw
    data_url_file=gcnet/input/LATEST_GOES.raw
    data_local=gcnet/input/LATEST_GOES.raw

**[columns] section**

The [columns] section is used to create a dictionary that matches column numbers with the column names. This section should not be altered!


----------------------------------
Configuration file: stations.ini
----------------------------------

Configuration files are in the directory "gcnet/config".

All station-specific information and parameters should be specified in "stations.ini"
To change a calibration parameter it is only necessary to edit this file and restart the backend without editing the code.

**[DEFAULT] section**

The [DEFAULT] section contains the base parameters that can be overwritten in the next sections that correspond to single stations.

  * *csv_data_dir* is the file path where csv files are located that will be used to import data into Postgres database. Do not put a slash at the end of the *csv_data_dir* value!
  * **Warning**: *csv_data_dir* must be the same location defined in "gcnet_metadata.ini" section [file] key 'csv_fileloc'
  * *no_data* is the value that will replace the values in the data that are missing or out of the bounds defined by the calibration parameters. For example, "999".
  * **Note**: the *active* key in the should be set to "True" in the production environment to ensure that the data of all stations will be processed.
  * Other values correspond to basic filters for various scientific measurements.

Example [DEFAULT] configuration::

    [DEFAULT]
    csv_data_dir = gcnet/output
    no_data = 999
    swmax = 1300
    swmin = 0
    hmpmin = -40
    hmpmax = 50
    tcmax = 50
    tcmin = -100
    wmax = 50
    wmin = 0
    wdmax = 360
    wdmin = 0
    pmin = 500
    pmax = 1200
    rhmax = 130
    rhmin = 0
    shmin = -10
    shmax = 10
    battmin = 8
    battmax = 24
    active = False



**[<station ID number>] section**

Each station has its own section in stations.ini

Stations can be added and removed from stations.ini. However, stations must also be added or removed from
gcnet/models.py and migrations must be run on the database (see documentation topic `Create/Modify Database`_).

Example station configuration::

    name = GC-NET GOES station Swiss Camp 10m
    station_num = 00
    active = True
    position = latlon (69.5647, 49.3308, 1176)
    type = goes
    swin = 200
    swout = 200
    swnet_pos = 80
    swnet_neg = 80
    pressure_offset = 400
    csv_temporary = 00_swisscamp_10m
    csv_input = 0_v.csv
    model = swisscamp_10m_tower_00d

Station configuration explanation::

    name = <station name>
    station_num = <station number>
    active = <if station is currently active, this means data will be processed and served in API>
    position = <latitude and longitude coordinates of station>
    type = <argos or goes> (this is the type of satellite transmission)
    swin = <specific calibration for station>
    swout = <specific calibration for station>
    swnet_pos = <specific calibration for station>
    swnet_neg = <specific calibration for station>
    pressure_offset = <specific calibration for station>
    csv_temporary = <first part of name of temporary csv file used in management/commands/csv_import.py>
    csv_input = <input csv file>
    model = <model to import data into, must match name of model used in gcnet/models.py>


-----------------------
Create/Modify Database
-----------------------

During development this project used a PostgreSQL database (version 12.2). Before creating a database stations may be added or removed in "gcnet/models.py"
Each station "model" is written as a child class that inherits its fields from the Station parent class.
Each model is a separate table in the Postgres database. The test model may be used for testing data imports and API calls.

    1. Navigate to project directory in terminal and run::

        python manage.py makemigrations gcnet

        python manage.py migrate gcnet --database=gcnet


    2. Open database using pgAdmin on local machine or server and verify that the tables in gcnet/models.py migrated correctly.

    3. It is possible to add or remove models after the initial database setup. First add new station or remove existing station information from
       "gcnet/config/stations.ini"

    4. Add or remove models from models.py and then rerun the commands listed in number 1 of this section.
       This project assumes that any new stations will inherit fields from the "Station" parent class. The source data
       for the new station must use one the field structures listed in the DEFAULT_HEADER of
       "gcnet/management/commands/importers/processor/dat_import.py" or "gcnet/management/commands/importers/processor/csv_import.py"

    Example new station model in models.py::

        # New Station Name
        class new_station(Station):
            pass

--------------------
Data Import Commands
--------------------

After creating a Postgres database there are several options for importing data into the GC-Net Django Postgres database
using the commands in the gcnet/management/commands directory. Continuous data imports are documented in documentation
topic `Continuous Data Processing and Import`_.

During data imports values that were assigned in the source files as errors or missing  are converted to null,
to change this modify "gcnet/fields.py" class CustomFloatField. Default erroneous values are: '999', '999.0', '999.00',
'999.000', '999.0000', '-999', NaN'


To import a file, copy it to the gcnet/data directory and navigate to project directory in terminal and run import command (see parameter description below).

**WARNING**: Always make sure that the input source data file and model used in an import command are for the same station, otherwise data could be imported into the wrong table.

Example usages of command gcnet/management/commands/import_csv.py::

        # Import a local csv file
        python manage.py import_csv -s local -i gcnet/output/1_v.csv -a gcnet -m swisscamp_01d

        # Import csv from a URL endpoint
        python manage.py import_csv -s url -i https://www.wsl.ch/gcnet/data/1_v.csv -a gcnet -m swisscamp_01d

Parameters used in "import_csv" command::

    -s, --source: Input data source. Valid options are a local machine file "local" or a url to download file from "url".

    -i, --inputfile: Path or URL to input csv file, for example "gcnet/output/1_v.csv" or "https://www.wsl.ch/gcnet/data/1_v.csv".

    -a, --app: App that Django model belongs to, for example "gcnet" or "lwf".

    -m, --model: Django Model to map data import to, for example "swisscamp_01d".


Example usages of command gcnet/management/commands/import_data.py::

        # Import a local csv file
        python manage.py import_data -s 01_swisscamp -c gcnet/config/stations.ini -i gcnet/data/1_2019_min.csv -m swisscamp_01d
        
        # Import csv from a URL endpoint
        python manage.py import_data -s 01_swisscamp -c gcnet/config/stations.ini -i https://www.wsl.ch/gcnet/data/1_v.csv -m swisscamp_01d
        
        # Validate (logging-only) a csv local file
        python manage.py import_data -s 01_swisscamp -c gcnet/config/stations.ini -i gcnet/data/1_2019_min.csv  -m swisscamp_01d -l True -d gcnet/data/output
        
        # Import a local dat file
        python manage.py import_data -s 01_swisscamp -c gcnet/config/stations.ini -i gcnet/data/1_1996_30lines.dat -m swisscamp_01d
        
        # Import a local NEAD file forcing the import to ignore duplicated records instead breaking on error and rolling back.
        python manage.py import_data -s 08_dye2 -c gcnet/config/stations.ini -i gcnet/data/8_nead_min.csv  -m dye2_08d -f True
        

More information about the NEAD format can be found at https://www.envidat.ch/#/metadata/new-environmental-data-archive-nead-format

Parameters used in "import_data" command::

    -s, --station: Station number and name, for example "02_crawford".

    -c, --config: Path to stations config file (.ini).

    -i, --inputfile: The supported formats are DAT (.dat), CSV (.csv) and NEAD (.csv)
        The format will be guessed from the input so please use the proper extension for the file name to import.
        It can be a path to a local file or a URL.

    -f, --force: Duplicated records (according to timestamp) will lead to complete abort and rollback of the
        import process ('-f False' by default). If the parameter force is specified as "-f True" then the duplicated
        records will be ignored and the rest of the rows imported.

    -m, --model: Django Model to map data import to.

The following parameters are only available for CSV file format import::

   -l, --loggeronly: If set to True, it will just validate the csv rows to import without saving any data to the database.
        Information will be shown in the console and written to a temporary file in the indicated output directory ('-d' parameter below).

   -d, --directory: If logging only is selected, then the output will be written to a temporary file in this directory.


There are two batch files to run several csv_import commands:

    1. **inputfile in directory**
        Edit the first line in batch/csv_import_directory.bat to the path of your project directory.
        Be sure that the csv files are in gcnet/data. Otherwise modify the inputfile (-i) arguments accordingly.
        Then open a file explorer window and navigate to the project's batch directory, double click on csv_import_directory.bat to execute.

    2. **inputfile on web**
        Edit the first line in batch/csv_import_web.bat to the path of your project directory.
        Be sure that the csv files are served at https://www.wsl.ch/gcnet/data. Otherwise modify the inputfile (-i) arguments accordingly.
        Then open a file explorer window and navigate to the project's batch directory, double click on csv_import_web.bat to execute.

--------------------------------------
Continuous Data Processing and Import
--------------------------------------

To continuously import data run main.py

main.py has two optional arguments::

    -r (--repeatInterval) This runs the the import every <interval> minutes

    -l (--localInput) Any string used in this argument will load local input files designated in config file
        "gcnet_metadata.ini" keys "data_local" and will skip downloading files from web

Open terminal and navigate to project directory. Make sure virtual environment is activated.

Run python and import main::

    python
    from gcnet.main import main


Then run main.py

Example commands::

    No arguments passed:            main.main()
    repeatInterval:                 main.main(['-r 10'])
    repeatInterval and localInput:  main.main(['-r 10', '-l True'])


----------------------
Development Server
----------------------

Django has an inbuilt development server.
This server should only be used during development and testing and not for production.

1. Navigate to project directory in terminal. Make sure virtual environment created earlier
with Django and other dependencies is activated. Run::

    python manage.py runserver

2. By default the development server is hosted at http://localhost:8000/

    * To test if the server is working properly browse to a valid API URL: http://localhost:8000/api/models/
    * A list of station values by the 'model' keys in the config/stations.ini file should be returned.
    * An overview of the API is in the section "API".
    * For a detailed explanation of the API please see https://www.envidat.ch/data-api/gcnet/
    * The source code for the API documentation website is "gcnet/templates/index.html"

-----
API
-----

The API has separate documentation.

Visit https://www.envidat.ch/data-api/gcnet/ or open :gcnet/templates/index.html" in a browser to view documentation.

Arguments used in API calls::

   ARGUMENT             NAME [UNITS]

   swin                 Shortwave Incoming Radiation [W m^-2]
   swout                Shortwave Outgoing Radiation [W m^-2]
   netrad               Net Radiation [W m^-2]
   airtemp1             Thermocouple Air Temperature 1 [degC]
   airtemp2             Thermocouple Air Temperature 2 [degC]
   airtemp_cs500air1    CS500 Air Temperature 1 [degC]
   airtemp_cs500air2    CS500 Air Temperature 2 [degC]
   rh1                  Relative Humidity 1 [%]
   rh2                  Relative Humidity 2 [%]
   windspeed1           Wind Speed 1 [m s^-1]
   windspeed2           Wind Speed 2 [m s^-1]
   winddir1             Wind Direction 1 [deg]
   winddir2             Wind Direction 2 [deg]
   pressure             Atmospheric Pressure [mb]
   sh1                  Snow Surface Distance 1 [m]
   sh2                  Snow Surface Distance 2 [m]
   battvolt             Battery Voltage [V]
   swin_maximum         Shortwave Incoming Radiation Maximum [W m^-2]
   swin_stdev           Shortwave Incoming Radiation Standard Deviation [W m^-2]
   netrad_stdev         Net Radiation Standard Deviation [W m^-2]
   airtemp1_maximum     Thermocouple Air Temperature 1 Maximum [degC]
   airtemp2_maximum     Thermocouple Air Temperature 2 Maximum [degC]
   airtemp1_minimum     Thermocouple Air Temperature 1 Minimum [degC]
   airtemp2_minimum     Thermocouple Air Temperature 2 Minimum [degC]
   windspeed_u1_maximum Wind Speed 1 Maximum [m s^-1]
   windspeed_u2_maximum Wind Speed 2 Maximum [m s^-1]
   windspeed_u1_stdev   Wind Speed 1 Standard Deviation [m s^-1]
   windspeed_u2_stdev   Wind Speed 2 Standard Deviation [m s^-1]
   reftemp              Reference Temperature [degC]
