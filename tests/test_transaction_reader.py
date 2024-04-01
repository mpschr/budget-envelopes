#!/usr/bin/env python

"""Tests for `budget_envelopes` package."""


import pytest

from budget_envelopes.transactions_reader import TransactionsReader


class TestTransactionReader:
    """Tests that budget reader is reading budget files correctly."""

    def test_csvtranscations(self):
        """Test the CLI."""

        reader = pytest.helpers.get_transactions_car()
        df = reader.get_statements()

        # input date is '11/10/2023 18:03' in US format (November 10th)
        assert df.loc[0].date.day == 10 and df.loc[0].date.month == 11
        assert df.loc[0].envelope == "Car"

    def test_jsontransactions(self):
        reader = pytest.helpers.get_transactions_petstore()
        df = reader.get_statements()
        assert df.shape[0] == 15  # 5 transactions over 3 envelope hierarchies

    # def test_wrong_envelope_string(self):
    #     reader = pytest.helpers.get_transactions_petstore(envelope_field = 'KK')
    #     df = reader.get_statements()
    #     assert df.shape[0] == 5 # 5 transactions over 1 hierarchy (top-level, because no envelope found)

    def test_different_date_fields(self):
        reader_bookingdate = pytest.helpers.get_transactions_petstore(
            date_field=["bookingdate"]
        )
        reader_analysisdate = pytest.helpers.get_transactions_petstore(
            date_field=["analysisdate", "transactiondate"]
        )

        bookingdates = reader_bookingdate.get_statements().date.unique().tolist()
        analysisdates = reader_analysisdate.get_statements().date.unique().tolist()

        assert bookingdates[0].day == 7
        assert analysisdates[0].day == 6

        assert analysisdates[2].day == 1 and analysisdates[2].month == 7


if __name__ == "__main__":
    pass
