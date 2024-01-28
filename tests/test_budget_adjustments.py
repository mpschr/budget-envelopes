#!/usr/bin/env python

"""Tests for `budget_envelopes` package."""


import unittest
from click.testing import CliRunner

from budget_envelopes.budget_reader import BudgetReader



class TestBudgetAdjustment(unittest.TestCase):
    """Tests for `budget_envelopes` package."""



    def test_budgetadjustments(self):
        """Test the CLI."""

        budget_reader = BudgetReader(filename='tests/budget_adjustments.csv');

        print(budget_reader.budgets)


if __name__ == '__main__':
    unittest.main()
