.. _possible_configurations:

Possible Configurations
=======================

.. index:: configurations

Given its specific aim, *Sound Speed Manager* is usually installed to run in one of two configurations:

On the machine used for sound speed profile acquisition
-------------------------------------------------------

This represents a quite common choice since many of the operations accomplished in the software are typically done
immediately after acquisition of a cast.

If the machine is on the same network as the multibeam acquisition workstation,
the processed profile can be directly delivered via network.

When this is not possible, the package can export the processed data to files that can then be manually uploaded
to the multibeam workstation.

On the multibeam acquisition workstation
----------------------------------------

This configuration is particularly useful when it is anticipated that the software will run in *Server Mode*.
In fact, it is important that multibeam watch standers are able to monitor the server, and to disable it
in the event that a measured profile is to be uploaded.
