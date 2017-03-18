How to distribute
-----------------


Preliminary steps
^^^^^^^^^^^^^^^^^

* First of all, run the full test suite and check that there are no failures.

* Verify the release version in the following files:

  * setup.cfg
  * setup.py
  * docs/conf.py
  * hydroffice/soundspeed/__init__.py
  * hydroffice/soundspeedmanager/__init__.py
  * hydroffice/soundspeedsettings/__init__.py

* Push any 'release' changes to GitHub/BitBucket

Update docs
^^^^^^^^^^^

* Build the new docs as html (make html) and as pdf (make latexpdf)

* Update the web site with the new html and pdf docs (urls too)

* Update the embedded pdf docs


Freeze the app
^^^^^^^^^^^^^^

* Update the pyinstaller files under 'freeze/'

* Freeze the application and test it on a 'clean' VM

* Upload the app on BitBucket

* Update the download link and the version on the SSM web page

* Update the latest file on the HydrOffice site


Final steps
^^^^^^^^^^^

* Push any 'release' changes to GitHub/BitBucket

* Create a 'tag' with the release

* Create a GitHub release

* Push the package on PyPI

* Start to work on the next release :)
