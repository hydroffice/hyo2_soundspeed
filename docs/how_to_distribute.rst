How to distribute
=================


Requirements
------------

To bump the version, you need ``bumpversion``:

* ``pip install sphinx sphinx-autobuild``


Update the version
------------------

Once installed, you can run something like:

* ``bumpversion --allow-dirty --new-version 0.1.4.dev0 patch``.

The above release value should then match with the variable ``version`` present in the ``conf.py`` under the `docs` folder.




