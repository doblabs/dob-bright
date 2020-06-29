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

import os
import platform
import tempfile

from gettext import gettext as _

import editor

from ..termio import dob_in_user_warning

__all__ = (
    'ask_edit_with_editor',
    'run_editor_safe',
)


# ***

def ask_edit_with_editor(controller, fact=None, content=''):
    def _ask_edit_with_editor():
        contents = prepare_contents(content)
        filename = temp_filename()
        return run_editor_safe(filename, contents)

    def prepare_contents(content):
        content = content if content else ''
        # # FIXME: py2 compatible? Or need to six.b()?
        # #contents = six.b(str(content))  # NOPE: Has problems with Unicode, like: ½
        # contents = text_type(content).encode()
        # FIXME/2020-01-26: (lb): Verify no longer an issue.
        contents = str(content).encode()
        return contents

    def temp_filename():
        tmpfile = tempfile.NamedTemporaryFile(
            prefix=prepare_prefix(),
            suffix=prepare_suffix(),
        )
        filename = tmpfile.name
        return filename

    def prepare_prefix():
        # Vim names the terminal with the file's basename, which is
        # normally meaningless, e.g., "tmprvapy77w.rst (/tmp)", but
        # we can give the randomly-named temp file a prefix to make
        # the title more meaningful.
        prefix = None
        if fact is not None:
            # (lb): Reminder that colon is not acceptable for Windows paths.
            #   (I originally had a ':' in the clock time here.)
            # E.g., "2018_04_07_1733_"
            timefmt = '%Y_%m_%d_%H%M_'
            if fact.start:
                prefix = fact.start.strftime(timefmt)
            elif fact.end:
                prefix = fact.end.strftime(timefmt)
        return prefix

    def prepare_suffix():
        # User can set a suffix, which can be useful so, e.g., Vim
        # sees the extension and set filetype appropriately.
        # (lb): I like my Hamster logs to look like reST documents!
        suffix = controller.config['term.editor_suffix'] or None
        return suffix

    return _ask_edit_with_editor()


# ***

def run_editor_safe(filename, contents=None):
    def _run_editor_safe():
        try:
            return run_editor()
        except Exception as err:
            msg = _('Unable to run $EDITOR: {}').format(str(err))
            dob_in_user_warning(msg)
            return ''

    def run_editor():
        if is_editor_set() or not running_windows():
            # If Linux and EDITOR not set, editor.edit runs Vim.
            return run_editor_normal()
        else:
            return run_editor_windows()

    def is_editor_set():
        try:
            return bool(os.environ['EDITOR'])
        except KeyError:
            return False

    def running_windows():
        return platform.system() == 'Windows'

    def run_editor_normal():
        # NOTE: You'll find EDITOR features in multiple libraries.
        #       The UX should be indistinguishable to the user.
        #       E.g., we could use click's `edit` instead of editor's:
        #
        #           click.edit(text=None,
        #                      editor=None,
        #                      env=None,
        #                      require_save=True,
        #                      extension='.txt',
        #                      filename=None)
        #
        #       Except that dob-viewer does not have click as a dependency.
        #
        # NOTE: Neither editor.edit nor click.edit appreciate arguments, e.g.,
        #       you might want to start Vim in insert mode and send cursor home:
        #
        #           export EDITOR="vim -c 'startinsert' -c 'norm! gg'"
        #
        #       but this'll crash (they treat the complete $EDITOR string as a
        #       path). (lb): But I'm not wrong expecting this! It works fine in
        #       other tools, e.g., `git commit -v` is perfectly happy with it.
        #
        #       As a work-around, you can put the command in an executable on
        #       PATH, e.g.,
        #
        #           echo -e '#!/bin/sh\nvim -c "startinsert" -c "norm! gg" "${@}"' \
        #               > ~/.local/bin/vim-wrap
        #           chmod 755 ~/.local/bin/vim-wrap
        #           export EDITOR="vim-wrap"
        #
        result = editor.edit(filename=filename, contents=contents)
        edited = result.decode()
        # Necessary?:
        #   edited = result.decode('utf-8')
        return edited

    def run_editor_windows():
        # NOTE: On Windows, EDITOR is not set by default, but neither is Vim, so
        #       editor.edit() will not work.
        #       - To set via PowerShell, try, e.g.,
        #           $Env:EDITOR = "notepad.exe"
        #       - In CMD.exe, use setx to set *persistent* variable (and then start
        #         another CMD prompt), e.g.,
        #           setx EDITOR "notepad.exe"
        # NOTE: There's a Windows-only os.startfile() that acts like double-clicking
        #       the file -- it opens the text file with the user's preferred editor --
        #       but it runs asynchronously. And we need to block. E.g., not this:
        #           os.startfile(filename, 'open')
        #       so just default to notepad, which will be installed. User should set
        #       EDITOR if they want to use a different text editor on Windows.
        with open(filename, 'wb') as temp_f:
            temp_f.write(contents)
        import subprocess
        subprocess.call(['notepad.exe', filename])
        with open(filename, 'r') as temp_f:
            edited = temp_f.read()
        return edited

    return _run_editor_safe()

