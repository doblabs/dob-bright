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

from gettext import gettext as _

from dob_bright.reports.render_results import render_results

__all__ = (
    'echo_config_decorator_table',
)


def echo_config_decorator_table(
    controller,
    cfg_decors,
    output_format='table',
    table_type='texttable',
    exclude_section=False,
    include_hidden=False,
):
    sec_key_vals = []

    def _echo_config_decorator_table():
        for condec in cfg_decors:
            condec.walk(visitor)
        echo_table()

    def visitor(condec, keyval):
        # MAYBE: Option to show hidden config.
        # MAYBE: Option to show generated config.
        if keyval.hidden and not include_hidden:
            return

        val_def = str(keyval.value)
        if val_def != str(keyval.default):
            val_def += val_def and ' ' or ''
            val_def += encode_default(str(keyval.default))
        val_row = [
            condec.section_path(sep='.')
        ] if not exclude_section else []
        val_row += [
            keyval.name,
            val_def,
            keyval.doc,
        ]
        sec_key_vals.append(val_row)

    def echo_table():
        headers = [
            _("Section")
        ] if not exclude_section else []
        headers += [
            _("Name"),
            _("Value {}").format(encode_default(_("Default"))),
            _("Help"),
        ]
        render_results(
            controller,
            results=sec_key_vals,
            headers=headers,
            output_format=output_format,
            table_type=table_type,
        )

    def encode_default(text):
        # 2019-11-30: (lb): I switched from [square brackets] to <angle brackets>
        # to avoid JSON-encoded lists being [[double bracketed]] (which triggered
        # extra mental cycles upon sight).
        return '<{}>'.format(text)

    _echo_config_decorator_table()

