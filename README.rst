make-deb: Helper Tool for getting your python code into debian packages
=============================================

Make-deb is a simple tool that generates Debian configuration based on your setuptools configuration and git history. When run, it will create a Debian directory at the root of your python project with the necessary files to build your package into a Debian package using `dh-virtualenv <https://github.com/spotify/dh-virtualenv>`_

.. code-block:: bash

   $ cd /my/python/repository
   $ make-deb

   'debian' directory successfully placed at the root of your repository

If setuptools does not have complete information, make-deb will ask for additional information (for example, maintainer email). After initialization, a directory named "debian" will be reated at the root of your repo. Assuming you have dh-virtualenv installed, you should be able to simply create a .deb from your python project by running the following command at the root of your project.

.. code-block:: bash

   $ dpkg-buildpackage -us -uc

Installation
------------

To install make-deb:

.. code-block:: bash

   $ pip install make-deb

Documentation
-------------

Generating your Debian configuration can be run from any operating system. However, in order to build a debian package, you must be on a Debian-based operating system and have dh-virtualenv installed. In the future, we plan to support Vagrant integration to build packages from any platform.
