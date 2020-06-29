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

"""Terminal input and output modules."""

# Import herein for convenience references.
# - NOTE: noqa: F401: Disable: 'foo.bar' imported but unused.
from .echoes import echo_block_header, highlight_value  # noqa: F401
from .errors import (  # noqa: F401
    barf_and_exit, dob_in_user_exit, dob_in_user_warning, echo_exit
)
from .paging import ClickEchoPager, click_echo  # noqa: F401
from .style import attr, bg, coloring, stylize, fg  # noqa: F401

