.. _app_b_connection_settings:

********************************
Appendix B - Connection Settings
********************************

Settings for data reception
===========================

Moving Vessel Profiler
----------------------

.. index:: MVP

The MVP controller interface can be configured to transmit data via UDP using a variety of data format
and transmission protocols (:ref:`mvp_configuration_fig`).

.. _mvp_configuration_fig:

.. figure:: ./_static/mvp_configuration.png
    :width: 600px
    :align: center
    :height: 400px
    :alt: alternate text
    :figclass: align-center

    Figure – MVP Controller configuration dialog. Boxes A through C are required for transmission of cast information. Box D can be configured to transmit sensor data.

The MVP computer IP address and the IP address of the machine running the *SSM* package can be configured in *Box A*.
For newer versions of the MVP controller, it is recommended to choose the ``NAVO_ISS60`` transmission protocol
as this will allow for large cast files to be transmitted in several packets without overflowing
the UDP maximum packet size limitation (*Box B*). Older versions of the MVP controller software
(up to version ``2.35`` to the best of our knowledge) do not support the ``NAVO_ISS60`` protocol and
the package must be configured to use the ``UNDEFINED`` protocol in the SSP package configuration file.
The file format can be adjusted to accommodate a CTD with the ``S12`` format or a sound speed sensor
with the ``CALC`` or ``ASVP`` formats (Box C).

Note that the transmission protocol and file format must be configured in both the MVP controller interface and
in the the *Setup* tab (in the *Input* tab, to activate the MVP listener and, in the *Listeners* sub-tab,
for the communication settings).

Boxes D and E refer to raw instrument transmission settings that are configurable for future use.
Since casts received from an MVP system do not have a filename embedded in the data stream,
the *Sound Speed* package will name casts received using the following convention: ``YYYYMMDD_HHMMSS_MVP``.
The date/time stamp embedded in the filename will be the time of the cast.

.. note:: Once the MVP listener is activated, a "MVP" token will be visualized on the left side of the SSM's status bar.


Sippican
--------

.. index:: Sippican

There does not currently exist any internal mechanism in the Sippican software to broadcast data via UDP,
this capability has been included to accommodate vessels that use UDP network broadcasts
to log data from various systems. The expected data format is the Sippican native ``.EDF`` file format.

Note that a single Sippican data file can sometimes exceed the maximum buffer size for UDP packet transmissions.
If software is written to transmit Sippican data files via UDP, this limitation should be kept in mind.
The *Sound Speed* package currently only accepts transfer of a single UDP packet thus transmission software may need
to reduce the data by thinning the profile. Received profiles will use the filename embedded in the .EDF.


Settings for data transmission
==============================

The *Sound Speed* package can be configured to transmit data to a number of systems by selecting the *Transmit data*
button in the *Editor* tab.

For installations with multiple clients, the *Sound Speed* package will deliver the cast sequentially to all clients.
Failure on transmission to one client will not interfere with other clients. However, it will slow down
the transmission sequence through all clients for any clients who are timing out on confirmation of reception
as the *Sound Speed* package will wait up to the 'RX timeout' value defined in the setup (default: 20 seconds) for confirmation.

.. note:: Server mode will only *currently* work with the *SIS* transmission protocol.


.. _sis4:

Kongsberg SIS v4
----------------

.. index:: SIS v4

*SIS v4* does not require additional configuration to receive sound speed files since it always listens on port 4001
for input sound speed data.

The following indications are useful for monitoring reception of sound speed profiles:

* The SSP profile filename will be updated in the Runtime parameters menu in the form: ``YYYYMMDD_HHMMSS.asvp``.
  The date and time fields are populated based on the time stamp in the profile that was received from the SSP package.
  In the case of measured casts, this is the time of acquisition, as found in the input file.
  In the case of synthetic WOA profiles, the date/time is based on the time of transmission of the cast
  (using the computer clock where the SSP package is installed).
* *SIS* creates several files in the last location from which it loaded a sound speed profile.
* The SVP display window, if being viewed in *SIS*, will update with the new cast.
* In the event that a cast is rejected, *SIS* will launch a warning dialog to indicate that the cast it received was rejected.

Although *SIS v4* will always allow incoming sound speed transmissions, it has several restrictions
that must be observed in order for the data to be accepted (see *Kongsberg manual*).
As this particular transmission protocol is used by other acquisition systems, it is worth describing in detail
what the *Sound Speed* package does to the cast data to satisfy the input criteria for *SIS*.

The transmission procedure used by the SSP package will format the temperature and salinity profiles
into the Kongsberg Maritime format. Since the WOA/RTOFS grids only extend to a maximum depth of 5,500 m,
the profile undergoes a final extrapolation to a depth of 12,000 m to satisfy *SIS v4* input criteria,
this is done with temperature and salinity values measured in the Mariana Trench by *Taira et al. (2005)*.

Since *SIS v4* input profiles have a limit on the maximum allowable number of data points,
the sound speed profile is thinned using a modified version of the Douglas-Peucker line reduction method
as described by *Beaudoin et al. (2011)*. The algorithm begins with a small tolerance and increases it linearly
until the number of points in the profile falls below the maximum allowed by *SIS*.

By default, the cast header is formatted to instruct *SIS v4* to accept the profile for immediate application
without launching the *Kongsberg SVP Editor*. This behavior can be changed through the configuration file
by setting *Auto apply profile* to *False* (in the *Setup* tab). In this case, *SIS v4* will accept the cast
but will then launch its own editor interface and user interaction will be required on the *SIS v4* computer
in order to have the cast applied to the multibeam system.

Once the cast has been prepared for transmission, it is sent to *SIS v4* via UDP transmission over the network.
If *SIS v4* receives the profile and accepts it, it will rebroadcast the SVP datagram.
The *Sound Speed* package waits for this rebroadcast to ensure reception of the cast. The profile that was re-broadcasted
from SIS is compared against that which was sent. If they match, then the transmission is considered successful.
If there is a discrepancy, or if no rebroadcast profile is received, the user is notified that reception
could not be confirmed. The lower left status bar notifies the user of the various stages of this verification process.

In deep water, the rebroadcast event may take several seconds to occur and the software will wait up
to a user-defined amount of time (e.g., 20 seconds) for reception of the re-broadcasted SVP.
All other package functionalities are suspended during this wait period.

Hypack
------

.. index:: Hypack

The *Sound Speed* package can transmit data to *HYPACK* using *HYPACK*'s driver
for Moving Vessel Profiler (MVP) systems (``MVP.dll`` version 23.3.0.0 and above). The next figures provide a guidance on how to configure
a *HYPACK* 2023 project to receive data from the *Sound Speed* package.

First, open an existing project or create a new project using the Project Manager or Project Wizard (see :numref:`hypack_1_fig` and :numref:`hypack_2_fig`)

.. _hypack_1_fig:

.. figure:: ./_static/hypack_1.png
    :width: 600px
    :align: center
    :alt: alternate text
    :figclass: align-center

    The *HYPACK* Project Manager or the Project Wizard can be used to load or create a project.

.. _hypack_2_fig:

.. figure:: ./_static/hypack_2.png
    :align: center
    :height: 400px
    :alt: alternate text
    :figclass: align-center

    Selecting or creating a *HYPACK* project from the Project Manager.

.. _hypack_3_fig:

Once your project is selected, click the *Add device* button to add the MVP driver to the list of installed drivers.

.. figure:: ./_static/hypack_3.png
    :width: 600px
    :align: center
    :alt: alternate text
    :figclass: align-center

    Selecting the Add device button.

.. _hypack_4_fig:

.. figure:: ./_static/hypack_4.png
    :width: 600px
    :align: center
    :alt: alternate text
    :figclass: align-center

    Adding the MVP device driver.

Now, configure the network parameters accordingly. In this case, *HYPACK* and the *Sound Speed* package are running on the same computer.

.. _hypack_5_fig:

.. figure:: ./_static/hypack_5.png
    :width: 600px
    :align: center
    :alt: alternate text
    :figclass: align-center

    Configuring the MVP driver. The network parameters of the driver are configured to use a UDP input protocol in a client role. The host IP address must match the address used by the computer running the *Sound Speed* package and the reception port must match the port configuration chosen in the package configuration file. The “Write Port” is left as zero.

Press the *Setup* button to configure the MVP driver accordingly. See :numref:`hypack_6_fig` for a short description of the driver configuration features. 

.. _hypack_6_fig:

.. figure:: ./_static/hypack_6.png
    :align: center
    :height: 400px
    :alt: alternate text
    :figclass: align-center

    Additional configuration of the MVP device driver.

Press the *Test Device* button to test the MVP driver together with the *Sound Speed* Package.

.. _hypack_7_fig:

.. figure:: ./_static/hypack_7.png
    :align: center
    :height: 500px
    :alt: alternate text
    :figclass: align-center

    Testing reception capabilities in *HYPACK*. After having loaded a sample cast into the *Sound Speed* package and sent it, the profile should be visualized in *HYPACK*.

Once you are satisfied that the connection between the *Sound Speed* package and *HYPACK* works, start *HYSWEEP Survey*. A new permanent window displaying the received casts should be visible (See :numref:`hypack_9_fig`). An update of the "SV From Profile" value in :numref:`hypack_8_fig` is also an indicator that *HYSWEEP Survey* has received a new cast. 

.. _hypack_8_fig:

.. figure:: ./_static/hypack_8.png
    :align: center
    :height: 300px
    :alt: alternate text
    :figclass: align-center

    In HYSWEEP Survey, an update of the “SV From Profile” field should occur after reception of a new cast.

.. _hypack_9_fig:

.. figure:: ./_static/hypack_9.png
    :align: center
    :height: 400px
    :alt: alternate text
    :figclass: align-center

    In HYSWEEP, the MVP plot will display all received casts.

If the MVP driver has been configured as per :numref:`hypack_6_fig`, a new sound velocity file should be visible in *HYPACK* (See :numref:`hypack_10_fig`). A target should be also be visible in both HYPACK (See :numref:`hypack_10_fig`) and in the *HYSWEEP* Map display (See :numref:`hypack_11_fig`).

.. _hypack_10_fig:

.. figure:: ./_static/hypack_10.png
    :width: 700px
    :align: center
    :alt: alternate text
    :figclass: align-center

    In HYPACK, a new sound velocity file and a new target will appear if these options were selected in the MVP driver setup page.

.. _hypack_11_fig:

.. figure:: ./_static/hypack_11.png
    :align: center
    :height: 500px
    :alt: alternate text
    :figclass: align-center

    In HYSWEEP, the new target corresponding to the received cast will be displayed in the Map view.


QINSy
-----

.. index:: QINSy

QINSy accepts the same SVP transmission protocol as *SIS*, but a method to verify reception of the cast is
not currently known thus the user should confirm reception in the acquisition system.

.. _qinsy_1_fig:

.. figure:: ./_static/qinsy_1.png
    :width: 600px
    :align: center
    :height: 400px
    :alt: alternate text
    :figclass: align-center

    Select *Setup* from the QINSy console after loading your project. Refer to QINSy documentation for information regarding setting up a project.

.. _qinsy_2_fig:

.. figure:: ./_static/qinsy_2.png
    :width: 600px
    :align: center
    :height: 400px
    :alt: alternate text
    :figclass: align-center

    Edit your project database

.. _qinsy_3_fig:

.. figure:: ./_static/qinsy_3.png
    :width: 600px
    :align: center
    :height: 400px
    :alt: alternate text
    :figclass: align-center

    Right click the *Auxiliary Systems* icon and select *New System*.

.. _qinsy_4_fig:

.. figure:: ./_static/qinsy_4.png
    :width: 400px
    :align: center
    :height: 400px
    :alt: alternate text
    :figclass: align-center

    Configure the new system as shown above. Choose the same port number that SSP package will be sending casts to (this is configured in the ``__config__.db`` file).

.. _qinsy_5_fig:

.. figure:: ./_static/qinsy_5.png
    :width: 600px
    :align: center
    :height: 300px
    :alt: alternate text
    :figclass: align-center

    Choose *Echosounder Settings* from the *Settings* menu. This will allow you to configure the behavior of QINSy when it receives new sound speed profiles from SSP package.

.. _qinsy_6_fig:

.. figure:: ./_static/qinsy_6.png
    :width: 600px
    :align: center
    :height: 400px
    :alt: alternate text
    :figclass: align-center

    Left­click the icon for the *SVP Editor* device.

.. _qinsy_7_fig:

.. figure:: ./_static/qinsy_7.png
    :width: 600px
    :align: center
    :height: 400px
    :alt: alternate text
    :figclass: align-center

    Choose appropriate options to control QINSy’s behavior when it receives casts from SSP package.
    If you plan to deliver casts using ef:`server_mode`, remember to set the "Automatically Update Profile" flag.

.. _qinsy_8_fig:

.. figure:: ./_static/qinsy_8.png
    :width: 600px
    :align: center
    :height: 300px
    :alt: alternate text
    :figclass: align-center

    With QINSy “online” and recording, send a test profile from SSP package. If you have chosen to be informed upon reception of a new cast, a message window will appear for acknowledgement.

.. _qinsy_9_fig:

.. figure:: ./_static/qinsy_9.png
    :width: 600px
    :align: center
    :height: 400px
    :alt: alternate text
    :figclass: align-center

    By choosing *Echosounder Settings* from the *Settings* menu again, you can verify that the cast was received.


PDS2000
-------

.. index:: PDS2000

PDS2000 accepts the same SVP transmission protocol as SIS, but a method to verify reception of the cast is
not currently known thus the user must confirm reception in the acquisition system.

.. _pds_1_fig:

.. figure:: ./_static/pds_1.png
    :width: 600px
    :align: center
    :height: 400px
    :alt: alternate text
    :figclass: align-center

    Adding an MVP driver to PDS2000.

.. _pds_2_fig:

.. figure:: ./_static/pds_2.png
    :width: 600px
    :align: center
    :height: 400px
    :alt: alternate text
    :figclass: align-center

    Configuring the MVP driver for PDS2000.

.. _pds_3_fig:

.. figure:: ./_static/pds_3.png
    :width: 600px
    :align: center
    :height: 400px
    :alt: alternate text
    :figclass: align-center

    Configuring an MVP driver for PDS2000. Be sure to scroll down in the list on the left side and choose the driver you added in the previous step before modifying the port number. The port number must match that which SSP package is sending data to (configured in the ``__config__.db`` file).

.. _pds_4_fig:

.. figure:: ./_static/pds_4.png
    :width: 600px
    :align: center
    :height: 400px
    :alt: alternate text
    :figclass: align-center

    After the driver is added, test the device to verify correct configuration of communication protocols.

.. _pds_5_fig:

.. figure:: ./_static/pds_5.png
    :width: 600px
    :align: center
    :height: 400px
    :alt: alternate text
    :figclass: align-center

    With the device driver open, send a test cast from SSP package. The data should appear in the Io port View window. Be sure that the correct device driver is selected from the top left list window.

.. _pds_6_fig:

.. figure:: ./_static/pds_6.png
    :width: 600px
    :align: center
    :height: 400px
    :alt: alternate text
    :figclass: align-center

    While running PDS2000 in acquisition mode, right click in the multibeam raw profile display and choose “Multibeam filters”. Choose “SVP Sensor” as the source of sound speed profiles to be used.

.. _pds_7_fig:

.. figure:: ./_static/pds_7.png
    :width: 600px
    :align: center
    :height: 400px
    :alt: alternate text
    :figclass: align-center

    While running PDS2000 in acquisition mode, you can verify reception in the Status displays and the “Raw Data” displays. Check the date, time, latitude, longitude against what you sent from SSP package.


Kongsberg EA440/EA640
---------------------

.. index:: EA440, EA640

The Konsgsberg EA440/EA640 single-beam echo sounder data acquisition system accepts SVP transmissions from the *Sound Speed* package. A method to verify reception of the cast is not currently known thus the user should confirm reception in the acquisition system.

In the *Setup* tab of the EA440 software, open the *Installation* window and under *I/O Setup*, configure the IP address and port number where the casts transmitted from the *Sound Speed* package should be received (:numref:`ea440_1_fig`).

.. _ea440_1_fig:

.. figure:: ./_static/ea440_1.png
    :width: 600px
    :align: center
    :alt: alternate text
    :figclass: align-center

    Add a new LAN Port to receive casts from SSP package.

Under *Sensor Installation*, add a new sensor with type *Sound Velocity Profile EM*. Select the newly created LAN Port as the port associated with this sensor. Make sure that the S01 datagram is enabled (:numref:`ea440_2_fig`).

.. _ea440_2_fig:

.. figure:: ./_static/ea440_2.png
    :width: 600px
    :align: center
    :alt: alternate text
    :figclass: align-center

    Add a new sensor in the EM S01 format to decode casts from SSP package.

Open the *Monitor* window to verify successfull reception of a cast from the *Sound Speed* package (:numref:`ea440_3_fig`). Make sure that the *Sound Speed* package is properly configured with an Output client using the EA440 protocol to accomplish this test.

    .. _ea440_3_fig:

.. figure:: ./_static/ea440_3.png
    :width: 600px
    :align: center
    :alt: alternate text
    :figclass: align-center

    Verify successfull reception of a cast from the *Sound Speed* package using the *Monitor* window

In the *Setup* tab of the EA440 software, open the *Environment* window and under *Water Column*, make sure that the sound speed and temperature sources are set to *Profile* (:numref:`ea440_4_fig`).

    .. _ea440_4_fig:

.. figure:: ./_static/ea440_4.png
    :width: 600px
    :align: center
    :alt: alternate text
    :figclass: align-center

    Source selection for sound speed and temperature

Under *Sound Velocity Profile*, select *Profile From Network* as source. Reception of a new cast from the *Sound Speed* package should immediately update in the sound speed plot (:numref:`ea440_5_fig`).

    .. _ea440_5_fig:

.. figure:: ./_static/ea440_5.png
    :width: 600px
    :align: center
    :alt: alternate text
    :figclass: align-center

    Sound speed profile received from the *Sound Speed* package and displayed in the EA440 software

