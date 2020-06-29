# This file exists within 'dob-bright':
#
#   https://github.com/tallybark/dob-bright
#
# Copyright © 2019-2020 Landon Bouma. All rights reserved.
#
# 'dob' is free software: you can redistribute it and/or modify it under the terms
# of the GNU General Public License  as  published by the Free Software Foundation,
# either version 3  of the License,  or  (at your option)  any   later    version.
#
# 'dob' is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY  or  FITNESS FOR A PARTICULAR
# PURPOSE.  See  the  GNU General Public License  for  more details.
#
# You can find the GNU General Public License reprinted in the file titled 'LICENSE',
# or visit <http://www.gnu.org/licenses/>.

from dob_bright.reports.tabulate_results import tabulate_results


# FIXME/2020-06-06 17:56: Move this module to dob-bright.

class TestGenerateTable(object):
    def test_generate_table(self, controller_with_logging, fact):
        """Make sure the table contains all expected fact data."""
        controller = controller_with_logging
        tabulation = tabulate_results(controller, [fact])
        assert tabulation.table[0].start == fact.start.strftime('%Y-%m-%d %H:%M:%S')
        assert tabulation.table[0].activity == fact.activity.name

    def test_generate_basic_table_column_count(self, controller_with_logging):
        """Make sure the number of table columns matches our expectation."""
        controller = controller_with_logging
        tabulation = tabulate_results(controller, [])
        # MAGIC_NUMBER: A basic query (without grouping or addition stats)
        # creates a table with the 8 following columns:
        #   key, start, end, activity, category, tags, description, duration
        assert len(tabulation.repcols) == 8

