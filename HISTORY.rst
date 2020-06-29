#######
History
#######

.. |dob| replace:: ``dob``
.. _dob: https://github.com/tallybark/dob

.. |dob-bright| replace:: ``dob-bright``
.. _dob-bright: https://github.com/tallybark/dob-bright

.. :changelog:

1.2.4 (2020-06-29)
==================

- Change ownership to ``github.com/tallybark``.

1.2.3 (2020-06-18)
==================

- Bugfix: Repair report issues exposed by upstream release testing.

1.2.2 (2020-06-18)
==================

- Feature: New 'journal' format shows ledger-style report.

  - Including sparklines and tag frequencies, e.g.::

      $ dob report
      Fri Jun 12  8.3 hours  ████▌    Sleep & Offline@Sleep
                  2.5 hours  █▍       Development@Tally Bark  #dob(5)

- Feature: Add JSON output format.

  - E.g., ``dob find --since yesterday --json``.

- Feature: Add markup-related output formats: html, mediawiki, rst, etc.

  - E.g., ``dob find --since 'last week' --rst``.

- Feature: Replace broken output truncate option with width option.

  - Also changes Factoid report to default to compact view (no blank
    lines) when width is used.

    - E.g., ``dob find --since 'last week' --factoid --width 110``.

- Improve: Align columns better in table formatted report.

  - E.g., align 'duration' column on decimal places, and right-align
    other number columns.

- Improve: Show hidden config options when requested directly.

  - E.g., ``dob config dump foo bar``.

- Config: New option, ``term.row_limit``, to improve dob-list experience.

  - This avoids overwhelming the terminal with too much output, unless
    the user explicitly asks for it.

1.2.1 (2020-04-26)
==================

- Packaging: Update dependency versions to pickup library changes.

1.2.0 (2020-04-26)
==================

- Bugfix: Config settings path shows incorrectly when displaying errors.

1.1.1 (2020-04-25)
==================

- Bugfix: ``dob edit`` fails when no config, rather than printing message.

  - Also affects other commands that require the config.

  - E.g., this happens if the user has not called ``dob init``.

    In other words, this affects new users.

- Bugfix: Config file errors crash dob.

  - But rather than just catch one error, print it, and exit,
    collect all errors, print them all, and then just keep chugging,
    choosing to use default values rather then exiting.

1.1.0 (2020-04-20)
==================

- Improve: Option to exclude section column from config table.

- Improve: Do not assume ASCII table width.

- UX: Change difficult to read 'red' warning text to 'yellow'.

  (Though really should be made configurable. Yellow works
  better on a dark background.)

- Harden: Prevent stylize from failing on user input.

- API: Rename to avoid confusion/match other usage: ``stylit`` → ``rules``.

- Library: Refactor, Relocate, and DRY work.

1.0.10 (2020-04-17)
===================

- Bugfix: ``dob config update`` command broken.

1.0.9 (2020-04-13)
==================

- API: New method to refresh "now".

1.0.8 (2020-04-12)
==================

- API: Pass Click context to post_processor handler.

1.0.7 (2020-04-09)
==================

- Bugfix: Allow Unicode characters in config values.

- Improve: Allow config to be reloaded, to support plugin config.

1.0.6 (2020-04-08)
==================

- Harden: Catch and report config file syntax error.

1.0.5 (2020-04-01)
==================

- Bugfix: Send package name to get_version, lest nark use its own.

1.0.4 (2020-04-01)
==================

- Refactor: DRY: Use new library get_version.

1.0.3 (2020-03-31)
==================

- UX: Fix help text indentation.

1.0.2 (2020-03-30)
==================

- DX: Process improvements.

1.0.0 (2020-03-30)
==================

- Booyeah: Inaugural release (spin-off from |dob|_).

