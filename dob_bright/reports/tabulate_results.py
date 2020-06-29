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

from click_hotoffthehamster._compat import term_len
from collections import namedtuple
from collections.abc import Iterable
from operator import attrgetter

from gettext import gettext as _

from nark.backends.sqlalchemy.managers import query_sort_order_at_index
from nark.backends.sqlalchemy.managers.fact import FactManager
from nark.helpers.format_time import format_delta
from nark.items.tag import Tag
from nark.managers.query_terms import QueryTerms

__all__ = (
    'report_table_columns',
    'tabulate_results',
    # Private:
    #  '_GrossTotals',
    #  '_ReportColumn',
    #  'ResultsTabulation',
    #  'FACT_TABLE_HEADERS',
)

# ***

_ReportColumn = namedtuple(
    '_ReportColumn',
    ('column', 'header', 'align', 'option'),
)

REPORT_COLUMNS = {
    # Fact attributes.
    _ReportColumn('key', _("Key"), 'l', True),
    _ReportColumn('start', _("Start"), 'l', True),
    _ReportColumn('end', _("End"), 'l', True),
    _ReportColumn('activity', _("Activity"), 'l', True),
    _ReportColumn('category', _("Category"), 'l', True),
    _ReportColumn('tags', _("Tags"), 'l', True),
    _ReportColumn('description', _("Description"), 'l', True),
    # Group-by aggregates. See: FactManager.RESULT_GRP_INDEX.
    # MAYBE/2020-06-02: Append units to header, e.g., "Duration (mins.)"
    # NOTE: Because we right-pad duration with spaces, use left-align,
    #       otherwise the texttable format will strip right whitespace.
    _ReportColumn('duration', _("Duration"), 'l', True),
    # The journal format shows a sparkline.
    # MAYBE/2020-05-18: Add sparkline option to ASCII table formats.
    _ReportColumn('sparkline', _("Sparkline"), 'l', True),
    _ReportColumn('group_count', _("Uses"), 'r', True),
    # MAYBE/2020-05-18: Format first_start and final_end per user --option.
    # - For now, ASCII table formatter is just str()'ifying.
    _ReportColumn('first_start', _("First Start"), 'l', True),
    _ReportColumn('final_end', _("Final End"), 'l', True),
    _ReportColumn('activities', _("Activities"), 'l', True),
    _ReportColumn('actegories', _("Actegories"), 'l', True),
    _ReportColumn('categories', _("Categories"), 'l', True),
    # The actegory is used for the journal format.
    _ReportColumn('actegory', _("Actegory"), 'l', True),
    # A singular 'tag' column happens when Act@Cat aggregated b/c group_tags.
    _ReportColumn('tag', _("Tag"), 'l', True),
    # More options for the journal format:
    _ReportColumn('start_date', _("Start date"), 'l', True),
    _ReportColumn('start_date_cmp', _("Startdate"), 'l', False),
    _ReportColumn('start_time', _("Start time"), 'l', True),
    _ReportColumn('end_date', _("End date"), 'l', True),
}


FACT_TABLE_HEADERS = {repcol.column: repcol for repcol in REPORT_COLUMNS}


def report_table_columns():
    return [item.column for key, item in FACT_TABLE_HEADERS.items() if item.option]


# ***

# (lb): I wrote tabulate_results as a procedural function because it's called
# just once, so it does not need to maintain state, but really to avoid cluttering
# the code with a bunch of `self.` references. (But take your pick: not everyone
# will like function-scoped functions; some devs might consider a class to be
# cleaner.) Nonetheless, tabulate_results generates a few different result
# structures, which we encapsulate using a named tuple (the following namedtuple),
# so at least the calling code is more readable and better maintainable, and the
# caller does not have to unpack a list and to know what's what by position alone.
# (Is this too explain-y? I figured I should at least rationalize why I started
# scoping functions within functions this past year, as opposed to my earlier
# hacking-development efforts where I tended toward writing classes instead.)
ResultsTabulation = namedtuple(
    'ResultsTabulation', ('table', 'repcols', 'max_widths')
)


# ***

class _GrossTotals(object):
    def __init__(self):
        # Durations summation (duration).
        self.cum_duration = 0
        self.max_duration = 0
        # Group count count (group_count).
        self.group_count = 0
        # First first_start (first_start).
        self.first_start = None
        # Final final_end (final_end).
        self.final_end = None
        # Accumulated tags (and their frequencies).
        self.amassed_tags = {}

    def update_durations(self, duration):
        self.cum_duration += duration
        self.max_duration = max(self.max_duration, duration)

    def update_group_count(self, group_count):
        self.group_count += group_count

    def update_first_and_final(self, first_start, final_end):
        if self.first_start is None:
            self.first_start = first_start
        else:
            self.first_start = min(self.first_start, first_start)

        if self.final_end is None:
            self.final_end = final_end
        else:
            self.final_end = max(self.final_end, final_end)

    def update_amassed_tags(self, fact_tags):
        for fact_tag in fact_tags:
            self.update_amassed_tag(fact_tag)

    def update_amassed_tag(self, fact_tag):
        try:
            gross_tag = self.amassed_tags[fact_tag.name]
        except KeyError:
            gross_tag = Tag(fact_tag.name, fact_tag.pk, freq=fact_tag.freq)
            self.amassed_tags[fact_tag.name] = gross_tag
        else:
            gross_tag.freq += fact_tag.freq


# ***

def tabulate_results(
    controller,
    results,
    row_limit=0,
    # If no QueryTerms is specified, the results is a simple list of items.
    # Otherwise, the query_terms will indicate the structure of the results
    # to be processed.
    query_terms=None,
    # Unless the caller specifies custom_columns, a default set of output
    # values will be chosen, based on query_terms and output_format. Some
    # of the default report values can be excluded by disabling these args.
    show_usage=True,
    show_duration=True,
    show_description=True,
    show_deleted=False,
    # The reported values (and their order) can be specified by the caller,
    # otherwise query_terms and output_format are used to determine a good
    # set of values to show in the report.
    custom_columns=None,
    # Unless custom_columns is specified, use output_format to decide on the
    # default set of values to report (e.g., 'table' shows different outputs
    # that 'journal' by default).
    output_format=None,
    # The value modifiers affect how specific values are computed and formatted.
    datetime_format=None,
    duration_fmt=None,
    spark_total=None,
    spark_width=None,
    spark_secs=None,
    # Include totals by default when aggregating results, except for Journal.
    show_totals=False,
    hide_totals=False,
    # The --re-sort option lets a developer force this function to re-sort the
    # results, even if the SQL query already guaranteed their ordering.
    re_sort=False,
    # Include maximum column widths if needed by the output formatter.
    track_widths=False,
):
    """
    Prepares Facts for display in an ASCII table.

    Returns a (table, header) tuple. 'table' is a list of ``TableRow``
    instances, each representing a single Fact, or the summary of a
    group of Facts.
    """
    qt = query_terms if query_terms is not None else QueryTerms()

    for_journal = output_format == 'journal'
    track_widths = True if for_journal else track_widths

    columns = []
    repcols = {}
    sorting_columns = None
    # YOU: Uncomment to force running re-sorting code, or use hidden --re-sort.
    #  re_sort = True

    if not custom_columns:
        include_usage = show_usage
        include_duration = show_duration
        include_description = show_description
        include_deleted = show_deleted
    else:
        include_usage = 'group_count' in custom_columns
        include_duration = 'duration' in custom_columns
        include_description = 'description' in custom_columns
        include_deleted = 'deleted' in custom_columns

    if datetime_format is None:
        if for_journal or qt.include_stats:
            # For Journal or when including stats, simply report by excluding seconds.
            datetime_format = '%Y-%m-%d %H:%M'
        else:
            # For single facts, export is often to CSV, etc., so include seconds.
            datetime_format = '%Y-%m-%d %H:%M:%S'

    if duration_fmt is None:
        if for_journal or qt.include_stats:
            # Use pedantic_timedelta to format the duration.
            duration_fmt = ''
        else:
            # Show duration as minutes. (lb): Though not sure what best default is.
            # - Another option: duration_fmt = '%H:%M'
            # - Another option: duration_fmt = '%S'
            duration_fmt = '%M'
    # A tracking variable to pad 'duration' so decimal points align in table view.
    col_adjust = {'duration_apres_dot': -1}

    i_cum_duration = FactManager.RESULT_GRP_INDEX['duration']
    i_group_count = FactManager.RESULT_GRP_INDEX['group_count']
    i_first_start = FactManager.RESULT_GRP_INDEX['first_start']
    i_final_end = FactManager.RESULT_GRP_INDEX['final_end']
    i_activities = FactManager.RESULT_GRP_INDEX['activities']
    i_actegories = FactManager.RESULT_GRP_INDEX['actegories']
    i_categories = FactManager.RESULT_GRP_INDEX['categories']
    i_start_date = FactManager.RESULT_GRP_INDEX['start_date']

    def _generate_facts_table():
        test_result = results[0] if results else None
        TableRow, sortref_cols = prepare_columns(test_result)
        max_widths = {column: -1 for column in columns}

        gross_totals = _GrossTotals()

        table_rows = []
        n_row = 0
        for result in results:
            n_row += 1
            if row_limit and row_limit > 0 and n_row > row_limit:
                break

            fact_etc = prepare_fact_and_aggs_list(result)
            table_row = prepare_row(fact_etc, max_widths)
            table_rows.append(table_row)

            update_gross(fact_etc, gross_totals)
            update_widths(table_row, max_widths)

        create_sparklines(table_rows, gross_totals, max_widths)

        results_final_sort(table_rows)

        table_row = produce_gross(gross_totals)
        if table_row is not None:
            empty_row = {key: '' for key in columns}
            table_rows.append(empty_row)
            table_rows.append(table_row)

        table = [TableRow(**finalize_row(row)) for row in table_rows]
        repcols = [FACT_TABLE_HEADERS[column] for column in columns]
        max_widths_tup = TableRow(**max_widths)
        tabulation = ResultsTabulation(table, repcols, max_widths_tup)

        return tabulation

    # ***

    def prepare_columns(test_result):
        # REMINDER: Use sneaky [:] slice trick to mutate outer-scoped 'columns' var.
        columns[:], sortref_cols = assemble_columns(test_result)
        repcols.update({
            key: val for key, val in FACT_TABLE_HEADERS.items() if key in columns
        })
        TableRow = namedtuple('TableRow', columns)
        return TableRow, sortref_cols

    # +++

    def assemble_columns(test_result):
        report_columns = assemble_columns_report(test_result)
        sortref_cols = extend_columns_sorting(report_columns)
        return report_columns, sortref_cols

    def assemble_columns_report(test_result):
        if custom_columns:
            return assemble_columns_report_custom()
        return assemble_columns_report_deduce(test_result)

    def assemble_columns_report_custom():
        custom_cols = assemble_columns_report_custom_build()
        return assemble_columns_report_custom_sanitize(custom_cols)

    def assemble_columns_report_custom_build():
        # Cull list of duplicates, retaining order.
        seen = set()
        seen_add = seen.add
        return [
            col for col in custom_columns
            if not (col in seen or seen_add(col))
        ]

    def assemble_columns_report_custom_sanitize(custom_cols):
        if qt.is_grouped:
            disallow = set([
                'key',
                'start',
                'end',
                'description',
            ])
            # MAYBE/2020-05-20: Should we disallow 'activity' if not group_activity?
            # - Disallow 'category' if not group_category.
            # - Disallow 'tags' if group_tags (and disallow 'tag' otherwise).
            # - What about 'activities', 'actegories', 'categories', 'actegory'?
        else:
            # Not is_grouped.
            disallow = set([
                'activities',
                'actegories',
                'categories',
                'actegory',
                'tag',
            ])
        return [col for col in custom_columns if col not in disallow]

    def assemble_columns_report_deduce(test_result):
        aggregate_cols = assemble_columns_sample_aggregate(test_result)
        if for_journal:
            return assemble_columns_for_journal(aggregate_cols)
        elif not qt.include_stats:
            return assemble_columns_single_fact()
        return assemble_columns_fact_and_aggs(aggregate_cols)

    def assemble_columns_sample_aggregate(test_result):
        if test_result and isinstance(test_result, Iterable):
            # Ignore the fact, which is the first element.
            aggregate_cols = test_result[1:]
        else:
            aggregate_cols = group_cols_shim(test_result)
        return aggregate_cols

    def extend_columns_sorting(report_columns):
        # reference_cols = set(sorting_columns).difference(set[report_columns])
        reference_cols = [col for col in sorting_columns if col not in report_columns]
        report_columns.extend(reference_cols)
        return (sorting_columns, reference_cols)

    # +++

    def assemble_columns_for_journal(aggregate_cols):
        # Start by deciding which columns to show first,
        # which depends on sorting and grouping.
        time_cols = []
        if qt.group_days:
            first_cols = ['start_date']
        else:
            sort_attr = attr_for_sort_col()
            first_cols = journal_first_columns(aggregate_cols, sort_attr)
            if not first_cols:
                # first_cols = ['start_date', 'start_time']
                first_cols = ['end_date', 'start_time']
            elif qt.is_grouped:
                # FIXME: make date format Fri Jun 29  9:30am but let user change...
                time_cols = ['first_start', 'final_end']
            else:
                time_cols = ['start', 'end']

        # Gather the Fact attribute columns to display, which depends on
        # which aggregate columns were used in the query. We also add the
        # separator, '@', because the journal view does not use column
        # headers, and without, the user would have no context, and would
        # not know their activities from their categories.
        meta_cols = assemble_columns_fact_and_aggs_meta(aggregate_cols)
        # Remove meta_cols that may have been promoted to first positions.
        meta_cols = [col for col in meta_cols if col not in first_cols]

        # Default order (unless user overrides, in which case this function
        # is not called), is to show some main identifier column(s) (as
        # determined by journal_first_columns), that some statistics (which
        # we'll add now), followed by the time columns (if not already shown)
        # and then the remaining attribute columns (not already shown).
        _columns = []
        _columns.extend(first_cols)
        _columns.append('duration')
        _columns.append('sparkline')
        _columns.extend(time_cols)
        _columns.extend(meta_cols)
        # If qt.group_days, may add 'start_date_cmp', per sort_col_actual(),
        # but only if re_sort is enabled; otherwise query SELECT sorts on it.

        return _columns

    def attr_for_sort_col():
        # --sort [name|activity|category|tag|fact|start|usage|time|day]
        sort_col = qt.sort_cols[0] if qt.sort_cols else ''
        if sort_col in ('activity', 'category', 'tag'):
            return sort_col
        return ''

    def journal_first_columns(aggregate_cols, sort_attr):
        # The special value used is 0, but cannot hurt to check None, too.
        if aggregate_cols[i_activities] not in [0, None]:
            # group_category (and maybe group_tags, too).
            if sort_attr == 'category':
                return ['category']
            elif sort_attr == 'activity':
                return ['activities']
            elif sort_attr == 'tag':
                return ['tags']
        elif aggregate_cols[i_actegories] not in [0, None]:
            # group_tags (but neither group_category or group_activity).
            if sort_attr == 'tag':
                if qt.group_days:
                    return ['tags']
                else:
                    return ['tag']
            elif sort_attr == 'activity' or sort_attr == 'category':
                return ['actegories']
        elif aggregate_cols[i_categories] not in [0, None]:
            # group_activity (and maybe group_tags, too).
            if sort_attr == 'activity':
                return ['activity']
            elif sort_attr == 'category':
                return ['categories']
            elif sort_attr == 'tag':
                return ['tags']
        elif qt.group_days:
            return None
        elif qt.is_grouped:
            # group_activity and group_category.
            return ['actegory']
        # else, nothing grouped, and not sorting on Fact attribute.
        # - So. --sort either not specified, or: [name|fact|start|usage|time]
        return None

    # +++

    def assemble_columns_single_fact():
        _columns = [
            'key',
            'start',
            'end',
            'activity',
            'category',
            'tags',
        ]
        if include_description:
            _columns.append('description')
        if include_duration:
            _columns.append('duration')
        if include_deleted:
            _columns.append('deleted')
        return _columns

    # +++

    def assemble_columns_fact_and_aggs(aggregate_cols):
        _columns = []
        _columns.extend(assemble_columns_fact_and_aggs_meta(aggregate_cols))
        assemble_columns_fact_and_aggs_duration(aggregate_cols, _columns)
        assemble_columns_fact_and_aggs_usage(aggregate_cols, _columns)
        return _columns

    def assemble_columns_fact_and_aggs_meta(aggregate_cols):
        meta_cols = []
        # The special value used is 0, but cannot hurt to check None, too.
        if aggregate_cols[i_activities] not in [0, None]:
            # group_category (and maybe group_tags, too).
            meta_cols.append('category')
            meta_cols.append('activities')
            meta_cols.append('tags')
        elif aggregate_cols[i_actegories] not in [0, None]:
            # group_tags (but neither group_category or group_activity).
            if qt.group_days:
                meta_cols.append('tags')
            else:
                meta_cols.append('tag')
            meta_cols.append('actegories')
        elif aggregate_cols[i_categories] not in [0, None]:
            # group_activity (and maybe group_tags, too).
            meta_cols.append('activity')
            meta_cols.append('categories')
            meta_cols.append('tags')
        else:
            # group_activity and group_category, or nothing grouped.
            if not for_journal:
                meta_cols.append('activity')
                meta_cols.append('category')
            else:
                meta_cols.append('actegory')
            meta_cols.append('tags')
        return meta_cols

    def assemble_columns_fact_and_aggs_duration(aggregate_cols, _columns):
        if not include_duration:
            return

        _columns.append('duration')

    def assemble_columns_fact_and_aggs_usage(aggregate_cols, _columns):
        if not include_usage:
            return

        _columns.append('group_count')
        _columns.append('first_start')
        _columns.append('final_end')

    # +++

    def group_cols_shim(fact):
        cols_shim = [None] * len(FactManager.RESULT_GRP_INDEX)
        # Because julianday, expects days. MAGIC_NUMBER: 86400 secs/day.
        if fact is not None:
            cols_shim[i_cum_duration] = fact.delta().total_seconds() / 86400.0
            cols_shim[i_group_count] = 1
            cols_shim[i_first_start] = fact.start
            cols_shim[i_final_end] = fact.end
        # 0 is what get_all uses in place of group_concat (which emits a string).
        cols_shim[i_activities] = 0
        cols_shim[i_actegories] = 0
        cols_shim[i_categories] = 0
        cols_shim[i_start_date] = None
        return cols_shim

    # ***

    def prepare_fact_and_aggs_list(result):
        # Get ready to unpack the Fact and the aggregate columns by first
        # ensuring that the result is unpackable (but creating the aggregate
        # columns if necessary).
        # - We could deduce the structure of the result by checking our bools:
        #     if not is_grouped and not include_usage:
        #   but checking if an iterable seems more robust/readable.
        if isinstance(result, Iterable):
            # Already packed.
            return result
        # The result is a simple Fact. Create the equivalent aggregate columns.
        aggregate_cols = group_cols_shim(result)
        return [result] + aggregate_cols

    def prepare_row(fact_etc, max_widths):
        # Each result is a tuple: First the Fact, and then the
        # aggregate columns (see FactManager.RESULT_GRP_INDEX).
        (
            fact,
            duration,
            group_count,
            first_start,
            final_end,
            activities,
            actegories,
            categories,
            start_date,
        ) = fact_etc

        if not final_end:
            final_end = controller.store.now

        table_row = {}

        prepare_key(table_row, fact)

        prepare_starts_and_end(
            table_row, fact, first_start, final_end, start_date,
        )
        prepare_activity_and_category(
            table_row, fact, activities, actegories, categories,
        )
        prepare_duration(table_row, fact, duration, max_widths)
        prepare_group_count(table_row, group_count)
        prepare_first_start(table_row, first_start)
        prepare_final_end(table_row, final_end)
        prepare_description(table_row, fact)
        prepare_deleted(table_row, fact)

        row_slice = unprepare_unmentioned_columns(table_row)

        return row_slice

    # ***

    def prepare_key(table_row, fact):
        if 'key' not in repcols:
            return

        table_row['key'] = fact.pk

    # +++

    def prepare_starts_and_end(table_row, fact, first_start, final_end, start_date):
        prepare_start_date(table_row, fact, first_start)
        prepare_start_date_cmp(table_row, fact, first_start, start_date)
        prepare_start_time(table_row, fact, first_start)
        prepare_end_date(table_row, fact, final_end)
        prepare_start(table_row, fact)
        prepare_end(table_row, fact)

    def prepare_start_date(table_row, fact, first_start):
        if 'start_date' not in repcols:
            return

        # MAYBE/2020-05-18: Make this and other strftime formats --option'able.
        start_date = first_start.strftime('%a %b %d') if first_start else ''
        table_row['start_date'] = start_date

    def prepare_start_date_cmp(table_row, fact, first_start, start_date):
        if 'start_date_cmp' not in repcols:
            return

        # The SQLite date(col) produces, e.g., '2020-05-14'.
        if start_date:
            start_date_cmp = start_date
        else:
            start_date_cmp = first_start.strftime('%Y-%m-%d') if first_start else ''
        table_row['start_date_cmp'] = start_date_cmp

    def prepare_start_time(table_row, fact, first_start):
        if 'start_time' not in repcols:
            return

        start_time = first_start.strftime(datetime_format) if first_start else ''
        table_row['start_time'] = start_time

    def prepare_end_date(table_row, fact, final_end):
        if 'end_date' not in repcols:
            return

        end_date = final_end.strftime('%a %b %d') if final_end else ''
        table_row['end_date'] = end_date

    def prepare_start(table_row, fact):
        if 'start' not in repcols:
            return

        table_row['start'] = fact.start_fmt(datetime_format)

    def prepare_end(table_row, fact):
        if 'end' not in repcols:
            return

        if fact.end:
            fact_end = fact.end_fmt(datetime_format)
        else:
            # FIXME: This is just the start of supporting open ended Fact in db.
            if for_journal or qt.include_stats:
                fact_end = _('<active>')
            else:
                fact_end = ''
            # Replace None with 'now', so that fact.delta() returns something
            # (that is, if we don't use the 'duration' from the results, which was
            # calculated by the SQL query (using the computed 'endornow' column)).
            fact.end = controller.now
        table_row['end'] = fact_end

    # +++

    def prepare_activity_and_category(
        table_row, fact, activities, actegories, categories,
    ):
        # The special value used is 0, but cannot hurt to check None, too.
        if activities not in [None, 0]:
            # Grouped by category (and possibly tags, too).
            prepare_category(table_row, fact)
            prepare_activities(table_row, activities)
            prepare_tagnames(table_row, fact)
        elif actegories not in [None, 0]:
            # Group by tags but not activity or category.
            prepare_actegories(table_row, actegories)
            if qt.group_days:
                prepare_tagnames(table_row, fact)
            else:
                # Else, group_tags, so one each.
                prepare_tagname(table_row, fact)
        elif categories not in [None, 0]:
            # Group by activity name (and possibly tags, too).
            prepare_activity(table_row, fact)
            prepare_categories(table_row, categories)
            prepare_tagnames(table_row, fact)
        else:
            # Group by activity ID and category ID, or no grouping.
            if not for_journal:
                prepare_activity(table_row, fact)
                prepare_category(table_row, fact)
            else:
                prepare_actegory(table_row, fact)
            prepare_tagnames(table_row, fact)

    def prepare_activity(table_row, fact):
        if 'activity' not in repcols:
            return

        table_row['activity'] = fact.activity_name + actcatsep()

    def prepare_activities(table_row, activities, sep=_(', ')):
        if 'activities' not in repcols:
            return

        table_row['activities'] = sep.join(
            [activity + actcatsep() for activity in sorted(activities)]
        )

    def prepare_actegories(table_row, actegories, sep=_(', ')):
        if 'actegories' not in repcols:
            return

        table_row['actegories'] = sep.join(sorted(actegories))

    def prepare_categories(table_row, categories, sep=_(', ')):
        if 'categories' not in repcols:
            return

        table_row['categories'] = sep.join(
            [actcatsep() + category for category in sorted(categories)]
        )

    def prepare_category(table_row, fact):
        if 'category' not in repcols:
            return

        table_row['category'] = actcatsep() + fact.category_name

    def prepare_actegory(table_row, fact):
        if 'actegory' not in repcols:
            return

        table_row['actegory'] = fact.oid_actegory()

    # MAYBE/2020-05-18: Make the '@' symbol configable.
    def actcatsep(sep=_('@')):
        if for_journal:
            return sep
        return ''

    # +++

    def prepare_tagnames(table_row, fact):
        if 'tags' not in repcols:
            return

        table_row['tags'] = assemble_tags(fact.tags)

    def prepare_tagname(table_row, fact):
        if 'tag' not in repcols:
            return

        table_row['tag'] = assemble_tags(fact.tags)

    def assemble_tags(fact_tags):
        tag_names = []
        for tag in fact_tags:
            if tag.freq == 1:
                tag_name = '#{}'.format(tag.name)
            else:
                tag_name = '#{}({})'.format(tag.name, tag.freq)
            tag_names.append(tag_name)

        tags = ' '.join(sorted(tag_names))
        return tags

    # +++

    def prepare_duration(table_row, fact, duration, max_widths):
        if 'duration' not in repcols:
            return

        # Note that the 'duration' will be similar to fact.format_delta()
        # unless is_grouped, in which case 'duration' is an aggregate value.
        # But in either case, the 'duration' in the results is expressed in days.
        if 'sparkline' not in columns:
            # Finalize the duration as a string value.
            duration = format_fact_or_query_duration(fact, duration)
            prepare_row_duration(table_row, duration, max_widths)
        else:
            # We'll prepare a sparkline later, so keep the durations value
            # (in secs.), until we post-process it.
            if not duration:
                duration = fact.delta().total_seconds()
            else:
                duration = convert_duration_days_to_secs(duration)
            table_row['duration'] = duration

    def format_fact_or_query_duration(fact, duration):
        if not duration:
            # MAYBE/2020-05-18: Use format_duration_secs() instead, to be
            # consistent.
            #  fmt_duration = fact.format_delta(style='')
            duration_secs = fact.delta().total_seconds()
        else:
            #  fmt_duration = format_duration_days(duration)
            duration_secs = convert_duration_days_to_secs(duration)
        fmt_duration = format_duration_secs(duration_secs)
        return fmt_duration

    # - MAGIC_NUMBER: 86400 seconds/day, to convert between timedelta
    #                 (seconds) and SQLite julianday computation (days).
    SECONDS_IN_DAY = 86400.0

    def convert_duration_days_to_secs(duration):
        # - The duration was computed by julianday math, so it's in days,
        #   and format_delta expects seconds, so convert to the latter.
        durasecs = duration * SECONDS_IN_DAY
        return durasecs

    def format_duration_days(duration):
        durasecs = convert_duration_days_to_secs(duration)
        fmt_duration = format_duration_secs(durasecs)
        return fmt_duration

    def format_duration_secs(durasecs):
        # Default to using pedantic_timedelta to format the duration.
        style = '' if duration_fmt is None else duration_fmt
        # MAGIC_NUMBERS: Specify the formatted field width and precision.
        # - Use a field width so the column values align --
        #   a field_width of 4 will align most values, e.g.,
        #        aligned:        not aligned:
        #       12.5 hours       12.5 hours
        #        1.0 mins.       1.0 mins.
        # - Also set precision=1, as the default, 2, is more precision
        #   than the user needs.
        #   - I also think that looking at, say, "7.02 minutes" is more
        #     complicated/distracting than seeing "7.0 minutes". My brain
        #     pauses longer to digest the hundredths place, but the extra
        #     information is of no value to me.
        fmt_duration = format_delta(
            durasecs, style=style, field_width=4, precision=1,
        )
        return fmt_duration

    def prepare_row_duration(table_row, duration, max_widths):
        table_row['duration'] = duration
        update_max_widths_column(table_row, 'duration', max_widths)
        update_duration_apres_dot(duration)

    def update_max_widths_column(table_row, column, max_widths):
        if not track_widths:
            return

        max_widths[column] = max(term_len(table_row[column]), max_widths[column])

    def update_duration_apres_dot(duration):
        if output_format not in ('table', 'journal'):
            return

        try:
            col_adjust['duration_apres_dot'] = max(
                term_len(duration) - duration.index('.'),
                col_adjust['duration_apres_dot'],
            )
        except ValueError:
            pass

    # +++

    def create_sparklines(table_rows, gross_totals, max_widths):
        if 'sparkline' not in columns:
            return

        # REMINDER: These values are in days.
        cum_duration = convert_duration_days_to_secs(gross_totals.cum_duration)
        max_duration = convert_duration_days_to_secs(gross_totals.max_duration)

        if not spark_total or spark_total == 'max':
            spark_max_value = max_duration
        elif spark_total == 'net':
            spark_max_value = cum_duration
        else:
            # The user directly specified some number of seconds.
            # - This sets a custom max value reference, e.g., you could
            #   set the full width of a sparkline to represent 8 hours:
            #       spark_max_value = 8 * 60 * 60  # 8 hours.
            #   Or from the CLI:
            #       dob list ... --spark-total '8 * 60 * 60'
            # - Note that if this is less than max_duration, some sparklines
            #   will run over their allotted column width.
            spark_max_value = spark_total

        # MAGIC_NUMBER: Prefer --spark-width, or default to a 12-character
        # width, just to do something so the width is not nothing.
        spark_chunk_width = spark_width or 12

        # User can specify --spark-secs, or we'll calculate from
        # the previous two values: this is the seconds represented
        # by one █ block, i.e., the full block time divided by the
        # total number of blocks being used (or at least the number
        # of blocks it would take to fill the specified field width).
        # - HINT: This option eval-aware, e.g., 1 hour: --spark-secs '60 * 60'.
        spark_chunk_secs = spark_secs or (spark_max_value / spark_chunk_width)

        def prepare_sparkline(table_row):
            # We stashed the duration as seconds.
            dur_seconds = table_row['duration']
            sparkline = spark_up(dur_seconds, spark_chunk_secs)
            table_row['sparkline'] = sparkline
            update_max_widths_column(table_row, 'sparkline', max_widths)

            # We've used the seconds value, so now we can format the duration.
            duration = format_duration_secs(dur_seconds)
            prepare_row_duration(table_row, duration, max_widths)

        def spark_up(dur_seconds, spark_chunk_secs):
            # Thanks to:
            #   https://alexwlchan.net/2018/05/ascii-bar-charts/
            # MAGIC_NUMBER: The ASCII block elements come in 8 widths.
            #   https://en.wikipedia.org/wiki/Block_Elements
            n_chunks, remainder = divmod(dur_seconds, spark_chunk_secs)
            n_eighths = int(8 * (remainder / spark_chunk_secs))
            # Start with the full-width block elements.
            sparkline = '█' * int(n_chunks)
            # Add the fractional block element. Note that the Unicode
            # code points for block elements are decreasingly ordered,
            # (8/8), (7/8), (6/8), etc., so subtract the number of eighths.
            if n_eighths > 0:
                # MAGIC_NUMBER: The Block Element code points are sequential,
                #   and there are 9 of them (1 full width + 8 eighths).
                sparkline += chr(ord('█') + (8 - n_eighths))
            # If the sparkline is empty, show at least a little something.
            # - Add a left one-eighth block.
            sparkline = sparkline or '▏'
            # Pad the result.
            sparkline = '{:{}s}'.format(sparkline, spark_chunk_width)
            return sparkline

        # +++

        for table_row in table_rows:
            prepare_sparkline(table_row)

    # +++

    def prepare_group_count(table_row, group_count):
        if 'group_count' not in repcols:
            return

        table_row['group_count'] = str(group_count)

    def prepare_first_start(table_row, first_start):
        if 'first_start' not in repcols:
            return

        first_start = first_start.strftime(datetime_format) if first_start else ''
        table_row['first_start'] = first_start

    def prepare_final_end(table_row, final_end):
        if 'final_end' not in repcols:
            return

        final_end = final_end.strftime(datetime_format) if final_end else ''
        table_row['final_end'] = final_end

    # +++

    def prepare_description(table_row, fact):
        if 'description' not in repcols:
            return

        table_row['description'] = fact.description or ''

    # +++

    def prepare_deleted(table_row, fact):
        if 'deleted' not in repcols:
            return

        table_row['deleted'] = str(fact.deleted)

    # ***

    # MAYBE/2020-05-20: This function can probably be removed.
    # (lb): I added `X not in repcols` checks to all the `table_row[Y] =` functions.
    # So I'd guess the table_row is has the correct attrs, and none superfluous.
    def unprepare_unmentioned_columns(table_row):
        if not custom_columns:
            return table_row

        # Rebuild the table row, but exclude excluded columns.
        # (lb): We could add `'column' not in columns` to every prepare_*
        # function, but that'd be noisy. Seems better to rebuild the dict.
        row_slice = {
            key: val for key, val in table_row.items() if key in columns
        }

        # Add any columns the user specified that are missing, e.g.,
        # if the user added, say, 'description' to an aggregate query.
        # (This is us being nice, so we don't stack trace just because
        # the user specified a "weird" combination of CLI options.)
        missing = [key for key in columns if key not in row_slice]
        for key in missing:
            row_slice[key] = ''

        # +++

        # 2020-05-21: (lb): If you're confident other mechanisms are WAD,
        # you could disable/delete unprepare_unmentioned_columns. The old
        # post-processing would populate most/all possible columns, and
        # then remove columns that are not needed (and that TableRow would
        # complain about). The new post-processing is more deliberate and
        # should not have extraneous columns to remove.
        if row_slice != table_row:
            controller.client_logger.warning(
                'Unexpected: row_slice != table_row / row_slice: {} / table_row: {}'
                .format(row_slice, table_row)
            )

        return row_slice

    # ***

    def update_gross(fact_etc, gross_totals):
        fact, *cols = fact_etc

        gross_totals.update_durations(cols[i_cum_duration])

        gross_totals.update_group_count(cols[i_group_count])

        first_start = cols[i_first_start]
        final_end = cols[i_final_end] or controller.store.now
        gross_totals.update_first_and_final(first_start, final_end)

        gross_totals.update_amassed_tags(fact.tags)

    # +++

    def update_widths(table_row, max_widths):
        if not track_widths:
            return

        for column in columns:
            try:
                max_widths[column] = max(term_len(table_row[column]), max_widths[column])
            except TypeError:
                # Not a string, e.g., an int or float.
                pass
            except KeyError:
                # 'sparkline' not computed until end so in columns but not in table_row.
                assert column == 'sparkline'
                pass

    # +++

    def produce_gross(gross_totals):
        if (
            (gross_totals is None or not qt.include_stats)
            or (not for_journal and hide_totals)
            or (for_journal and not show_totals)
        ):
            return None

        # Start with defaults for each column.
        # - We could show empty cells for most of the columns:
        #     table_row = {name: '' for name in columns}
        #   But it seems more helpful to label the row as containing totals.
        #   - Without making this more complicated and poking around
        #     'columns' for an appropriate column cell to label, let's
        #     just label all the values in the row 'TOTAL', and then
        #     overwrite some of those cell values from gross_totals.
        #   - MAYBE/2020-05-18: Improve the look of the final column.
        #     I.e., don't just blindly write 'TOTAL' in each cell,
        #     but figure out the first non-gross_totals column (from
        #     'columns') and write 'TOTAL' to just that one cell.
        table_row = {name: _('TOTAL') for name in columns}

        # Now set values for appropriate columns.
        produce_gross_duration(gross_totals, table_row)
        produce_gross_group_count(gross_totals, table_row)
        produce_gross_first_start(gross_totals, table_row)
        produce_gross_final_end(gross_totals, table_row)
        produce_gross_amassed_tags(gross_totals, table_row)

        # Remove columns that may be omitted.
        row_slice = unprepare_unmentioned_columns(table_row)

        return row_slice

    def produce_gross_duration(gross_totals, table_row):
        if 'duration' not in repcols:
            return

        # The SQLite aggregate result is in (julian)days, but the
        # timedelta is specified in seconds, so convert to the latter.
        fmt_duration = format_duration_days(gross_totals.cum_duration)
        table_row['duration'] = fmt_duration
        return fmt_duration

    def produce_gross_group_count(gross_totals, table_row):
        if 'group_count' not in repcols:
            return

        table_row['group_count'] = str(gross_totals.group_count)

    def produce_gross_first_start(gross_totals, table_row):
        if 'first_start' not in repcols:
            return

        first_start = gross_totals.first_start
        first_start = first_start.strftime(datetime_format) if first_start else ''
        table_row['first_start'] = first_start

    def produce_gross_final_end(gross_totals, table_row):
        if 'final_end' not in repcols:
            return

        final_end = gross_totals.final_end
        final_end = final_end.strftime(datetime_format) if final_end else ''
        table_row['final_end'] = final_end

    def produce_gross_amassed_tags(gross_totals, table_row):
        if 'tags' not in repcols:
            return

        table_row['tags'] = assemble_tags(gross_totals.amassed_tags.values())

    # ***

    def finalize_row(row):
        finalize_row_duration(row)
        return row

    def finalize_row_duration(row):
        if 'duration' not in row or col_adjust['duration_apres_dot'] < 0:
            return

        try:
            apres_dot = term_len(row['duration']) - row['duration'].index('.')
        except ValueError:
            pass
        else:
            if apres_dot < col_adjust['duration_apres_dot']:
                row['duration'] += ' ' * (col_adjust['duration_apres_dot'] - apres_dot)

    # ***

    def results_final_sort(table):
        if not table or not qt.sort_cols:
            return

        # Check each sort_col to see if we care, i.e. if get_all was not
        # able to sort on that value in the SQL statement. First check
        # lazily, that is, only indicate which sort cols are ones that
        # did not work in the SQL statement.
        needs_sort = any([
            sort_attrs_for_col(sort_col, lazy=True)
            for sort_col in qt.sort_cols
        ])

        if not needs_sort and not re_sort:
            controller.client_logger.warning('Skipping re-sort.')
            return
        controller.client_logger.warning('Post Processing: Re-SORTing.')

        expect_cols = sorting_columns.copy()
        for idx, sort_col in reversed(list(enumerate(qt.sort_cols))):
            sort_order = query_sort_order_at_index(qt.sort_orders, idx)
            sort_results_sort_col(table, sort_col, sort_order, expect_cols)

    def sort_results_sort_col(table, sort_col, sort_order, expect_cols):
        # Because we are redoing the whole sort, use lazy=False.
        sort_attrs = sort_attrs_for_col(sort_col, lazy=False)
        verify_available_sort_cols_match_anticipated(sort_attrs, expect_cols)
        sort_attrs.reverse()
        for sort_attr in sort_attrs:
            reverse = sort_order == 'desc'
            table.sort(key=attrgetter(sort_attr), reverse=reverse)

        return table

    def sort_attrs_for_col(sort_col, lazy):
        # MAYBE/2020-05-20: Replace this fnc. with sort_col_actual.
        # - (lb): I wrote sort_col_actual after this one... sort_col_actual
        #   is more predictive (it forecasts the columns, from the SQL query
        #   or that we'll calculate during post-processing, that will be
        #   needed to sort); whereas this function is more reactive (it
        #   looks at the actual columns after post-processing and uses
        #   what's available). / Or maybe the 2 fcns. are nice to have,
        #   1 to tell us what columns to maintain during post processing,
        #   and then this fcn. to not accidentally sort on a missing column.
        # - For now, I verify the two sets of columns are equivalent;
        #   see: verify_available_sort_cols_match_anticipated.
        sort_attrs = []

        if sort_col == 'activity':
            if 'activities' in repcols:
                # group_category on its own; SQL could not sort.
                sort_attrs = ['activities']
            elif not lazy:
                # Both of these cases can be sorted by SQL (hence not lazy).
                if 'actegory' in repcols:
                    # group_activity and group_category.
                    sort_attrs = ['actegory']
                elif 'activity' in repcols:
                    sort_attrs = ['activity']
                else:
                    controller.client_logger.warning(
                        "Did not identify sort column for --sort activity!"
                    )

        elif sort_col == 'category':
            if 'categories' in repcols:
                sort_attrs = ['categories']
            # else, if hasattr(row_cls, 'actegory'), category information
            # is missing. We could make a special case in the get_all
            # query, but doesn't seem like a big priority to handle.
            elif not lazy:
                if 'category' in repcols:
                    # FIXME/2020-05-20: This a thing?
                    sort_attrs = ['category']
                else:
                    controller.client_logger.warning(
                        "Did not identify sort column for --sort category!"
                    )

        elif sort_col == 'tag':
            if 'tag' in repcols:
                sort_attrs = ['tag']
            elif 'tags' in repcols:
                sort_attrs = ['tags']
            # elif not lazy:
                # FIXME/2020-05-20 06:03: What path is this??
                # sort_attrs = '???'
                # In get_all, it sorts on Tag.name itself.
            else:
                controller.client_logger.warning(
                    "Did not identify sort column for --sort tag!"
                )

        elif not lazy:
            # We could verify the return column exists, e.g., check
            # `'foo' in repcols`, but the sort will just fail.
            # Should be a programming error, anyway, the code checks
            # the sort columns before processing results, and ensures
            # the necessary sort columns are ready for us here.
            if sort_col == 'start':
                if not qt.is_grouped:
                    sort_attrs = ['start', 'end', 'key']
                else:
                    sort_attrs = ['first_start', 'final_end']
            elif sort_col == 'time':
                sort_attrs = ['duration']
            elif sort_col == 'day':
                # FIXME/2020-05-20: Should we auto-add start_date_cmp sort option when
                #   --group-days? Or should we require user to specify `-o days`?
                #   Another option: `dob journal` command with sort_cols default, etc.
                sort_attrs = ['start_date_cmp']
            elif sort_col == 'usage':
                sort_attrs = ['group_count']
            elif sort_col == 'name':
                sort_attrs = ['description']
            elif sort_col == 'fact':
                sort_attrs = ['key']
            else:
                # If this fires, you probably added a --sort choice that you did
                # not wire herein.
                controller.client_logger.warning(
                    "Did not identify sort column for --sort {}!".format(sort_col)
                )

        return sort_attrs

    def verify_available_sort_cols_match_anticipated(sort_attrs, expect_cols):
        # NOTE: (lb): This is just a verification check, because I coded three
        #       very similar sort_cols processors:
        #           nark.backends.sqlalchemy.managers.fact.FactManager.query_order_by_aggregate
        #           dob_bright.reports.tabulate_results.sort_col_actual
        #           dob_bright.reports.tabulate_results.sort_attrs_for_col
        #       It just happened!
        # Before processing results, we called sort_on_cols_later() and
        # determined the sort cols based on sort_cols and the group_* state.
        # After processing results, we called sort_attrs_for_col to see what
        # columns were actually populated that we can sort on.
        # - The two should match, and if they don't, log a complaint.
        subexpect = expect_cols[-len(sort_attrs):]
        if subexpect != sort_attrs:
            controller.client_logger.warning(
                "Sort discrepency: sort_attrs: {} / expect_cols: {} (subexpect: {})"
                .format(sort_attrs, expect_cols, subexpect)
            )
            controller.affirm(False)
        else:
            # Remove the trailing, verified items from the expecting list.
            expect_cols[:] = expect_cols[:-len(sort_attrs)]

    # ***

    def sort_on_cols_later():
        actual_cols = []
        must_sort_later = False
        for sort_col in qt.sort_cols or []:
            target_cols, must_later = sort_col_actual(sort_col)
            actual_cols.extend(target_cols)
            must_sort_later = must_sort_later or must_later
        if not must_sort_later and not re_sort:
            actual_cols = []
        return actual_cols

    # Ref: nark.FactManager.query_order_by_sort_col.
    def sort_col_actual(sort_col):
        must_sort_later = False

        if sort_col == 'start' or not sort_col:
            if not qt.is_grouped:
                sort_attrs = ['start', 'end', 'key']
            else:
                sort_attrs = ['first_start', 'final_end']
        elif sort_col == 'time':
            sort_attrs = ['duration']
        elif sort_col == 'day':
            sort_attrs = ['start_date_cmp']
        elif sort_col == 'activity':
            if not qt.is_grouped or (qt.group_activity and qt.group_category):
                if not for_journal:
                    sort_attrs = ['activity']
                else:
                    sort_attrs = ['actegory']
            elif qt.group_activity:
                sort_attrs = ['activity']
            elif qt.group_tags or qt.group_days:
                must_sort_later = True
                sort_attrs = ['actegories']
            else:
                # group_category (by PK).
                must_sort_later = True
                sort_attrs = ['activities']
        elif sort_col == 'category':
            if not qt.is_grouped or (qt.group_activity and qt.group_category):
                if not for_journal:
                    sort_attrs = ['category']
                else:
                    # The journal generally use just actegory,
                    #   sort_attrs = ['actegory']
                    # but user did request sorting by category.
                    sort_attrs = ['category']
            elif qt.group_category:
                sort_attrs = ['category']
            elif qt.group_tags or qt.group_days:
                must_sort_later = True
                sort_attrs = ['actegories']
            else:
                # group_activity (by name, not PK).
                must_sort_later = True
                sort_attrs = ['categories']
        elif sort_col == 'tag':
            if not qt.is_grouped or not qt.group_tags:
                sort_attrs = ['tags']
            else:
                sort_attrs = ['tag']
        elif sort_col == 'usage':
            sort_attrs = ['group_count']
        elif sort_col == 'name':
            sort_attrs = ['description']
        elif sort_col == 'fact':
            sort_attrs = ['key']
        else:
            controller.client_logger.warning("Unknown sort_col: {}".format(sort_col))

        # Return True to have this module's sort_results_sort_col sort,
        # regardless of what we this the SQL query accomplished. E.g,
        # uncomment this to test re-sorting results:
        #  must_sort_later = True
        must_sort_later = must_sort_later or re_sort

        return sort_attrs, must_sort_later

    # ***

    # Check each sort_col to see if the get_all was able to sort on that value.
    # FIXME: Should really just add an outer select to get_all to do the sort.
    #        (See must_sort_later: there are only 4 sort_col values to handle.)
    # sorting_columns lists column keys on which to sort after calculating values.
    sorting_columns = sort_on_cols_later()

    return _generate_facts_table()

