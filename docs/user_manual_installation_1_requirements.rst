************
Requirements
************

.. index:: requirements
.. index:: dependencies

.. role:: bash(code)
   :language: bash

.. note::
    If you download the frozen application (`from the download page <https://www.hydroffice.org/soundspeed/main>`_),
    you don't need to care about dependencies (and you may just skip this section).

Installation using the Pydro distribution
=========================================

.. index:: Pydro

.. _pydro_logo:
.. figure:: ./_static/noaa_ocs_pydro.png
    :width: 100px
    :align: center
    :alt: Pydro logo
    :figclass: align-center

    The Pydro logo.

If you are on Windows, you can easily install Sound Speed Manager as part of the `NOAA Office of Coast Survey Pydro <http://svn.pydro.noaa.gov/Docs/Pydro/_build_online/html/>`_ distribution.

Pydro is a suite of software tools used to support hydrography. It is (almost exclusively) built from open source components as well as public domain custom developed software. Pydro is maintained by Hydrographic Systems and Technology Branch (HSTB) to support NOAA operations (aiding Office of Coast Survey fleet) and is made available for public use.

You can download the latest Pydro installer from `here <http://svn.pydro.noaa.gov/Docs/Pydro/_build_online/html/downloads.html>`_.

Installation as stand-alone Python package
==========================================

If you decide to install the package in a Python environment, the dependencies are:

* `basemap <https://github.com/matplotlib/basemap>`_
* `gdal <https://github.com/OSGeo/gdal>`_
* `gsw <https://github.com/TEOS-10/python-gsw>`_ *(version == 3.0.6)*
* `matplotlib <https://github.com/matplotlib/matplotlib>`_
* `pillow <https://github.com/python-pillow/Pillow>`_
* `netcdf4 <https://github.com/Unidata/netcdf4-python>`_
* `numpy <https://github.com/numpy/numpy>`_
* `pyproj <https://github.com/jswhit/pyproj>`_
* `pyserial <https://github.com/pyserial/pyserial>`_
* `PySide <https://github.com/PySide/PySide>`_ *(only for the application)*

If you want to install the last stable version (from PyPI):

* :bash:`pip install hyo2.soundspeed`

Or, if you prefer the last bleeding edge code:

* :bash:`pip install https://github.com/hydroffice/hyo_soundspeed/archive/master.zip`

