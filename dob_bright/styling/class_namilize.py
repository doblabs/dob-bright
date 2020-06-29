# This file exists within 'dob-bright':
#
#   https://github.com/tallybark/dob-bright
#
# Copyright © 2019-2020 Landon Bouma. All rights reserved.
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

import re

__all__ = (
    'namilize',
    # Private:
    #  'CLASS_NAME_NOTSET',
)

# SYNC_ME: Use similar re as PPT. From prompt_toolkit/styles/style.py::
#  CLASS_NAMES_RE = re.compile(r'^[a-z0-9.\s_-]*$')  # This one can't contain a comma!
# - We use the regex for intra-line character substitution, so drop the ^, *, and $.
# - (lb): Also, drop the \s, because we're forming a single classname.
#   - I think technically classnames may contain spaces, but if we don't replace
#     spaces, PTK parsing raises (at ValueError("Wrong color format %r" % text)).
CLASS_NAME_NOTSET = re.compile(r'[^a-z0-9._-]')

# MAYBE/2020-03-31: Behave like, say, PyPI.org, and condense multiple dashes into one?
# - Would this make writing the styling config simpler? Or more restrictive?
# - Without a good use case, I'll note the idea here, but that's it. -lb.
#
#  COMPRESS_DASHES = re.compile(r'-+')


def namilize(name):
    """Normalizes a string so it can be used as a prompt_toolkit (PPT) classname.
    """
    classname = CLASS_NAME_NOTSET.sub('-', name.lower())
    # See comment above: To condense dashes, or not. For now, not!
    #  classname = COMPRESS_DASHES.sub('-', classname)
    return classname

