HydrOffice Sound Speed Manager
==============================

.. image:: https://github.com/hydroffice/hyo2_soundspeed/raw/master/hyo2/ssm2/app/gui/soundspeedmanager/media/app_icon.png
    :alt: logo

|

.. image:: https://img.shields.io/pypi/v/hyo2.ssm2.svg
    :target: https://pypi.python.org/pypi/hyo2.ssm2
    :alt: PyPi version

.. image:: https://img.shields.io/badge/docs-latest-brightgreen.svg
    :target: https://www.hydroffice.org/manuals/ssm2/index.html
    :alt: Latest Documentation

.. image:: https://github.com/hydroffice/hyo2_soundspeed/actions/workflows/ssm_on_windows.yml/badge.svg?branch=master
    :target: https://github.com/hydroffice/hyo2_soundspeed/actions/workflows/ssm_on_windows.yml
    :alt: Windows

.. image:: https://github.com/hydroffice/hyo2_soundspeed/actions/workflows/ssm_on_linux.yml/badge.svg?branch=master
    :target: https://github.com/hydroffice/hyo2_soundspeed/actions/workflows/ssm_on_linux.yml
    :alt: Linux

.. image:: https://app.codacy.com/project/badge/Grade/c1eccd9e15a7408fb05aab06034e005e
    :target: https://www.codacy.com/gh/hydroffice/hyo2_soundspeed/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=hydroffice/hyo2_soundspeed&amp;utm_campaign=Badge_Grade
    :alt: codacy

.. image:: https://coveralls.io/repos/github/hydroffice/hyo2_soundspeed/badge.svg?branch=master
    :target: https://coveralls.io/github/hydroffice/hyo2_soundspeed?branch=master
    :alt: coverall

.. image:: https://zenodo.org/badge/54854024.svg
   :target: https://zenodo.org/badge/latestdoi/54854024
   :alt: Zenodo DOI

|

* Code: `GitHub repo <https://github.com/hydroffice/hyo2_soundspeed>`_
* Project page: `url <https://www.hydroffice.org/soundspeed/>`_, `download <https://bitbucket.org/hydroffice/hyo_sound_speed_manager/downloads/>`_
* License: LGPLv2.1 or IA license (See `Dual license <https://www.hydroffice.org/license_lgpl21/>`_)

|

General Info
------------

The HydrOffice's Sound Speed package provides a library and tools to manage sound speed profiles.
The package is part of HydrOffice, a research development framework for ocean mapping.  HydrOffice aims to provide
a collection of hydro-packages to deal with specific issues in the field, speeding up both algorithms testing and
research-to-operation (R2O).

Among the tools developed in the package, Sound Speed Manager (SSM) is a software application that provides the user
with a streamlined workflow to perform accurate processing and management of sound speed profiles
for underwater acoustic systems.

SSM has been designed to ease integration into existing data acquisition workflows.
The liberal open source license used by the project (specifically, GNU LGPL) provides for understanding
of the chosen processing solutions through ready inspection of the source code, as well as the ability
to adapt the application to specific organization needs.

This adaptation is eased by the modular design of the application, with the NOAA-specific
functionalities organized so that they can be easily deactivated for non-NOAA users.

The main functionalities include:

* Wide support of commonly-used sound speed profile formats
* Compatibility with various data sources
* Integration with common data acquisition/integration applications (e.g., Kongsberg SIS)
* Profile enhancement based on real-time and climatologic models
* Database management of the collected data with built-in functionalities for analysis and visualization.

With a long-term support and development plan, Sound Speed Manager is a turnkey application ready
to be used (and extended) by professionals and institutions in the hydrographic community.

The package is jointly developed by the `Center for Coastal and Ocean Mapping, UNH <https://ccom.unh.edu/>`_ and
`NOAA Coast Survey Development Laboratory (CSDL) <https://www.nauticalcharts.noaa.gov/>`_.

.. image:: https://www.hydroffice.org/static/app_soundspeed/img/noaa_ccom.png
    :alt: joint efforts

For further information, visit the `manual <https://www.hydroffice.org/manuals/ssm2/index.html>`_.

.. note::
   If you want to help improving SSM, this is the recommended
   `starting point <https://www.hydroffice.org/manuals/ssm2/stable/developer_guide_how_to_contribute.html>`_.
