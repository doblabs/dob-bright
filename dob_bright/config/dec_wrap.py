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

"""dob_bright.config sub.package provides Carousel UX user configuration settings."""

from config_decorator.config_decorator import ConfigDecorator

from dob_bright.config.fileboss import create_configobj

__all__ = (
    'decorate_and_wrap',
)


def decorate_and_wrap(section_name, style_classes, complete=False):
    def _decorate_and_wrap():
        # Sink the section once so we can get ConfigObj to print
        # the leading [section_name].
        condec = ConfigDecorator.create_root_for_section(section_name, style_classes)
        return wrap_in_configobj(condec, complete=complete)

    def wrap_in_configobj(condec, complete=False):
        config_obj = create_configobj(conf_path=None)
        # Set skip_unset so none of the default values are spit out (keeps the
        # config more concise); and set keep_empties so empty sections are spit
        # out (so, e.g., `[default]` at least appears).
        config_obj.merge(condec.as_dict(
            skip_unset=not complete,
            keep_empties=not complete,
        ))
        return config_obj

    return _decorate_and_wrap()

