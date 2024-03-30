#!/usr/bin/env python

"""Tests for `budget_envelopes` package."""


import unittest

from budget_envelopes.budget_reader import BudgetReader
from budget_envelopes.envelope_stats_calculator import EnvelopeStatsCalculator

class TestBudgetAdjustment(unittest.TestCase):
    """Tests that budget reader is reading budget files correctly."""

    def test_budgetadjustments(self):
        """Test the CLI."""


        budget_reader = BudgetReader(filename='examples/envelope_adjustments.csv');
        # no budgets, only adjustments in this file
        assert budget_reader.budgets.budget.fillna(0).sum() == 0

        # total ('') sum of adjustment is 300 
        assert budget_reader.budgets.loc[''].adjustment.sum() == 300


    def test_budgetadjustments(self):
        """Test the CLI."""

        calculator = EnvelopeStatsCalculator()

        budgetsreader = BudgetReader(filename='examples/envelope_budgets.csv')
        adjustmentsreader = BudgetReader(filename='examples/envelope_adjustments.csv')
        calculator.add_budgets(budgetsreader)
        calculator.add_budgets(adjustmentsreader)
        # no budgets, only adjustments in this file

        # Health:Insurance,2023-01,h,2000,
        # 2000 / 12
        assert calculator.budgets.loc['Health:Insurance','2023-07'].budget == 333

        # Living:Power,2023-01,q,300,A bill every three months arrives
        # 300 / 4
        assert calculator.budgets.loc['Living:Power','2023-11'].budget  == 100

        # assert correct downcast of amounts
        assert calculator.budgets.loc['Household:Clothing','2023-01'].budget + \
        calculator.budgets.loc['Household:Groceries','2023-01'].budget + \
        calculator.budgets.loc['Household:Pets','2023-01'].budget == \
        calculator.budgets.loc['Household','2023-01'].budget

        # assert correct downcast of amounts
        assert calculator.budgets.loc['Household','2024-01'].budget - \
        calculator.budgets.loc['Household','2023-01'].budget  == 250

        # Budget + adjustment of Car in 2023-11
        assert calculator.budgets.loc['Car','2023-11'].sum() == 531

   

if __name__ == '__main__':
    unittest.main()
