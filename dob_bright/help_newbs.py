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

"""Module to provide u18n friendly help text strings for our controller needs."""

from gettext import gettext as _

from . import __arg0name__
from .config.fileboss import default_config_path
from .config.urable import ConfigUrable
from .termio import attr, bg, fg, highlight_value


__all__ = (
    'NEWBIE_HELP_WELCOME',
    'NEWBIE_HELP_ONBOARDING',
    'NEWBIE_HELP_CREATE_CONFIG',
    'NEWBIE_HELP_REPAIR_CONFIG',
    'NEWBIE_HELP_CREATE_STORE',
    # Private:
    #  'common_format',
    #  'section_heading',
)


def common_format():
    # (lb): Eh: This is a method because ENABLE_COLORS is False on startup,
    # and fg and attr will return empty strings if called when module is
    # sourced. So wait until help strings are built and it's known if color
    # or not.
    # FIXME: (lb): Replace hardcoding. Retrieve styles from styles.conf. #styling
    #        - Or probably disable for newbie message: we cannot discern terminal
    #          colors, and user will not have assigned a style, probably.
    common_format = {
        'appname': highlight_value(__arg0name__),
        'rawname': __arg0name__,
        'codehi': fg('turquoise_2'),
        'reset': attr('reset'),
        'bold': attr('bold'),
        'italic': attr('italic'),
        'underlined': attr('underlined'),
        'wordhi': fg('chartreuse_3a'),
        'errcol': bg('red_1') + attr('bold'),
    }
    return common_format


# ***
# *** [INDUCTEE] help.
# ***

def NEWBIE_HELP_WELCOME(ctx):
    # FIXME: (lb): Need to test colors on light vs. night terminals. #styling
    _help = _(
        """
        {color}┏━━━━━━━━━━━━━━━━━┓{reset}
        {color}┃ Welcome to dob! ┃{reset}
        {color}┗━━━━━━━━━━━━━━━━━┛{reset}
        """
    ).rstrip().strip('\n').format(
        # FIXME: (lb): Replace hardcoding. Assign from styles.conf. #styling
        color=(fg('spring_green_2a') + attr('bold')),
        **common_format(),
    )
    return _help


def section_heading(title):
    return (
        """
        {color}{title}{reset}
        {line_color}{sep:{sep}<{len_title}}{reset}
        """
    ).strip().format(
        title=title,
        sep='─',
        len_title=len(title),
        line_color='',
        color='',
        **common_format()
    )


def NEWBIE_HELP_ONBOARDING(ctx):
    # NOTE: This help is not automatically formatted like other text.
    _help = _(
        """
        {banner}

        Let’s get you setup!

        {init_title}
        To create a fresh, empty database, run:

          {cmd_color}{rawname} init{reset}

        {upgrade_title}
        To learn how to import from the old hamster app,
        or to import an existing dob database, run:

          {cmd_color}{rawname} migrate -h{reset}

        {demo_title}
        If you’d like to get your hands dirty, you can demo
        the application with some example data that you can
        follow as a walk-through. Run:

          {cmd_color}{rawname} demo{reset}
        \b
        """
    ).lstrip().format(
        banner=NEWBIE_HELP_WELCOME(ctx),
        upgrade_title=section_heading(_('Import existing facts')),
        init_title=section_heading(_('Start from scratch')),
        demo_title=section_heading(_('Demo Dob')),
        help_title=section_heading(_('Such Help')),
        # FIXME: (lb): Replace hardcoding. Assign from styles.conf. #styling
        cmd_color=fg('spring_green_2a'),
        **common_format(),
    )
    return _help


def NEWBIE_HELP_CREATE_CONFIG(ctx, cfg_path):
    _help = _(
        """
        {errcol}ERROR: No config file found at: “{cfg_path}”{reset}

        Where's your config file??

        Verify and correct the configuration file path.

        The configuration file defaults to:

            {default_config_path}

        but you can override it using an environ:

            {envkey}=PATH

        or by specifying a global option:

            -F/--configfile PATH

        If you are certain the path is correct and you want to create
        a new configuration file at the path specified, run init, e.g.,:

            {rawname} -F "{cfg_path}" init
        """
    ).strip().format(
        # FIXME/2019-11-19 14:42: Make wrapper for format() with common colors defined.
        # - Maybe change errors to white on red, like here,
        #   but only for white on black terms (based on some setting?).
        cfg_path=cfg_path,
        default_config_path=default_config_path(),
        envkey=ConfigUrable.DOB_CONFIGFILE_ENVKEY,
        **common_format()
    )
    return _help


def NEWBIE_HELP_REPAIR_CONFIG(ctx, cfg_path):
    _help = _(
        """
        {errcol}ERROR: Please fix the config file found at: “{cfg_path}”{reset}

        The configuration file is at least missing the db.orm setting, if not others.

        Either edit and repair the confirguration file manually, or blow it away:
          \b
          {codehi}{rawname} config create --force{reset}
        """
    ).strip().format(
        cfg_path=cfg_path,
        default_config_path=default_config_path(),
        envkey=ConfigUrable.DOB_CONFIGFILE_ENVKEY,
        **common_format()
    )
    return _help


def NEWBIE_HELP_CREATE_STORE(ctx, db_path, val_source):
    _help = _(
        """
        {errcol}ERROR: No database file found.{reset}

        - There was no file found at: {db_path}

        - The db.path value was set from the ‘{val_source}’ source.

        - For help on configuring settings, try the config help:
          \b
          {codehi}{rawname} config --help{reset}
        """
    ).strip().format(
        db_path=db_path,
        val_source=val_source,
        **common_format()
    )
    return _help

