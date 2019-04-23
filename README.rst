=============================
vaultify - hexagon of secrets
=============================

    :Author: Georg vom Endt (krysopath@gmail.com)

.. contents::



1 Installation
--------------

This section explains different installation methods.

1.1 Requirements
~~~~~~~~~~~~~~~~

- python3.6, python3.7

- pip

- docker (obsoletes the above)

1.2 from pypi
~~~~~~~~~~~~~

Most implementers will fetch the package from pypi and build their own
things on another layer.

.. code:: shell

    pip3 install vaultify

1.3 from git
~~~~~~~~~~~~

Alternatively fetch the sources from github to develop your own
adapter classes.

.. code:: shell

    git clone git@github.com:krysopath/vaultify.git

1.4 os dependencies
~~~~~~~~~~~~~~~~~~~

These tools can greatly speed up local development, when used in
conjunction via ``make``, so install them. They can overwhelm you with
output, too.

1.4.1 ubuntu
^^^^^^^^^^^^

.. code:: shell

    apt install make entr yamllint pylint bandit
