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

"""Applies Styles to components that do not have config access."""

import re

from ..crud.fact_dressed import FactDressed
from ..crud.facts_diff import FactsDiff

from .load_styling import load_style_classes

__all__ = (
    'pre_apply_style_conf',
)


def pre_apply_style_conf(controller):
    def _pre_apply_style_conf():
        style_conf = load_style_classes(controller)
        register_factoid_style(style_conf)
        register_facts_diff_style(style_conf)
        register_tags_tuples_style(style_conf)
        # Cache the style conf for the Carousel (if `dob edit` being called). #PROFILING
        controller.style_conf = style_conf
        return style_conf

    # ***

    RE_COMMA_WHITESPACE = re.compile(r',\s*')

    def unpack(csv):
        return RE_COMMA_WHITESPACE.split(csv)

    # ***

    def register_factoid_style(style_conf):
        factoioid_style = unpack_factoioid_style(style_conf)
        FactDressed.register_factoid_style(factoioid_style)

    def unpack_factoioid_style(style_conf):
        factoioid_style = {
            'pk': unpack(style_conf['factoid-pk']),
            'act@gory': unpack(style_conf['factoid-act@gory']),
            '#': unpack(style_conf['factoid-#']),
            'tag': unpack(style_conf['factoid-tag']),
            '#tag': unpack(style_conf['factoid-#tag']),
            'start': unpack(style_conf['factoid-start']),
            'end': unpack(style_conf['factoid-end']),
            'at': unpack(style_conf['factoid-at']),
            'to': unpack(style_conf['factoid-to']),
            'duration': unpack(style_conf['factoid-duration']),
        }
        return factoioid_style

    # ***

    def register_facts_diff_style(style_conf):
        facts_diff_style = unpack_facts_diff_style(style_conf)
        FactsDiff.register_facts_diff_style(facts_diff_style)

    def unpack_facts_diff_style(style_conf):
        facts_diff_style = {
            'value-diff-old-raw': unpack(style_conf['value-diff-old-raw']),
            'value-diff-old-ptk': style_conf['value-diff-old-ptk'],
            'value-diff-new-raw': unpack(style_conf['value-diff-new-raw']),
            'value-diff-new-ptk': style_conf['value-diff-new-ptk'],
        }
        return facts_diff_style

    # ***

    def register_tags_tuples_style(style_conf):
        tags_tuples_style = unpack_tags_tuples_style(style_conf)
        FactDressed.register_tags_tuples_style(tags_tuples_style)

    def unpack_tags_tuples_style(style_conf):
        tags_tuples_style = {
            'value-tag-#': style_conf['value-tag-#'],
            'value-tag-label': style_conf['value-tag-label'],
        }
        return tags_tuples_style

    return _pre_apply_style_conf()

