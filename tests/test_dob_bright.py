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

import logging
import os
from unittest import mock

import pytest
from easy_as_pypi_appdirs import app_dirs_with_mkdir
from easy_as_pypi_config.urable import ConfigUrable
from nark.config import ConfigRoot, decorate_config
from nark.helpers import logging as logging_helpers

from dob_bright.controllers.app_controller import Controller


class TestSetupLogging(object):
    """Make sure that our logging setup is executed as expected."""

    def test_setup_logging_and_log_level(self, controller):
        """
        Test that library and client logger have log level set according to config.
        """
        controller.setup_logging()
        assert controller.lib_logger.level == (
            logging_helpers.resolve_log_level(controller.config["dev.lib_log_level"])[0]
        )
        assert controller.client_logger.level == (
            logging_helpers.resolve_log_level(controller.config["dev.cli_log_level"])[0]
        )

    def test_setup_logging_log_console_true(self, controller):
        """Ensure if console logging, lib and client have streamhandlers."""
        controller.config["log.use_console"] = True
        controller.setup_logging()
        assert isinstance(
            controller.client_logger.handlers[0],
            logging.StreamHandler,
        )
        assert isinstance(
            controller.client_logger.handlers[1],
            logging.FileHandler,
        )
        assert isinstance(
            controller.lib_logger.handlers[0],
            logging.StreamHandler,
        )
        assert isinstance(
            controller.lib_logger.handlers[1],
            logging.FileHandler,
        )
        assert len(controller.client_logger.handlers) == 2
        assert len(controller.lib_logger.handlers) == 2
        assert controller.client_logger.handlers[0].formatter

    def test_setup_logging_no_logging(self, controller):
        """Make sure that if no logging enabled, our loggers don't have any handlers."""
        controller.setup_logging()
        # Default loggers are set up in ~/.cache/<app>/log/<app>.log
        assert len(controller.lib_logger.handlers) == 1
        assert len(controller.client_logger.handlers) == 1

    def test_setup_logging_log_file_true(self, controller, tmp_appdirs):
        """
        Make sure that if we enable logfile_path, both loggers receive ``FileHandler``.
        """
        controller.config["log.filepath"] = os.path.join(
            tmp_appdirs.user_log_dir,
            "foobar.log",
        )
        controller.setup_logging()
        assert isinstance(
            controller.lib_logger.handlers[0],
            logging.FileHandler,
        )
        assert isinstance(
            controller.client_logger.handlers[0],
            logging.FileHandler,
        )


class TestGetConfig(object):
    """Make sure turning a config instance into proper config dictionaries works."""

    @pytest.mark.parametrize("cli_log_level", ["debug"])
    def test_log_levels_valid(self, cli_log_level, config_instance):
        """
        Make sure *string loglevels* translates to their respective integers properly.
        """
        config_obj = config_instance(cli_log_level=cli_log_level)
        assert config_obj["dev"]["cli_log_level"] == cli_log_level
        config = decorate_config(config_obj)
        assert config["dev"]["cli_log_level"] == 10
        assert config["dev.cli_log_level"] == 10
        assert config.asobj.dev.cli_log_level.value == 10

    @pytest.mark.parametrize("cli_log_level", ["foobar"])
    def test_log_levels_invalid(self, cli_log_level, config_instance, capsys):
        """Test that invalid *string loglevels* raise ``ValueError``."""
        config_obj = config_instance(cli_log_level=cli_log_level)
        with pytest.raises(
            ValueError,
            match=r"^Unrecognized value for setting ‘cli_log_level’: “foobar”.*",
        ):
            _config = decorate_config(config_obj)  # noqa: F841 unused local
        out, err = capsys.readouterr()
        assert out == ""
        assert err == ""

    def test_invalid_store(self, config_instance):
        """Make sure that passing an ORM other than 'sqlalchemy' raises an exception."""
        config_obj = config_instance(orm="foobar")
        match_former = r"Unrecognized value for setting ‘orm’"
        match_latter = r"“foobar” \(Choose from: ‘sqlalchemy’\)"
        with pytest.raises(
            ValueError,
            match=r"^{}: {}$".format(match_former, match_latter),
        ):
            _config = decorate_config(config_obj)  # noqa: F841 unused local

    def test_non_sqlite(self, config_instance):
        """Make sure that passing a postgres config works.

        Albeit actual postgres connections not tested."""
        confnstnc = config_instance(engine="postgres")
        config = decorate_config(confnstnc)
        assert config["db.host"] == confnstnc["db"]["host"]
        assert config["db.port"] == confnstnc["db"]["port"]
        assert config["db.name"] == confnstnc["db"]["name"]
        assert config["db.user"] == confnstnc["db"]["user"]
        assert config["db.password"] == confnstnc["db"]["password"]


# DUNNO/2023-12-21: This looks like a leftover duplicate from
# the 2020-12-15 refactor (when a single dob monolith was split
# into ten separate packages), but it (somehow?) provides 38 lines
# of coverage (though it looks like it only runs EAPP-config code).
# - CXREF: See same-named and similiar class upstream:
#     ~/.kit/py/easy-as-pypi-config/tests/test_urable.py
class TestGetConfigInstance(object):
    def get_configurable(self):
        return ConfigUrable(
            config_root=ConfigRoot,
            # EAPP-config uses:
            #  configfile_envkey=self.EASY_AS_PYPI_CONFIG_CONFIGFILE_ENVKEY,
            configfile_envkey=Controller.DOB_CONFIGFILE_ENVKEY,
        )

    def test_no_file_present(self, tmp_appdirs, mocker):
        # In lieu of testing from completely vanilla account, ensure config file does
        # not exist (which probably exists for your user at ~/.config/dob/dob.conf).
        # NOTE: AppDirs is a module-scope object with immutable attributes, so we
        # need to mock the entire object (i.e., cannot just patch attribute itself).
        app_dirs_mock = mock.Mock()
        app_dirs_mock.configure_mock(user_config_dir="/XXX")
        app_dirs_mock.configure_mock(user_data_dir="/XXX")
        mocker.patch.object(
            app_dirs_with_mkdir, "AppDirsWithMkdir", return_value=app_dirs_mock
        )
        self.configurable = self.get_configurable()
        self.configurable.load_config(configfile_path=None)
        assert len(list(self.configurable.config_root.items())) > 0
        assert self.configurable.cfgfile_exists is False

    def test_file_present(self, config_instance):
        """Make sure we try parsing a found config file."""
        self.configurable = self.get_configurable()
        self.configurable.load_config(configfile_path=None)
        cfg_val = self.configurable.config_root["db"]["orm"]
        assert cfg_val == config_instance()["db"]["orm"]
        assert config_instance() is not self.configurable.config_root

    def test_config_path_getter(self, tmp_appdirs, mocker):
        """Make sure the config target path is constructed to our expectations."""
        # DRY?/2020-01-09: (lb): Perhaps move repeated ConfigUrable code to fixture.
        self.configurable = self.get_configurable()
        mocker.patch.object(self.configurable, "_load_config_obj")
        self.configurable.load_config(configfile_path=None)
        # The config path, e.g., '/home/user/.config/test__dob-bright/app.conf'
        expectation = self.configurable.configfile_path
        self.configurable._load_config_obj.assert_called_with(expectation)
