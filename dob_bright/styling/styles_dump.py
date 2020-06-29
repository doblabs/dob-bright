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

"""Prints styles config to stdout to help user setup custom styling."""

from gettext import gettext as _

from config_decorator.config_decorator import ConfigDecorator

from ..config.dec_wrap import decorate_and_wrap
from ..config.fileboss import create_configobj, echo_config_obj
from ..termio import dob_in_user_warning

from .load_styling import (
    load_style_classes,
    load_styles_conf,
    resolve_path_styles
)
from .style_conf import KNOWN_STYLES

__all__ = (
    'echo_styles_conf',
)


def echo_styles_conf(controller, style_name='', internal=False, complete=False):
    """Prints style config section(s) from styles.conf or internal sources.
    """
    config = controller.config

    def _echo_styles_conf():
        if not internal:
            config_obj = load_config_obj()
        else:
            config_obj = load_style_conf()
        if config_obj:
            echo_config_obj(config_obj)
        # Else, already printed error message.

    # ***

    def load_config_obj():
        config_obj, failed = load_styles_conf(config)
        if config_obj:
            return filter_config_obj(config_obj)
        if failed:
            # load_styles_conf prints a ConfigObj error message. Our job is done.
            return None
        return echo_error_no_styles_conf()

    def filter_config_obj(config_obj):
        if not style_name:
            return config_obj
        new_config = create_configobj(conf_path=None)
        try:
            new_config.merge({style_name: config_obj[style_name]})
        except KeyError:
            return echo_error_no_styles_section()
        else:
            return new_config

    def echo_error_no_styles_conf():
        msg = _("No styles file at: {0}").format(resolve_path_styles(config))
        dob_in_user_warning(msg)
        return None

    def echo_error_no_styles_section():
        msg = _("No matching section “{0}” found in styles file at: {1}").format(
            style_name, resolve_path_styles(config),
        )
        dob_in_user_warning(msg)
        return None

    # ***

    def load_style_conf():
        if style_name:
            return load_single_style()
        return load_known_styles()

    def load_single_style():
        style_classes = load_style_classes(controller, style_name, skip_default=True)
        if not style_classes:
            # load_obj_from_internal will have output a warning message.
            return None
        return decorate_and_wrap(style_name, style_classes, complete=complete)

    def load_known_styles():
        """Adds all internal styles to a configobj.

        Includes all settings for the first style ('default'), but only
        those settings that are explicitly set for the remaining styles.
        """
        config_obj = create_configobj(conf_path=None)
        is_default = True
        for name in KNOWN_STYLES:
            style_classes = load_style_classes(controller, name, skip_default=True)
            styles_conf = ConfigDecorator(object, cls_or_name='', parent=None)
            styles_conf.set_section(name, style_classes)
            config_obj.merge(styles_conf.as_dict(
                skip_unset=not is_default and not complete,
                keep_empties=not is_default and not complete,
            ))
            is_default = False
        return config_obj

    # ***

    return _echo_styles_conf()

