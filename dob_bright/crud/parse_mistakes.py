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

""""""

from gettext import gettext as _

from ..termio import attr, bg, fg

__all__ = (
    'conflict_prefix',
    'prepare_log_msg',
)


# ***

def conflict_prefix(prefix):
    return (
        '{}{}{}'
        .format(
            bg('medium_violet_red'),
            prefix,
            attr('reset'),
        )
    )


# ***

def prepare_log_msg(fact_or_dict, msg_content):
    def _prepare_log_msg():
        try:
            line_num = fact_or_dict['line_num']
            line_raw = fact_or_dict['line_raw']
        except KeyError:
            line_num = fact_or_dict['parsed_source.line_num']
            line_raw = fact_or_dict['parsed_source.line_raw']
        except TypeError:
            line_num = fact_or_dict.parsed_source.line_num
            line_raw = fact_or_dict.parsed_source.line_raw
        line_num = line_num or 0
        line_raw = line_raw or ''
        # NOTE: Using colors overrides logger's coloring, which is great!
        # FIXME: (lb): Replace hardcoding. Assign from styles.conf. #styling
        return _(
            '{}{}{}: {}{}: {}{} / {}{}{}\n\n{}: {}“{}”{}\n\n{}: {}{}{}'
            .format(
                attr('bold'),
                conflict_prefix(_('Problem')),
                attr('reset'),

                fg('dodger_blue_1'),
                _('On line'),
                line_num,
                attr('reset'),

                attr('underlined'),
                msg_content,
                attr('reset'),

                conflict_prefix(_('  Typed')),
                fg('hot_pink_2'),
                line_raw.strip(),
                attr('reset'),

                conflict_prefix(_(' Parsed')),
                fg('grey_78'),
                fact_or_dict,
                attr('reset'),
            )
        )

    return _prepare_log_msg()

