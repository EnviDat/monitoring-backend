# Monitoring-Backend

Python software package that processes, filters and calibrate times
series environmental monitoring data. Serves the data in a dynamic
Django API.

## Important Information

WARNING: project/settings.py LINE 30 DEBUG setting should be False for
security reasons before production deployment. Leaving this setting at
True is only ok during testing and development.

## Application Configuration and Operation

For details on how to operate the GC-Net application, please see the
README documentation at gcnet/README.rst

## Installation

This software requires Python 3.8 and Django, it was developed using
PyCharm IDE.

To install gcnet-backend follow these steps:

1.  Clone the gcnet-backend repo from Github:

        https://github.com/EnviDat/monitoring-backend.git

2.  Ensure PDM is installed on your system and pep528 support is
    enabled.

    <https://pdm.fming.dev/latest/usage/pep582/>

3.  Install the dependencies using PDM

    For example:

        pdm install

        As per PEP582, dependencies are located under __pypackages__

## Database Setup and .env Configuration

WARNING: Never commit the .env file to GitHub!

Create a .env file at project/.env and enter your secret key, port, and
database settings ("db" means database). A .env file must be added to
the "project" directory so that that database and NGINX server operate
securely and correctly. project/settings.py reads the values from this
.env file. This project was developed using a Postgres database. If
using a local Postgres database the port number will probably be 5432.

Official documentation on why it is critical to set and protect
SECRET_KEY:
<https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/#secret-key>

ALLOWED_HOSTS contains the IP or domain of the server.
This is set to '\*' during development automatically.

PORT is the port number used by the NGINX server in runserver.py

By default Django writes to the public schema of a Postgres database.
These settings should be entered in the DATABASE_xxx settings.

This application uses the MonitoringRouter in project/routers.py to
direct database operations to the correct schema. In your database make
sure to have a "lwf" schema in the database used in the LWF_DB_xxx
settings and a "gcnet" schema in the database used in the
GCNET_DB_xxx settings.

.env Configuration Template:

    SECRET_KEY=<secret key>

    ALLOWED_HOSTS='["<IP or Domain>", "<IP or Domain>"]'
    PROXY_PREFIX=<Optional URL prefix if required / served behind a proxy>
    LOG_LEVEL=<Log level for app printing to STDOUT>

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
