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

"""~/.config/dob/styling/rules.conf definition and encapsulating class."""

import os

from gettext import gettext as _

from prompt_toolkit.layout.containers import Container
from prompt_toolkit.widgets.base import Label
from prompt_toolkit.widgets.base import TextArea

from ..config.fileboss import warn_user_config_errors
# MAYBE/2019-12-02: (lb) Is using normal stdout to print errors okay?
#                        Or should we use the Carousel (e.g., PPT modal)?
from ..termio import dob_in_user_warning

from .rules_conf import create_style_rules_object

__all__ = (
    'StyleEngine',
)


class StyleEngine(object):
    """Encapsulate Carousel-specific user configurable styling, PPT class names,
    and Pygments style syntax."""

    def __init__(self, rules_confobj):
        # The caller passes a dict-like object of rules read from
        # the user's rules.conf file. We convert that to a RulesRoot
        # object, which encapsulates business logic in a dict-like
        # candy wrapper.
        self.rulesets = self.consume_style_rules_conf(rules_confobj)

        # As the Carousel builds the PPT UX and creates and add components
        # to it, it'll register each stylable component. At that time, we
        # will find all the applicable user-defined rules (from self.rulesets),
        # and we'll cache them here, in self.componentry. (We'll also see what
        # rules apply to the component, but if the rules are applied a second
        # time, at least the rulesets will be cached.)
        # - tl;dr, This is a ruleset cache for each of the stylable PPT components.
        self.componentry = {}

    # ***

    def consume_style_rules_conf(self, rules_confobj):

        def _consume_style_rules_conf():
            if rules_confobj is None:
                return {}
            return _create_rulesets()

        def _create_rulesets():
            rulesets = {}
            for section, rules in rules_confobj.items():
                ruleset = create_ruleset_from_rules(rulesets, rules)
                rulesets[section] = ruleset
            return rulesets

        def create_ruleset_from_rules(rulesets, rules):
            ruleset = create_style_rules_object()
            unconsumed, errs = ruleset.update_known(rules, errors_ok=True)
            warn_if_smelly_config(unconsumed, errs)
            return ruleset

        def warn_if_smelly_config(unconsumed, errs):
            basename = os.path.basename(rules_confobj.filename)
            warn_user_config_errors(unconsumed, errs, which=basename)

        return _consume_style_rules_conf()

    # ***

    def process_style_rules(self, ppt_widget, friendly_name, fact):
        # Here's an example rules.conf contents that'll get you here:
        #   $ cat ~/.config/dob/styling/rules.conf
        #   [My Category Style]
        #   category_name = 'My Category'
        #   scrollable_frame = class:my-category
        # and then your corresponding class could be defined as:
        #   $ cat ~/.config/dob/styling/styles.conf
        #   [my-style]
        #   my-category = 'bg:#CA85AC #000000'
        # and then wire it all via the config:
        #   $ dob config set style my-style

        def _process_style_rules():
            rulesets = rules_for_component(friendly_name)
            return apply_triggered_style_rules(ppt_widget, rulesets, fact)

        # ***

        def rules_for_component(friendly_name):
            try:
                return self.componentry[friendly_name]
            except KeyError:
                return assemble_component_rulesets(friendly_name)

        def assemble_component_rulesets(friendly_name):
            rebuild_component_rulesets_list(friendly_name)
            return self.componentry[friendly_name]

        def rebuild_component_rulesets_list(friendly_name):
            self.componentry[friendly_name] = {}
            for section, ruleset in self.rulesets.items():
                # The friendly_name is the name of the component in the UX.
                # The user uses the friendly_name in the rules.conf to add
                # a class string to the component. Check here if it's empty,
                # meaning the user does not have this setting in their conf
                # (and the default '' was used); or, the user specified the
                # setting by set it to the empty string.
                if not ruleset[friendly_name]:
                    continue
                if ruleset['disabled']:
                    continue
                # We're just building a convenience lookup of rules that apply
                # to the named component. We'll run the rules check later.
                self.componentry[friendly_name][section] = ruleset

        # ***

        def apply_triggered_style_rules(ppt_widget, rulesets, fact):
            accumulated = ''
            for section, ruleset in rulesets.items():
                if not ruleset_triggered(section, ruleset, fact):
                    continue
                accumulated += apply_style_rule_class(ppt_widget, ruleset)
            return accumulated

        # ***

        def ruleset_triggered(section, ruleset, fact):
            # NOTE: If more than one rule applies, we assume AND (because
            #       user can OR simply by using additional [ruleset]s).
            triggered = False

            # This is a tad bit funky: returning False because not triggered
            #   could be because the user did not configure any conditionals for
            #   this ppt_widget, or because one of the conditionals failed.
            # There are two False paths:
            #   - We want to return False either *after* checking that there are no
            #     conditionals, or;
            #   - We want to return False on the first conditional to fail;
            # As such, we use a trinary, aka three-level digital logic, -1, 0, 1.
            #   - 0 means the probe did not find any conditionals to test.
            #   - 1 means there were one or more conditionals, and all passed.
            #   - -1 means there were one or more conditionals, and one failed.
            # So on 0 or 1, keep processing, but on -1 or all 0s, return False;
            # and only return True if all 1s.

            trinary = probe_fact(section, ruleset, fact)
            if trinary == -1:
                return False
            triggered = trinary == 1 or triggered

            trinary = probe_eval(section, ruleset, fact)
            if trinary == -1:
                return False
            triggered = trinary == 1 or triggered

            return triggered

        def probe_fact(section, ruleset, fact):
            # For each attribute, there are multiple rules the user can choose
            # from to specify one of more names, e.g., one or more Activity
            # names might share the same style, and user could specify:
            #   [my-custom-rule]
            #   activities = Name1, Name2
            # or, if the user wants to be absurd, they could instead specify:
            #   [my-custom-rule]
            #   activity = Name1
            #   activities = Name2
            # because we'll just combine both rules and check for one to match.
            # - But for tags, the user might want to distinguish between
            #   AND and OR, so we'll go to the trouble to let the user
            #   specify if we should AND tags, or OR them.

            trinary = 0

            activities = set()
            if ruleset['activity']:
                activities.add(ruleset['activity'])
            if ruleset['activities']:
                activities = activities.union(ruleset['activities'])
            if activities:
                if fact.activity_name in activities:
                    trinary = 1
                else:
                    return -1

            categories = set()
            if ruleset['category']:
                categories.add(ruleset['category'])
            if ruleset['categories']:
                categories = categories.union(ruleset['categories'])
            if categories:
                if fact.category_name in categories:
                    trinary = 1
                else:
                    return -1

            # (lb): Because I'm too accommodating, a zillion ways to conditional tags.

            tags_any = set()
            if ruleset['tag']:
                tags_any.add(ruleset['tag'])
            if ruleset['tags']:
                tags_any = tags_any.union(ruleset['tags'])
            if ruleset['tags-any']:
                tags_any = tags_any.union(ruleset['tags-any'])
            if ruleset['tags-or']:
                tags_any = tags_any.union(ruleset['tags-or'])

            tags_all = set()
            if ruleset['tags-all']:
                tags_all = tags_all.union(ruleset['tags-all'])
            if ruleset['tags-and']:
                tags_all = tags_all.union(ruleset['tags-and'])

            if tags_any or tags_all:
                fact_tags = set([tag.name for tag in fact.tags])
                if tags_any:
                    if tags_any.intersection(fact_tags):
                        trinary = 1
                    else:
                        return -1
                if tags_all:
                    if not tags_all.difference(fact_tags):
                        trinary = 1
                    else:
                        return -1

            return trinary

        def probe_eval(section, ruleset, fact):
            # (lb): `'<str>' in ruleset` sends 0, not '<str>', to __getitem__?!
            # So do `'__eval__' not in ruleset.keys()`. Except no need, because
            # the key should exist, because create_style_rules_object.
            compiled_code = ruleset['__eval__']
            if compiled_code is None:
                return 0
            try:
                trinary = eval(compiled_code)
            except Exception as err:
                msg = _(
                    "eval() failed on style rule ‘eval’ from “{0}”: {1}"
                ).format(section, str(err))
                # MAYBE/2019-12-02: (lb): Show errors in Carousel?
                # - Also one of few places where traverser imports ...helpers
                #   (and I want to make traverser less dob-dependent (coupled)).
                dob_in_user_warning(msg)
                # Such that we never do this error dance again!
                ruleset['__eval__'] = None
                return False
            return trinary and 1 or -1

        # ***

        def apply_style_rule_class(ppt_widget, ruleset):
            custom_classes = ' {}'.format(ruleset[friendly_name])
            if ppt_widget is None:
                # Style being used in a (style, text, handler) tuple.
                pass
            elif isinstance(ppt_widget, Label):
                apply_style_rule_to_label(ppt_widget, custom_classes)
            elif isinstance(ppt_widget, Container):
                apply_style_rule_to_container(ppt_widget, custom_classes)
            elif isinstance(ppt_widget, TextArea):
                apply_style_rule_to_text_area(ppt_widget, custom_classes)
            else:
                # Unexpected path. Unhandled PPT type.
                # (lb): This is a wee bit coupled to the whole application
                # framework: Get the Context from Click, and from that, get
                # our Controller object, which has an affirm method (which
                # is wired to the dob config's catch_errors).
                # MAYBE/2019-12-05: (lb): Decouple dob-viewer from click,
                #   used only for term. size.
                #   - Except here, where it's used to call our affirm, but
                #     also honors user's dev.catch_errors config setting.
                #     - Ideally, dob would set this up when it calls Carousel;
                #       or, dob, could configure dob-bright, and maybe dob-bright
                #       could offer an affirm() singleton or module method
                #       that is enabled after the config is read.
                import click_hotoffthehamster as click
                click.get_current_context().obj.affirm(False)
                pass
            return custom_classes

        def apply_style_rule_to_label(label, custom_classes):
            # (lb): I'm totally wingin' it, in the sense that this works,
            # but I'm sure I'm bending the rules. The Label object has
            # three children we can play with to affect style:
            #   ∗ label.text, a list of (style, text, mouse-handler) tuples;
            #   ∗ label.formatted_text_control, which contains the text; and
            #   ∗ label.window, which extends further right to the parent edge.
            # Either of the first two options sets the style of just the text;
            # setting the window option affects the style to the parent edge.
            # - Because to be complicated, we let the user customize either
            # just the text, or the text and line padding.
            #   - We use the magical suffix, "-line", to decide which it is, e.g.,
            #         value-activity = class:my-style-text-only
            #         value-activity-line = class:my-style-whole-line
            if not friendly_name.endswith('-line'):
                # If label.text is tuples, their style beats formatted_text_control,
                # so rebuild the tuples list if present.
                if (
                    (isinstance(label.text, list))
                    and (len(label.text) > 0)
                    and (isinstance(label.text[0], tuple))
                    and (len(label.text[0]) > 1)
                ):
                    # Discard tup[0] (style component) and replace.
                    # (lb): Rules replace, not append, widget's style. #rule_replace
                    label.text = [
                        (custom_classes, tup[1], *tup[2:]) for tup in label.text
                    ]
                else:
                    # Otherwise, label.text is a simple 'string' (not a tuple),
                    # so we can use the formatted_text_control style.
                    label.formatted_text_control.style += custom_classes
            else:
                label.window.style += custom_classes

        def apply_style_rule_to_container(container, custom_classes):
            container.style += custom_classes

        def apply_style_rule_to_text_area(container, custom_classes):
            container.window.style += custom_classes

        # ***

        return _process_style_rules()

