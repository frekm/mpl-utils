====================
Installation & Usage
====================

Installation
============

There are multiple ways to install the package:

1. Simple drop-in
2. Using ``git`` and ``pip``.
3. From source


Simple drop-in
--------------

- From the latest `release page <https://github.com/frekm/mpl-utils/releases/latest>`__,
  download ``mplutils.zip``.
- Extract the contents of `mplutils.zip` into the same path as your python script.

If you don't have ``matplotlib`` installed, you will need to do this manually.
The simplest way is using ``pip``:

.. code-block:: shell

    pip install matplotlib

Other methods are listed `here <https://matplotlib.org/stable/install/index.html>`__.



Install using ``git`` and ``pip``
---------------------------------

If you have ``git`` installed on your system, you can install the package directly
from GitHub.

.. code-block:: shell

    pip install git+https://github.com/frekm/mpl-utils.git

You can install a particular version by appending it, e.g. ``v0.1.0``,

.. code-block:: shell

    pip install git+https://github.com/frekm/mpl-utils.git@v0.1.0

Check the `release page <https://github.com/frekm/mpl-utils/releases/>`__
which versions exist.

You can also install a particular commit using its SHA. Go to
`the commit history <https://github.com/frekm/mpl-utils/commits/main/>`__, copy the
SHA of the commit in question, and install it, e.g.,

.. code-block:: shell

    pip install git+https://github.com/frekm/mpl-utils.git@52ef552a15a7b096824dd6457f35f40542f30686


Install using https
-------------------

If you don't have git installed on your system, you can install version
(not necessarily the latest release) using

.. code-block:: shell

    pip install https://github.com/frekm/mpl-utils/archive/refs/heads/main.zip

or a paticular tag (corresponding to a particular release) using

.. code-block:: shell

    pip install https://github.com/frekm/mpl-utils/archive/refs/tags/v0.1.0.zip

Replace "v0.1.0" with the particular version you want.

Install from source
-------------------

- From the latest `release page <https://github.com/frekm/mpl-utils/releases/latest>`__,
  and download the source code (not ``mplutils.zip``).
- Extract the contents.
- Run ``pip install <path>/mpl-utils-<version>/src``.




Usage
=====

Once you have installed the package using any of the above methods, simply
import it into your project

.. code-block:: python

    import mplutils as mplu

Some basic examples can be found at :doc:`examples`.

The documentation of all provided methods is available at :doc:`api_reference/index`.
