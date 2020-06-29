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

"""Hamter CLI Nonbusiness Helper modules."""

import sys

import click_hotoffthehamster as click

from .ascii_art import infection_notice, lifeless
from .paging import click_echo, flush_pager
from .style import stylize

__all__ = (
    'dob_in_user_exit',
    'dob_in_user_warning',
    'barf_and_exit',
    'echo_exit',
)


# ***

def dob_in_user_exit(msg):
    # (lb): I made two similar error-and-exit funcs. See also: barf_and_exit.
    dob_in_user_warning(msg)
    sys.exit(1)


# ***

# (lb): Oh, bother.
BEEN_WARNED = [False, ]


def dob_in_user_warning(msg):
    # FIXME: (lb): Replace hardcoded styles. Assign from styles.conf. #styling
    # A lighter red works for white-on-black.
    # - FIXME: Add to 'light'.
    #  click.echo(stylize(msg, 'red_1'), err=True)  # 196
    # Yellow pops and at least says caution. Works for dark.
    # - FIXME: Add to 'night'.
    click.echo(stylize(msg, 'yellow_1'), err=True)  # 226
    BEEN_WARNED[0] = True


def dob_been_warned_reset():
    been_warned = BEEN_WARNED[0]
    BEEN_WARNED[0] = False
    return been_warned


# ***

def barf_and_exit(msg, crude=True):
    # (lb): I made two similar error-and-exit funcs. See also: dob_in_user_exit.
    if crude:
        click_echo()
        click_echo(lifeless().rstrip())
        click_echo(infection_notice().rstrip())
        # click.pause(info='')
    click_echo()
    # FIXME: (lb): Replace hardcoded styles. Assign from styles.conf. #styling
    click_echo(stylize(msg, 'yellow_1'))
    sys.exit(1)


# ***

def echo_exit(ctx, message, exitcode=0):
    def _echo_exit(message):
        click_echo(message)
        _flush_pager()
        ctx.exit(exitcode)

    def _flush_pager():
        # To get at the PAGER_CACHE, gotta go through the decorator.
        # So this is quite roundabout.
        @flush_pager
        def __flush_pager():
            pass
        __flush_pager()

    _echo_exit(message)


