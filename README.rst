================
Budget Envelopes
================


This python package is an implementation of the `envelope budget system`_.

.. _envelope budget system: https://letmegooglethat.com/?q=envelope+budget+system

In other words, when supplied with target budgets (envelope start balances) and 
categorised transactions (money drawn from envelopes), this software can be run via cli, to 
calculate what the envelope balances are taking into account the expenses and the set budgets.


Installation
-------------

**Disclaimer**: This library has been written to meet personal needs and is 
thoroughly **not** tested. In any case of interest, I am glad to assist, improve documentation and accept pull requests.

Via poetry: :code:`poetry install`

Via pip: :code:`pip install`

Features
--------

Done:

* Reads transactions from file in custom formats (see CLI options: :code:`budget-envelopes --help`)
   * Example JSON-transactions & example csv-transactions. See `examples/`
* Reads budgets from file in specific format (see example file :code:`examples/envelope_budget.csv`)
   * Supply budgets indicating the budgeting period as 
      * month: :code:`m`
      * quarter: :code:`q`
      * half-year: :code:`h`
      * year:  :code:`y`
* Adjustments: One-off adjustments and transfer between envelopes (see example file :code:`examples/envelope_adjustments.csv`)
   * Adjust a budget for a single month 
      * one-off entries: :code:`o`
      * envelope-transfers entries: :code:`t`
* Envelope carryovers to next month
* Output envelope stats and plot
* For home assistant integration see the `budgetenvelope-homeassistant`-repository

Todo:

* proper testing (surpriiiiise!). Available tests probablyl don't work anymore
  * Pytest is set up.
* Proper visualisation in homeassistant
* Explain envelope_budget.csv and envelope_adjustments.csv better  

Command line options:
--------------------------------

see also * Documentation: http://budget-envelopes.rtfd.io

.. image:: https://readthedocs.org/projects/budget-envelopes/badge/?version=latest
        :target: https://budget-envelopes.readthedocs.io/en/latest/?version=latest
        :alt: Documentation Status

.. code-block:: bash

        > budget-envelopes --help
        
        Usage: budget-envelopes [OPTIONS]

        Console script for budget_envelopes.

        Options:
        -b, --budgets TEXT         Path to budgets csv file (fixed format)
        -t, --transactions TEXT    Path to file including transactions in either csv
                                or json format. Json should be an array of
                                objects.
        -$, --amount-field TEXT    The field which supplying the amount of the
                                transactions
        -D, --date-field TEXT      The field supplying the date of the transaction.
                                Can be supplied multiple times in order of
                                priority (e.g. transaction date, booking date)
        -E, --envelope-field TEXT  Field supplying the envelope (category) from
                                which the money is drawn or put into. Must match
                                categories in budgets-file
        --debit-flag-field TEXT    Field supplying the debit/credit flag. Also
                                supply --debit-flag
        --debit-flag TEXT          Content of --debit-flag-field when transaction is
                                a debit transaction. Otherwise credit transaction
                                assumed.
        --first-month TEXT         Supply from which month the transctions and
                                budgets should be calculated forwards. The format
                                is '2023-05'
        -o, --output-file TEXT     Output file name for .json file
        -S, --session TEXT         When adding multiple files per CLI, use a session
                                string that ties the calls together
        --help                     Show this message and exit.




Credits
-------

- This package was created with poetry
- Docs tutorials: 
  - https://eikonomega.medium.com/getting-started-with-sphinx-autodoc-part-1-2cebbbca5365
  - https://leanmind.es/en/blog/how-to-publish-your-python-project-documentation-on-read-the-docs/


Other blabla's
---------------

.. image:: https://img.shields.io/pypi/v/budget_envelopes.svg
        :target: https://pypi.python.org/pypi/budget_envelopes

.. image:: https://img.shields.io/travis/mpschr/budget_envelopes.svg
        :target: https://travis-ci.com/mpschr/budget_envelopes



* Free software: MIT license
