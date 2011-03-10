Descartes-bi	
=============

Descartes-bi is a database agnostic, Django based business intelligence tool.

![screenshot](http://img263.imageshack.us/img263/1582/screenshotbo.png)


Implementation
--------------

Descartes-bi encapsulates small snnipets of SQL in pseudo-objects called series, that can later be combined to create comparative charts.  Aside from containing series, charts can also define parameters for user interaction.  Parameters (called filters) can be programmed to be restrictive using a custom permission system.

Installation
------------

 * Python 2.6
 * Django 1.2.5


Setting up
----------

By default the project is set up to run on a SQLite database. Run::

    $ python manage.py syncdb

Point SOURCE_DATABASE_* to the data source from with you will extract the data for your charts:
Example:

    SOURCE_DATABASE_ENGINE = 'mysql'

    SOURCE_DATABASE_NAME = 'domain_users'

    SOURCE_DATABASE_USER = 'it_user1'

    SOURCE_DATABASE_PASSWORD = 'it_user_password'

    SOURCE_DATABASE_HOST = ''

    SOURCE_DATABASE_PORT = ''


Executing
---------

Use:

    $ python manage.py runserver



Creating charts
---------------

Go into the admin site and start creating SQL queries to extract data from your data source DB and combine them into different charts.


License
-------
Descartes-bi is licensed under the terms of the GNU License version 3, see the included LICENSE file.
