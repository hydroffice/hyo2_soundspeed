********
In Brief
********


.. image:: https://github.com/hydroffice/hyo2_soundspeed/raw/master/hyo2/ssm2/app/gui/soundspeedmanager/media/app_icon.png
    :alt: logo

Sound Speed Manager (SSM) is a software application that provides the user with a streamlined workflow to perform
accurate processing and management of sound speed profiles for underwater acoustic systems.

SSM has merged together functionalities present in several applications that process sound speed profiles (SSP):

* *Velocipy*, an application originally developed at the `NOAA Coast Survey Development Laboratory (CSDL) <https://www.nauticalcharts.noaa.gov/>`_
  as part of the `Pydro environment <https://svn.pydro.noaa.gov/Docs/html/Pydro/universe_overview.html>`_.

* *SVP Editor*, an application originally developed at the `Center for Coastal and Ocean Mapping, UNH <https://ccom.unh.edu/>`_
  for the MAC project (`Multibeam Advisory Committee <http://mac.unols.org/>`_)
  under the NSF grant 1150574.

* *SSP Manager*, an application developed at the `Center for Coastal and Ocean Mapping, UNH <https://ccom.unh.edu/>`_
  as part of the HydrOffice framework under NOAA grants NA10NOS4000073 and NA15NOS4000200.

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

The current development of Sound Speed Manager is partially supported by:

* NOAA grant NA20NOS4000196, and
* NSF grant 1933720.

Operation modes
===============

.. index::
   single: mode; operation

Currently, the hydro-package can operate in two mutually exclusive operation modes:

1.	*Operator Mode*
2.	*Synthetic Profile Server Mode*

The :ref:`operator_mode` represents the primary mode, and it is used to convert data from different source formats,
to graphically edit them, and to export/send the resulting profiles for use by underwater acoustic systems.
Optional steps are the augmentation with measurements from a reference cast (to either improve salinity modeling
or extrapolate the cast to the required depth), either manually specifiying a loaded profile as reference cast,
or deriving the reference from oceanographic models (currently, WOA09, WOA13, WOA18 and RTOFS) as described
in :ref:`app_a_oceanographic_atlases`.

The :ref:`server_mode` was developed to deliver WOA/RTOFS-derived synthetic SSPs to one or more network clients in
a continuous manner, enabling opportunistic mapping while underway. Given the uncertainty of such an approach,
this mode is expected to only be used in transit, capturing the current position and using it as input to lookup
into the selected oceanographic model.


Currently implemented features
==============================

* Import of several commonly used sensor/file formats:

  * AML (.csv)
  * AOML AMVER-SEAS XBT (.txt)
  * CARIS (.svp)
  * Castaway (.csv)
  * Digibar Pro (.txt), and S (.csv)
  * ELAC Hydrostar (.sva)
  * Hypack (.vel)
  * Idronaut (.txt)
  * ISS Fugro (.svp, .v*, .d*)
  * Kongsberg Maritime (.asvp)
  * Rolls-Royce Moving Vessel Profiler (MVP) (.asvp, .calc, .m1, .s12)
  * Oceanscience Underway CTD (.asc)
  * SAIV (.txt)
  * Sea&Sun (.tob)
  * Seabird (.cnv)
  * Sippican XBT, XSV, and XCTD (.EDF)
  * Sonardyne (.pro)
  * Turo XBT (.nc)
  * University of New Brunswick (.unb)
  * Valeport Midas, MiniSVP, Monitor, RapidSVT, and SWiFT (.000, .txt, .vp2)

.. index:: format; supported inputs

* Network reception of data from:

  * Kongsberg Maritime SIS4 and SIS5
  * Basic NMEA 0183 streams (only GGA and GLL)
  * Sippican systems
  * Moving Vessel Profiler (MVP) systems

* Data visualization and interactive graphical inspection (e.g., outlier removal, point additions) of sound speed, temperature and salinity profiles

* Use of the World Ocean Atlas of 2009/2013/2018 (WOA09/13/18) and Real-Time Ocean Forecast System (RTOFS) for tasks such as:

  * Salinity augmentation for Sippican XBT probes
  * Temperature/salinity augmentation for Sippican XSV probes and SVP sensors
  * Vertical extrapolation of measured profiles
  * Creation of synthetic sound speed profiles from the model of choice

* Augmentation of sound speed profile surface layer with measured surface sound speed (from Kongsberg SIS or manually)

* Designation of a reference profile, for example from a deep CTD, for use in tasks such as:

  * Salinity augmentation for Sippican XBT probes
  * Temperature/salinity augmentation for Sippican XSV probes and SVP sensors
  * Vertical extrapolation of measured profiles

* Export of several file formats:

  * Caris (.svp) (V2, multiple casts supported)
  * Comma separated values (.csv)
  * ELAC Hydrostar (.sva)
  * Hypack (.vel)
  * iXBlue (.txt)
  * Kongsberg Maritime (.asvp, .ssp and .abs)
  * NCEI (.nc)
  * QPS (.bsvp)
  * Sonardyne (.pro)
  * University of New Brunswick (.unb)

.. index:: format; supported outputs

* Network transmission of processed casts to data acquisition systems (see :ref:`app_b_connection_settings`):

  * Kongsberg Maritime SIS4 and SIS5
  * QPS QINSy
  * Reson PDS2000
  * Hypack

.. index:: transmission; supported protocols

* Persistent storage of collected SSP data in a SQLite database

* Survey data monitoring (see :ref:`data_monitor_tool`)

Compared Functionalities
========================

============================================ ============================== ================ ===================
                Functionality                       Sound Speed Manager         Velocipy         SSP Manager
============================================ ============================== ================ ===================
Input of Kongsberg format                                **x**                   **x**
Input of OceanScience format                             **x**                   **x**
Input of Seacat serial data                              **x**                   **x**
Output of NCEI format                                   **\^**                   **x**
Output of QPS format                                     **x**                   **x**
Support of WOA13 atlas                                   **x**                   **x**
Data filtering/smoothing                                 **x**                   **x**
DQA analysis                                             **x**                   **x**
Calculation of profile statistics                        **x**                   **x**
Input of Digibar Pro format                              **x**                   **x**              **x**
Input of Idronaut format                                 **x**                                      **x**
Input of Fugro ISS format                               **\^**                                      **x**
Input of SAIV format                                     **x**                                      **x**
Input of Turo format                                     **x**                                      **x**
Input of Valeport format                                **\^**                                      **-**
Output of Elac format                                    **x**                   **x**              **x**
Output of iXBlue format                                  **x**                                      **x**
Output of Sonardyne format                               **x**                                      **x**
Output of UNB format                                     **x**                                      **x**
Retrieval of current SIS profile                         **x**                                      **x**
Retrieval/View/Use of SIS data                          **\^**                                      **x**
SIS data view                                            **x**                                      **x**
Portable profiles database (SQLite)                      **x**                                      **x**
Export to geospatial formats                            **\^**                                      **x**
Multiple setups                                          **x**                                      **x**
HTML/PDF manuals                                         **x**                                      **x**
Public stand-alone installer                             **x**                                      **x**
Synthetic Profile Server mode                            **x**                                      **x**
Output of Kongsberg format                               **\^**                  **x**              **x**
Input of AML format                                      **x**
Input of AOML format                                     **x**
Input of Caris format                                    **x**
Input of ELAC format                                     **x**
Input of Hypack format                                   **x**
Input of Sonardyne format                                **x**
Automated processing steps                               **x**
Data management for multiple projects                    **x**
Surface sound speed monitoring                           **x**
Cast timing based on past data                           **x**
============================================ ============================== ================ ===================

Symbols: **x** = *New functionality*; **-** = *Basic functionality*; **\^** = *Improved functionality*
