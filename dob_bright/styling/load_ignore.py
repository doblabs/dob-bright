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

"""Manages User file containing regex for filtering completions/suggestions."""

import os
import re

from gettext import gettext as _

from ..crud.enc_actegory_re import RegExpActegory
from ..termio import dob_in_user_warning

__all__ = (
    'ignore_file_path',
    'load_no_completion',
    'NoComplete',
)


class NoComplete(object):
    """"""

    def __init__(self, re_act=None, re_cat=None, re_tag=None):
        self.re_act = re_act
        self.re_cat = re_cat
        self.re_tag = re_tag

        self.raw = {}


def load_no_completion(controller):
    """"""

    class SectionState(object):
        """File parsing state machine."""

        section_activity = re.compile(r'^\s*\[activity\]\s*$')
        section_category = re.compile(r'^\s*\[category\]\s*$')
        section_tagnames = re.compile(r'^\s*\[tag\]\s*$')

        def __init__(self):
            self.state = None

        def changes_state(self, rule):
            for possible_section in (
                SectionState.section_activity,
                SectionState.section_category,
                SectionState.section_tagnames,
            ):
                # We can use match() because only care about start of string.
                if possible_section.match(rule):
                    self.state = possible_section
                    return True
            return False

        @property
        def on_activity(self):
            return self.state is SectionState.section_activity

        @property
        def on_category(self):
            return self.state is SectionState.section_category

        @property
        def on_tagnames(self):
            return self.state is SectionState.section_tagnames

    # ***

    affirm = controller.affirm
    config = controller.config

    _activities = []
    _categories = []
    _tagsofname = []

    comment_line = re.compile(r'^\s*#')
    comment_decode = re.compile(r'^(\s*)\\#')

    nothing_but_blankness = re.compile(r'^\s*$')

    matches_nothing = re.compile(r'[^\w\W]')
    nothing_matches = 3 * [matches_nothing]

    sep_sym = '@'
    re_actegory = RegExpActegory(sep=sep_sym)

    state = SectionState()

    def decode_leading_comment(text):
        return comment_decode.sub('\\1#', text)

    def _load_no_completion():
        try:
            re_act, re_cat, re_tag = re_compiled_user_ignores()
        except Exception as err:
            # FIXME/2019-11-30: (lb): Better error message.
            dob_in_user_warning(str(err))
            re_act, re_cat, re_tag = nothing_matches
        no_completions = NoComplete(re_act, re_cat, re_tag)
        no_completions.raw = {
            'activities': _activities,
            'categories': _categories,
            'tags': _tagsofname,
        }
        return no_completions

    def re_compiled_user_ignores():
        ignore_fpath = ignore_file_path(config)
        if not os.path.exists(ignore_fpath):
            return nothing_matches
        compiled_re = ignores_file_parse(ignore_fpath)
        return compiled_re

    def ignores_file_parse(ignore_fpath):
        if not ignore_fpath:
            return nothing_matches
        return open_and_parse(ignore_fpath)

    def open_and_parse(ignore_fpath):
        open_and_consume_rules(ignore_fpath)
        return process_consumed_rules()

    def open_and_consume_rules(ignore_fpath):
        with open(ignore_fpath, 'r', encoding='utf-8') as ignore_fpath_f:
            for line in ignore_fpath_f:
                consume_if_not_empty_line(line.rstrip('\n'))

    def consume_if_not_empty_line(rule):
        if nothing_but_blankness.match(rule):
            return
        consume_if_not_comment(rule)

    def consume_if_not_comment(rule):
        if comment_line.match(rule):
            return
        cleaned_rule = decode_leading_comment(rule)
        check_state_maybe_consume(cleaned_rule)

    def check_state_maybe_consume(rule):
        if state.changes_state(rule):
            return
        consume_completion_exclusion_rule(rule)

    def consume_completion_exclusion_rule(rule):
        if state.on_tagnames:
            _tagsofname.append(rule)
        else:
            activity, category = re_actegory.split_parts(rule)
            consume_actegory_rule(activity, category, rule)

    def consume_actegory_rule(activity, category, rule):
        if not activity and not category:
            # User has a solo '@' in their ignore file. Ignore it.
            return
        if state.on_activity:
            if not activity:
                # User has '@foo' in [activity] section. Interpret as category.
                _categories.append(category)
            else:
                _activities.append(rule)
        elif state.on_category:
            if not category:
                # There was no @ in the name, so was category anyway.
                category = activity
            if category:
                _categories.append(category)
            else:
                affirm(False)
        else:
            # Haven't seen first section yet!
            # FIXME/2019-11-30: (lb): Better error message.
            dob_in_user_warning(_(
                'Cannot discern no-completion rule seen before first section: ‘{}’'
            ).format(rule))

    def process_consumed_rules():
        re_act = compile_rules(_activities)
        re_cat = compile_rules(_categories)
        re_tag = compile_rules(_tagsofname)
        return re_act, re_cat, re_tag

    def compile_rules(rules):
        if not rules:
            return matches_nothing
        return re.compile(r'^({})$'.format('|'.join(rules)))

    # ***

    return _load_no_completion()


# ***

CFG_KEY_IGNORE_FPATH = 'editor.ignore_fpath'


def ignore_file_path(config):
    ignore_fpath = config[CFG_KEY_IGNORE_FPATH]
    return ignore_fpath

