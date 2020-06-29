# This file exists within 'dob-bright':
#
#   https://github.com/tallybark/dob-bright
#
# Copyright © 2018-2020 Landon Bouma, © 2015-2016 Eric Goller. All rights reserved.
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

"""
Fixtures available to the tests/.

- In general, fixtures should return a single instance.

- If a fixture is a factory, its name should reflect that.

- A fixture that is parametrized should be suffixed with
  ``_parametrized`` to imply it has increased complexity.
"""

import codecs
import os
import py
import tempfile
from configobj import ConfigObj

import fauxfactory
import pytest
from unittest.mock import MagicMock

from nark.config import decorate_config
from nark.helpers.app_dirs import ensure_directory_exists
from nark.items.fact import Fact

from dob_bright.config import app_dirs  # Needs container of AppDirs.
from dob_bright.controller import Controller
from dob_bright.termio.errors import dob_been_warned_reset

# Register fixtures: 'fact_factory', 'fact', 'activity', etc.
# - (lb): Disabled for now, because not used in dob_bright, but if we
#   improve dob-bright test coverage, I'd guess we'll want this back.
#
#    from nark.tests.item_factories import *

test_lib_log_level = 'WARNING'
test_cli_log_level = 'WARNING'
# DEV: Uncomment to see more log trace while testing:
test_lib_log_level = 'DEBUG'
test_cli_log_level = 'DEBUG'


# ***

@pytest.fixture
def filename():
    """Provide a filename string."""
    return fauxfactory.gen_utf8()


@pytest.fixture
def filepath(tmpdir, filename):
    """Provide a fully qualified pathame within our tmp-dir."""
    return os.path.join(tmpdir.strpath, filename)


# ***

@pytest.fixture
def appdirs(mocker, tmpdir):
    """Provide mocked version specific user dirs using a tmpdir."""
    mock_dirs = mocker.MagicMock()
    mock_dirs.user_config_dir = ensure_directory_exists(
        os.path.join(tmpdir.mkdir('config').strpath, 'dob/'),
    )
    mock_dirs.user_data_dir = ensure_directory_exists(
        os.path.join(tmpdir.mkdir('data').strpath, 'dob/'),
    )
    mock_dirs.user_cache_dir = ensure_directory_exists(
        os.path.join(tmpdir.mkdir('cache').strpath, 'dob/'),
    )
    mock_dirs.user_log_dir = ensure_directory_exists(
        os.path.join(tmpdir.mkdir('log').strpath, 'dob/'),
    )

    app_dirs.AppDirs = mock_dirs

    return mock_dirs


# ***

def _config_root(nark_config, dob_config):
    """Provide a generic baseline configuration."""
    config_root = decorate_config(nark_config)
    config_root.update(dob_config)
    # Beware config_decorator settings' _conform_f(), which mutates source values.
    # To layer config collections, be sure to use the original, pre-mutation values.
    config = config_root.as_dict(unmutated=True)
    return config


@pytest.fixture
def config_root(nark_config, dob_config):
    return _config_root(nark_config, dob_config)


@pytest.fixture(scope="session")
def config_root_ro(nark_config_ro, dob_config_ro):
    return _config_root(nark_config_ro, dob_config_ro)


# This method essentially same as: nark:tests/conftest.py::base_config.
def _nark_config(tmpdir):
    """
    Provide a static backend config fixture.
    """
    # FETREQ/2020-01-09: (lb): Support dot-notation in dict keys on `update`.
    # - For now, create deep dictionary; not flat with dotted key names.
    return {
        'db': {
            'orm': 'sqlalchemy',
            'engine': 'sqlite',
            'path': ':memory:',
            # MAYBE/2019-02-20: (lb): Support for alt. DBMS is wired, but not tested.
            #   'host': '',
            #   'port': '',
            #   'name': '',
            #   'user': '',
            #   'password': '',
        },
        'dev': {
            'lib_log_level': test_lib_log_level,
            'sql_log_level': 'WARNING',
        },
        'time': {
            # 2019-02-20: (lb): Note that allow_momentaneous=False probably Bad Idea,
            #                   especially for user upgrading from legacy hamster db.
            'allow_momentaneous': True,

            # MAYBE/2019-02-20: (lb): I don't day_start, so probably broke; needs tests.
            #   'day_start': datetime.time(hour=0, minute=0, second=0).isoformat(),
            #   'day_start': datetime.time(hour=5, minute=0, second=0).isoformat(),
            'day_start': '',

            # MAYBE/2019-02-20: (lb): Perhaps test min-delta, another feature I !use!
            #   'fact_min_delta': '60',
            'fact_min_delta': '0',

            # FIXME/2019-02-20: (lb): Implement tzawareness/tz_aware/timezone sanity.
            'tz_aware': False,

            # FIXME/2019-02-20: (lb): Needs testing, e.g.,
            #   'default_tzinfo': 'America/Menominee',
            'default_tzinfo': '',
        },
    }


@pytest.fixture
def nark_config(tmpdir):
    return _nark_config(tmpdir)


@pytest.fixture(scope="session")
def nark_config_ro():
    return _nark_config(tmpdir=None)


def _dob_config(tmpdir):
    """
    Provide a static client config fixture.
    """
    return {
        # 'editor.centered': '',
        'editor.centered': 'True',

        'editor.lexer': '',

        'term.editor_suffix': '',

        # Disable color, otherwise tests will have to look for color codes.
        'log.use_color': False,

        # Don't log to console, otherwise tests have to deal with that noise.
        # 'log_console': True,  # Default.
        'log.use_console': False,

        # The default log filename does not need to be changed.
        # 'log_filename': 'dob.log',  # Default.
        # See also:
        #  'logfile_path': '',  # Generated value.

        'dev.cli_log_level': test_cli_log_level,

        'fact.separators': '',  # [,:\n]

        'term.show_greeting': False,

        'editor.styling': '',

        'term.use_color': False,
        'term.use_pager': False,
    }


@pytest.fixture
def dob_config(tmpdir):
    return _dob_config(tmpdir)


@pytest.fixture(scope="session")
def dob_config_ro(request):
    # https://stackoverflow.com/questions/25525202/py-test-temporary-folder-for-the-session-scope
    # Make a temporary directory, and wrap the path string in a Path object,
    # so that `.remove` works, and so test fixtures can treat it same as a
    # `tmpdir` builtin pytest fixture.
    _tmpdir = py.path.local(tempfile.mkdtemp())
    request.addfinalizer(lambda: _tmpdir.remove(rec=1))
    return _dob_config(_tmpdir)


@pytest.fixture
def config_instance(tmpdir, faker):
    """Provide a (dynamicly generated) ConfigObj instance."""

    def generate_config(**kwargs):
        cfg_dict = generate_dict(**kwargs)
        # NOPE: You'd overwrite your user's file with the default path:
        #   from dob_bright.config.fileboss import default_config_path
        #   configfile_path = default_config_path()
        configfile_path = os.path.join(tmpdir, 'dob.conf')
        config = ConfigObj(configfile_path)
        config.merge(cfg_dict)
        return config

    def generate_dict(**kwargs):
        cfg_dict = {}

        # ***

        cfg_db = {}
        cfg_dict['db'] = cfg_db

        cfg_db.setdefault('orm', kwargs.get('orm', 'sqlalchemy'))
        cfg_db.setdefault('engine', kwargs.get('engine', 'sqlite'))
        # HARDCODED: This filename value does not matter, really.
        db_path = os.path.join(tmpdir.strpath, 'dob.sqlite')
        cfg_db.setdefault('path', kwargs.get('path', db_path))
        cfg_db.setdefault('host', kwargs.get('host', ''))
        cfg_db.setdefault('port', kwargs.get('port', ''))
        cfg_db.setdefault('name', kwargs.get('name', ''))
        cfg_db.setdefault('user', kwargs.get('user', '')),
        cfg_db.setdefault('password', kwargs.get('password', ''))

        # ***

        cfg_dev = {}
        cfg_dict['dev'] = cfg_dev

        lib_log_level = kwargs.get('lib_log_level', test_lib_log_level)
        cfg_dev.setdefault('lib_log_level', lib_log_level)
        sql_log_level = kwargs.get('sql_log_level', 'WARNING')
        cfg_dev.setdefault('sql_log_level', sql_log_level)

        # ***

        cfg_time = {}
        cfg_dict['time'] = cfg_time

        # (lb): Need to always support momentaneous, because legacy data bugs.
        # cfg_time.setdefault('allow_momentaneous', 'False')
        cfg_time.setdefault('allow_momentaneous', 'True')

        # day_start = kwargs.get('day_start', '')
        day_start = kwargs.get('day_start', '00:00:00')
        cfg_time.setdefault('day_start', day_start)

        # fact_min_delta = kwargs.get('fact_min_delta', '0')
        fact_min_delta = kwargs.get('fact_min_delta', '60')
        cfg_time.setdefault('fact_min_delta', fact_min_delta)

        cfg_time.setdefault('tz_aware', kwargs.get('tz_aware', 'False'))
        # FIXME/2019-02-20: (lb): Fix timezones. And parameterize, e.g.,
        #  default_tzinfo = kwargs.get('default_tzinfo', 'America/Menominee')
        default_tzinfo = kwargs.get('default_tzinfo', '')
        cfg_time.setdefault('default_tzinfo', default_tzinfo)

        # ***

        cfg_editor = {}
        cfg_dict['editor'] = cfg_editor

        cfg_editor.setdefault('centered', False)
        cfg_editor.setdefault('lexer', '')
        cfg_editor.setdefault('styling', '')

        # ***

        cfg_fact = {}
        cfg_dict['fact'] = cfg_fact

        cfg_fact.setdefault('separators', '')  # [,:\n]

        # ***

        assert 'dev' in cfg_dict

        cli_log_level = kwargs.get('cli_log_level', test_cli_log_level)
        cfg_dev.setdefault('cli_log_level', cli_log_level)

        # ***

        cfg_log = {}
        cfg_dict['log'] = cfg_log

        cfg_log.setdefault('filename', kwargs.get('log_filename', faker.file_name()))
        # The log_filename is used to make log.filepath, which we don't need to set.
        cfg_log.setdefault('use_color', 'False')
        cfg_log.setdefault('use_console', kwargs.get('log_console', 'False'))

        # ***

        cfg_term = {}
        cfg_dict['term'] = cfg_term

        cfg_term.setdefault('editor_suffix', '')
        cfg_term.setdefault('show_greeting', 'False')
        cfg_term.setdefault('use_color', 'True')
        cfg_term.setdefault('use_pager', 'False')

        # ***

        return cfg_dict

    return generate_config


@pytest.fixture
def config_file(config_instance, appdirs):
    """Provide a config file store under our fake config dir."""
    conf_path = os.path.join(appdirs.user_config_dir, 'dob.conf')
    with codecs.open(conf_path, 'w', encoding='utf-8') as fobj:
        config_instance().write(fobj)


@pytest.fixture
def get_config_file(config_instance, appdirs):
    """Provide a dynamic config file store under our fake config dir."""
    def generate(**kwargs):
        instance = config_instance(**kwargs)
        conf_path = os.path.join(appdirs.user_config_dir, 'dob.conf')
        with codecs.open(conf_path, 'w', encoding='utf-8') as fobj:
            instance.write(fobj)
        return instance
    return generate


# *** Various config settings

@pytest.fixture
def db_name(request):
    """Return a randomized database name."""
    return fauxfactory.gen_utf8()


@pytest.fixture
def db_user(request):
    """Return a randomized database username."""
    return fauxfactory.gen_utf8()


@pytest.fixture
def db_password(request):
    """Return a randomized database password."""
    return fauxfactory.gen_utf8()


@pytest.fixture(params=(fauxfactory.gen_latin1(), fauxfactory.gen_ipaddr()))
def db_host(request):
    """Return a randomized database username."""
    return request.param


@pytest.fixture
def db_port(request):
    """Return a randomized database port."""
    return str(fauxfactory.gen_integer(min_value=0, max_value=65535))


# ***

@pytest.fixture
def ongoing_fact(controller_with_logging, fact):
    """Fixture tests that ``ongoing fact`` can be saved to data store."""
    fact.end = None
    fact = controller_with_logging.facts.save(fact)
    return fact


# ***

def prepare_controller(config_root):
    controller = Controller()
    controller.wire_configience(config_root=config_root)
    # (lb): My apologies for this assault. Reset module variable between tests.
    # (2020-05-26: We could try using @contextlib.contextmanager and `with:`,
    #  with setup code, a `yield`, and then teardown.)
    dob_been_warned_reset()
    return controller


@pytest.fixture
def test_fact_cls():
    return Fact


@pytest.fixture(scope="session")
def test_fact_cls_ro():
    return Fact


@pytest.yield_fixture
def controller(config_root, mocker, test_fact_cls):
    """Provide a pseudo controller instance."""
    controller = prepare_controller(config_root=config_root)
    controller.ctx = mocker.MagicMock()
    controller.configurable = mocker.MagicMock()
    controller.standup_store(fact_cls=test_fact_cls)
    yield controller
    controller.store.cleanup()


def _controller_with_logging(config_root, magic_mock, test_fact_cls):
    """Provide a pseudo controller instance with logging setup."""
    controller = prepare_controller(config_root=config_root)
    controller.ctx = magic_mock()
    controller.configurable = magic_mock()
    controller.setup_logging()
    controller.standup_store(fact_cls=test_fact_cls)
    return controller


@pytest.yield_fixture
def controller_with_logging(config_root, mocker, test_fact_cls):
    controller = _controller_with_logging(
        config_root, mocker.MagicMock, test_fact_cls,
    )
    yield controller
    controller.store.cleanup()


@pytest.yield_fixture(scope="session")
def controller_with_logging_ro(config_root_ro, test_fact_cls_ro):
    controller = _controller_with_logging(
        config_root_ro, MagicMock, test_fact_cls_ro,
    )
    yield controller
    controller.store.cleanup()

