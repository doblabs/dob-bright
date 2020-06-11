# This file exists within 'dob-bright':
#
#   https://github.com/hotoffthehamster/dob-bright
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

"""Factoid writer output format module."""

from .line_writer import LineWriter

__all__ = (
    'FactoidWriter',
)


class FactoidWriter(LineWriter):
    def __init__(
        self,
        *args,
        colorful=False,
        cut_width_complete=None,
        factoid_sep='',
        hide_duration=False,
        **kwargs,
    ):
        super(FactoidWriter, self).__init__(*args, **kwargs)
        self.colorful = colorful
        self.cut_width_complete = cut_width_complete
        self.factoid_sep = factoid_sep
        self.show_elapsed = not hide_duration

    def _write_fact(self, idx, fact):
        # Note that specifying cut_width_complete makes the output not technically
        # Factoid format, because the complete Fact will not be represented. But
        # it's nonetheless still useful for showing abbreviated output. Just FYI.
        # (lb): Same with show_elapsed, that text will not be parsable, either.
        line = fact.friendly_str(
            shellify=False,
            description_sep='\n\n',
            localize=True,
            include_id=False,
            colorful=self.colorful,
            cut_width_complete=self.cut_width_complete,
            show_elapsed=self.show_elapsed,
        )
        self.output_write() if idx > 0 else None
        self.output_write(line)
        if self.factoid_sep:
            self.output_write()
            self.output_write(self.factoid_sep)

    def write_report(self, table, headers):
        raise NotImplementedError

