inciweb-wildfires
=================

Download wildfire incidents data from `InciWeb <https://inciweb.nwcg.gov/>`_.

Installation
------------

::

    $ pipenv install inciweb-wildfires


Command-line usage
------------------

::

    Usage: inciwebwildfires [OPTIONS] COMMAND [ARGS]...

      A command-line interface for downloading wildfire incidents data from InciWeb.

      Returns GeoJSON.

    Options:
      --help  Show this message and exit.

    Commands:
      fires  Download active fire incidents from InciWeb


Download active fire incidents from inciweb. ::

    $ inciwebwildfires fires


Python usage
------------

Import the library. ::

    >>> import inciweb_wildfires

Download a GeoJSON of active fire incidents from inciweb. Returns GeoJSON. ::

    >>> data = inciweb_wildfires.get_fires()


Contributing
------------

Install dependencies for development. ::

    $ pipenv install --dev

Run tests.::

    $ make test

Shipping new version to PyPI. ::

    $ make ship


Developing the CLI
------------------

The command-line interface is implemented using Click and setuptools. To install it locally for development inside your virtual environment, run the following installation command, as `prescribed by the Click documentation <https://click.palletsprojects.com/en/7.x/setuptools/#setuptools-integration>`_. ::

    $ pip install --editable .
