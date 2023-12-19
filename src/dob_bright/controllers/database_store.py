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

"""Controller functionality: Database *store* features."""

import os
import sys
from gettext import gettext as _

from easy_as_pypi_termio.echoes import click_echo, highlight_value
from easy_as_pypi_termio.errors import exit_warning
from nark.items.fact import Fact

from .setup_coloring import Controller_SetupColoring

__all__ = ("Controller_DatabaseStore",)


class Controller_DatabaseStore(
    # For self.config, depends on:
    #  Controller_ConfigManager  # self.config['db.*']
    # For self.arg0name, depends on:
    #  Controller_PdbSubprocess
    # but for deliberate super() chaining: load data store layer next:
    Controller_SetupColoring,
):
    """Helps manage NarkControl.store for the CLI."""

    def __init__(self, *args, **kwargs):
        super(Controller_DatabaseStore, self).__init__(*args, **kwargs)

    @property
    def now(self):
        return self.store.now

    def now_refresh(self):
        return self.store.now_refresh()

    @property
    def data_store_exists_at(self):
        return _("Data store already exists at {}").format(self.config["db.path"])

    @property
    def data_store_url(self):
        return self.store.db_url

    @property
    def sqlite_db_path(self):
        if self.config["db.engine"] == "sqlite":
            return self.config["db.path"]

        # (lb): I don't super-like this. It's a weird side effect.
        #   And it's knowledgeable about the CLI command API. Meh.
        exit_warning(
            _("Not a SQLite database. Try `{} store url`").format(self.arg0name)
        )

    @property
    def is_germinated(self):
        if not self.store_exists:
            return False

        return Controller_SetupColoring.is_germinated.fget(self)

    @property
    def has_no_user_files(self):
        has_no_user_files = Controller_SetupColoring.has_no_user_files.fget(self)
        if has_no_user_files and not self.store_exists:
            return True

        return False

    @property
    def store_exists(self):
        # Check either db.path is set, or all of db.host/port/name/user.
        if self.config["db.engine"] == "sqlite":
            if self.config["db.path"] == ":memory:":
                return True
            return os.path.isfile(self.config["db.path"])
        else:
            # NOTE: db_url is an attribute of SQLAlchemyStore, not BaseStore.
            return bool(self.store.db_url)

    def standup_store(self, fact_cls=Fact):
        self.store.fact_cls = fact_cls
        return super(Controller_DatabaseStore, self).standup_store()

    # ***

    def create_data_store(self, force, fact_cls=Fact):
        unlinked_db = False
        skip_standup = self.check_sqlite_store_ready()
        if skip_standup:
            if force:
                self._reset_data_store()
                unlinked_db = True
            else:
                exit_warning(self.data_store_exists_at)
        self._standup_and_version_store(fact_cls)
        if unlinked_db:
            self._announce_recreated_store()

    # ***

    def check_sqlite_store_ready(self):
        if self.config["db.engine"] != "sqlite":
            return None
        db_path = self.config["db.path"]
        if not os.path.isfile(db_path):
            return False
        return True

    def _reset_data_store(self):
        if self.config["db.engine"] != "sqlite":
            # raise NotImplementedError
            exit_warning(_("FIXME: Reset non-SQLite data store not supported (yet)."))
        else:
            self.must_unlink_db_path(force=True)

    # ***

    def must_unlink_db_path(self, *_args, force):
        db_path = self.config["db.path"]
        if not os.path.exists(db_path):
            return
        if not os.path.isfile(db_path):
            exit_warning(
                _("Data store exists but is not a file, so not overwriting {}").format(
                    db_path
                )
            )
        if not force:
            exit_warning(self.data_store_exists_at)
        os.unlink(db_path)

    # ***

    def _announce_recreated_store(self):
        click_echo(
            _("Recreated data store at {}").format(
                highlight_value(self.config["db.path"])
            )
        )

    # ***

    def _standup_and_version_store(self, fact_cls):
        created_fresh = self.standup_store(fact_cls)
        if created_fresh:
            verb = _("created")
        else:
            verb = _("already ready")
        click_echo(
            _("Dob database {verb} at {url}").format(
                verb=verb,
                url=highlight_value(self.store.db_url),
            )
        )

    # ***

    def process_config(self):
        super(Controller_DatabaseStore, self).process_config()

        # *cough*hack!*cough*”
        # Because invoke_without_command, we allow command-less invocations.
        #   For one such call -- `dob -v` -- tell the store not to log.
        # Also tell the store not to log if user did not specify anything,
        #   because we'll show the help/usage (which Click would normally
        #   handle if we had not tampered with invoke_without_command).
        if (len(sys.argv) > 2) or (
            (len(sys.argv) == 2) and (sys.argv[1] not in ("-v", "version"))
        ):
            return
        # FIXME/EXPLAIN/2019-01-22: (lb): What about other 2 loggers?
        #   dev.cli_log_level
        #   dev.lib_log_level
        # (lb): Normally I'd prefer the []-lookup vs. attr., e.g., not:
        #   self.config.asobj.dev.sql_log_level.value_from_forced = 'WARNING'
        # because the self.config has non-key-val attributes (like
        # setdefault) so I think for clarity we should lookup via [].
        # Except the []-lookup returns the value, not the keyval object.
        # So here we have to use dotted attribute notation.
        self.config.asobj.dev.sql_log_level.value_from_forced = "WARNING"

    # ***
