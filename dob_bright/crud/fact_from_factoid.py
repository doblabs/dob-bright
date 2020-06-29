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

import json

from gettext import gettext as _

from nark.helpers.parsing import ParserException

from ..termio import dob_in_user_exit

from .fact_dressed import FactDressed
from .fix_times import reduce_time_hint

__all__ = (
    'must_create_fact_from_factoid',
)


# ***

def must_create_fact_from_factoid(
    controller, factoid, time_hint,
):

    def _must_create_fact_from_factoid(
        controller, factoid, time_hint,
    ):
        separators = must_prepare_factoid_item_separators(controller)
        use_hint = reduce_time_hint(time_hint)
        try:
            fact, err = FactDressed.create_from_factoid(
                factoid=factoid,
                time_hint=use_hint,
                separators=separators,
                lenient=True,
            )
            controller.client_logger.info(str(err)) if err else None
        except ParserException as err:
            msg = _('Oops! {}').format(err)
            controller.client_logger.error(msg)
            dob_in_user_exit(msg)
        # This runs for verify_after, not verify_none/"blank time".
        fact_set_start_time_after_hack(fact, time_hint=use_hint)
        return fact

    def must_prepare_factoid_item_separators(controller):
        sep_string = controller.config['fact.separators']
        if not sep_string:
            return None
        try:
            separators = json.loads(sep_string)
        except json.decoder.JSONDecodeError as err:
            msg = _(
                "The 'separators' config value is not valid JSON: {}"
            ).format(err)
            controller.client_logger.error(msg)
            dob_in_user_exit(msg)
        return separators

    # FIXME/DRY: See create.py/transcode.py (other places that use "+0").
    #   (lb): 2019-01-22: Or maybe I don't care (not special enough to DRY?).
    #   (lb): 2019-12-06: My knowledge of this code is now so crusty that
    #                     it's too dangerous to consider DRYing anything!
    #                     Especially not without good test coverage first.
    def fact_set_start_time_after_hack(fact, time_hint):
        # FIXME/2019-01-19 13:00: What about verify_next: and verify_then: ???
        #   TESTME: Write more tests first to see if there's really an issue.
        if time_hint != "verify_after":
            return
        assert fact.start is None and fact.end is None
        # (lb): How's this for a hack!?
        fact.start = "+0"

    # ***

    return _must_create_fact_from_factoid(controller, factoid, time_hint)

