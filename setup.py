# This file exists within 'dob-bright':
#
#   https://github.com/tallybark/dob-bright

"""
Packaging instruction for setup tools.

Refs:

  https://setuptools.readthedocs.io/

  https://packaging.python.org/en/latest/distributing.html

  https://github.com/pypa/sampleproject
"""

from setuptools import find_packages, setup

# *** Package requirements.

# FIXME/2020-01-31: Cull this (and other split-packages') requirements.

requirements = [
    # Platform-specific directory magic.
    #  https://github.com/ActiveState/appdirs
    'appdirs >= 1.4.3, < 2',
    # Enable Click color support (we don't use colorama directly, but it does),
    #  "on Windows, this ... is only available if colorama is installed".
    #  https://click.palletsprojects.com/en/5.x/utils/#ansi-colors
    #  https://pypi.org/project/colorama/
    'colorama >= 0.4.3, < 1',
    # INI/config parser, even better (preserves comments and ordering).
    #  https://github.com/DiffSK/configobj
    #  https://configobj.readthedocs.io/en/latest/
    'configobj >= 5.0.6, < 6',
    # Vocabulary word pluralizer.
    #  https://github.com/ixmatus/inflector
    'Inflector >= 3.0.1, < 4',
    # https://github.com/mnmelo/lazy_import
    'lazy_import >= 0.2.2, < 1',

    # *** HOTH packages.

    # "Very simple Python library for color and formatting in terminal."
    # Forked (for italic "support") to:
    #  https://github.com/hotoffthehamster/ansi-escape-room
    # Forked from:
    #  https://gitlab.com/dslackw/colored
    # See wrapper file:
    #  dob_bright/termio/style.py
    'ansi-escape-room == 1.4.2',
    # (lb): Click may be the best optparser of any language I've used.
    #  https://github.com/pallets/click
    #    'click',
    #  - Still, had to make one adjustment, and too impatient to ask for a pull...
    #  https://github.com/hotoffthehamster/click
    'click-hotoffthehamster >= 7.1.1, <= 7.1.2',
    # Pythonic config @decorator.
    #  https://github.com/hotoffthehamster/config-decorator
    'config-decorator == 2.0.14',
    # The heart of Hamster. (Ye olde `hamster-lib`).
    #  https://github.com/tallybark/nark
    'nark > 3.2.2, < 3.2.4',  # I.e., release 3.2.3, or whatever dev's running.
]

# *** Minimal setup() function -- Prefer using config where possible.

# (lb): Most settings are in setup.cfg, except identifying packages.
# (We could find-packages from within setup.cfg, but it's convoluted.)

setup(
    # Run-time dependencies installed on `pip install`. To learn more
    # about "install_requires" vs pip's requirements files, see:
    #   https://packaging.python.org/en/latest/requirements.html
    install_requires=requirements,

    # Specify which package(s) to install.
    # - Without any rules, find_packages returns, e.g.,
    #     ['dob_bright', 'tests', 'tests.dob_bright']
    # - With the 'exclude*' rule, this call is essentially:
    #     packages=['dob_bright']
    packages=find_packages(exclude=['tests*']),

    # Tell setuptools to determine the version
    # from the latest SCM (git) version tag.
    #
    # Note that if the latest commit is not tagged with a version,
    # or if your working tree or index is dirty, then the version
    # from git will be appended with the commit hash that has the
    # version tag, as well as some sort of 'distance' identifier.
    # E.g., if a project has a '3.0.0a21' version tag but it's not
    # on HEAD, or if the tree or index is dirty, the version might
    # be:
    #   $ python setup.py --version
    #   3.0.0a22.dev3+g6f93d8c.d20190221
    # But if you clean up your working directory and move the tag
    # to the latest commit, you'll get the plain version, e.g.,
    #   $ python setup.py --version
    #   3.0.0a31
    # Ref:
    #   https://github.com/pypa/setuptools_scm
    setup_requires=['setuptools_scm'],
    use_scm_version=True,
)

