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

"""Controller functionality: Config features."""

import inspect

from easy_as_pypi_config.urable import ConfigUrable
from easy_as_pypi_termio.echoes import click_echo
from nark.control import NarkControl

from .. import help_newbs as help_strings
from ..config import ConfigRoot

__all__ = ("Controller_ConfigManager",)


class Controller_ConfigManager(
    NarkControl,
):
    """This is final (lowermost) class in the Controller() super()-chain."""

    DOB_CONFIGFILE_ENVKEY = "DOB_CONFIGFILE"

    def __init__(self, *args, **kwargs):
        super(Controller_ConfigManager, self).__init__(*args, **kwargs)
        self.configurable = None
        self.configfile_path = None
        self.config_keyvals = None

    # ***

    @property
    def is_germinated(self):
        if not self.looks_like_config:
            return False

        # Nothing upstream, e.g.,:
        #   # return NarkControl.is_germinated.fget(self)
        return True

    @property
    def has_no_user_files(self):
        if not self.configurable.cfgfile_exists:
            return True

        return False

    # ***

    def alert_user_if_config_file_unwell(self):
        def _alert_user_if_config_file_unwell():
            if not self.configurable.cfgfile_exists:
                oblige_user_create_config()
            elif not self.looks_like_config:
                oblige_user_repair_config()

        def oblige_user_create_config():
            cfg_path = self.configurable.config_path
            message = help_strings.NEWBIE_HELP_CREATE_CONFIG(self.ctx, cfg_path)
            click_echo(inspect.cleandoc(message), err=True)

        def oblige_user_repair_config():
            cfg_path = self.configurable.config_path
            message = help_strings.NEWBIE_HELP_REPAIR_CONFIG(self.ctx, cfg_path)
            click_echo(inspect.cleandoc(message), err=True)

        _alert_user_if_config_file_unwell()

    # ***

    def ensure_config(self, ctx, configfile_path, *keyvals):
        if self.configurable is not None:
            return
        # NOTE: This ctx.command.name == 'run', i.e., not the same context
        # passed to the Click command handlers. See: pass_context_wrap.
        self.ctx = ctx
        self.configfile_path = configfile_path
        self.config_keyvals = keyvals
        self.setup_config(configfile_path, *keyvals)
        self.wire_configience()

    def setup_config(self, configfile_path, *keyvals):
        self.configurable = self.setup_config_from_file_and_cli(
            configfile_path,
            *keyvals,
        )

    def setup_config_from_file_and_cli(self, configfile_path, *keyvals):
        configurable = ConfigUrable(
            config_root=ConfigRoot,
            configfile_envkey=Controller_ConfigManager.DOB_CONFIGFILE_ENVKEY,
        )
        configurable.load_config(configfile_path)
        configurable.inject_from_cli(*keyvals)
        return configurable

    # ***

    def create_config(self, force):
        self.configurable.create_config(force=force)
        self.wire_configience()

    @property
    def looks_like_config(self):
        def _looks_like_config():
            if not self.configurable or not self.configurable.cfgfile_exists:
                return False

            return cfgfile_looks_like_config()

        def cfgfile_looks_like_config():
            # What's a reasonable expectation to see if the config file
            # legitimately exists? Check that the file exists? Or parse it
            # and verify one or more settings therein? Let's do the latter,
            # seems more robust. We can check the `store` settings, seems
            # like the most obvious setting to check. In any case, we do
            # this just to tell the user if they need to create a config;
            # the app will run just fine without a config file, because
            # defaults!
            try:
                # SYNC_ME: Referenced by NEWBIE_HELP_REPAIR_CONFIG text.
                self.configurable.config_root.asobj.db.orm.value_from_config
                return True
            except AttributeError:
                return False

        return _looks_like_config()

    def round_out_config(self):
        self.configurable.round_out_config()

    def write_config(self, skip_unset=False):
        self.configurable.write_config(skip_unset=skip_unset)

    # ***

    def wire_configience(self, config_root=None):
        self.config = config_root or self.configurable.config_root
        self.capture_config(self.config)
        self.process_config()

    def process_config(self):
        # Used by derived classes if necessary.
        pass

    # ***
