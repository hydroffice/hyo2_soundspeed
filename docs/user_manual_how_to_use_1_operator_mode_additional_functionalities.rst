.. _additional_functionalities:

**************************
Additional Functionalities
**************************

Create a WOA or RTOFS profile
-----------------------------

.. index:: WOA, synthetic profile
.. index:: RTOFS, synthetic profile

It is possible to upload a single WOA or RTOFS profile to *SIS*.
This can be done by first selecting WOA09 atlas or RTOFS atlas under the *Input data* button in the *Editor* toolbar
(:numref:`editor_tab12`).

.. _editor_tab12:
.. figure:: ./_static/editor_tab12.png
    :width: 360px
    :align: center
    :alt: data storage
    :figclass: align-center

    The *Input data* button in the *Editor* toolbar.

This will trigger a series of question dialogs for the query position that will use the SIS data/position
input or a user provided input. After, a surface sound speed can be applied,
and finally the resulting cast can be sent as described in :ref:`data_transmission`.

The new cast will be given the filename YYYYMMDD_HHMMSS_WOA or YYYYMMDD_HHMMSS_RTOFS with the date/time
in the filename based on the query time of the cast.


Request profile from SIS
------------------------

.. index:: SIS, profile

The *Input data* in the *Editor* toolbar can also be used to retrieve the cast currently being used by *SIS* and
use it to create a new profile.

This is only possible if the package is receiving data transmissions from *SIS*.
If it is not, the package will request a cast and will wait a few seconds until it times out on the request.
During this wait period, the package will be unresponsive to further user interaction.

If a profile is received, it will be given the name ``YYYYMMDD_HHMMSS_SIS`` with the date/time in the filename
based on the cast time recorded by *SIS*.

There are a number of shortcomings regarding the Kongsberg datagram format for sound speed profiles:

* It does not preserve the latitude/longitude of the observed cast. You will be prompted to enter the position of the cast when you request the cast from SIS. It is up to you to determine the position as accurately as you require it to be, perhaps by consulting CTD/XBT logs.
* The observation time associated with the cast is known to be incorrect in the *SIS* sound speed profile datagram format so it is not necessarily straightforward to use the observation time to look up the navigation.
* Temperature and salinity are not included in the datagram, even if they are provided to *SIS* when the associated cast was originally uploaded (they are preserved internally in SIS, however).

These shortcomings are overcome through the use of the “W” datagram in *SIS*, however, it is not currently possible
to dynamically request this datagram from *SIS* (though it is possible to have *SIS* broadcast it
as discussed in the section :ref:`method_2`).

Using a reference cast
----------------------

There are several scenarios where a CTD profile can be used as a reference cast by this package:

* To support XBT measurements by providing a salinity profile measurement in place of using an assumed constant salinity
* To augment SVP/XSV casts with temperature and salinity profiles to improve seafloor backscatter attenuation corrections
* Since CTD casts typically sample much deeper than most XBT probes, to provide an improved vertical extrapolation to the XBT cast.

To establish a reference cast, the desired cast is imported using the same mechanism described in :ref:`data_import`.
After that the profile is verified, edited and perhaps extended further in depth using an oceanographic database,
it is set as the reference profile by selecting "Reference cast" in the *Editor* toolbar (:numref:`editor_tab13`).

.. _editor_tab13:
.. figure:: ./_static/editor_tab13.png
    :width: 640px
    :align: center
    :alt: data storage
    :figclass: align-center

    The *Reference cast* button in the *Editor* toolbar.

Once a profile is set as the reference cast, the reference profile is drawn in orange.
This cast is retained in memory as the currently loaded cast to allow for additional operations,
such as exporting or transmission to a sounder. The reference profile can be cleared from memory at any time
via the *Clear reference cast* option under the *Reference cast* menu (:numref:`editor_tab14`).
Further extensions and augmentations will then use WOA/RTOFS.

.. _editor_tab14:
.. figure:: ./_static/editor_tab14.png
    :width: 280px
    :align: center
    :alt: reference cast
    :figclass: align-center

    The *Reference cast* tool.

The reference cast can be reimported into memory by choosing *Reload reference cast as current profile* from the *Reference cast* menu.
This will load a copy of the reference cast into memory for further manipulation.
If desired, the edited version can then be set as the new reference cast and will replace the previous version.
Prior to setting a cast as the reference cast, it is advisable to store it in database such that future sessions
do not need to repeat any reference cast processing.

Refraction monitor
------------------

.. note::
    This plugin is currently disabled.

An experimental feature has been set up to allow the user to establish the impact
of their currently loaded sound speed profile on the refraction correction by plotting swath data
with the new sound speed profile applied prior to sending the profile to the multibeam echosounder.

This provides a preview of the effect of the new sound speed profile allowing appropriate action
if the results are not as expected without introducing artifacts into the multibeam data stream.

.. Figure – Refraction monitor showing the effects of new sound speed profile before its application, as well as the application of a bias using the Profile Correction slider (at the bottom)

.. As an example scenario, the currently loaded profile is requested from *SIS* and is set as the reference profile.
    A new WOA profile can then be generated using the reported position from *SIS*.

.. The refraction monitor can thus be used to evaluate if the profile in use by *SIS* does a better refraction correction
    than the WOA profile. The refraction correction from the WOA profile can be adjusted using the slider bar
    in the *Refraction Monitor*, this adds a bias to the WOA profile (units are dm/s) and then recomputes
    the new potential swath profile using the adjusted WOA profile.
    If the user decided to send this profile to *SIS* and if the refraction corrector was non-zero,
    the package will ask the user whether or not they want to apply this corrector to the currently loaded profile
    prior to sending it to the echosounder.

.. A few other notes on the *Refraction Monitor*:
    * If the *Refraction Monitor* window is closed, the slider bar corrector value is ignored during transmission of a profile.
    * The *Refraction Monitor* window will close automatically when the package closes a profile or generates a new profile.
    * If running in *Server mode*, the slider bar corrector value is applied during transmission without user confirmation.
    * The slider bar corrector value is reset to zero after transmission of the profile both for measured profiles and server profiles.

.. index:: refraction; monitor

Network data reception
----------------------

The package is configurable to listen on specified ports for UDP input of sound speed cast data.
Currently supported systems are *MVP* and *Sippican*. See :ref:`app_b_connection_settings` for more on how
to configure these systems. The port numbers associated with various data sources can be changed
in the ``setup.db`` file using the *Setup* tab.

Upon reception of a network cast, the display panels will be colored red to indicate that operator intervention
is required in order to further process the data and deliver it to the multibeam acquisition system.
Once the cast has been processed and delivered, the statusbar color-coding will return to the normal background.

If the *Server mode* happened to have been running at the moment of reception, it will be stopped and
the received cast will be displayed as described above.
