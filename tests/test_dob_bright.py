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

from nark.config import decorate_config
from nark.helpers import logging as logging_helpers

from dob_bright.config import app_dirs, fileboss
from dob_bright.config.fileboss import write_config_obj
from dob_bright.config.urable import ConfigUrable


class TestSetupLogging(object):
    """Make sure that our logging setup is executed as expected."""

    def test_setup_logging_and_log_level(self, controller):
        """
        Test that library and client logger have log level set according to config.
        """
        controller.setup_logging()
        assert controller.lib_logger.level == (
            logging_helpers.resolve_log_level(
                controller.config['dev.lib_log_level']
            )[0]
        )
        assert controller.client_logger.level == (
            logging_helpers.resolve_log_level(
                controller.config['dev.cli_log_level']
            )[0]
        )

    def test_setup_logging_log_console_true(self, controller):
        """Ensure if console logging, lib and client have streamhandlers."""
        controller.config['log.use_console'] = True
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

    def test_setup_logging_log_file_true(self, controller, appdirs):
        """
        Make sure that if we enable logfile_path, both loggers receive ``FileHandler``.
        """
        controller.config['log.filepath'] = os.path.join(
            appdirs.user_log_dir, 'foobar.log',
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
    """Make sure that turning a config instance into proper config dictionaries works."""

    @pytest.mark.parametrize('cli_log_level', ['debug'])
    def test_log_levels_valid(self, cli_log_level, config_instance):
        """
        Make sure *string loglevels* translates to their respective integers properly.
        """
        config_obj = config_instance(cli_log_level=cli_log_level)
        assert config_obj['dev']['cli_log_level'] == cli_log_level
        config = decorate_config(config_obj)
        assert config['dev']['cli_log_level'] == 10
        assert config['dev.cli_log_level'] == 10
        assert config.asobj.dev.cli_log_level.value == 10

    @pytest.mark.parametrize('cli_log_level', ['foobar'])
    def test_log_levels_invalid(self, cli_log_level, config_instance, capsys):
        """Test that invalid *string loglevels* raise ``ValueError``."""
        config_obj = config_instance(cli_log_level=cli_log_level)
        with pytest.raises(
            ValueError,
            match=r"^Unrecognized value for setting ‘cli_log_level’: “foobar”.*"
        ):
            _config = decorate_config(config_obj)  # noqa: F841 unused local
        out, err = capsys.readouterr()
        assert out == ''
        assert err == ''

    def test_invalid_store(self, config_instance):
        """Make sure that passing an ORM other than 'sqlalchemy' raises an exception."""
        config_obj = config_instance(orm='foobar')
        match_former = r'Unrecognized value for setting ‘orm’'
        match_latter = r'“foobar” \(Choose from: ‘sqlalchemy’\)'
        with pytest.raises(
            ValueError, match=r"^{}: {}$".format(match_former, match_latter),
        ):
            _config = decorate_config(config_obj)  # noqa: F841 unused local

    def test_non_sqlite(self, config_instance):
        """Make sure that passing a postgres config works.

        Albeit actual postgres connections not tested."""
        confnstnc = config_instance(engine='postgres')
        config = decorate_config(confnstnc)
        assert config['db.host'] == confnstnc['db']['host']
        assert config['db.port'] == confnstnc['db']['port']
        assert config['db.name'] == confnstnc['db']['name']
        assert config['db.user'] == confnstnc['db']['user']
        assert config['db.password'] == confnstnc['db']['password']


class TestGetConfigInstance(object):
    def test_no_file_present(self, appdirs, mocker):
        # In lieu of testing from completely vanilla account, ensure config file does
        # not exist (which probably exists for your user at ~/.config/dob/dob.conf).
        # NOTE: AppDirs is a module-scope object with immutable attributes, so we
        # need to mock the entire object (i.e., cannot just patch attribute itself).
        app_dirs_mock = mock.Mock()
        app_dirs_mock.configure_mock(user_config_dir='/XXX')
        app_dirs_mock.configure_mock(user_data_dir='/XXX')
        mocker.patch.object(fileboss, 'AppDirs', app_dirs_mock)
        self.configurable = ConfigUrable()
        self.configurable.load_config(configfile_path=None)
        assert len(list(self.configurable.config_root.items())) > 0
        assert self.configurable.cfgfile_exists is False

    def test_file_present(self, config_instance):
        """Make sure we try parsing a found config file."""
        self.configurable = ConfigUrable()
        self.configurable.load_config(configfile_path=None)
        cfg_val = self.configurable.config_root['db']['orm']
        assert cfg_val == config_instance()['db']['orm']
        assert config_instance() is not self.configurable.config_root

    def test_config_path_getter(self, appdirs, mocker):
        """Make sure the config target path is constructed to our expectations."""
        mocker.patch('dob_bright.config.fileboss.load_config_obj')
        # DRY?/2020-01-09: (lb): Perhaps move repeated ConfigUrable code to fixture.
        self.configurable = ConfigUrable()
        self.configurable.load_config(configfile_path=None)
        # 'dob.conf' defined and used in dob_bright.config.fileboss.default_config_path.
        expectation = os.path.join(appdirs.user_config_dir, 'dob.conf')
        assert fileboss.load_config_obj.called_with(expectation)


class TestWriteConfigFile(object):
    def test_file_is_written(self, filepath, config_instance):
        """Ensure file is written. Content not checked; that's ConfigObj's job."""
        config_obj = config_instance()
        write_config_obj(config_obj)
        assert os.path.lexists(config_obj.filename)

    def test_non_existing_path(self, tmpdir, filename, config_instance):
        """Make sure that the path-parents are created if not present."""
        filepath = os.path.join(tmpdir.strpath, filename)
        assert os.path.lexists(filepath) is False
        config_obj = config_instance()
        config_obj.filename = filepath
        write_config_obj(config_obj)
        assert os.path.lexists(config_obj.filename)


class TestDobAppDirs(object):
    """AppDirs tests."""

    def _test_app_dir_returns_directoy(self, app_dirname, tmpdir, **kwargs):
        """Make sure method returns directory."""
        path = tmpdir.strpath
        with mock.patch(
            'appdirs.{}'.format(app_dirname),
            new_callable=mock.PropertyMock,
        ) as mock_app_dir:
            mock_app_dir.return_value = path
            appdir = app_dirs.DobAppDirs('dob')
            assert getattr(appdir, app_dirname) == path
            # (lb): Guh. After py3.5 dropped, we could simplify this to:
            #   mock_app_dir.assert_called_once()
            # Until then, gotta specify args and kwargs.
            # MAYBE/2020-01-29: Ha! Dropped py3.5 because PTK3 dropped it!
            # - So now we could see about simplifying this.
            kwargs['version'] = None
            mock_app_dir.assert_called_once_with('dob', None, **kwargs)

    def _test_app_dir_creates_file(self, app_dirname, create, tmpdir, faker, **kwargs):
        """Make sure that path creation depends on ``create`` attribute."""
        path = os.path.join(tmpdir.strpath, '{}/'.format(faker.word()))
        # We want NarkAppDirs's call to appdirs.XXX_dir to return our /tmp path.
        # (lb): Note that mocker (from pytest-mock) merely takes care of teardown,
        #   which is also accomplished with your simply use with-mock, as follows.
        with mock.patch(
            'appdirs.{}'.format(app_dirname),
            new_callable=mock.PropertyMock,
            return_value=path,
        ) as mock_app_dir:
            appdir = app_dirs.DobAppDirs('dob')
            appdir.create = create
            # DEVS: Weird: If this assert fires and you're running `py.test --pdb`,
            # entering e.g., `appdir.user_data_dir` at the pdb prompt shows the
            # non-mocked value! But if you capture the value first and print it,
            # it's correct! So in code you'd have:
            #   show_actual = appdir.user_data_dir
            # And in pdb you'd type:
            #   (pdb) show_actual
            #   '/tmp/pytest-of-user/pytest-1142/test_user_data_dir_creates_fil0/relationship/'
            #   (pdb) appdir.user_data_dir
            #   '/home/user/.local/share/dob'
            assert os.path.exists(getattr(appdir, app_dirname)) is create
            # MAYBE/2020-01-29: New min. Py now 3.6, so might be able to simplify:
            #   mock_app_dir.assert_called_once()
            # but currently doing it hard way _with() args and kwargs (circa py3.5).
            kwargs['version'] = None
            mock_app_dir.assert_called_once_with('dob', None, **kwargs)

    # ***

    def test_user_data_dir_returns_directoy(self, tmpdir):
        """Make sure method returns directory."""
        self._test_app_dir_returns_directoy(
            'user_data_dir', tmpdir, roaming=False,
        )

    @pytest.mark.parametrize('create', [True, False])
    def test_user_data_dir_creates_file(self, tmpdir, faker, create):
        """Make sure that path creation depends on ``create`` attribute."""
        self._test_app_dir_creates_file(
            'user_data_dir', create, tmpdir, faker, roaming=False,
        )

    # ---

    def test_site_data_dir_returns_directoy(self, tmpdir):
        """Make sure method returns directory."""
        self._test_app_dir_returns_directoy(
            'site_data_dir', tmpdir, multipath=False,
        )

    @pytest.mark.parametrize('create', [True, False])
    def test_site_data_dir_creates_file(self, tmpdir, faker, create):
        """Make sure that path creation depends on ``create`` attribute."""
        self._test_app_dir_creates_file(
            'site_data_dir', create, tmpdir, faker, multipath=False,
        )

    # ---

    def test_user_config_dir_returns_directoy(self, tmpdir):
        """Make sure method returns directory."""
        self._test_app_dir_returns_directoy(
            'user_config_dir', tmpdir, roaming=False,
        )

    @pytest.mark.parametrize('create', [True, False])
    def test_user_config_dir_creates_file(self, tmpdir, faker, create):
        """Make sure that path creation depends on ``create`` attribute."""
        self._test_app_dir_creates_file(
            'user_config_dir', create, tmpdir, faker, roaming=False,
        )

    # ---

    def test_site_config_dir_returns_directoy(self, tmpdir):
        """Make sure method returns directory."""
        self._test_app_dir_returns_directoy(
            'site_config_dir', tmpdir, multipath=False,
        )

    @pytest.mark.parametrize('create', [True, False])
    def test_site_config_dir_creates_file(self, tmpdir, faker, create):
        """Make sure that path creation depends on ``create`` attribute."""
        self._test_app_dir_creates_file(
            'site_config_dir', create, tmpdir, faker, multipath=False,
        )

    # ---

    def test_user_cache_dir_returns_directoy(self, tmpdir):
        """Make sure method returns directory."""
        self._test_app_dir_returns_directoy('user_cache_dir', tmpdir)

    @pytest.mark.parametrize('create', [True, False])
    def test_user_cache_dir_creates_file(self, tmpdir, faker, create):
        """Make sure that path creation depends on ``create`` attribute."""
        self._test_app_dir_creates_file('user_cache_dir', create, tmpdir, faker)

    # ---

    def test_user_log_dir_returns_directoy(self, tmpdir):
        """Make sure method returns directory."""
        self._test_app_dir_returns_directoy('user_log_dir', tmpdir)

    @pytest.mark.parametrize('create', [True, False])
    def test_user_log_dir_creates_file(self, tmpdir, faker, create):
        """Make sure that path creation depends on ``create`` attribute."""
        self._test_app_dir_creates_file('user_log_dir', create, tmpdir, faker)

