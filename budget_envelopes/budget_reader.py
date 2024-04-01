"""Main module."""
import pandas
import logging

logging.basicConfig(encoding="utf-8", level=logging.DEBUG)

FILENAME = "filename"


class BudgetReader(object):
    def __new__(cls, *args, **kwargs):
        if cls == BudgetReader:
            # Factory class has been instantiated: enter if in base class factory mode
            if kwargs["filename"].endswith(".json"):
                return super().__new__(JSONBudgetReader)
            elif kwargs["filename"].endswith(".csv"):
                return super().__new__(CSVBudgetReader)
            else:
                raise Exception("Budget-input: Either .json or .csv-file needed.")
        else:
            # one of the factory products has been instantiated directly
            instance = super().__new__(cls)
            return instance

    def __init__(self, *args, **kwargs):
        self.budgets = None
        self.budgets_filename = kwargs["filename"]
        self._read_budgets(kwargs["filename"])

    def _read_budgets(self, filename):
        # abstract method
        raise NotImplementedError

    def _calc_parent_budgets(self, budgets: pandas.DataFrame) -> pandas.DataFrame:
        envelope_products = self._product_budgets(budgets).reset_index()
        hierarchy_adjusted = envelope_products.apply(
            self._duplicate_entry_for_parent_envelopes, axis=1
        )

        # return duplicated
        return (
            hierarchy_adjusted.explode("envelope")
            .groupby(["envelope", "month"])
            .agg(
                {
                    "budget": lambda x: x.sum(min_count=1),
                    "adjustment": lambda x: x.sum(min_count=1),
                }
            )
        )

    def _break_down_to_monthly_budgets(self, s: pandas.Series):
        if pandas.isnull(s.budget):
            s.budget = 0
        if s.period == "y":  ## budget for a year
            s["budget"] = round(s.budget / 12)
        if s.period == "h":  ## budget for half a year
            s["budget"] = round(s.budget / 6)
        elif s.period == "q":  ## budget for a quarter year
            s["budget"] = round(s.budget / 3)
        return s

    def _transform_transfers_to_oneoffs(
        self, adj: pandas.DataFrame
    ) -> pandas.DataFrame:
        # add a sign multiplicator array to transfer entries: [-1,1]. Fro all others simply a 1
        adj = adj.reset_index().assign(
            signmultiplicator=lambda df: df.period.apply(
                lambda v: [-1, 1] if v == "t" else [1]
            )
        )
        # split the transfer envelope names and explode them into two lines
        adj.envelope = adj.envelope.apply(lambda v: v.split("->"))
        adj = adj.explode(["envelope", "signmultiplicator"])
        # use signmultiplicator to mark the giving and receiving budget adjustment
        if adj.shape[0] > 0:
            adj.adjustment = adj.apply(
                lambda row: row.adjustment * row.signmultiplicator, axis=1
            )
        return (
            adj.replace("t", "o")
            .drop("signmultiplicator", axis=1)
            .set_index(["envelope", "month"])
        )

    ## make sure all envelopes and budgets are available for all specified months
    def _product_budgets(self, budgets: pandas.DataFrame) -> pandas.DataFrame:
        # make sure each possible index is listed only once (transfers lead to repeated index)
        budgets = budgets.groupby(["envelope", "month"]).sum(min_count=1)

        # create cross (product) index of motnhs and envelopes
        budget_months = budgets.reset_index("month").month.unique()
        budget_envelopes = budgets.reset_index("envelope").envelope.unique()
        productindex = pandas.MultiIndex.from_product(
            [budget_envelopes, budget_months], names=["envelope", "month"]
        )

        # fill missing values for budgets, but not adjustments
        productbudgets = budgets.reindex(productindex).sort_index()
        propagedbudgets = (
            productbudgets.reset_index()
            .groupby("envelope")
            .apply(lambda gdf: gdf.ffill().bfill())
            .set_index(["envelope", "month"])
        )
        productbudgets["budget"] = propagedbudgets.budget
        return productbudgets  # .set_index(['envelope','month'])

    ## add up budgets to the parent envelopes by
    ## duplicating each entry
    def _duplicate_entry_for_parent_envelopes(self, r: pandas.Series):
        hierarchy = r.envelope.split(":")
        parent_envelopes = [r.envelope]
        for _ in hierarchy[::-1]:
            hierarchy.remove(_)
            parent_envelope = ":".join(hierarchy)
            # if parent_envelope == "":
            #    parent_envelope = "TOTAL"

            parent_envelopes.append(parent_envelope)

        r.envelope = parent_envelopes
        return r


class CSVBudgetReader(BudgetReader):

    """
    CSV Reader class.
    Args:
        *args (list): list of arguments
        **kwargs (dict): dict of keyword arguments
    Attributes:
        self
    """

    def _read_budgets(self, filename):
        budgets = (
            pandas.read_csv(filename).set_index(["envelope", "month"]).sort_index()
        )

        # type 'o' (one-off) and 't' (transfer). 't' are converted into 'o'
        adjustments = budgets.query(f'period in ["o","t"]')
        adjustments = adjustments.rename(columns={"budget": "adjustment"})
        adjustments = self._transform_transfers_to_oneoffs(adjustments)
        # type 'y' (yearly), & 'q'
        budgets = budgets.query(f'period not in ["o","t"]')

        ## TODO detect contradicting budgets (same month and envelope)

        budgets.loc[:, "budget_input"] = budgets.budget

        # normalize budgets to monthly budgets
        budgets = budgets.apply(self._break_down_to_monthly_budgets, axis=1)
        # add adjustments (only monthly)
        budgets = budgets.join(adjustments.adjustment, how="outer")
        # sum up budgets over parent envelopes
        added_up_bugdets = self._calc_parent_budgets(budgets)
        self.budgets = added_up_bugdets


class JSONBudgetReader(BudgetReader):
    """
    JSON Reader class.
    Args:
        *args (list): list of arguments
        **kwargs (dict): dict of keyword arguments
    Attributes:
        self
    """

    def _read_transactions(self):
        """
        Function.
        """

        raise NotImplementedError()


if __name__ == "__main__":
    # pass
    budget_reader = BudgetReader(filename="data/budget_adjustments.csv")
    print(budget_reader.budgets)
