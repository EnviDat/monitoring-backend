GC-Net Data Processing and API
===============================

Python software package that processes, filters and calibrate meteorological station data. Serves the data
in a dynamic Django API.

GC-Net (Greenland Climate Network) transmits data from several  meteorological stations via satellite.
They are equipped with communication satellite transmitters that enable near real-time monitoring of weather conditions on the
Greenland ice sheet. Data are periodically manually retrieved from station data loggers in Greenland.

The GC-Net API is a Django project that imports .dat and pre-processed csv files with meteorological
station data, processes and copies the data into a Postgres database, and serves the data
with a dynamic web API.

.. image:: ./gc_net_overview.jpg

-------------------------------------
In Honor of Prof. Dr. Konrad Steffen
-------------------------------------

Prof. Dr. Konrad Steffen was the principal investigator of GC-Net and tragically died during a research expedition
in Greenland on August 8, 2020 in an accident.
His dedication made GC-Net possible and he encouraged the developers of this API to ensure
that the application was robust to guarantee access to the meteorological data.
Prof. Dr. Steffen was a committed scientist and generous friend and is deeply missed.

----------------------
Configuration
----------------------

- **gcnet_metadata.ini**: This configuration file contains the general application execution parameters such as *newloadflag, short_term_days, etc*.

  * The paths can be expressed with linux-style slashes also for Windows, the software will translate them into the proper format for the current OS. Both absolute and relative paths are accepted.
  * The [file] section is usually the ONLY that may need to be edited to run this application, in particular the parameters *json_fileloc* and *csv_fileloc* should be set to existing paths in the system.
  * The [goes] and [argos] sections contain the parameters related to the raw data files retrieval and processing. The raw data processors can only be executed in Windows systems, to make tests in Unix or OSX environments you willl need to provide the corresponding .dat files (see commandline parameters in the section "Continuous Data Processing and Import")
  * The [columns] section specifies the data columns


All station-specific information and parameters should be defined in stations.ini:

- **stations.ini**: This file contains the calibration parameters such as *swmax, swmin, rhmin, etc*.

  * The [DEFAULT] section contains the base parameters that can be overwritten in the next sections that correspond to single stations.
  * The *no_data* value that will replace the values in the data that are missing or out of the bounds defined by the calibration parameters.
  * To change a calibration parameter it is only necessary to edit this file and restart the backend without editing the code.
  * **Note**: the *active* parameter in the default section should be set to true in the production environment to ensure the data all stations will be processed.


**[DEFAULT]**

Be sure to modify as needed the directory and/or URL with the input data in stations.ini::

    csv_data_dir = path/to/input/csv/files
    csv_data_url = https://www.wsl.ch/gcnet/data


**[<STATION ID NUMBER>]**

Each station has its own section in stations.ini

Stations can be added and removed from stations.ini. However, stations must also be added or removed from
gcnet/models.py and migrations must be run on the database (see section "Create/Modify Database").

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
    api = True

Station configuration explanation::

    name = <station name>
    station_num = <station number>
    active = <if station is currently active>
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
    api = <True> (should be used in API) or <False> (should not be used in API)


-----------------------
Create/Modify Database
-----------------------

Before creating a database stations may be added or removed in gcnet/models.py.
Each station "model" is written as a child class that inherits its fields from the Station parent class.
Each model is a separate table in the Postgres database. The test model may be used for testing data imports and API calls.

1. Navigate to project directory in terminal and run::

    python manage.py makemigrations gcnet

    python manage.py migrate gcnet --database=gcnet


2. Open database using PG Admin on local machine or server and verify that the tables in gcnet/models.py migrated correctly.

3. It is possible to add or remove models after the initial database setup. First add new station or remove existing station information from
gcnet/config/stations.ini

4. Add or remove models from models.py and then rerun the commands listed in number 1 of this section.
This project assumes that any new stations will inherit fields from the "Station" parent class. The source data
for the new station must use one the field structures listed in the DEFAULT_HEADER of
gcnet/management/commands/importers/processor/dat_import.py or gcnet/management/commands/importers/processor/csv_import.py

Example new station model in models.py::

    # New Station
    class new_station(Station):
        pass

--------------------
Data Import Commands
--------------------

After creating a Postgres database there are several options for importing data into the GC-Net Django Postgres database
using the commands in the gcnet/management/commands directory. Continuous data imports are documented in the
section "Continuous Data Processing and Import".

During data imports values that were assigned in the source files as errors or missing  are converted to null, to change this modify gcnet/fields.py

    The erroneous values are: '999', '999.0', '999.00', '999.000', '999.0000', '-999', NaN'


To import a file, copy it to the gcnet/data directory and navigate to project directory in terminal and run import command (see parameter description below). For example::

        # import a local csv file
        python manage.py import_data -s 01_swisscamp -c gcnet/config/stations.ini -i gcnet/data/1_2019_min.csv -m swisscamp_01d
        
        # import csv from a URL endpoint
        python manage.py import_data -s 01_swisscamp -c gcnet/config/stations.ini -i https://www.wsl.ch/gcnet/data/1_v.csv -m swisscamp_01d
        
        # validate (logging-only) a csv local file
        python manage.py import_data -s 01_swisscamp -c gcnet/config/stations.ini -i gcnet/data/1_2019_min.csv  -m swisscamp_01d -l True -d gcnet/data/output
        
        # import a local dat file
        python manage.py import_data -s 01_swisscamp -c gcnet/config/stations.ini -i gcnet/data/1_1996_30lines.dat -m swisscamp_01d
        
        # import a local NEAD file forcing the import to ignore duplicated records instead breaking on error and rolling back.
        python manage.py import_data -s 08_dye2 -c gcnet/config/stations.ini -i gcnet/data/8_nead_min.csv  -m dye2_08d -f True
        

WARNING: Always make sure that the input source data file and model used in an import command are for the same station, otherwise data could be imported into the wrong table.


PARAMETERS
----------
* **parameter -s, station name:** Station number and name, for example "02_crawford".

* **parameter -m, model name:** Django Model to map data import to.

* **parameter -c, config file:** Path to stations config file (.ini).

* **parameter -i, input file:** The supported formats are DAT (.dat), CSV (.csv) and NEAD (.csv) described at https://www.envidat.ch/#/metadata/new-environmental-data-archive-nead-format . The format will be guessed from the input so please use the proper extension for the file name to import. It can be a path to a local file or a URL.

* **parameter -f, force import:** Duplicated records (according to timestamp) will lead to complete abort and rollback of the import process ('-f False' by default). If the parameter force is specified as "-f True" then the duplicated records will be ignored and the rest of the rows imported.

The following parameters are **only available for CSV** file format import:

* **parameter -l, logging only:** If set to True, it will just validate the csv rows to import without saving any data to the database. Information will be shown in the console and written to a temporary file in the indicated output directory ('-d' parameter below).

* **parameter -d, output directory:** If logging only is selected, then the output will be written to a temporary file in this directory.


There are two batch files to run several csv_import commands.

    inputfile in directory: Edit the first line in batch/csv_import_directory.bat to the path of your project directory.
    Be sure that the csv files are in gcnet/data. Otherwise modify the inputfile (-i) arguments accordingly.
    Then open a file explorer window and navigate to the project's batch directory, double click on csv_import_directory.bat to execute.

    inputfile on web: edit the first line in batch/csv_import_web.bat to the path of your project directory.
    Be sure that the csv files are served at https://www.wsl.ch/gcnet/data. Otherwise modify the inputfile (-i) arguments accordingly.
    Then open a file explorer window and navigate to the project's batch directory, double click on csv_import_web.bat to execute.

--------------------------------------
Continuous Data Processing and Import
--------------------------------------

To continuously import data run main.py

main.py has three arguments::

    -r (--repeatInterval) This runs the the import every <interval> minutes

    -i (--inputType) Input data source read from stations.ini config. This is a required argument.
            Options:
                "file" = directory path (csv_data_dir in stations.ini)
                "url" = URL address hosting files (csv_data_url in stations.ini)

    -l (--localFolder) Load local .dat files from folder and skip processing. Optional argument.

Open terminal and navigate to project directory. Make sure virtual environment is activated.

Run python and import main::

    python
    from gcnet.main import main


Then run main.py

Example commands running every 15 minutes::

    Import data from URL:         main(['-r 15', '-i url'])
    Import data from directory:   main(['-r 15', '-i file'])


- **-l <folder>**: For Unix and OSX environments, you can use this option to provide locally stored dat files that should be present in the designated folder with the exact names *argos_decoded.dat* or *goes_decoded.dat*. For example if you place the input dat files in a subfolder called *input* in the project root directory the command should be::

     main(['-r 15', '-i url', '-l input'])


----------------------
Development Server
----------------------

Django has an inbuilt development server.
This server should only be used during development and testing and not for production.

1. Navigate to project directory in terminal. Make sure virtual environment created earlier
with Django and other dependencies is activated. Run::

    python manage.py runserver

2. By default the development server is hosted at http://localhost:8000/

    To test if the server is working properly browse to a valid API URL: http://localhost:8000/api/models/

    A list of station values by the 'model' keys in the config/stations.ini file should be returned.

    An overview of the API is in the section "API".

    For a detailed explanation of the API please see https://www.envidat.ch/data-api/gcnet/
    (The source code for the API documentation website is at gcnet/templates/index.html)

--------------------
NGINX Configuration
--------------------

Make sure you have installed NGINX on your machine. During development NGINX version 1.19.1 was
used. NGINX can be downloaded at http://nginx.org/en/download.html

A helpful guide can be found at (scroll to "NGINX and Waitress")
https://github.com/Johnnyboycurtis/webproject and accompanying tutorial video at
https://www.youtube.com/watch?v=BBKq6H9Rm5g

1. Edit ALLOWED_HOST_2  in project/.env if needed to include server domain name. For example::

    ALLOWED_HOST_2 = ['wunderbar.server.ch']

2. Edit nginx_waitress/monitoring_nginx.conf::

    LINE 8: Edit the port number the site will be served on,
            it should not be the same port that the database uses in project/.env

    LINE 11: Edit the server_name to your machine's IP address or FQDN

    LINES 23-25: If using static files uncomment these lines and put the path to your project's
        static folder in LINE 24

    LINE 29: Edit proxy_pass if wanted to match the server running from Waitress (i.e. runserver.py, LINE 8).
        This will usually be localhost or your IP address.

3. Open runserver.py::

    LINE 8: Make sure that host and port are match the settings used in gcnet_nginx.conf

    For example, if you used localhost and port 60 in gcnet_nginx.conf like this:
        LINE 8:  listen      60;
        LINE 29: proxy_pass http://localhost:8060;

4. Create two directories inside of C:/nginx/ or wherever you downloaded nginx::

    Create directories:
        sites-enabled
        sites-available

    Copy monitoring_nginx.conf into the two directories


5. Edit C:/nginx/conf/nginx.conf (or wherever the nginx parent directory is stored on your machine)::

    Insert after line with "default_type  application/octet-stream;"
    (the syntax must have the exact gap between include and the path!):
    include         C:/nginx-1.19.1/sites-enabled/monitoring_nginx.conf;


    After line with " #gzip  on;" change the port in this section:

        server {
            listen       80;
            server_name  localhost;

    Change port from 80 to a non-essential port like 10, as 80 will be utilized for the Django project.

    For example:

        server {
            listen       10;
            server_name  localhost;

    Make sure to save changes to nginx.conf

6. Open a terminal at C:/nginx/ (or wherever the nginx parent directory is stored on your machine)
   and run this to check that the syntax of nginx.conf is correct::

    nginx.exe -t

    If the syntax of correct a message similar to this one will print:
        nginx: the configuration file C:\nginx-1.19.1/conf/nginx.conf syntax is ok
        nginx: configuration file C:\nginx-1.19.1/conf/nginx.conf test is successful


7. If everything is successful run this to start the server::

        nginx.exe

       To verify NGINX is running you can check Task Manager.


8. Next navigate to the project directory in a terminal. Make sure virtual environment created earlier
with Django and other dependencies is activated. Run the server::

    python runserver.py

9. Then open a web browser and navigate to::

    http://localhost (or the IP address or domain name used in the conf files)

-----
API
-----

The API has separate documentation.

Visit https://www.envidat.ch/data-api/gcnet/ or open gcnet/templates/index.html in a browser to view documentation.

Parameters used in API calls::

   {parameter}          NAME [UNITS]

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
   swout_minimum        Shortwave Outgoing Radiation Minimum [W m^-2]
   netrad_max           Net Radiation Maximum [W m^-2]
   airtemp1_maximum     Thermocouple Air Temperature 1 Maximum [degC]
   airtemp2_maximum     Thermocouple Air Temperature 2 Maximum [degC]
   airtemp1_minimum     Thermocouple Air Temperature 1 Minimum [degC]
   airtemp2_minimum     Thermocouple Air Temperature 2 Minimum [degC]
   windspeed_u1_maximum Wind Speed 1 Maximum [m s^-1]
   windspeed_u2_maximum Wind Speed 2 Maximum [m s^-1]
   windspeed_u1_stdev   Wind Speed 1 Standard Deviation [m s^-1]
   windspeed_u2_stdev   Wind Speed 2 Standard Deviation [m s^-1]
   reftemp              Reference Temperature [degC]


