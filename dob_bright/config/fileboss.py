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

from gettext import gettext as _

import os
import re
import tempfile
from pathlib import Path

from configobj import ConfigObj, ConfigObjError, DuplicateError, ParseError

from nark.helpers.app_dirs import ensure_directory_exists

from dob_bright.termio import click_echo

from ..termio import dob_in_user_exit, dob_in_user_warning

from .app_dirs import AppDirs

__all__ = (
    'create_configobj',
    'default_config_path',
    'default_config_path_abbrev',
    'echo_config_obj',
    'empty_config_obj',
    'ensure_file_path_dirred',
    'load_config_obj',
    'warn_user_config_errors',
    'write_config_obj',
)


# ***

def default_config_path():
    config_dir = AppDirs.user_config_dir
    config_filename = 'dob.conf'
    configfile_path = os.path.join(config_dir, config_filename)
    return configfile_path


def default_config_path_abbrev():
    # Path.home() is Python 3.5+. See os.path.expanduser('~') for older Python.
    user_home = str(Path.home())
    abbrev_path = re.sub(r'^{}'.format(user_home), '~', default_config_path())
    return abbrev_path


# ***

def create_configobj(conf_path, errname=''):
    try:
        return ConfigObj(
            conf_path,
            encoding='UTF8',
            interpolation=False,
            write_empty_values=False,
        )
    except ConfigObjError as err:
        # Catches DuplicateError, and other errors, e.g.,
        #       Parsing failed with several errors.
        #       First error at line 55.
        msg = _("Failed to load {0} config at “{1}”: {2}").format(
            errname, conf_path, str(err),
        )
        dob_in_user_warning(msg)
        return None


# ***

def echo_config_obj(config_obj):
    def _echo_config_obj():
        temp_f = prepare_temp_file(config_obj)
        write_config_obj(config_obj)
        open_and_print_dump(temp_f)

    def prepare_temp_file(config_obj):
        # Not that easy:
        #   config_obj.filename = sys.stdout
        # (lb): My understanding is that for the TemporaryFile to be openable
        # on Windows, we should close it first (Linux can open an opened file
        # again, but not Windows).
        #   https://docs.python.org/3/library/tempfile.html#tempfile.NamedTemporaryFile
        temp_f = tempfile.NamedTemporaryFile(delete=False)
        temp_f.close()
        config_obj.filename = temp_f.name
        return temp_f

    def write_styles_conf(config_obj):
        config_obj.write()

    def open_and_print_dump(temp_f):
        with open(temp_f.name, 'r') as fobj:
            click_echo(fobj.read().strip())
        os.unlink(temp_f.name)

    return _echo_config_obj()


# ***

def empty_config_obj(configfile_path):
    """"""
    def _empty_config_obj():
        try:
            config_obj = create_config_obj()
        except ParseError as err:
            # E.g., "configobj.ParseError: Invalid line ('<>') (...) at line <>."
            exit_parse_error(str(err))
        return config_obj

    def create_config_obj():
        config_obj = ConfigObj(
            configfile_path,
            encoding='UTF8',
            interpolation=False,
            write_empty_values=False,
            # Note that ConfigObj has a raise_errors param, but if False, it
            # just defers the error, if any; it'll still get raised, just at
            # the end. So what's the point? -(lb)
            #   raise_errors=False,
        )
        return config_obj

    def exit_parse_error(err):
        msg = _(
            'ERROR: Your config file at “{}” has a syntax error: “{}”'
        ).format(configfile_path, str(err))
        dob_in_user_exit(msg)

    return _empty_config_obj()


# ***

def load_config_obj(configfile_path):
    """"""

    def _load_config_obj():
        try:
            config_obj = empty_config_obj(configfile_path)
        except DuplicateError as err:
            # (lb): The original (builtin) configparser would let you
            # choose to error or not on duplicates, but the ConfigObj
            # library (which is awesome in many ways) does not have
            # such a feature (it's got a raise_errors that does not
            # do the trick). Consequently, unless we code a way around
            # this, we gotta die on duplicates. Sorry, User! Seems
            # pretty lame. But also seems pretty unlikely.
            exit_duplicates(str(err))

        return config_obj

    def exit_duplicates(err):
        msg = _(
            'ERROR: Your config file at “{}” has a duplicate setting: “{}”'
        ).format(configfile_path, str(err))
        dob_in_user_exit(msg)

    return _load_config_obj()


# ***

def write_config_obj(config_obj):
    def _write_config_obj():
        if not config_obj.filename:
            raise AttributeError('ConfigObj missing ‘filename’')
        ensure_file_path_dirred(config_obj.filename)
        try:
            config_obj.write()
        except UnicodeEncodeError as err:
            die_write_failed(config_obj, err)

    def die_write_failed(config_obj, err):
        # E.g.,:
        #   UnicodeEncodeError: 'ascii' codec can't encode character
        #     '\u2018' in position 1135: ordinal not in range(128)
        msg = _(
            'ERROR: Failed to write file at “{}”: “{}”\n'
            'Perhaps unknown character(s): {}'
        ).format(
            config_obj.filename,
            str(err),
            err.object[err.start:err.end],
        )
        dob_in_user_exit(msg)

    return _write_config_obj()


# ***

def ensure_file_path_dirred(filename):
    # Avoid: FileNotFoundError: [Errno 2] No such file or directory: ....
    configfile_dir = os.path.dirname(filename)
    if configfile_dir:
        ensure_directory_exists(configfile_dir)


# ***

def warn_user_config_errors(_unconsumed, errs, which=''):
    """"""

    def _warn_user_config_errors():
        # Don't actually care about _unconsumed, for a few reasons. First, because
        # plugins, the first time setup_config() is called, it will not recognize
        # plugin settings. Second, there's no harm in config.
        # MAYBE: (lb): Well, unless it's a user typo, then a config-audit command
        #        might be useful.
        warned = warn_user_config_settings(errs, _('value errors'))
        return warned

    def warn_user_config_settings(lookup, what):
        if not lookup:
            return False
        lines = assemble_lines(lookup)
        msg = _(
            "The {} contains {}:\n{}"
        ).format(which, what, '\n'.join(lines))
        dob_in_user_warning(msg)
        return True

    def assemble_lines(node, keys='', lines=None):
        if lines is None:
            lines = []
        for key, item in node.items():
            if isinstance(item, dict):
                nkey = keys + '.' if keys else ''
                assemble_lines(item, nkey + key, lines)
            elif not keys and not item:
                # Unrecognized section.
                lines.append('- [{}]'.format(key))
            else:
                lines.append('- {}.{} → {}'.format(keys, key, str(item)))
        return lines

    return _warn_user_config_errors()

