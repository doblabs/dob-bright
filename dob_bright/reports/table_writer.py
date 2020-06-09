# This file exists within 'nark':
#
#   https://github.com/hotoffthehamster/nark
#
# Copyright © 2018-2020 Landon Bouma
# Copyright © 2015-2016 Eric Goller
# All  rights  reserved.
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
        table_style='texttable',
        term_width=None,
        chop=False,
        desc_col_idx=None,
        **kwargs,
    ):
        super(TableWriter, self).__init__(*args, **kwargs)
        self.table_style = table_style
        self.term_width = term_width
        self.chop = chop
        self.desc_col_idx = desc_col_idx

    @property
    def requires_table(self):
        return True

    def write_report(self, table, headers):
        # SKIP:
        #   super(TableWriter, self).write_report(table, columns)
        generate_table(
            table,
            headers,
            table_style=self.table_style,
            truncate=self.chop,
            trunccol=self.desc_col_idx,
        )
        return len(table)
