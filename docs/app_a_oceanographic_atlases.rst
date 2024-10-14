.. _app_a_oceanographic_atlases:

**********************************
Appendix A - Oceanographic Atlases
**********************************


World Ocean Atlas
=================

.. index:: WOA; description

The World Ocean Atlas is a 3-dimensional grid of mean temperature and salinity for the world’s oceans
that is based upon a large set of archived oceanographic measurements in the World Ocean Database.

More information about the World Ocean Atlas 2009 (WOA09) can be found
`online <http://www.nodc.noaa.gov/OC5/WOA09/pr_woa09.html>`_

The WOA09 netCDF temperature and salinity grids used by the package can be accessed
from `http://www.nodc.noaa.gov/OC5/WOA09/netcdf_data.html <http://www.nodc.noaa.gov/OC5/WOA09/netcdf_data.html>`_

The files required are:

* *temperature_annual_1deg.nc*
* *temperature_seasonal_1deg.nc*
* *temperature_monthly_1deg.nc*
* *salinity_annual_1deg.nc*
* *salinity_seasonal_1deg.nc*
* *salinity_monthly_1deg.nc*

Basin and land/sea masks can be downloaded
from: `http://www.nodc.noaa.gov/OC5/WOA09/masks09.html <http://www.nodc.noaa.gov/OC5/WOA09/masks09.html>`_


Global Real-Time Ocean Forecast System
======================================

.. index:: RTOFS; description

The Global Real-Time Ocean Forecast System (RTOFS Global) is a 1/12°, 3-D oceanographic forecast model.
More information can be found online at: `http://polar.ncep.noaa.gov/global/ <http://polar.ncep.noaa.gov/global/>`_

Daily forecast/nowcast grids can be downloaded via the URL listed above, but the file sizes for the daily forecast
are prohibitive for use at sea. Instead, the package relies on the OpenDAP portal to download only small segments
of the nowcast grids for surrounding a specified query location. The downloaded subset is a 5x5 grid centered
on the query location.


Regional Operational Forecast System
====================================

.. index:: RegOFS; description

The NOAA Operational Forecast System (RegOFS) is a network of operational nowcast/forecast hydrodynamic models covering
a number of coastal regions in the USA. Models are run 4 times a day and generate current and short-term (0 to 48 hour)
forecast predictions of pertinent parameters such as water levels, currents, temperature, and salinity.

More information about RegOFS models can be found at:
`https://tidesandcurrents.noaa.gov/models.html <https://tidesandcurrents.noaa.gov/models.html>`_

Daily forecast/nowcast grids can be downloaded via the URL:
`https://opendap.co-ops.nos.noaa.gov/thredds/catalog.html <https://opendap.co-ops.nos.noaa.gov/thredds/catalog.html>`_

Similar to the RTOFS Global atlas, the package relies on the OpenDAP portal to download only small segments of the
nowcast grids surrounding a specified query location.

Currently the package supports a limited number of the RegOFS models. The full list of models with related support is
provided in the table below.

=========================================== =========== =======
Regional Operational Forecast System Model  Descriptor  Support
=========================================== =========== =======
Chesapeake Bay                              CBOFS       X
Deleware Bay                                DBOFS       X
Gulf of Maine                               GoMOFS      X
Northern Gulf of Mexico 2                   NGOFS2      X
Tampa Bay                                   TBOFS       X
Lake Erie                                   LEOFS       X
Lake Michignan and Huron                    LMHOFS      X
Lake Ontario                                LOOFS       X
Lake Superior                               LSOFS       X
Salish Sea and Columbia River               SSCOFS      X
San Francisco Bay                           SFBOFS      X
West Coast                                  WCOFS       X
New York and New Jersey                     NYOFS
St. John’s River                            SJROFS
=========================================== =========== =======


Synthetic cast values derived from atlases
==========================================

The cast extrapolation algorithm vertically extends temperature and salinity profiles as deep as possible
using the estimates immediately local to the area of the cast in either WOA or OFS.


WOA09-based profiles
--------------------

.. index:: WOA; WOA09

The World Ocean Atlas 2009 (WOA09) extension algorithm uses a nearest neighbor lookup in each of the 33 depth levels
in the grids within a 3x3 grid node search box centered on the cast’s geographic position.
This is roughly equivalent to a search radius of 1.5° or 90 nmi at the equator.
Note that this grid node search box becomes rapidly narrower in the east-west direction with latitude.
The nearest-neighbor geodetic distance is, however, correctly computed and the nearest neighbor will indeed be
the geographically most proximal grid node; the only shortcoming is that the lookup will ignore potentially
closer data in the east-west direction at high latitudes.

Future updates to the WOA09 extraction algorithms will remedy this shortcoming. The search radius is set this large
to enable the extension to at least estimate deeper temperature and salinity values in the case where the true depth
at the requested location is significantly larger than the coarse depth reported in the WOA09 grid
for that location (the WOA09 grid depth will generally always be smaller than the true depth).

The search algorithm will not respect topographic boundaries and may extrapolate profiles using data
from a neighboring oceanographic basin. Future versions of the algorithm will address this shortcoming as well,
likely with the use of the basin mask file provided with the WOA09 data set.


WOA13-based and WOA18-based profiles
------------------------------------

.. index:: WOA; WOA13; WOA18

WOA13 represents the ocean state variables of temperature and salinity with more detail and less uncertainty than
WOA09 due to large increases in data holdings and better temporal and spatial coverage coupled with refined analysis
and quality control techniques:

* Increased vertical resolution (3x in the upper ocean, 2x below 1500 m.)
* Increased spatial resolution (16x)
* Release of the decadal climatologies which were used to calculate the final 1955-2012 long-term climatological mean fields.

In the specific, the package uses the WOA13v2 release that was prepared to address both methodology concerns and,
to a lesser extent, quality control concerns which have surfaced since the initial release of WOA13.

WOA18 was released September 30, 2018. It includes approximately 3 million new oceanographic casts added to the WOD,
as well as renewed and updated quality control.

.. _rtofs_based_profiles:

RTOFS-based profiles
--------------------

.. index:: RTOFS; synthetic profile

The RTOFS extension algorithm differs in the size of the search area (5x5), roughly equivalent to a search radius
of 0.2° or 12.5 nmi at the equator. All of the shortcomings of the WOA09 lookup described above also apply
to the RTOFS lookup.

RegOFS-based profiles
---------------------

.. index:: RegOFS; synthetic profile

The Regional Operational Forecast System Models follow an approach similar to the :ref:`rtofs_based_profiles`.
However, the resulting search radius is function of the regular grid resolution at which each model output is published.


Profile Finalization
--------------------

The final extrapolation to a depth of 12,000 m is done using the values measured by *(Taira et al., 2005)*
in Challenger Deep. This could be improved by searching for the nearest neighbor grid node at the deepest level
observed in the basin using the basin mask file.
