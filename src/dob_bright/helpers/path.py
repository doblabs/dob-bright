# This file exists within 'dob-bright':
#
#   https://github.com/tallybark/dob-bright
#
# Copyright © 2018-2020 Landon Bouma. All rights reserved.
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

import os

__all__ = (
    'touch',
)


def touch(filepath):
    try:
        import pathlib
        pathlib.Path(filepath).touch()
    except ImportError:
        # Python <3.4 [2020-01-27: now unreachable!]
        # MAYBE/2020-01-27: Move pathlib import to module level...
        #   or leave here in method, to be lazy-loaded.
        if not os.path.exists(filepath):
            open(filepath, 'w').close()

