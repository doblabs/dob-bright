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

"""Factoid writer output format module."""

from .line_writer import LineWriter

__all__ = (
    'FactoidWriter',
)


class FactoidWriter(LineWriter):
    # Note that specifying cut_width_complete makes the output not technically
    # Factoid format, because the complete Fact will not be represented. But
    # it's nonetheless still useful for showing abbreviated output. Just FYI.
    # (lb): Same with show_elapsed, that text will not be parsable, either.
    def __init__(
        self,
        *args,
        colorful=False,
        cut_width_complete=None,
        factoid_sep='',
        show_duration=False,
        **kwargs,
    ):
        super(FactoidWriter, self).__init__(*args, **kwargs)
        self.colorful = colorful
        self.cut_width_complete = cut_width_complete
        self.factoid_sep = factoid_sep
        # TESTME/FIXME/2020-06-18: (lb): I doubt dob-import parses duration correctly.
        self.show_elapsed = show_duration

    def _write_fact(self, idx, fact):
        one_liners = self.cut_width_complete is not None and self.cut_width_complete > 0
        description_sep = '\n\n' if not one_liners else ': '
        # FIXME: (lb): Add UTC support. Currently, all time assumed "local".
        localize = True
        line = fact.friendly_str(
            shellify=False,
            description_sep=description_sep,
            localize=localize,
            include_id=False,
            colorful=self.colorful,
            cut_width_complete=self.cut_width_complete,
            show_elapsed=self.show_elapsed,
        )
        if (not one_liners or self.factoid_sep) and idx > 0:
            self.output_write()
        self.output_write(line)
        if self.factoid_sep:
            self.output_write()
            self.output_write(self.factoid_sep)

    def write_report(self, table, headers, tabulation=None):
        raise NotImplementedError

