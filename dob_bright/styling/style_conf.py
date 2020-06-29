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

"""Facts Carousel Custom User (Pygment-defined) Styles."""

from gettext import gettext as _

import click_hotoffthehamster as click

from config_decorator import section

from .class_namilize import namilize

__all__ = (
    'color',
    'default',
    'light',
    'night',
    'KNOWN_STYLES',
    # PRIVATE:
    # '_create_style_object',
    # '_stylize_all_one',
)


KNOWN_STYLES = ['default', 'night', 'light', 'color']


def _create_style_object():
    """Define and return a ConfigDecorator for ~/.config/dob/styling/styles.conf."""

    # (lb): We want to wrap the @setting decorator (aka decorate the decorator),
    # which means we need to use two classes -- one to define the decorator, and
    # another that can call the decorator after the first class has been defined.

    @section(None)
    class StylesRoot(object):
        """"""

        def __init__(self):
            pass

        # ***

        NOT_STYLE_CLASSES = set()

        @classmethod
        def setting_wrap(cls, *args, not_a_style=False, **kwargs):
            def decorator(func):
                name = kwargs.get('name', func.__name__)
                if not_a_style:
                    cls.NOT_STYLE_CLASSES.add(name)
                return StylesRoot.setting(*args, **kwargs)(func)
            return decorator

        @classmethod
        def collect_tups(cls):
            style_classes = [
                (namilize(key), val.value) for key, val in StylesRoot._key_vals.items()
                if key not in cls.NOT_STYLE_CLASSES
            ]
            return style_classes

    # Now that the @section re-decorator is defined, we declare a class that
    # uses it to build a settings config. Note that we use a little @section
    # decorator magic on this second class -- by using a None section name,
    # in @StylesRoot.section(None), it causes the class being decorated (in
    # this case, CustomScreen) to be an alias to the root config (StylesRoot)!
    # So the settings defined in CustomScreen will be added to the root config,
    # and not to a sub-section. Somewhat wonky, but wonky is our jam.

    # (lb): 2 hacks, because eccentric magic of @section and ConfigDecorator:
    #
    # 1.) We wrap @ConfigDecorator.setting so we can identify which of our
    #     key-value settings are "class:..." assignments, and which of our
    #     key-value settings are the rules to decide if the class assignments
    #     should be applied.
    #     - The reason we mix the two types of settings in the same config
    #     section, rather than using two separate sections, is to keep the
    #     config flat and simple. It helps minimize the types of errors the
    #     user can make while editing their rules.conf file.
    #     - The hack is reaching into StylesRoot (which is also a hack: it's
    #     not a class, but an object instance! because of the eccentric magic
    #     of @section) and finding our @setting_wrap through the special
    #     _innerobj attribute.
    #
    # 2.) Hack number two here is specifying a `None` @section when defining
    #     the CustomScreen class, telling the @setting decorator to attach
    #     each setting to the root config, and not to a sub-section.
    #     - I.e., each setting herein will be applied to the StylesRoot object.
    #     In fact, CustomScreen disappears, in a sense, because the decorator
    #     returns the section to which the class settings apply, so you'll find:
    #       assert CustomScreen is StylesRoot  # Totally crazy, I know!
    #
    # 3?) I suppose there's actually a third hack, or maybe it's a trick, or just
    #     The Way To Do It: we use the encompassing _create_style_object() method
    #     to localize the defined classes/objects (StylesRoot and CustomScreen)
    #     so that we don't end up creating singletons, but rather create unique
    #     config objects each time.

    setting = StylesRoot._innerobj.setting_wrap

    def evaluate_content_dimension(value, dim):
        if isinstance(value, int):
            return value
        term_width, term_height = click.get_terminal_size()
        # E.g., = value.replace('term_width', str(term_width))
        evalable = value.replace(dim, str(locals()[dim]))
        compiled = compile(evalable, filename='<string>', mode='eval')
        executed = eval(compiled)
        return int(executed)

    @StylesRoot.section(None)
    class CustomScreen(object):
        """"""

        def __init__(self):
            pass

        # ***

        @property
        @setting(
            _("Generated value."),
            hidden=True,
            not_a_style=True,
        )
        def collect_tups(self):
            return StylesRoot._innerobj.collect_tups()

        # ***

        @property
        @setting(
            _("Name of the style to use for default values."),
            choices=['', 'default', 'night', 'light', 'color'],
            name='base-style',
            not_a_style=True,
        )
        def base_style(self):
            return ''

        # ***

        @property
        @setting(
            _("JUSTIFY/CENTER UX in terminal, or position LEFT or RIGHT."
              " See also: content-width."),
            choices=['LEFT', 'CENTER', 'RIGHT', 'JUSTIFY'],
            name='editor-align',
            not_a_style=True,
        )
        def editor_align(self):
            # (lb): AFAICT, 'CENTER' is equivalent to 'JUSTIFY'.
            return 'CENTER'

        # ***

        def evaluate_content_height(value):
            return evaluate_content_dimension(value, 'term_height')

        @property
        @setting(
            # NOTE: If content-height is set to None, the content height changes
            #       every time the user switches between Facts in the editor.
            _("Sizes content area height; may ref. term, e.g., “term_height - 15”."),
            name='content-height',
            not_a_style=True,
            # Use conform to change value used internally, but to keep the user's
            # input, e.g., when writing config to file, be sure to return, say,
            # "term_height - 15", and not the calculated internal value.
            conform=evaluate_content_height,
            allow_none=True,
        )
        def content_height(self):
            #
            # PPT will gripe "Window too small..." if we make the content
            # too large, and because we add a border box around the content,
            # the minimum height is:
            #
            #     minimum_height = term_height - 2
            #
            # except that accommodates *only* the content area, and
            # it pushes out (clips) the streamer, header, and footer.
            #
            # (lb): I'm hardcoding the height adjustment value (the 15, below),
            # in lieu of poking around our zone_details and other structures to
            # compute the height of each component. We'll just hardcode this now
            # and determine later if we should encode less UX knowledge here.
            #
            # Subtract from the terminal height the height of other components.
            # (I.e., grow the content area vertically to fill in the UX.)
            #
            # - The maths:
            #   - +1: There's 1 blank line above the streamer.
            #   - +3: The streamer is 3 lines, e.g.,
            #           ┌───────────────────────────────────────────────────────╮
            #           │ Wed 23 Jan 2019 ◐ 11:00 AM — 02:21 PM Thu 05 Dec 2019 │
            #           ╰───────────────────────────────────────────────────────╯
            #   - +1: There's 1 blank line between streamer and headers.
            #   - +6: +1 l. each: duration|start|end|activity|category|tags.
            #   - +1: There's 1 blank line between headers and content.
            #   - +2: The content area itself is bordered.
            #   - +1: The footer is a single line.
            #     --
            #     15

            # NOTE: There's no need to cache the calculated default value.
            # - (lb): This method is called only once per runtime, AFAICT.

            # We could `return click.get_terminal_size()[1] - 15` directly here,
            # but let's use a string and show off how to use the magic value. If
            # the user dumps the styling config, they'll see this string and have
            # a better idea how best to customize this value.

            # FIXME/2019-12-05: (lb): I bet this clips for Facts w/ 2+ lines of #tags.

            return 'term_height - 15'

        # ***

        def evaluate_content_width(value):
            return evaluate_content_dimension(value, 'term_width')

        @property
        @setting(
            # NOTE: To get 1 column of whitespace on both (the left and right)
            #       sides of the UX, subtract 3 (not 2) from the terminal width.
            #       E.g., in ~/.config/dob/styling/styles.conf:
            #         [my-style-1]
            #         content-width = term_width - 3
            # (lb): Here's nice dims that works well in many terminal sizings::
            #         [adaptive-style]
            #         content-width = 'min(term_width * 0.62432, term_height * 3.35988)'
            #         content-height = 'max(term_height - 22, 10)'
            _("Specifies UX width; may ref. curr. dims., e.g., “term_width - 3”."),
            name='content-width',
            not_a_style=True,
            # Use conform to change value used internally, but to keep the user's
            # input, e.g., when writing config to file, be sure to return, say,
            # "term_width - 3", and not the calculated internal value.
            conform=evaluate_content_width,
            allow_none=True,
        )
        def content_width(self):
            # We could return None and PPT would default to terminal width.
            # But let's use the magic string value, so when the user dumps
            # the styling config, they get a better idea what the default is.
            return 'term_width'

        # ***

        @property
        @setting(
            _("If True, wraps the content area text; otherwise, scrolls horizontally."),
            name='content-wrap',
            not_a_style=True,
        )
        def content_wrap(self):
            return True

        # ***

    # ***

    # The following class adds its members to the same root config object as the
    # previous class, but none of the settings below identify as a not_a_style.

    @StylesRoot.section(None)
    class CustomStyles(object):
        """"""

        # DRY alert: RulesClassify and CustomStyles have similarly-named methods,
        # but they're used differently.
        # - In RulesClassify, the methods are the (style) class names, and the
        #   values are the style definitions (e.g., bg and fg colors) that are
        #   used to make the PPT Style object. (The Style() object is used to
        #   lookup a class name and get the style definition).
        #   - Currently, the runtime makes the Style() object once, and never
        #     modifies it.
        # - In CustomStyles, the methods are also the (style) class names, but
        #   the values are class names and color styles (as a string) to add to
        #   the widget styles when a conditional rule applies.
        #   - I.e., the values in this class, when used by a conditional, are
        #     appended to the style of the widget that is identified by that
        #     class name. That is, the style string is not used to change the
        #     class name it references, but instead the class name refers to the
        #     widgets that identify with that class name. Got it?
        #     - E.g., if a conditional triggers and its styles are added to the
        #       activity value component, that component would have `style`:
        #         'class:value-normal class:value-activity class:{custom-value}'
        #       where {custom-value} is the value of the value-activity setting
        #       from this class (which gets the value from the user's rules.conf).
        #       - Note that 'class:value-activity' (a string) is always added to
        #         the component, regardless of any conditionals, and its definition
        #         comes from the user's styles.conf.
        #       - By specifying 'value-activity' in rules.conf, what ends up
        #         happening is that the conditional style is appended to the
        #         component style, following 'class:value-activity', thereby
        #         shadowing the basic style. What you have, in a sense, is
        #         'class:value-activity' serving as a default value, and the
        #         style rules' 'value-activity' being applied after that default.
        # (lb): I hope this isn't too confusing. But I think it'd be more confusing
        #   if the names were not the same in both configs. In any case, the methods
        #   listed here should be ordered like in the other class, to make it easier
        #   to keep the two config modules maintained and synced.
        # - Note that it's not necessary to define any of the attributes here,
        #   because the styles.conf parser treats any unknown setting from the
        #   user's conf as a class definition -- which has the same effect as
        #   declaring each @setting here. But by declaring them here, we can use
        #   the object for producing help, or to built a template file to make
        #   user onboarding easier.

        def __init__(self):
            pass

        # ***

        @property
        @setting(
            _("Shared style set on every widget (aka how to set the background color)."),
        )
        def label(self):
            return ''

        # ***

        @property
        @setting(
            _("Styles the streamer UX banner (topmost UX)."),
        )
        def streamer(self):
            return ''

        @property
        @setting(
            _("Styles the streamer UX banner (topmost UX) including empty lines."),
            name='streamer-line',
        )
        def streamer_line(self):
            return ''

        # ***

        @property
        @setting(
            _("Styles the header titles."),
            name='title-normal',
        )
        def title_normal(self):
            return ''

        @property
        @setting(
            _("Styles the header titles, including adjacent whitespacing."),
            name='title-normal-line',
        )
        def title_normal_line(self):
            return ''

        @property
        @setting(
            _("Styles the header title whose value has focus and is editable."),
            name='title-focus',
        )
        def title_focus(self):
            return ''

        @property
        @setting(
            _("Styles the header title and its whitespacing, when its value focused."),
            name='title-focus-line',
        )
        def title_focus_line(self):
            return ''

        # ***

        # See below for other title-* settings: title-duration → title-tags-line.

        # ***

        @property
        @setting(
            _("Styles the header value text."),
            name='value-normal',
        )
        def value_normal(self):
            return ''

        @property
        @setting(
            _("Styles the header value line (text and the whitespace right of it)."),
            name='value-normal-line',
        )
        def value_normal_line(self):
            return ''

        @property
        @setting(
            _("Styles the header value text when it has focus and is editable."),
            name='value-focus',
        )
        def value_focus(self):
            return ''

        @property
        @setting(
            _("Styles the header value line of the editable value with focus."),
            name='value-focus-line',
        )
        def value_focus_line(self):
            return ''

        # ***

        # The remaining title-* settings: title-duration through title-tags-line.
        # And remaining value-* settings: value-duration through value-tags-line.

        for prefix in ('title', 'value'):
            for part in (
                'duration',
                'start',
                'start-focus',
                'end',
                'end-focus',
                'activity',
                'category',
                'tags',
            ):
                for suffix in ('', '-line'):
                    class_name = '{}-{}{}'.format(prefix, part, suffix)

                    is_line = suffix == '-line'
                    is_focus = part.endswith('-focus')
                    help_l = is_line and _(', including adjacent whitspace') or ''
                    help_f = is_focus and _(', when value focused') or ''
                    doc = _("{} {} style{}{}.").format(part, prefix, help_l, help_f)

                    @setting(doc, name=class_name)
                    def _title_setting(self):
                        return ''

        # ***

        @property
        @setting(
            _("Styles the empty line between the tags and the content area."),
            name='blank-line',
        )
        def blank_line(self):
            return ''

        # ***

        @property
        @setting(
            _("Style the content area when showing the Fact description."),
            name='content-fact',
        )
        def content_fact(self):
            return ''

        # ***

        @property
        @setting(
            _("Styles the content area when showing the one-page help."),
            name='content-help',
        )
        def content_help(self):
            return ''

        # ***

        @property
        @setting(
            _("Styles the content area when showing a generated, unsaved gap Fact."),
            name='interval-gap',
        )
        def interval_gap(self):
            return ''

        # ***

        @property
        @setting(
            _("Styles the content area when showing an edited, unsaved Fact."),
            name='unsaved-fact',
        )
        def unsaved_fact(self):
            return ''

        # ***

        @property
        @setting(
            _("Styles of footer section of the UX (bottommost line)."),
            name='footer',
        )
        def footer_normal(self):
            return ''

        @property
        @setting(
            _("Styles the Fact ID or Hot Notif text in the UX footer."),
            name='footer-fact-id',
        )
        def footer_fact_id(self):
            return ''

        # ***

    # ***

    # The following class adds its members to the same root config object as the
    # previous class -- it uses not_a_style, like the first class above, to keep
    # these strings out of the Application object -- but these settings are sorta
    # styles, they're just handled manually by dob-viewer.

    @StylesRoot.section(None)
    class CustomHeaderValues(object):
        """"""

        def __init__(self):
            pass

        # ***

        # EXPLAIN: (lb): I don't recall how these two ended up so special,
        # I think because FactsDressed formats the tags for the Carousel
        # header. But for the other metadata -- Activity@Category, and start
        # and end times, even duration -- you can modify the style using one
        # of the 'value-*' options defined above. There's even a 'value-tag'
        # options, which leads me to believe I had this hardcoded because it
        # lets you style the hash symbol separately from the tag label.
        #
        # EXPLAIN: How do these interact with value-tag?

        @property
        @setting(
            _("Default style to apply to tag hashmarks in editor header."),
            name='value-tag-#',
            not_a_style=True,
        )
        def header_value_hash(self):
            return ''

        # ***

        @property
        @setting(
            _("Default style to apply to tag labels in editor header."),
            name='value-tag-label',
            not_a_style=True,
        )
        def header_value_tag(self):
            return ''

    # ***

    @StylesRoot.section(None)
    class CustomFactsDiff(object):
        """"""

        def __init__(self):
            pass

        # ***

        @property
        @setting(
            _("Style to apply to old Fact parts when not running editor."),
            name='value-diff-old-raw',
            not_a_style=True,
        )
        def value_diff_old_raw(self):
            return ''

        # ***

        @property
        @setting(
            _("Style to apply to old Fact parts in the editor header."),
            name='value-diff-old-ptk',
            not_a_style=True,
        )
        def value_diff_old_ptk(self):
            return ''

        # ***

        @property
        @setting(
            _("Style to apply to new Fact parts when not running editor."),
            name='value-diff-new-raw',
            not_a_style=True,
        )
        def value_diff_new_raw(self):
            return ''

        # ***

        @property
        @setting(
            _("Style to apply to new Fact parts in the editor header."),
            name='value-diff-new-ptk',
            not_a_style=True,
        )
        def value_diff_new_ptk(self):
            return ''

    # ***

    @StylesRoot.section(None)
    class CustomFactoid(object):
        """"""

        def __init__(self):
            pass

        # ***

        @property
        @setting(
            _("Style to apply to Fact ID in Factoid output (e.g., `dob show`)."),
            name='factoid-pk',
            not_a_style=True,
        )
        def factoid_pk(self):
            return ''

        # ***

        @property
        @setting(
            _("Style to apply to act@gory in Factoid output (e.g., `dob show`)."),
            name='factoid-act@gory',
            not_a_style=True,
        )
        def factoid_actegory(self):
            return ''

        # ***

        @property
        @setting(
            _("Style to apply to # symbol in Factoid output (e.g., `dob show`)."),
            name='factoid-#',
            not_a_style=True,
        )
        def factoid_hash(self):
            return ''

        # ***

        @property
        @setting(
            _("Style to apply to Tag in Factoid output (e.g., `dob show`)."),
            name='factoid-tag',
            not_a_style=True,
        )
        def factoid_tag(self):
            return ''

        # ***

        @property
        @setting(
            _("Style to apply to #tag in Factoid output (e.g., `dob show`)."),
            name='factoid-#tag',
            not_a_style=True,
        )
        def factoid_hashtag(self):
            return ''

        # ***

        @property
        @setting(
            _("Style to apply to start time in Factoid output (e.g., `dob show`)."),
            name='factoid-start',
            not_a_style=True,
        )
        def factoid_start(self):
            return ''

        # ***

        @property
        @setting(
            _("Style to apply to end time in Factoid output (e.g., `dob show`)."),
            name='factoid-end',
            not_a_style=True,
        )
        def factoid_end(self):
            return ''

        # ***

        @property
        @setting(
            _("Style to apply to ‘at’ in Factoid output (e.g., `dob show`)."),
            name='factoid-at',
            not_a_style=True,
        )
        def factoid_at(self):
            return ''

        # ***

        @property
        @setting(
            _("Style to apply to ‘to’ in Factoid output (e.g., `dob show`)."),
            name='factoid-to',
            not_a_style=True,
        )
        def factoid_to(self):
            return ''

        # ***

        @property
        @setting(
            _("Style to apply to duration in Factoid output (e.g., `dob show`)."),
            name='factoid-duration',
            not_a_style=True,
        )
        def factoid_duration(self):
            return ''

        # ***

    return StylesRoot


# ***

def default():
    """Default defines all options so tweaked stylings may omit any."""
    # (lb): Because of the magic of @section and how StylesRoot is not
    # really a class, but rather a ConfigDecorator object, we use a wrapper
    # function to both define the config (every time it's called) and to
    # return the newly instantiated ConfigDecorator object (which can only
    # be accessed using the name of the @section-decorated class!).
    styling = _create_style_object()
    return styling


# ***

def _stylize_all_one(styling, style):
    """"""
    # BEWARE: Don't do it this way! If you set all the classes,
    # it makes it more difficult to tweak just the styles you
    # want -- remember that some widgets have multiple classes
    # assigned to them, e.g., the end time widget has these set:
    #   class:title-normal-line class:title-normal class:title-end-line class:title-end
    # and PTK assigns styles from left to right, stacking them, so if
    # all four of those classes are assigned a style, the user would
    # have to set title-end to override the style, because setting
    # something to the left, like title-normal, would just get
    # overridden by styles listed after it. (Meaning, if you call
    # this function and assigns a value to all styles, it makes the
    # more generic classes, like title-normal, sorta meaningless to
    # have around. And might confuse the user when they set it and
    # wonder why it doesn't change anything.)
    # MAYBE/2020-04-21: (lb): I want to delete this function; but
    # I also want to be reminded later not to do this again. Give
    # me a few releases, then I'll probably nix this.
    assert False  # Abandoned!

    styling['streamer'] = style
    # (lb): I cannot decide if I like the streamer bold or not.
    styling['streamer'] += ' bold'

    styling['streamer-line'] = style

    # Set all the title-* and value-* values,
    #   title-normal through value-tags-line.
    for prefix in ('title', 'value'):
        for part in (
            'normal',
            'focus',
            'duration',
            'start',
            'start-focus',
            'end',
            'end-focus',
            'activity',
            'category',
            'tags',
        ):
            for suffix in ('', '-line'):
                class_name = '{}-{}{}'.format(prefix, part, suffix)
                styling[class_name] = style

    styling['blank-line'] = style

    styling['content-fact'] = style
    styling['content-help'] = style
    styling['interval-gap'] = style
    styling['unsaved-fact'] = style

    styling['footer'] = style
    styling['footer-fact-id'] = style


# ***

def light():
    styling = default()
    # (lb): I originally set all styles the same, but that makes customizing
    # difficult and tedious. So use the lowest-ordered, most universal class
    # of them all, and set class:label to the base color for this style.
    #   NOPE: _stylize_all_one(styling, 'bg:#FFFFFF #000000')
    styling['label'] = 'bg:#FFFFFF #000000'

    # FIXME/2020-04-21: See night(): Add some default colors for things.
    #  set_header_tag_parts_style(styling)
    #  set_header_facts_diff_style(styling)
    #  set_factoid_parts_style(styling)

    return styling


# ***

def night():
    def _night():
        styling = default()
        # See comment in light(). Use lowest-ordered class to set common style color.
        #   NOPE: _stylize_all_one(styling, 'bg:#000000 #FFFFFF')
        styling['label'] = 'bg:#000000 #FFFFFF'
        set_header_tag_parts_style(styling)
        set_header_facts_diff_style(styling)
        set_factoid_parts_style(styling)

        # Fact.description background when showing help.
        # https://en.wikipedia.org/wiki/International_orange
        styling['content-help'] = 'bg:#F04A00 #000000'

        return styling

    # FIXME: (lb): Devise similar #styling for 'light'.

    def set_header_tag_parts_style(styling):
        # (lb): Did I pick these color when testing, to be jarring and noticeable?
        # Should smooth these out a bit.
        # Note that you can use either value-tag-# for value-tag-label (to style
        # hash mark separately from tag); or you can use value-tags to do both.
        # The value-tag-# and value-tag-label take precedence.
        # Note: User can override color easily -- just specify a different one --
        # but remember to nobold/noitalic/nounderline as desired.
        #   https://pygments.org/docs/styles/
        # For help testing:
        #   styling['value-tags'] = 'fg:#0000FF bold italic'
        #   styling['value-tag-#'] = 'fg:#C6C6C6 underline'
        #   styling['value-tag-label'] = 'fg:#D7FF87 underline'
        styling['value-tags'] = 'fg:#D7FF87 underline'

    def set_header_facts_diff_style(styling):
        # The *-raw styles are sent to ansi_escape_room's color() and attr() lookups.
        # - They are used when not running the interactive editor.
        # The *-ptk styles are inserted into Python Prompt Toolkit (style, tuples, ).
        # - These styles are used in the interactive editor's header area.
        # Styles for the 'before' Fact parts -- from before user edited it.
        styling['value-diff-old-raw'] = 'spring_green_3a'
        spring_green_3a = '00AF5F'
        styling['value-diff-old-ptk'] = (
            'fg:#{} nobold noitalic nounderline'.format(spring_green_3a)
        )
        # Styles for the 'after' Fact parts -- edits ready to be saved.
        styling['value-diff-new-raw'] = 'light_salmon_3b, bold, underlined'
        light_salmon_3b = 'D7875F'
        styling['value-diff-new-ptk'] = 'fg:#{} bold underline'.format(light_salmon_3b)

    def set_factoid_parts_style(styling):
        styling['factoid-pk'] = 'grey_78'
        styling['factoid-act@gory'] = 'cornflower_blue, bold, underlined'
        styling['factoid-#'] = 'grey_78'
        styling['factoid-tag'] = 'dark_olive_green_1b'
        styling['factoid-#tag'] = 'underlined'
        styling['factoid-start'] = 'sandy_brown'
        styling['factoid-end'] = 'sandy_brown'
        styling['factoid-at'] = 'grey_85'
        styling['factoid-to'] = 'grey_85'
        styling['factoid-duration'] = 'grey_78'

    return _night()


# ***

def color():
    styling = night()

    styling['streamer'] = 'fg:#5F5FFF bold'
    # styling['streamer-line'] = ...

    # styling['title-normal'] = ...
    #  through
    # styling['value-focus-line'] = ...

    # styling['blank-line'] = ...

    # Default Fact.description frame background.
    styling['content-fact'] = 'bg:#9BC2C2 #000000'
    # Fact.description background when showing help.
    styling['content-help'] = 'bg:#66AAAA #000000'
    # Other contextual Fact.description background colors.
    styling['interval-gap'] = 'bg:#AA6C39 #000000'
    styling['unsaved-fact'] = 'bg:#D0EB9A #000000'

    # styling['footer'] = ...
    # styling['footer-fact-id'] = ...

    return styling

