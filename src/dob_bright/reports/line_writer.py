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

"""Line writer output format module."""

from nark.reports import ReportWriter

__all__ = (
    'LineWriter',
)


class LineWriter(ReportWriter):
    def __init__(self, *args, **kwargs):
        super(LineWriter, self).__init__(*args, **kwargs)

    def output_setup(self, *args, **kwargs):
        super(LineWriter, self).output_setup(*args, **kwargs)

    def output_write(self, line=''):
        self.output_file.write(line + '\n')

