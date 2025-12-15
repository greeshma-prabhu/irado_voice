Microsoft Azure CLI 'rdbms-connect' Extension
==========================================

This extension enables the command to connect to Azure Database for MySQL and Azure Database for PostgreSQL flexible server instances. .  

-----
Usage
-----

To install the extension separately can run:

:: 
    az extension add --name rdbms-connect

Then can run connect commands:

::
    az postgres flexible-server connect -n testServer -u username -p password

::
    az mysql flexible-server connect -n testServer -u username -p password

::
    az postgres flexible-server connect -n testServer -u username --interactive

::
    az mysql flexible-server connect -n testServer -u username --interactive

::
    az postgres flexible-server execute -n testServer -u username -p password --querytext "select * from pg_user;" --output table

::
    az mysql flexible-server execute -n testServer -u username -p password --querytext "select host, user from mysql.user;" --output table

::
    az postgres flexible-server execute -n testServer -u username -p password --file-path "./test.sql"

::
    az mysql flexible-server execute -n testServer -u username -p password --file-path "./test.sql"

--------
Switches
--------

**--name -n**
Name of the server. The name can contain only lowercase letters, numbers, and the hyphen (-) character. Minimum 3 characters and maximum 63 characters.
Can be pulled from local context.

**--admin-user -u**
The login username of the administrator.
Can be pulled from local context.

**--admin-password -p**
The login password of the administrator. 

**--database-name -d**
(Optional) The name of the database.  Uses default database if no value provided. 

**--querytext -q**
A query to run against the flexible server. 

**--file-path -f**
A sql file to run against the flexible server. 

.. :changelog:

Release History
===============

1.0.7
++++++
+ Remove msrestazure dependency

1.0.6
++++++
+ Add support for Python versions 3.9, 3.10 and 3.11 for dependency of psycopg2

1.0.5
++++++
+ Use compatible release for `setproctitle` to support Python 3.11

1.0.4
++++++
+ Update mycli and pgcli versions

1.0.3
++++++
+ Add support to read UTF-8 files with and without BOM

1.0.2
++++++
+ Use compatible release for `setproctitle` to support Python 3.10

1.0.1
++++++
+ Add rdbms-module to cloud shell

1.0.0
++++++
+ GA release for 'az postgres flexible-server connect' and 'az postgres flexible-server execute' commands.

0.1.4
++++++
+ GA release for 'az mysql flexible-server connect' and 'az mysql flexible-server execute' commands.

0.1.3
++++++
* Introduce query/sql file execution command as 'flexible server execute' command.
* [BREKAING CHANGE] Move query execution of the 'flexible server connect' command to 'flexible server execute' command.

0.1.2
++++++
* Improvements for the 'flexible server connect' command.

0.1.1
++++++
* Fix for --interactive mode for 'flexible server connect' command.

0.1.0
++++++
* Initial release of 'flexible server connect' command.
