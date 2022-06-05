********
In Brief
********


.. image:: https://github.com/hydroffice/hyo2_soundspeed/raw/master/hyo2/soundspeedmanager/media/app_icon.png
    :alt: logo

The Sound Speed package is part of the `HydrOffice <https://www.hydroffice.org/license/>`_ framework. HydrOffice is
a research development environment for ocean mapping. It provides a collection of hydro-packages, each of them dealing
with a specific issue of the field. The main goal is to speed up both algorithms testing and research-to-operation (R2O).

The Sound Speed package provides both a library and an application with functionalities to manage sound speed profiles,
and to provide pre-processing ocean mapping tools to help bridge the gap between sound speed profiling instrumentation
and multibeam echosounder acquisition systems.

It has been developing with the aim to merge together functionalities present in several applications that process sound
speed profiles (SSP) for underwater acoustic systems:

* *Velocipy*, an application originally developed at the `NOAA Coast Survey Development Laboratory (CSDL) <http://www.nauticalcharts.noaa.gov/>`_
  as part of the Pydro environment.

* *SVP Editor*, an application originally developed at the `Center for Coastal and Ocean Mapping (CCOM, UNH) <http://ccom.unh.edu/>`_
  for the MAC project (`Multibeam Advisory Committee <http://mac.unols.org/>`_)
  under the NSF grant 1150574.

* *SSP Manager*, an application developed at the `Center for Coastal and Ocean Mapping (CCOM, UNH) <http://ccom.unh.edu/>`_
  as part of the HydrOffice framework under NOAA grants NA10NOS4000073 and NA15NOS4000200.

In the integration of all these implementations to the current package several improvements have been
introduced to enhance code maintainability (e.g., Python 3 support) and to store the collected data for further
processing and analysis.

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

  * Kongsberg Maritime SIS
  * Kongsberg Maritime K-Controller (*experimental*)
  * Sippican systems
  * Moving Vessel Profiler (MVP) systems

* Data visualization and interactive graphical inspection (e.g., outlier removal, point additions) of sound speed, temperature and salinity profiles

* Use of the World Ocean Atlas of 2009/2013 (WOA09/13) and Real-Time Ocean Forecast System (RTOFS) for tasks such as:

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
  * Kongsberg Maritime (.asvp and .abs)
  * NCEI (.nc)
  * QPS (.bsvp)
  * Sonardyne (.pro)
  * University of New Brunswick (.unb)

.. index:: format; supported outputs

* Network transmission of processed casts to data acquisition systems (see :ref:`app_b_connection_settings`):

  * Kongsberg Maritime SIS
  * Kongsberg Maritime K-Controller (*experimental*)
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
