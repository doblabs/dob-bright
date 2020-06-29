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

"""~/.config/dob/styling/rules.conf definition and encapsulating class."""

from gettext import gettext as _

from config_decorator import section

__all__ = (
    'create_style_rules_object',
)


def create_style_rules_object():

    COMPONENTRY_CLASSIFIER_HELP = _(
        "For component.style or (style, text) tuple, e.g., 'class:my-class1 fg:#000000'."
    )

    @section(None)
    class RulesRoot(object):

        def __init__(self):
            pass

    # ***

    @RulesRoot.section(None)
    class Ruleset(object):
        """"""

        def __init__(self):
            pass

        # ***

        @property
        @RulesRoot.setting(
            _("If True, skip this ruleset."),
        )
        def disabled(self):
            return False

        # ***

        @property
        @RulesRoot.setting(
            _("ADVANCED: Optional code to run in context of rules evaluator."),
        )
        def eval(self):
            # E.g.,
            #   eval = fact.category_name == 'My Category'
            return ''

        @property
        @RulesRoot.setting(
            _("Generated value."),
            name='__eval__',
            hidden=True,
            # Not necessary, because we generate the value, but could say:
            #   validate=inspect.iscode,
        )
        def compiled_eval(self):
            return None

        # ***

        @property
        @RulesRoot.setting(
            _("Match Facts with the specified Activity name."),
        )
        def activity(self):
            return ''

        # ---

        @property
        @RulesRoot.setting(
            _("Match Facts with specified comma-separated list of Activities."),
        )
        def activities(self):
            return []

        # ***

        @property
        @RulesRoot.setting(
            _("Match Facts with the specified Category name."),
        )
        def category(self):
            return ''

        # ---

        @property
        @RulesRoot.setting(
            _("Match Facts with specified comma-separated list of Categories."),
        )
        def categories(self):
            return []

        # ***

        @property
        @RulesRoot.setting(
            _("Match Facts with the specified Tag."),
        )
        def tag(self):
            return ''

        # ---

        @property
        @RulesRoot.setting(
            _("Match Facts with any of the matching tags."),
        )
        def tags(self):
            return []

        # ...

        @property
        @RulesRoot.setting(
            _("Match Facts with any of the matching tags."),
            name='tags-any',
        )
        def tags_any(self):
            return []

        # (lb): I'm indecisive. tags-any, or tags-or, or both??
        # - We can just 'hidden' one of them, and still let users decide.
        @property
        @RulesRoot.setting(
            _("Match Facts with any of the matching tags."),
            name='tags-or',
            hidden=True,
        )
        def tags_or(self):
            return []

        # ...

        @property
        @RulesRoot.setting(
            _("Match Facts with *all* of the matching tags."),
            name='tags-all',
        )
        def tags_all(self):
            return []

        # (lb): I'm indecisive. tags-all, or tags-and, or both??
        # - We can just 'hidden' one of them, and still let users decide.
        @property
        @RulesRoot.setting(
            _("Match Facts with *all* of the matching tags."),
            name='tags-and',
            hidden=True,
        )
        def tags_and(self):
            return []

        # ***

        # (lb): See Backlog for Feature Request to add additional conditionals,
        #   e.g., for start/end/duration.
        # Until then (if ever), use the 'eval' conditional to work with time
        #   or any of the other Fact attributes that are not magically wired
        #   to a style rule setting.

    # ***

    @RulesRoot.section(None)
    class RulesClassify(object):
        """"""

        def __init__(self):
            pass

        # ***
        # ***

        # (lb): I feel like I should DRY up all the very similar method
        # definitions below (and, e.g., make a generator to create them).
        #
        # - On the other hand, having the long-winded method definitions
        #   below makes it pretty clear what's happening, and clearly
        #   shows what are the acceptable config keys and values.

        # ***
        # *** APPLICATION STREAMER AND ADJACENT EMPTY LINES
        # ***

        @property
        @RulesRoot.setting(
            COMPONENTRY_CLASSIFIER_HELP,
        )
        def streamer(self):
            return ''

        @property
        @RulesRoot.setting(
            COMPONENTRY_CLASSIFIER_HELP,
            name='streamer-line',
        )
        def streamer_line(self):
            return ''

        # ***
        # *** HEADER META LINES -- TITLES HALF (LEFT SIDE)
        # ***

        @property
        @RulesRoot.setting(
            COMPONENTRY_CLASSIFIER_HELP,
            name='title-normal',
        )
        def title_normal(self):
            return ''

        @property
        @RulesRoot.setting(
            COMPONENTRY_CLASSIFIER_HELP,
            name='title-normal-line',
        )
        def title_normal_line(self):
            return ''

        @property
        @RulesRoot.setting(
            COMPONENTRY_CLASSIFIER_HELP,
            name='title-focus',
        )
        def title_focus(self):
            return ''

        @property
        @RulesRoot.setting(
            COMPONENTRY_CLASSIFIER_HELP,
            name='title-focus-line',
        )
        def title_focus_line(self):
            return ''

        # ***

        @property
        @RulesRoot.setting(
            COMPONENTRY_CLASSIFIER_HELP,
            name='title-duration',
        )
        def title_duration(self):
            return ''

        @property
        @RulesRoot.setting(
            COMPONENTRY_CLASSIFIER_HELP,
            name='title-duration-line',
        )
        def title_duration_line(self):
            return ''

        # ***

        @property
        @RulesRoot.setting(
            COMPONENTRY_CLASSIFIER_HELP,
            name='title-start',
        )
        def title_start(self):
            return ''

        @property
        @RulesRoot.setting(
            COMPONENTRY_CLASSIFIER_HELP,
            name='title-start-line',
        )
        def title_start_line(self):
            return ''

        @property
        @RulesRoot.setting(
            COMPONENTRY_CLASSIFIER_HELP,
            name='title-start-focus',
        )
        def title_start_focus(self):
            return ''

        @property
        @RulesRoot.setting(
            COMPONENTRY_CLASSIFIER_HELP,
            name='title-start-focus-line',
        )
        def title_start_focus_line(self):
            return ''

        # ***

        @property
        @RulesRoot.setting(
            COMPONENTRY_CLASSIFIER_HELP,
            name='title-end',
        )
        def title_end(self):
            return ''

        @property
        @RulesRoot.setting(
            COMPONENTRY_CLASSIFIER_HELP,
            name='title-end-line',
        )
        def title_end_line(self):
            return ''

        @property
        @RulesRoot.setting(
            COMPONENTRY_CLASSIFIER_HELP,
            name='title-end-focus',
        )
        def title_end_focus(self):
            return ''

        @property
        @RulesRoot.setting(
            COMPONENTRY_CLASSIFIER_HELP,
            name='title-end-focus-line',
        )
        def title_end_focus_line(self):
            return ''

        # ***

        @property
        @RulesRoot.setting(
            COMPONENTRY_CLASSIFIER_HELP,
            name='title-activity',
        )
        def title_activity(self):
            return ''

        @property
        @RulesRoot.setting(
            COMPONENTRY_CLASSIFIER_HELP,
            name='title-activity-line',
        )
        def title_activity_line(self):
            return ''

        # ***

        @property
        @RulesRoot.setting(
            COMPONENTRY_CLASSIFIER_HELP,
            name='title-category',
        )
        def title_category(self):
            return ''

        @property
        @RulesRoot.setting(
            COMPONENTRY_CLASSIFIER_HELP,
            name='title-category-line',
        )
        def title_category_line(self):
            return ''

        # ***

        @property
        @RulesRoot.setting(
            COMPONENTRY_CLASSIFIER_HELP,
            name='title-tags',
        )
        def title_tags(self):
            return ''

        @property
        @RulesRoot.setting(
            COMPONENTRY_CLASSIFIER_HELP,
            name='title-tags-line',
        )
        def title_tags_line(self):
            return ''

        # ***
        # *** HEADER META LINES -- VALUES HALF (RIGHT SIDE)
        # ***

        @property
        @RulesRoot.setting(
            COMPONENTRY_CLASSIFIER_HELP,
            name='value-normal',
        )
        def value_normal(self):
            return ''

        @property
        @RulesRoot.setting(
            COMPONENTRY_CLASSIFIER_HELP,
            name='value-normal-line',
        )
        def value_normal_line(self):
            return ''

        @property
        @RulesRoot.setting(
            COMPONENTRY_CLASSIFIER_HELP,
            name='value-focus',
        )
        def value_focus(self):
            return ''

        @property
        @RulesRoot.setting(
            COMPONENTRY_CLASSIFIER_HELP,
            name='value-focus-line',
        )
        def value_focus_line(self):
            return ''

        # ***

        @property
        @RulesRoot.setting(
            COMPONENTRY_CLASSIFIER_HELP,
            name='value-duration',
        )
        def value_duration(self):
            return ''

        @property
        @RulesRoot.setting(
            COMPONENTRY_CLASSIFIER_HELP,
            name='value-duration-line',
        )
        def value_duration_line(self):
            return ''

        # ***

        @property
        @RulesRoot.setting(
            COMPONENTRY_CLASSIFIER_HELP,
            name='value-start',
        )
        def value_start(self):
            return ''

        @property
        @RulesRoot.setting(
            COMPONENTRY_CLASSIFIER_HELP,
            name='value-start-line',
        )
        def value_start_line(self):
            return ''

        @property
        @RulesRoot.setting(
            COMPONENTRY_CLASSIFIER_HELP,
            name='value-start-focus',
        )
        def value_start_focus(self):
            return ''

        @property
        @RulesRoot.setting(
            COMPONENTRY_CLASSIFIER_HELP,
            name='value-start-focus-line',
        )
        def value_start_focus_line(self):
            return ''

        # ***

        @property
        @RulesRoot.setting(
            COMPONENTRY_CLASSIFIER_HELP,
            name='value-end',
        )
        def value_end(self):
            return ''

        @property
        @RulesRoot.setting(
            COMPONENTRY_CLASSIFIER_HELP,
            name='value-end-line',
        )
        def value_end_line(self):
            return ''

        @property
        @RulesRoot.setting(
            COMPONENTRY_CLASSIFIER_HELP,
            name='value-end-focus',
        )
        def value_end_focus(self):
            return ''

        @property
        @RulesRoot.setting(
            COMPONENTRY_CLASSIFIER_HELP,
            name='value-end-focus-line',
        )
        def value_end_focus_line(self):
            return ''

        # ***

        @property
        @RulesRoot.setting(
            COMPONENTRY_CLASSIFIER_HELP,
            name='value-activity',
        )
        def value_activity(self):
            return ''

        @property
        @RulesRoot.setting(
            COMPONENTRY_CLASSIFIER_HELP,
            name='value-activity-line',
        )
        def value_activity_line(self):
            return ''

        # ***

        @property
        @RulesRoot.setting(
            COMPONENTRY_CLASSIFIER_HELP,
            name='value-category',
        )
        def value_category(self):
            return ''

        @property
        @RulesRoot.setting(
            COMPONENTRY_CLASSIFIER_HELP,
            name='value-category-line',
        )
        def value_category_line(self):
            return ''

        # ***

        @property
        @RulesRoot.setting(
            COMPONENTRY_CLASSIFIER_HELP,
            name='value-tags',
        )
        def value_tags(self):
            return ''

        @property
        @RulesRoot.setting(
            COMPONENTRY_CLASSIFIER_HELP,
            name='value-tags-line',
        )
        def value_tags_line(self):
            return ''

        # ***

        @property
        @RulesRoot.setting(
            COMPONENTRY_CLASSIFIER_HELP,
            name='blank-line',
        )
        def blank_line(self):
            return ''

        # ***
        # *** CONTENT AREA CONDITIONAL STYLE RULE
        # ***

        @property
        @RulesRoot.setting(
            COMPONENTRY_CLASSIFIER_HELP,
            name='content-fact',
        )
        def scrollable_frame(self):
            return ''

        @property
        @RulesRoot.setting(
            COMPONENTRY_CLASSIFIER_HELP,
            name='content-help',
        )
        def content_help(self):
            return ''

        @property
        @RulesRoot.setting(
            COMPONENTRY_CLASSIFIER_HELP,
            name='interval-gap',
        )
        def interval_gap(self):
            return ''

        @property
        @RulesRoot.setting(
            COMPONENTRY_CLASSIFIER_HELP,
            name='unsaved-fact',
        )
        def unsaved_fact(self):
            return ''

        # ***
        # *** FACT ID CONDITIONAL STYLE RULE (LOWER LEFT CORNER)
        # ***

        @property
        @RulesRoot.setting(
            COMPONENTRY_CLASSIFIER_HELP,
            name='footer',
        )
        def footer_normal(self):
            return ''

        @property
        @RulesRoot.setting(
            COMPONENTRY_CLASSIFIER_HELP,
            name='footer-fact-id',
        )
        def footer_fact_id(self):
            return ''

        # ***
        # ***

    return RulesRoot

