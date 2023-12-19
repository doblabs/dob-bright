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

"""Controller functionality: Application plugin features."""

from .database_store import Controller_DatabaseStore

__all__ = ("Controller_PostProcessor",)


class Controller_PostProcessor(
    # For self.setup_config, depends on:
    #  Controller_ConfigManager
    # but for deliberate super() chaining: load data store layer next:
    Controller_DatabaseStore,
):
    """Implements the @post_process decorator and calls plugins post-command."""

    POST_PROCESSORS = []

    def __init__(self, *args, **kwargs):
        super(Controller_PostProcessor, self).__init__(*args, **kwargs)

    # ***

    def replay_config(self):
        # Called by ensure_plugged_in after loading plugin config.
        # NOTE: This'll re-print any errors messages from the first setup_config.
        #       Except that color will not have been set the first time, so errors
        #       before will be plain; and errors reprinted here will be colorful.
        self.setup_config(self.configfile_path, *self.config_keyvals)

    # ***

    @staticmethod
    def post_processor(func):
        Controller_PostProcessor.POST_PROCESSORS.append(func)

    @staticmethod
    def _post_process(
        ctx,
        controller,
        fact_facts_or_true,
        show_plugin_error=None,
        carousel_active=False,
    ):
        # facts_or_true is one of:
        # - The saved/edited Fact;
        # - a list of Facts;
        # - or True, on upgrade-legacy.
        for handler in Controller_PostProcessor.POST_PROCESSORS:
            handler(
                ctx,
                controller,
                fact_facts_or_true,
                show_plugin_error=show_plugin_error,
                carousel_active=carousel_active,
            )

    def post_process(
        self,
        controller,
        fact_facts_or_true,
        show_plugin_error=None,
        carousel_active=False,
    ):
        Controller_PostProcessor._post_process(
            self.ctx,
            controller,
            fact_facts_or_true,
            show_plugin_error=show_plugin_error,
            carousel_active=carousel_active,
        )

    # ***
