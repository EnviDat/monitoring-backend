Monitoring-Backend
===============================

Python software package that processes, filters and calibrate times series environmental monitoring data. Serves the data
in a dynamic Django API.

----------------------
Important Information
----------------------

WARNING: project/settings.py LINE 30 DEBUG setting should be False for security reasons before production deployment.
Leaving this setting at True is only ok during testing and development.

-----------------------------------------
Application Configuration and Operation
-----------------------------------------

For details on how to operate the GC-Net application, please see the README documentation at gcnet/README.rst

------------
Installation
------------

This software requires Python 3.8 and Django, it was developed using PyCharm IDE.

To install gcnet-backend follow these steps:

1. Clone the gcnet-backend repo from Github::

    https://github.com/EnviDat/monitoring-backend.git



2. It is recommended to create a virtual environment for this project.

   For example::

    python -m venv <path/to/project/<venv-name>


3. Activate new virtual environment::

    On macOS and Linux:
    source <venv_name>/bin/activate

    On Windows:
    .\<venv_name>\Scripts\activate


4. Install the dependencies into your virtual environment::

     pip install -r requirements.txt


5. Verify dependencies are installed correctly by running::

    pip list --local


--------------------
.env Configuration
--------------------

WARNING: Never commit the .env file to GitHub!

Create a .env file at project/.env and enter your secret key, port, and database settings ("db" means database).
A .env file must be added to the "project" directory so that that database and NGINX server operate securely and correctly.
project/settings.py reads the values from this .env file. This project was developed using a Postgres database.
If using a local Postgres database the port number will probably be 5432.

Official documentation on why it is critical to set and protect SECRET_KEY: https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/#secret-key

ALLOWED_HOST_1 and ALLOWED_HOST_2 are the IP address(es) of the server. One of these can be set to 'localhost' during development.

PORT is the port number used by the NGINX server in runserver.py

By default Django writes to the public schema of a Postgres database. These settings should be entered in the DATABASE_xxx settings.

This application uses the MonitoringRouter in project/routers.py to direct database operations to the correct schema.
In your database make sure to have a "lwf" schema in the database used in the LWF_DB_xxx settings and a "gcnet" schema
in the database used in the GCNET_DB_xxx settings.

.env Configuration Template::

    SECRET_KEY=<secret key>

    ALLOWED_HOST_1=<localhost or IP address of server>
    ALLOWED_HOST_2=<localhost or IP address of server>
    PORT=<port number used by NGINX server in runserver.py>

    DATABASE_NAME=<db_name>
    DATABASE_USER=<db_user>
    DATABASE_PASSWORD=<db_password>
    DATABASE_HOST=<localhost or IP address of server where DB is hosted>
    DATABASE_PORT=<5432 or whichever port is assigned to DB>

    LWF_DB_SCHEMA="-c search_path=lwf"
    LWF_DB_NAME=<db_name>
    LWF_DB_USER=<db_user>
    LWF_DB_PASSWORD=<db_password>
    LWF_DB_HOST=<localhost or IP address of server where DB is hosted>
    LWF_DB_PORT=<5432 or whichever port is assigned to DB>

    GCNET_DB_SCHEMA="-c search_path=gcnet"
    GCNET_DB_NAME=<db_name>
    GCNET_DB_USER=<db_user>
    GCNET_DB_PASSWORD=password
    GCNET_DB_HOST=<localhost or IP address of server where DB is hosted>
    GCNET_DB_PORT=<5432 or whichever port is assigned to DB>


