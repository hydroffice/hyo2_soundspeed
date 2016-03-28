How to build the documentation
==============================


Requirements
------------

The documentation is built using ``sphinx``, so you neeed to have it:

* ``pip install sphinx sphinx-autobuild``


First-time creation of documentation template
---------------------------------------------

Just once for each project, you can create the documentation template as follows:

* ``mkdir docs``
* ``cd docs``
* ``sphinx-quickstart``


Generate the documentation
--------------------------

To update the API documentation:

* ``sphinx-apidoc -f -o docs/api hydroffice hydroffice/soundspeed/scripts``

To create the html

* ``make html``


