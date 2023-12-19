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

"""Controller functionality: Terminal *color* enablement."""

from easy_as_pypi_termio.style import disable_colors, enable_colors

from .pdb_subprocess import Controller_PdbSubprocess

__all__ = ("Controller_SetupColoring",)


class Controller_SetupColoring(
    # For self.config, depends on:
    #  Controller_ConfigManager  # self.config['term.*']
    # but for deliberate super() chaining: load data store layer next:
    Controller_PdbSubprocess,
):
    """Enables/Disables terminal output coloring per config's term.use_color."""

    def __init__(self, *args, **kwargs):
        super(Controller_SetupColoring, self).__init__(*args, **kwargs)

    # ***

    def setup_tty_color(self, use_color):
        if use_color is None:
            use_color = self.config["term.use_color"]
        else:
            self.config["term.use_color"] = use_color
        if use_color:
            enable_colors()
        else:
            disable_colors()

    # ***
