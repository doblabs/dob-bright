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

from easy_as_pypi_config.echo_cfg import (
    echo_config_decorator_table as _echo_config_decorator_table,
)

from ..reports.render_results import render_results

__all__ = ("echo_config_decorator_table",)


def echo_config_decorator_table(
    cfg_decors,
    exclude_section=False,
    include_hidden=False,
    controller=None,
    output_format="table",
    table_type="texttable",
    **kwargs,
):
    _echo_config_decorator_table(
        cfg_decors=cfg_decors,
        exclude_section=exclude_section,
        include_hidden=include_hidden,
        render_results=render_results,
        controller=controller,
        output_format=output_format,
        table_type=table_type,
        **kwargs,
    )
