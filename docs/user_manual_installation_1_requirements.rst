************
Requirements
************

.. index:: requirements
.. index:: dependencies

.. role:: bash(code)
   :language: bash

.. note::
    If you download the frozen application (`from the download page <https://www.hydroffice.org/soundspeed/main>`_),
    you don't need to care about dependencies (and may just skip this section).

If you decide to install the package in a Python environment, the dependencies are:

* `basemap <https://github.com/matplotlib/basemap>`_
* `gdal <https://github.com/OSGeo/gdal>`_
* `gsw <https://github.com/TEOS-10/python-gsw>`_
* `matplotlib <https://github.com/matplotlib/matplotlib>`_
* `pillow <https://github.com/python-pillow/Pillow>`_
* `netcdf4 <https://github.com/Unidata/netcdf4-python>`_
* `numpy <https://github.com/numpy/numpy>`_
* `pyproj <https://github.com/jswhit/pyproj>`_
* `pyseriale <https://github.com/pyserial/pyserial>`_
* `PySide <https://github.com/PySide/PySide>`_ *(only for the application)*

If you want to install the last stable version (from PyPI):

* :bash:`pip install hyo.soundspeed`

Or, if you prefer the last bleeding edge code:

* :bash:`pip install https://github.com/hydroffice/hyo_soundspeed/archive/master.zip`
