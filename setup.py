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

requirements = [
    # Just Another EDITOR package.
    #  https://github.com/fmoo/python-editor
    # - Imports as `editor`.
    'python-editor >= 1.0.4, < 2',

    # *** HOTH packages.

    # (lb): Click may be the best optparser of any language I've used.
    #  https://github.com/pallets/click
    #    'click',
    #  - Still, had to make one adjustment, and too impatient to ask for a pull...
    #  https://github.com/hotoffthehamster/click
    'click-hotoffthehamster >= 7.1.1, <= 7.1.2',
    # Pythonic config @decorator.
    #  https://github.com/hotoffthehamster/config-decorator
    'config-decorator > 2.0.14, < 2.0.16',  # I.e., release 2.0.15, or dev vers after.
    # ActiveState/appdirs + Singleton (app-wide access w/out appname) + `mkdir -p`.
    #  https://github.com/tallybark/easy-as-pypi-apppth#🛣
    'easy-as-pypi-apppth',
    # configobj + config-decorator helper.
    #  https://github.com/tallybark/easy-as-pypi-config
    'easy-as-pypi-config',
    # Get-package-or-Git-version helper.
    #  https://github.com/tallybark/easy-as-pypi-getver
    'easy-as-pypi-getver',
    # Click + ansi_escape_room (color) + convenience.
    #  https://github.com/tallybark/easy-as-pypi-termio
    'easy-as-pypi-termio',

    # The heart of Hamster. (Ye olde `hamster-lib`).
    #  https://github.com/tallybark/nark
    'nark > 3.2.3, < 3.2.5',  # I.e., release 3.2.4, or whatever dev's running.
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

