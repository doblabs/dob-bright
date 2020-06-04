# This file exists within 'dob-bright':
#
#   https://github.com/hotoffthehamster/dob-bright
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
from nark.reports.tsv_writer import TSVWriter
from nark.reports.xml_writer import XMLWriter

from ..termio.paging import ClickEchoPager
from ..termio.style import stylize

from .factoid_writer import FactoidWriter
from .journal_writer import JournalWriter
from .table_writer import TableWriter
from .tabulate_results import headers_for_columns, tabulate_results

__all__ = (
    'render_results',
)


def render_results(
    controller,
    results,
    headers=None,
    query_terms=None,
    hide_usage=False,
    hide_duration=False,
    hide_description=False,
    custom_columns=None,
    output_format='friendly',
    datetime_format=None,
    duration_fmt=None,
    spark_total=None,
    spark_width=None,
    spark_secs=None,
    output_path=None,
    row_limit=0,
    term_width=None,
    chop=False,
    factoid_rule='',
    re_sort=False,
):
    """"""

    def _render_results():
        # Send output to the path indicated, or stdout or pager.
        output_obj = output_path or ClickEchoPager
        writer = fetch_report_writer(output_format, output_obj)
        n_written = prepare_and_render_results(writer)
        return n_written

    # ***

    def fetch_report_writer(output_format, output_obj):
        row_width = restrict_width(term_width)
        writer = fetch_report_writer_cls(output_format, term_width=row_width)
        writer.output_setup(
            output_obj=output_obj,
            row_limit=row_limit,
            datetime_format=datetime_format,
            duration_fmt=duration_fmt,
        )
        return writer

    def fetch_report_writer_cls(output_format, term_width):
        writer = None
        if output_format == 'csv':
            writer = CSVWriter()
        elif output_format == 'tsv':
            writer = TSVWriter()
        elif output_format == 'ical':
            writer = ICALWriter()
        elif output_format == 'xml':
            writer = XMLWriter()
        elif output_format == 'factoid':
            colorful = controller.config['term.use_color']
            cut_width = term_width if chop else None
            rule_mult = term_width if len(factoid_rule) == 1 else 1
            # FIXME: This should be customizable, eh.
            factoid_sep = stylize(factoid_rule * rule_mult, 'indian_red_1c')
            writer = FactoidWriter(
                colorful=colorful,
                cut_width=cut_width,
                factoid_sep=factoid_sep,
                hide_duration=hide_duration,
            )
        elif output_format == 'journal':
            writer = JournalWriter()
        else:
            writer = TableWriter(
                output_format=output_format,
                chop=chop,
                term_width=term_width,
            )
        return writer

    # ***

    def prepare_and_render_results(writer):
        # MAYBE: Do we care?: The desc_col_idx feature only works if
        #                     prepare_table_and_columns is called.
        if headers is not None:
            # For list/usage act/cat/tag, already have ready table and headers.
            n_written = writer.write_report(results, headers)
        elif query_terms.include_stats or writer.requires_table:
            # For reports with stats, post-process results; possibly sort.
            table, columns = prepare_table_and_columns()
            writer.desc_col_idx = deduce_trunccol(columns) if chop else None
            col_headers = headers_for_columns(columns)
            n_written = writer.write_report(table, col_headers)
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
        table, columns = tabulate_results(
            controller,
            results,
            row_limit=row_limit,
            query_terms=query_terms,
            show_usage=not hide_usage,
            show_duration=not hide_duration,
            show_description=not hide_description,
            custom_columns=custom_columns,
            output_format=output_format,
            datetime_format=datetime_format,
            duration_fmt=duration_fmt,
            spark_total=spark_total,
            spark_width=spark_width,
            spark_secs=spark_secs,
            re_sort=re_sort,
        )
        return table, columns

    # ***

    def deduce_trunccol(columns):
        # This is very inexact psyence. (We could maybe expose this as a CLI
        # option.) Figure out which column is appropriate to truncate.
        # - (lb): Back in 2018 when I first wrote this, the 'description'
        #   seemed like the obvious column. But it's no longer always there.
        #   And also, now you can group-by columns, which can make for a
        #   very long actegories column. Even tags might be a candidate.
        if columns is None:
            return 'description'

        for candidate in [
            'description',
            'actegories',
            'activities',
            'categories',
            'tags',
        ]:
            try:
                return columns.index(candidate)
            except ValueError:
                pass
        # Give up. No column identified.
        return None

    # ***

    def restrict_width(term_width):
        if term_width is not None:
            return term_width
        elif sys.stdout.isatty():
            return click.get_terminal_size()[0]
        else:
            return 80

    # ***

    return _render_results()

# ***

