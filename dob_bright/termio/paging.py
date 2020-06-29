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

"""Methods to control paging and manage (accumulate) pager output."""

from functools import update_wrapper

import click_hotoffthehamster as click

from .style import coloring

__all__ = (
    'ClickEchoPager',
    'click_echo',
    'flush_pager',
)


# ***

class ClickEchoPager(object):

    PAGER_ON = False

    PAGER_CACHE = []

    @classmethod
    def disable_paging(cls):
        cls.PAGER_ON = False

    @classmethod
    def enable_paging(cls):
        cls.PAGER_ON = True

    @classmethod
    def paging(cls):
        return cls.PAGER_ON

    @classmethod
    def set_paging(cls, new_paging):
        was_paging = cls.PAGER_ON
        cls.PAGER_ON = new_paging
        return was_paging

    @classmethod
    def flush_pager(cls):
        if cls.paging() and cls.PAGER_CACHE:
            click.echo_via_pager(u'\n'.join(cls.PAGER_CACHE))
        cls.PAGER_CACHE = []

    @classmethod
    def write(cls, message=None, **kwargs):
        if not cls.paging():
            if coloring():
                kwargs['color'] = True
            if 'nl' not in kwargs:
                kwargs['nl'] = False
            click.echo(message, **kwargs)
        else:
            # Collect echoes and show at end, otherwise every call
            # to echo_via_pager results in one pager session, and
            # user has to click 'q' to see each line of output!
            cls.PAGER_CACHE.append(message or '')


# ***

def click_echo(message=None, **kwargs):
    if 'nl' not in kwargs:
        kwargs['nl'] = True
    ClickEchoPager.write(message, **kwargs)


# ***

def flush_pager(func):
    def flush_echo(*args, **kwargs):
        func(*args, **kwargs)
        ClickEchoPager.flush_pager()

    return update_wrapper(flush_echo, func)

