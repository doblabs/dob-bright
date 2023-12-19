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

from easy_as_pypi_termio.echoes import click_echo, highlight_value
from easy_as_pypi_termio.errors import exit_warning
from easy_as_pypi_termio.style import attr

from ..crud.interrogate import run_editor_safe
from ..reports.render_results import render_results
from .create_conf import create_basic_conf
from .load_ignore import ignore_file_path, load_no_completion

__all__ = (
    "create_ignore_conf",
    "echo_ignore_sections",
    "echo_ignore_table",
    "edit_ignore_file",
)

# Note that there's no `dob ignore conf` command like `dob styles conf`
# or `dob rules conf`, because the ignore file is not a true conf (there
# are no `key=values`, only `[sections]`, `# comments`, and `^rules$`.


# *** [CREATE] IGNORE

BASIC_IGNORE_FILE = _(
    """
# `dob edit` prompt suggestion ignore file.

# YOU: Add names and regex below to exclude matches
#      from auto-complete and drop-down suggestions.

[activity]

# Add names of Activities you want to exclude, e.g.,
#   Task1@Project
#   Task2@Project
# or you could exclude all Activities in a Category
# with a dot-star regular expression, e.g.,
#   .*@Project

[category]

# List Categories to exclude, e.g.,
#   @Project
#   @Job.*

[tag]

# List Tags to exclude, e.g.,
#   some-tag
#   feature-*
#   .*PROJ-.*

"""
).lstrip()


def create_ignore_conf(controller, force):
    def _create_ignore_conf():
        # SIMILAR funcs: See also: ConfigUrable.create_config and
        #   reset_config; and styles_cmds.create_styles_conf;
        #                  and rules_cmds.create_rules_conf.
        object_name = _("Ignore file")
        ignore_path = ignore_file_path(controller.config)
        create_basic_conf(ignore_path, object_name, create_ignore_file, force)

    def create_ignore_file(ignore_path):
        with open(ignore_path, "w") as ignore_f:
            ignore_f.write(BASIC_IGNORE_FILE)

    _create_ignore_conf()


# *** [EDIT] IGNORE


def edit_ignore_file(controller):
    ignore_path = ignore_file_path(controller.config)
    run_editor_safe(filename=ignore_path)


# *** [LIST] IGNORE


def echo_ignore_sections(controller):
    """"""

    def _echo_ignore_sections():
        no_completion = load_no_completion(controller)
        sections = no_completion.raw
        print_ignore_sections(sections, _("Ignore file sections"))

    def print_ignore_sections(sections, title):
        click_echo("{}{}{}".format(attr("underlined"), title, attr("reset")))
        for section_name in sections.keys():
            click_echo("  " + highlight_value(section_name))

    return _echo_ignore_sections()


# *** [SHOW] IGNORE


def echo_ignore_table(controller, name, output_format):
    def _echo_ignore_table():
        no_completion = load_no_completion(controller)
        if not name:
            sections = no_completion.raw
        else:
            sections = {name: fetch_existing_rule(no_completion, name)}
        print_ignore_table(sections)

    def fetch_existing_rule(no_completion, section_name):
        try:
            section = no_completion.raw[section_name]
        except KeyError:
            exit_section_unknown(section_name)
        return section

    def exit_section_unknown(section_name):
        exit_warning(_("No section named “{}”").format(section_name))

    def print_ignore_table(sections):
        sec_key_vals = []
        section_names = sorted(sections.keys())
        for section_name in section_names:
            rules = sections[section_name]
            sec_key_vals += [(section_name, rule) for rule in rules]
        headers = [
            _("Section"),
            _("Rule"),
        ]
        render_results(
            controller,
            results=sec_key_vals,
            headers=headers,
            output_format=output_format,
        )

    _echo_ignore_table()
