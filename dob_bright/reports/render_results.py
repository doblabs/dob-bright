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

import sys

import click_hotoffthehamster as click

from nark.reports.csv_writer import CSVWriter
from nark.reports.ical_writer import ICALWriter
from nark.reports.json_writer import JSONWriter
from nark.reports.tsv_writer import TSVWriter
from nark.reports.xml_writer import XMLWriter

from ..termio import dob_in_user_exit
from ..termio.paging import ClickEchoPager
from ..termio.style import stylize

from .factoid_writer import FactoidWriter
from .journal_writer import JournalWriter
from .table_writer import TableWriter
from .tabulate_results import tabulate_results

__all__ = (
    'render_results',
)


def render_results(
    controller,
    results,
    headers=None,
    query_terms=None,
    show_usage=False,
    show_duration=False,
    hide_description=False,
    custom_columns=None,
    output_format='table',
    table_type='texttable',
    max_width=-1,
    row_limit=0,
    output_obj_or_path=None,
    factoid_rule='',
    datetime_format=None,
    duration_fmt=None,
    spark_total=None,
    spark_width=None,
    spark_secs=None,
    show_totals=False,
    hide_totals=False,
    re_sort=False,
):
    """"""

    def _render_results():
        # Send output to the path or object indicated, or stdout or pager.
        output_obj = output_obj_or_path or ClickEchoPager
        writer = fetch_report_writer(output_format, output_obj)
        n_written = prepare_and_render_results(writer)
        return n_written

    # ***

    def fetch_report_writer(output_format, output_obj):
        writer = fetch_report_writer_cls(
            output_format=output_format,
            table_type=table_type,
        )
        must_prepare_output(writer, output_obj)
        return writer

    def must_prepare_output(writer, output_obj):
        try:
            writer.output_setup(
                output_obj=output_obj,
                row_limit=row_limit,
                datetime_format=datetime_format,
                duration_fmt=duration_fmt,
            )
        except Exception as err:
            # I.e., FileNotFoundError, or PermissionError.
            dob_in_user_exit(str(err))

    def fetch_report_writer_cls(output_format, table_type):
        writer = None
        if output_format == 'csv':
            writer = CSVWriter()
        elif output_format == 'tsv':
            writer = TSVWriter()
        elif output_format == 'ical':
            writer = ICALWriter()
        elif output_format == 'json':
            writer = JSONWriter()
        elif output_format == 'xml':
            writer = XMLWriter()
        elif output_format == 'factoid':
            colorful = controller.config['term.use_color']
            factoid_sep = ''
            if factoid_rule:
                # MAYBE/2020-06-16: (lb): Now that max_width truncates, this no
                # longer works as expected. max_width will generally be -1 now...
                # so either caller has to make ruler the length they want, or we
                # need a separate argument here... sorta think leave up to caller.
                rule_mult = 1
                if max_width > 0 and len(factoid_rule) == 1:
                    rule_mult = max_width
                # FIXME: This color should be customizable, eh. #styling
                factoid_sep = stylize(factoid_rule * rule_mult, 'indian_red_1c')
            writer = FactoidWriter(
                colorful=colorful,
                cut_width_complete=max_width,
                factoid_sep=factoid_sep,
                show_duration=show_duration,
            )
        elif output_format == 'journal':
            # For default `dob report` command, or when otherwise grouping
            # results by day, show a blank line between sections (Days).
            print_blank_line_between_sections = (
                query_terms.group_days
                and query_terms.sort_cols
                and query_terms.sort_cols[0] == 'day'
            )
            writer = JournalWriter(
                section_nls=print_blank_line_between_sections,
            )
        elif output_format == 'table':
            writer = TableWriter(
                table_type=table_type,
                max_width=restrict_width(max_width),
            )
        else:
            raise Exception('Unknown output_format: {}'.format(output_format))
        return writer

    # ***

    def prepare_and_render_results(writer):
        if headers is not None:
            # For list/usage act/cat/tag, already have ready table and headers.
            n_written = writer.write_report(results, headers, tabulation=None)
        elif query_terms.include_stats or writer.requires_table:
            # For reports with stats, post-process results; possibly sort.
            tabulation = prepare_table_and_columns()
            tabn_headers = [repcol.header for repcol in tabulation.repcols]
            n_written = writer.write_report(tabulation.table, tabn_headers, tabulation)
        else:
            # When dumping Facts to a simple format (e.g., CSV), we can write
            # each Fact on the fly and avoid looping through the results (and,
            # e.g., making a namedtuple for each row). (All Facts are still
            # loaded into memory, but it would be unexpected to have a data
            # store larger than 10s of MBs. So our only concern is speed of
            # the operation, not necessarily how much memory it consumes.)
            n_written = writer.write_facts(results)
        return n_written

    # ***

    def prepare_table_and_columns():
        tabulation = tabulate_results(
            controller,
            results,
            row_limit=row_limit,
            query_terms=query_terms,
            show_usage=show_usage,
            show_duration=show_duration,
            show_description=not hide_description,
            custom_columns=custom_columns,
            output_format=output_format,
            datetime_format=datetime_format,
            duration_fmt=duration_fmt,
            spark_total=spark_total,
            spark_width=spark_width,
            spark_secs=spark_secs,
            show_totals=show_totals,
            hide_totals=hide_totals,
            re_sort=re_sort,
        )
        return tabulation

    # ***

    def restrict_width(max_width):
        if max_width is not None and max_width >= 0:
            return max_width
        elif sys.stdout.isatty():
            # MAGIC_NUMBER: Subtract 1 to leave an empty column border on the right.
            return click.get_terminal_size()[0] - 1
        else:
            return 80

    # ***

    return _render_results()

# ***

