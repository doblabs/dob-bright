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

import os

from gettext import gettext as _

from config_decorator.config_decorator import ConfigDecorator

from ..config.dec_wrap import decorate_and_wrap
from ..config.fileboss import ensure_file_path_dirred
from ..crud.interrogate import run_editor_safe
from ..termio import click_echo, dob_in_user_exit, highlight_value
from ..termio.config_table import echo_config_decorator_table
from ..termio.style import attr

from .load_styling import (
    load_style_classes,
    load_styles_conf,
    resolve_named_style,
    resolve_path_styles,
    DEFAULT_STYLE
)
from .style_conf import KNOWN_STYLES
from .styles_dump import echo_styles_conf as dump_styles_conf

__all__ = (
    'create_styles_conf',
    'echo_styles_conf',
    'echo_styles_list',
    'echo_styles_table',
    'edit_styles_conf',
)


# *** [CONF] STYLES

def echo_styles_conf(controller, name, internal=False, complete=False):
    dump_styles_conf(controller, name, internal, complete)


# *** [CREATE] STYLES

def create_styles_conf(controller, name, force):

    def _create_styles_conf():
        # SIMILAR funcs: See also: ConfigUrable.create_config and
        #   reset_config; and styles_cmds.create_styles_conf;
        #                  and rules_cmds.create_rules_conf.
        styles_path = resolve_path_styles(controller.config)
        exit_if_exists_unless_force(styles_path, force)
        ensure_file_path_dirred(styles_path)
        create_styles_file(styles_path)
        echo_path_created(styles_path)

    def exit_if_exists_unless_force(styles_path, force):
        path_exists = os.path.exists(styles_path)
        if path_exists and not force:
            exit_path_exists(styles_path)

    def exit_path_exists(styles_path):
        dob_in_user_exit(_('Styles file already at {}').format(styles_path))

    def create_styles_file(styles_path):
        # Load specified style, or DEFAULT_STYLE if not specified.
        style_name = name or DEFAULT_STYLE
        style_classes = load_style_classes(controller, style_name=style_name)
        config_obj = decorate_and_wrap(style_name, style_classes, complete=True)
        config_obj.filename = styles_path
        config_obj.write()

    def echo_path_created(styles_path):
        click_echo(
            _('Initialized basic styles file at {}').format(
                highlight_value(styles_path),
            )
        )

    _create_styles_conf()


# *** [EDIT] STYLES

def edit_styles_conf(controller):
    styles_path = resolve_path_styles(controller.config)
    run_editor_safe(filename=styles_path)


# *** [LIST] STYLES

def echo_styles_list(controller, internal=False):
    """"""
    def _echo_styles_list():
        active_style = resolve_named_style(controller.config)
        print_styles_list(KNOWN_STYLES, active_style, _('Built-in styles'))
        if not internal:
            user_styles = fetch_user_styles_list()
            print_styles_list(user_styles, active_style, _('After-market styles'))

    def fetch_user_styles_list():
        config_obj, failed = load_styles_conf(controller.config)
        if config_obj:
            return config_obj.keys()
        return []

    def print_styles_list(styles_list, active_style, title):
        click_echo('{}{}{}'.format(attr('underlined'), title, attr('reset')))
        for style_name in styles_list:
            if style_name == active_style:
                sparkler = '* '
                ornament = attr('bold')
            else:
                sparkler = '  '
                ornament = ''
            click_echo('{}{}'.format(ornament, highlight_value(sparkler + style_name)))

    return _echo_styles_list()


# *** [SHOW] STYLES

def echo_styles_table(controller, name, output_format):
    def _echo_styles_table():
        style_name = name or resolve_named_style(controller.config)
        style_classes = load_style_classes(
            controller, style_name=style_name, skip_default=True,
        )
        if style_classes is not None:
            echo_table(style_name, style_classes)
        # Else, already printed error.

    def echo_table(style_name, style_classes):
        condec = ConfigDecorator.create_root_for_section(style_name, style_classes)
        conf_objs = [condec]
        echo_config_decorator_table(
            controller,
            conf_objs,
            output_format,
            exclude_section=False,
        )

    _echo_styles_table()

