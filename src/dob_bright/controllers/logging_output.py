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

"""Controller functionality: Logging features."""

import logging

from nark.helpers import logging as logging_helpers

from .config_manager import Controller_ConfigManager

__all__ = ("Controller_LoggingOutput",)


class Controller_LoggingOutput(
    # For self.config, depends on:
    #  Controller_ConfigManager  # self.config['dev.*' and 'log.*']
    # but for deliberate super() chaining: load data store layer next:
    Controller_ConfigManager,
):
    """Maintains Controller's self.client_logger."""

    def __init__(self, *args, **kwargs):
        super(Controller_LoggingOutput, self).__init__(*args, **kwargs)

    # ***

    def setup_logging(self, verbose=False, verboser=False):
        """Setup logging for the lib_logger as well as client specific logging."""
        self.client_logger = logging.getLogger("dob")
        loggers = self.get_loggers()
        for logger in loggers:
            logger.handlers = []
        # Clear existing Handlers, and set the level.
        # MAYBE: Allow user to specify different levels for different loggers.
        cli_log_level_name = self.config["dev.cli_log_level"]
        cli_log_level, warn_name = logging_helpers.resolve_log_level(cli_log_level_name)
        # We can at least allow some simpler optioning from the command args.
        if verbose:
            cli_log_level = min(logging.INFO, cli_log_level)
        if verboser:
            cli_log_level = min(logging.DEBUG, cli_log_level)
        # 2019-01-25 (lb): I have not had any issues for past few weeks, but,
        #   just FYI in case you do, you might need to clear handlers on
        #   lib_logger and sql_logger, e.g.,:
        #        for logger in loggers:
        #            logger.handlers = []
        #            logger.setLevel(cli_log_level)
        self.client_logger.handlers = []
        self.client_logger.setLevel(cli_log_level)

        color = self.config["log.use_color"]
        formatter = logging_helpers.formatter_basic(color=color)

        if self.config["log.use_console"]:
            console_handler = logging.StreamHandler()
            logging_helpers.setup_handler(console_handler, formatter, *loggers)

        logfile = self.config["log.filepath"]
        if logfile:
            file_handler = logging.FileHandler(logfile, encoding="utf-8")
            logging_helpers.setup_handler(file_handler, formatter, *loggers)

        if warn_name:
            self.client_logger.warning(
                "Unknown Client.cli_log_level specified: {}".format(cli_log_level)
            )

    def get_loggers(self):
        loggers = [
            self.lib_logger,
            self.sql_logger,
            self.client_logger,
        ]
        return loggers

    def bulk_set_log_levels(self, log_level):
        for logger in self.get_loggers():
            logger.setLevel(log_level)

    def disable_logging(self):
        loggers = [
            self.lib_logger,
            self.sql_logger,
            self.client_logger,
        ]
        for logger in loggers:
            logger.handlers = []
            logger.setLevel(logging.NOTSET)

    # ***
