#!/usr/bin/env python

"""Tests for `budget_envelopes` package."""
import pytest

from budget_envelopes.budget_reader import BudgetReader
from budget_envelopes.transactions_reader import TransactionsReader
from budget_envelopes.envelope_stats_calculator import EnvelopeStatsCalculator

@pytest.helpers.register
def get_envelope_adjustments() -> BudgetReader:
    return BudgetReader(filename='examples/envelope_adjustments.csv')

@pytest.helpers.register
def get_budgets() -> BudgetReader:
    return BudgetReader(filename='examples/envelope_budgets.csv')
    
@pytest.helpers.register
def get_transactions_car() -> TransactionsReader:
    return TransactionsReader(
        filename='examples/transactions-car.csv',
        amount_field='amount',
        date_field=['transactiontime-us'],
        envelope_field='category'
    )
        
@pytest.helpers.register
def get_transactions_petstore(date_field: list = ['bookingdate'], envelope_field = 'envelope') -> TransactionsReader:
    return TransactionsReader(
        filename='examples/transactions-petstore.json',
        amount_field='amount',
        date_field=date_field,
        envelope_field=envelope_field
    )

if __name__ == '__main__':
    pass
