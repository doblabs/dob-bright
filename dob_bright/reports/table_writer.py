# This file exists within 'dob-bright':
#
#   https://github.com/tallybark/dob-bright
#
# Copyright © 2019-2020 Landon Bouma. All rights reserved.
#
# 'nark' is free software: you can redistribute it and/or modify it under the terms
# of the GNU General Public License  as  published by the Free Software Foundation,
# either version 3  of the License,  or  (at your option)  any   later    version.
#
# 'nark' is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY  or  FITNESS FOR A PARTICULAR
# PURPOSE.  See  the  GNU General Public License  for  more details.
#
# You can find the GNU General Public License reprinted in the file titled 'LICENSE',
# or visit <http://www.gnu.org/licenses/>.

"""ASCII Table writer output format module."""

from ..termio.ascii_table import generate_table

from nark.reports import ReportWriter

__all__ = (
    'TableWriter',
)


class TableWriter(ReportWriter):
    def __init__(
        self,
        *args,
        table_type='texttable',
        max_width=0,
        **kwargs,
    ):
        super(TableWriter, self).__init__(*args, **kwargs)
        self.table_type = table_type
        self.max_width = max_width

    @property
    def requires_table(self):
        return True

    def write_report(self, table, headers, tabulation=None):
        # SKIP:
        #   super(TableWriter, self).write_report(table, headers, tabulation)
        cols_align = None
        if tabulation is not None:
            cols_align = [repcol.align for repcol in tabulation.repcols]
        generate_table(
            table,
            headers,
            output_obj=self.output_file,
            table_type=self.table_type,
            max_width=self.max_width,
            cols_align=cols_align,
        )
        return len(table)

