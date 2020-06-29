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

"""User configurable interactive editor styling settings loaders."""

from gettext import gettext as _

import os

from ..config.fileboss import create_configobj
from ..termio import dob_in_user_warning

from . import load_obj_from_internal, style_conf

__all__ = (
    'load_style_classes',
    'load_style_rules',
    'load_rules_conf',
    'resolve_named_style',
    'resolve_path_rules',
    'resolve_path_styles',
    'DEFAULT_STYLE',
)


DEFAULT_STYLE = 'default'


def load_style_classes(controller, style_name='', skip_default=False):
    # (lb): It's times like these -- adding a dict to get around scoping
    # when sharing a variable -- that I think a method (load_style_classes)
    # should be a class. But this works for now.
    load_failed = {'styles': False}

    def _load_style_classes():
        named_style = style_name or resolve_named_style(controller.config)
        classes_dict = load_dict_from_styles_conf(named_style)
        style_classes = instantiate_or_try_internal_style(named_style, classes_dict)
        return style_classes

    def load_dict_from_styles_conf(named_style):
        styles_conf, failed = load_styles_conf(controller.config)
        if failed:
            load_failed['styles'] = True
        elif styles_conf and named_style in styles_conf:
            # We could keep as ConfigObj, but not necessary, e.g.:
            #   classes_dict = create_configobj(styles_conf[named_style])
            classes_dict = styles_conf[named_style]
            return classes_dict
        return None

    def instantiate_or_try_internal_style(named_style, classes_dict):
        if classes_dict is not None:
            controller.affirm(isinstance(classes_dict, dict))
            defaults = prepare_base_style(classes_dict)
            update_base_style(named_style, classes_dict, defaults)
            return defaults
        return load_internal_style(named_style)

    def prepare_base_style(classes_dict):
        # Load base-style (e.g., style_conf.default) to ensure
        # all keys present (and defaulted), and then update that.
        base_style = DEFAULT_STYLE
        if 'base-style' in classes_dict:
            base_style = classes_dict['base-style'] or 'default'
        try:
            # This gets a StylesRoot object created by _create_style_object.
            defaults = getattr(style_conf, base_style)()
        except AttributeError as err:  # noqa: F841
            # Unexpected, because of choices= on base-style @setting def.
            controller.affirm(False)
            defaults = style_conf.default()
        return defaults

    def update_base_style(named_style, classes_dict, defaults):
        try:
            defaults.update_gross(classes_dict)
        except Exception as err:
            msg = _("Failed to load style named “{0}”: {1}").format(
                named_style, str(err),
            )
            dob_in_user_warning(msg)

    def load_internal_style(named_style):
        # HARDCODED/DEFAULT: style_classes default: 'default' (Ha!).
        # - This style uses no colors, so the UX will default to however
        #   the terminal already looks.
        style_classes_fn = load_obj_from_internal(
            controller,
            obj_name=named_style,
            internal=style_conf,
            default_name=not skip_default and DEFAULT_STYLE or None,
            warn_tell_not_found=not load_failed['styles'],
            config_key=CFG_KEY_ACTIVE_STYLE,
        )
        # The Carousel/`dob edit` path leaves skip_default=False, so it will
        # receive at least the default config. The fetch styles config path/
        # `dob config styles.conf` wants None if nothing found (skip_default=True).
        controller.affirm(skip_default or style_classes_fn is not None)
        return style_classes_fn and style_classes_fn() or None

    # ***

    return _load_style_classes()


# ***

def load_styles_conf(config):
    """Return 2-tuple, the styles.conf ConfigObj, and a bool indicating failure.

    The config object will be None if the path does not exist, or if it failed to
    loaded. Failure will be False if the object was loaded, or if the path does
    not exists; failure is True if the file exists, but ConfigObj failed to load it.
    """
    def _load_styles_conf():
        styles_path = resolve_path_styles(config)
        if not os.path.exists(styles_path):
            return None, False
        return load_dict_from_user_styling(styles_path)

    def load_dict_from_user_styling(styles_path):
        styles_conf = create_configobj(styles_path, errname='styles_conf')
        if styles_conf is None:
            return None, True
        return styles_conf, False

    return _load_styles_conf()


# ***

def load_style_rules(controller):
    def _load_style_rules():
        rules_confobj = try_load_dict_from_user_style_rules()
        return rules_confobj

    def try_load_dict_from_user_style_rules():
        rules_confobj, failed = load_rules_conf(controller.config)
        if rules_confobj is None:
            return None
        compile_eval_rules(rules_confobj)
        return rules_confobj

    def compile_eval_rules(rules_confobj):
        # Each section may optionally contain one code/eval component. Compile
        # it now to check for errors, with the bonus that it's cached for later
        # ((lb): not that you'd likely notice any change in performance with or
        # without the pre-compile).
        for section, rules in rules_confobj.items():
            if 'eval' not in rules:
                continue
            try:
                rules['__eval__'] = compile(
                    source=rules['eval'],
                    filename='<string>',
                    # Specifying 'eval' because single expression.
                    # Could use 'exec' for sequence of statements.
                    mode='eval',
                )
            except Exception as err:
                rules_path = resolve_path_rules(controller.config)
                msg = _("compile() failed on 'eval' from “{0}” in “{1}”: {2}").format(
                    section, rules_path, str(err),
                )
                dob_in_user_warning(msg)

    # ***

    return _load_style_rules()


# ***

def load_rules_conf(config):
    def _load_rules_conf():
        rules_path = resolve_path_rules(config)
        if not os.path.exists(rules_path):
            return None, False
        return wrap_in_configobj(rules_path)

    def wrap_in_configobj(rules_path):
        rules_confobj = create_configobj(rules_path, errname='rules_conf')
        if rules_confobj is None:
            return None, True
        return rules_confobj, False

    return _load_rules_conf()


# ***

CFG_KEY_ACTIVE_STYLE = 'editor.styling'


def resolve_named_style(config):
    return config[CFG_KEY_ACTIVE_STYLE]


# ***

CFG_KEY_STYLES_FPATH = 'editor.styles_fpath'


def resolve_path_styles(config):
    return config[CFG_KEY_STYLES_FPATH]


# ***

CFG_KEY_RULESETS_FPATH = 'editor.rules_fpath'


def resolve_path_rules(config):
    return config[CFG_KEY_RULESETS_FPATH]

