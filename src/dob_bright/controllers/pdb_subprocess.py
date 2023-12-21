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

"""Controller functionality: pdb-related developer-friendly features."""

from gettext import gettext as _

from .. import __arg0name__
from .logging_output import Controller_LoggingOutput

__all__ = ("Controller_PdbSubprocess",)


class Controller_PdbSubprocess(
    # For self.config, depends on:
    #  Controller_ConfigManager  # self.config['dev.catch_errors']
    # For self.client_logger, depends on.
    #  Controller_LoggingOutput,
    # but for deliberate super() chaining: load data store layer next:
    Controller_LoggingOutput,
):
    """Exposes Controller.affirm and Controller.pdb_set_trace.

    - Especially useful for debugging TUI applications.
    """

    def __init__(self, *args, **kwargs):
        super(Controller_PdbSubprocess, self).__init__(*args, **kwargs)

        # Not necessarily pdb-related, but doesn't fit in any existing Controller
        # sub-class (so this class is as good as any a container for it).
        self.arg0name = __arg0name__

    # ***

    def affirm(self, condition, message=None):
        if condition:
            return
        self.client_logger.error(_("Dob detected an Illegal State!"))

        append_context = ""
        if message:
            append_context = f": {message}"

        self.client_logger.error(_("Dob detected an Illegal State") + append_context)
        if not self.config["dev.catch_errors"]:
            return
        import traceback

        traceback.print_stack()
        traceback.print_exc()
        self.pdb_set_trace()

    # ***

    def pdb_set_trace(self):
        import pdb

        self.pdb_break_enter()
        pdb.set_trace()
        self.pdb_break_leave()

    def pdb_break_enter(self):
        import subprocess

        # If the developer breaks into code from within the Carousel,
        # i.e., from within the Python Prompt Toolkit library, then
        # pdb terminal echo of stdin back to stdout is broken. You'll
        # see that pdb.stdin and pdb.stdout still match the sys.__stdin__
        # and sys.__stdout__, so that's not the issue -- it's that pdb
        # terminal is in *raw* mode. We can fix this by shelling to stty.
        proc = subprocess.Popen(["stty", "--save"], stdout=subprocess.PIPE)
        (stdout_data, stderr_data) = proc.communicate()
        self.stty_saved = stdout_data.strip()
        # Before breaking, twiddle the terminal away from PPT temporarily.
        subprocess.Popen(["stty", "sane"])

    def pdb_break_leave(self):
        import subprocess

        # Aha! This is awesome! We can totally recover from an interactive
        # debug session! First, restore the terminal settings (which we
        # reset so the our keystrokes on stdin were echoed back to us)
        # so that sending keys to PPT works again.
        subprocess.Popen(["stty", self.stty_saved])
        # And then the caller, if self.carousel, will redraw the interface
        # (because it has the handle to the application).
        self.client_logger.debug(_("Get on with it!"))

    # ***
