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

"""Journal writer output format module."""

from click_hotoffthehamster._compat import term_len

from .line_writer import LineWriter

__all__ = (
    'JournalWriter',
)


class JournalWriter(LineWriter):
    def __init__(self, *args, section_nls=False, **kwargs):
        super(JournalWriter, self).__init__(*args, **kwargs)
        self.section_nls = section_nls

    @property
    def requires_table(self):
        return True

    def write_report(self, table, headers, tabulation=None):
        self.curr_section = None
        return super(JournalWriter, self).write_report(table, headers, tabulation)

    def _write_result(self, row, headers, tabulation=None):
        line = ''

        next_section = self.curr_section
        if self.curr_section is None or row[0] != self.curr_section:
            next_section = row[0]
            if self.section_nls and self.curr_section is not None:
                # Emit a blank row-line.
                self.output_write()

            line += row[0]
            line += ' ' * (tabulation.max_widths[0] - term_len(row[0]))
        else:
            # Omit the first column value when it's the same as the previous row's.
            # Strip Unicode/ASNI control characters to compute whitespace to fill.
            line += ' ' * tabulation.max_widths[0]

        i_remainder = 1
        line += '  ' + '  '.join([str(val) for val in row[i_remainder:]])

        # LATER/2020-06-03: Print formatted text.
        #  from prompt_toolkit import print_formatted_text
        #  print_formatted_text(...)

        self.output_write(line)

        self.curr_section = next_section

