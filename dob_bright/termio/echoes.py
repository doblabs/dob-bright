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

"""Methods for common terminal echo operations."""

import click_hotoffthehamster as click

from .paging import click_echo
from .style import attr, fg

__all__ = (
    # Callers might want to import click_echo from this module, because it
    # feels more natural here (but its in paging module because pager-aware).
    'click_echo',
    'echo_block_header',
    'highlight_value',
    # PRIVATE:
    # '__format_block_header',
)


# ***

def echo_block_header(title, **kwargs):
    click_echo()
    click_echo(__format_block_header(title, **kwargs))


def __format_block_header(title, sep='━', full_width=False):
    """"""
    def _fact_block_header():
        header = []
        append_highlighted(header, title)
        append_highlighted(header, hr_rule())
        return '\n'.join(header)

    def append_highlighted(header, text):
        highlight_col = 'red_1'
        header.append('{}{}{}'.format(
            fg(highlight_col),
            text,
            attr('reset'),
        ))

    def hr_rule():
        if not full_width:
            horiz_rule = sep * len(title)
        else:
            # NOTE: When piping (i.e., no tty), width defaults to 80.
            term_width = click.get_terminal_size()[0]
            horiz_rule = '─' * term_width
        return horiz_rule

    return _fact_block_header()


# ***

def highlight_value(msg):
    # FIXME: (lb): Replace hardcoding. Assign from styles.conf. #styling
    highlight_color = 'medium_spring_green'
    return '{}{}{}'.format(fg(highlight_color), msg, attr('reset'))

