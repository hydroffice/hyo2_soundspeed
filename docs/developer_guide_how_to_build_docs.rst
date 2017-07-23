How to build the documentation
------------------------------


Requirements
^^^^^^^^^^^^

The documentation is built using ``sphinx``, so you neeed to have it:

* ``pip install sphinx sphinx-autobuild``

To build the pdf manual on Ubuntu:

* ``sudo apt-get install texlive-full``


First-time creation of documentation template
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Just once for each project, you can create the documentation template as follows:

* ``mkdir docs``
* ``cd docs``
* ``sphinx-quickstart``


Generate the documentation
^^^^^^^^^^^^^^^^^^^^^^^^^^

To create the html

* ``make html``


