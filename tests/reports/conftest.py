# This file exists within 'dob-bright':
#
#   https://github.com/tallybark/dob-bright
#
# Copyright © 2020 Landon Bouma. All rights reserved.
#
# This program is free software:  you can redistribute it  and/or  modify it under the
# terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3  of the License,  or  (at your option)  any later version  (GPLv3+).
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY;  without even the implied warranty of MERCHANTABILITY or  FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU  General  Public  License  for  more  details.
#
# If you lost the GNU General Public License that ships with this software
# repository (read the 'LICENSE' file), see <http://www.gnu.org/licenses/>.

""""""

# Note: Cannot use pytest_plugins here, e.g.,:
#   pytest_plugins = (
#       "nark.tests.backends.sqlalchemy.conftest",
#       # Make sure fixtures required by fixtures available, e.g., 'base_config'.
#       "nark.tests.conftest",
#   )
# because:
#   Defining 'pytest_plugins' in a non-top-level conftest is no longer supported.
from nark.tests.conftest import *  # noqa: F401, F403
from nark.tests.backends.sqlalchemy.conftest import *  # noqa: F401, F403

