hatch-docstring-description
===========================

|PyPI Version| |PyPI Python Version| |Coverage|

A ``hatchling`` plugin to read the ``description`` from the package docstring like ``flit`` does.

Usage
-----

#. Include it as a plugin to your ``pyproject.toml``:

   .. code:: toml

      [build-system]
      requires = ["hatchling", "hatch-docstring-description"]
      build-backend = "hatchling.build"

#. Mark your ``description`` field as ``dynamic``:

   .. code:: toml

      [project]
      dynamic = ["description"]

#. And make sure Hatchling uses it:

   .. code:: toml

      [tool.hatch.metadata.hooks.docstring-description]

Contributing
------------

- Use Hatch_ to run the tests: ``hatch test``
- Use pre-commit_ to lint: ``pre-commit run --all-files``

.. _Hatch: https://hatch.pypa.io/latest
.. _pre-commit: https://pre-commit.com

License
-------

``hatch-docstring-description`` is distributed under the terms of the `GPL 3 (or later)`_ license.


.. |PyPI Version| image:: https://img.shields.io/pypi/v/hatch-docstring-description.svg
   :target: https://pypi.org/project/hatch-docstring-description
.. |PyPI Python Version| image:: https://img.shields.io/pypi/pyversions/hatch-docstring-description.svg
   :target: https://pypi.org/project/hatch-docstring-description
.. |Coverage| image:: https://codecov.io/github/flying-sheep/hatch-docstring-description/branch/main/graph/badge.svg?token=FZCw1cXSTL
   :target: https://codecov.io/github/flying-sheep/hatch-docstring-description

.. _GPL 3 (or later): https://spdx.org/licenses/GPL-3.0-or-later.html
