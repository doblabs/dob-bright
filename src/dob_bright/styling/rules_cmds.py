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

from config_decorator.config_decorator import ConfigDecorator
from easy_as_pypi_config.dec_wrap import decorate_and_wrap
from easy_as_pypi_config.fileboss import create_configobj, echo_config_obj
from easy_as_pypi_termio.echoes import click_echo, highlight_value
from easy_as_pypi_termio.errors import echo_warning, exit_warning
from easy_as_pypi_termio.style import attr

from ..config.config_table import echo_config_decorator_table
from ..crud.interrogate import run_editor_safe
from .create_conf import create_basic_conf
from .load_styling import load_rules_conf, load_style_rules, resolve_path_rules
from .rules_conf import create_style_rules_object
from .style_engine import StyleEngine

__all__ = (
    "create_rules_conf",
    "echo_rules_conf",
    "echo_rule_names",
    "echo_rules_table",
    "edit_rules_conf",
)


# *** [CONF] RULES


def echo_rules_conf(controller, rule_name, complete=False):
    config = controller.config

    def _echo_rules_conf():
        rules_confobj = load_rules_confobj()
        if rules_confobj:
            echo_config_obj(rules_confobj)
        # Else, already printed error message.

    def load_rules_confobj():
        rules_confobj, failed = load_rules_conf(config)
        if rules_confobj:
            return filter_rules_confobj(rules_confobj)
        if failed:
            # load_styles_conf prints a ConfigObj error message. Our job is done.
            return None
        return echo_error_no_rules_conf()

    def filter_rules_confobj(rules_confobj):
        if not rule_name:
            return rules_confobj
        new_config = create_configobj(conf_path=None)
        try:
            new_config.merge({rule_name: rules_confobj[rule_name]})
        except KeyError:
            return echo_error_no_rules_section(rule_name)
        else:
            return new_config

    def echo_error_no_rules_conf():
        msg = _("No rules file at: {0}").format(resolve_path_rules(config))
        echo_warning(msg)
        return None

    def echo_error_no_rules_section(rule_name):
        msg = _("No matching section “{0}” found in rules file at: {1}").format(
            rule_name,
            resolve_path_rules(config),
        )
        echo_warning(msg)
        return None

    # ***

    return _echo_rules_conf()


# *** [CREATE] RULES


def create_rules_conf(controller, force):
    def _create_rules_conf():
        object_name = _("Rules file")
        rules_path = resolve_path_rules(controller.config)
        create_basic_conf(rules_path, object_name, create_rules_file, force)

    def create_rules_file(rules_path):
        # Load specified style, or DEFAULT_STYLE if not specified.
        ruleset = create_style_rules_object()
        rule_name = _("Example Style Rule - Showing all built-in options")
        config_obj = decorate_and_wrap(rule_name, ruleset, complete=True)
        config_obj.filename = rules_path
        config_obj.write()

    _create_rules_conf()


# *** [EDIT] RULES


def edit_rules_conf(controller):
    rules_path = resolve_path_rules(controller.config)
    run_editor_safe(filename=rules_path)


# *** [LIST] RULES


def echo_rule_names(controller):
    """"""

    def _echo_rule_names():
        rules_confobj = load_style_rules(controller)
        print_rules_names(rules_confobj, _("User-created rules"))

    def print_rules_names(rules_confobj, title):
        click_echo("{}{}{}".format(attr("underlined"), title, attr("reset")))
        for rule_name in rules_confobj.keys():
            click_echo("  " + highlight_value(rule_name))

    return _echo_rule_names()


# *** [SHOW] RULES


def echo_rules_table(controller, name, output_format):
    def _echo_rules_table():
        if not name:
            rule_name, ruleset = create_example_rule()
        else:
            rule_name, ruleset = fetch_existing_rule()
        print_ruleset_table(rule_name, ruleset)

    def create_example_rule():
        rule_name = _("example")
        ruleset = create_style_rules_object()
        return rule_name, ruleset

    def fetch_existing_rule():
        rules_confobj = load_style_rules(controller)
        styling_rules = StyleEngine(rules_confobj)
        try:
            ruleset = styling_rules.rulesets[name]
        except KeyError:
            exit_rule_unknown(name)
        return name, ruleset

    def exit_rule_unknown(rule_name):
        exit_warning(_("No rule named “{}”").format(rule_name))

    def print_ruleset_table(rule_name, ruleset):
        condec = ConfigDecorator.create_root_for_section(rule_name, ruleset)
        conf_objs = [condec]
        echo_config_decorator_table(
            cfg_decors=conf_objs,
            exclude_section=False,
            # Passed on to render_results:
            controller=controller,
            output_format=output_format,
        )

    _echo_rules_table()
