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

import lazy_import

from dob_bright.termio import dob_in_user_exit

# (lb): This module uses 2 popular table generator packages, texttable and tabulate.
# - We use 'texttable' to generate an ASCII table that'll fit nicely in the user's
#   terminal, appropriately constrained to whatever width we pass it.
# - We use 'tabulate' to generate alternative table formats, such as HTML or reST.
# - This module does not use any generator that does not automatically wrap long cell
#   values. That is, it does not use tabulate to generate an ASCII table, because that
#   package does not wrap cell values automatically -- it'll wrap on newlines, but our
#   code would have to first call ansiwrap.wrap to embed those newlines, which is more
#   work that it's worth, considering that we can use texttable instead. (That said,
#   tabulate does offer a multitude of ASCII table formats from which to choose that
#   use different border characters. But we only need to output an ASCII table; we
#   don't need to offer the user a zillion different ASCII table border styles.)
# - I also tried humanfriendly, but its generator also does not wrap long cell values
#   (at least AFAICT, but I did not dig too deep).
# - See similar comment in dob/dob/clickus/cmd_options_search.py.
# - tl;dr: Use 'texttable' to make ASCII tables;
#          Use 'tabulate' to make markup tables.

# Profiling: load times:
#  ~ 0.004 secs.  / from tabulate import tabulate
#  ~ 0.015 secs.  / from texttable import Texttable
tabulate = lazy_import.lazy_module('tabulate')
texttable = lazy_import.lazy_module('texttable')

__all__ = (
    'generate_table',
)


def generate_table(
    rows,
    headers,
    output_obj,
    table_type='texttable',
    max_width=0,
    cols_align=None,
):
    """Generates and prints a table in the format specified."""
    def _generate_table():
        if table_type == 'texttable' or not table_type:
            # Default is 'texttable', which will balance and wrap long cell values.
            generate_table_texttable(rows, headers)
        else:
            # We support tabulate, too, but the front end CLI only shows a few of
            # its markup formats, and none of its ASCII table formats, because
            # wrapping issue described above.
            generate_table_tabulate(rows, headers, table_type)

    # ***

    def generate_table_texttable(rows, headers):
        # PROS:
        # - texttable wraps long column values by default.
        # - texttable defaults to an 80-character wide table.
        # CONS:
        # - texttable counts control characters when calculating column width.
        #   So you cannot, e.g., underline header values, because then column
        #   row values (which are not ANSI-encoded) will not align properly.
        #   (lb): So I abandoned my plan to emphasize the header values.
        ttable = texttable.Texttable()
        set_cols_align(ttable)
        # Set the table width. Note that we could be
        # deliberate about each column's width, e.g.,
        #   ttable.set_cols_width([a, b, c, d])
        # but the library does an excellent job on its own.
        # Note that texttable defaults to an 80 width.
        # Note that using max_width=0 generates unconstrained table.
        ttable.set_max_width(max_width)
        # Prepend the headers to the row data.
        rows.insert(0, headers)
        ttable.add_rows(rows)
        # Render the table.
        textable = generate_table_texttable_draw(ttable)
        output_obj.write(textable)
        output_obj.write('\n')

    def set_cols_align(ttable):
        if cols_align is None:
            set_cols_align_right_then_lefts(ttable)
        else:
            cols_align[0] = 'r'
            ttable.set_cols_align(cols_align)

    def set_cols_align_right_then_lefts(ttable):
        # Right-align the first column; left-align the rest.
        cols_align = ['r']
        for idx in range(1, len(headers)):
            cols_align.append('l')
        ttable.set_cols_align(cols_align)

    def generate_table_texttable_draw(ttable):
        try:
            return ttable.draw()
        except ValueError as err:
            msg = str(err)
            if msg == "max_width too low to render data":
                msg = _('Please specify a larger table width.')
            dob_in_user_exit(msg)

    # ***

    def generate_table_tabulate(rows, headers, table_type):
        tabulation = generate_table_tabulate_tabulate(rows, headers, table_type)
        output_obj.write(tabulation)
        output_obj.write('\n')

    def generate_table_tabulate_tabulate(rows, headers, table_type):
        try:
            return tabulate.tabulate(
                rows, headers=headers, tablefmt=table_type,
            )
        except Exception as err:
            # The CLI front end should preclude this path, but still.
            raise ValueError(
                'Unknown table_type: ‘{}’ ({})'.format(table_type, str(err))
            )

    # ***

    _generate_table()

