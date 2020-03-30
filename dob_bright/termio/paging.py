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

"""Methods to control paging and manage (accumulate) pager output."""

import sys
from functools import update_wrapper

import click_hotoffthehamster as click

from .style import coloring

__all__ = (
    'click_echo',
    'disable_paging',
    'enable_paging',
    'flush_pager',
    'paging',
    'set_paging',
)


# ***

this = sys.modules[__name__]

this.PAGER_ON = False

# (lb): This module-scope global makes me feel somewhat icky.
# MAYBE/2020-02-01: See newly added nark.helpers.singleton.
this.PAGER_CACHE = []


def disable_paging():
    this.PAGER_ON = False


def enable_paging():
    this.PAGER_ON = True


def paging():
    return this.PAGER_ON


def set_paging(new_paging):
    was_paging = this.PAGER_ON
    this.PAGER_ON = new_paging
    return was_paging


# ***

def click_echo(message=None, **kwargs):
    if coloring():
        kwargs['color'] = True
    if not paging():
        click.echo(message, **kwargs)
    else:
        # Collect echoes and show at end, otherwise every call
        # to echo_via_pager results in one pager session, and
        # user has to click 'q' to see each line of output!
        this.PAGER_CACHE.append(message or '')


# ***

def flush_pager(func):
    def flush_echo(*args, **kwargs):
        func(*args, **kwargs)
        if paging() and this.PAGER_CACHE:
            click.echo_via_pager(u'\n'.join(this.PAGER_CACHE))
            this.PAGER_CACHE = []

    return update_wrapper(flush_echo, func)

