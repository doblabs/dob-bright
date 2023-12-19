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

"""Creates and populates basic config files or (gracefully) dies trying."""

import os
from gettext import gettext as _

from easy_as_pypi_appdirs.exists_or_mkdirs import must_ensure_file_path_dirred
from easy_as_pypi_termio.echoes import click_echo, highlight_value
from easy_as_pypi_termio.errors import exit_warning

__all__ = ("create_basic_conf",)


def create_basic_conf(object_path, object_name, create_object_file_f, force):
    def _create_basic_conf():
        # Exit if config already exists and not --force.
        exit_if_exists_unless_force(object_path, force)
        # This, too, might exit if, e.g., PermissionError.
        must_ensure_file_path_dirred_or_exit(object_path)
        create_object_file_f(object_path)
        echo_path_created(object_path)

    def exit_if_exists_unless_force(object_path, force):
        path_exists = os.path.exists(object_path)
        if path_exists and not force:
            exit_path_exists(object_path)

    def exit_path_exists(object_path):
        exit_warning(_("{} already at {}").format(object_name, object_path))

    def must_ensure_file_path_dirred_or_exit(object_path):
        try:
            must_ensure_file_path_dirred(object_path)
        except Exception as err:
            msg = _("Cannot create path to {} at {}: {}").format(
                object_name,
                object_path,
                str(err),
            )
            exit_warning(msg)

    def echo_path_created(object_path):
        click_echo(
            _("Initialized basic {} at {}").format(
                object_name,
                highlight_value(object_path),
            )
        )

    _create_basic_conf()
