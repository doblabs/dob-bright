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

"""The Controller."""

import inspect
import os
import sys
from gettext import gettext as _

from easy_as_pypi_termio.echoes import click_echo, highlight_value
from easy_as_pypi_termio.errors import echo_warning, exit_warning
from nark.items.fact import Fact

from .. import help_newbs as help_strings
from .config_manager import Controller_ConfigManager
from .database_store import Controller_DatabaseStore
from .logging_output import Controller_LoggingOutput
from .pdb_subprocess import Controller_PdbSubprocess
from .post_processor import Controller_PostProcessor
from .setup_coloring import Controller_SetupColoring

__all__ = ("Controller",)


# ***
# *** [CONTROLLER] NarkControl Controller.
# ***

# (lb): This was originally one long class... now it's a class conglomeration.
# Both approaches have their pros and cons, the latter being more reusable and
# composable, but at the expense of readability. And it's not like using
# multiple class inheritance decouples this class at all; it just spreads
# to code out to separate files, which could make grokking more difficult.


class Controller(
    # Ordered so earlier items depend on later items, and also
    # to implement cooperative inheritance chaining. Note that
    # we might want to reduce this complexity and make attributes
    # for each of the classes instead, and maybe also shim functions,
    # but right now the Controller acts as a large multifaceted interface.
    Controller_PostProcessor,
    Controller_DatabaseStore,
    Controller_SetupColoring,
    Controller_PdbSubprocess,
    Controller_LoggingOutput,
    Controller_ConfigManager,
):
    """
    Organizes the Controller stack for dob, layering various functionality.

    Nark provides a basic Controller, and then dob adds all the CLI/TUI
    goodies, like config handling, logging, debugging capabilities,
    coloring, a UX interface to the database store, and arbitrary dob
    command post processing (that plugins use to add value to the app).
    """

    def __init__(self, config=None):
        super(Controller, self).__init__(config)

    # ***

    def insist_germinated(self, fact_cls=Fact):
        """Assist user if config or database not present."""

        def _insist_germinated():
            # Check if both self.store_exists and self.looks_like_config.
            if self.is_germinated:
                # We're good!
                self.standup_store(fact_cls)
                return

            if self.has_no_user_files:
                help_newbie_onboard()
            else:
                alert_user_if_config_file_unwell_or_store_absent()
            sys.exit(1)

        def help_newbie_onboard():
            message = help_strings.NEWBIE_HELP_ONBOARDING(self.ctx)
            click_echo(inspect.cleandoc(message), err=True)

        def alert_user_if_config_file_unwell_or_store_absent():
            self.alert_user_if_config_file_unwell()
            if not self.store_exists:
                oblige_user_create_store()

        def oblige_user_create_store():
            message = help_strings.NEWBIE_HELP_CREATE_STORE(
                self.ctx,
                db_path=self.config["db.path"],
                val_source=self.config.asobj.db.path.source,
            )
            click_echo(inspect.cleandoc(message), err=True)

        _insist_germinated()

    # ***

    def create_config_and_store(self, fact_cls=Fact):
        def _create_config_and_store():
            if not self.is_germinated:
                germinate_config_and_store()
            else:
                exit_already_germinated()

        def germinate_config_and_store():
            create_config_maybe()
            create_store_maybe()

        def create_config_maybe():
            cfg_path = self.configurable.config_path
            if not os.path.exists(cfg_path):
                self.create_config(force=False)
            else:
                click_echo(
                    _("Configuration already exists at {}").format(
                        highlight_value(cfg_path),
                    )
                )

        def create_store_maybe():
            # MEH: (lb): If the engine is not SQLite, this function cannot behave
            # like create_config_maybe, which tells the user if the things exists
            # already, because the storage class, SQLAlchemyStore, blindly calls
            # create_all (in create_storage_tables) without checking if db exists.
            skip_standup = self.check_sqlite_store_ready()
            if skip_standup:
                click_echo(self.data_store_exists_at)
            else:
                self._standup_and_version_store(fact_cls)

        def exit_already_germinated():
            exit_warning(
                _("Dob is already setup. Run `{} details` for info.").format(
                    self.arg0name
                )
            )

        _create_config_and_store()

    # ***

    # (lb): MAYBE/2020-12-27: This seems misplaced.

    def find_latest_fact(self, restrict=None):
        try:
            return self.facts.find_latest_fact(restrict=restrict)
        except Exception as err:
            # (lb): Unexpected! This could mean more than one ongoing Fact found!
            echo_warning(str(err))

    def find_oldest_fact(self):
        return self.facts.find_oldest_fact()

    # ***
