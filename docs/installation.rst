############
Installation
############

.. |dob-bright| replace:: ``dob-bright``
.. _dob-bright: https://github.com/hotoffthehamster/dob-bright

.. |virtualenv| replace:: ``virtualenv``
.. _virtualenv: https://virtualenv.pypa.io/en/latest/

.. |workon| replace:: ``workon``
.. _workon: https://virtualenvwrapper.readthedocs.io/en/latest/command_ref.html?highlight=workon#workon

To install system-wide, run as superuser::

    $ pip3 install dob-bright

To install user-local, simply run::

    $ pip3 install -U dob-bright

To install within a |virtualenv|_, try::

    $ mkvirtualenv dob-bright
    (dob-bright) $ pip install dob-bright

To develop on the project, link to the source files instead::

    (dob-bright) $ deactivate
    $ rmvirtualenv dob-bright
    $ git clone git@github.com:hotoffthehamster/dob-bright.git
    $ cd dob-bright
    $ mkvirtualenv -a $(pwd) --python=/usr/bin/python3.7 dob-bright
    (dob-bright) $ make develop

After creating the virtual environment,
to start developing from a fresh terminal, run |workon|_::

    $ workon dob-bright
    (dob-bright) $ ...

