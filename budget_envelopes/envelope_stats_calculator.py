from budget_envelopes.transactions_reader import TransactionsReader
from budget_envelopes.budget_reader import BudgetReader
import logging
import warnings

# Suppress FutureWarning messages
warnings.simplefilter(action='ignore', category=FutureWarning)

import pandas
FIRST_MONTH = 'first_month'

class EnvelopeStatsCalculator(object):

    def __init__(self, *args, **kwargs) -> None:

        if FIRST_MONTH in kwargs:
            self._first_month = kwargs[FIRST_MONTH]
        self._last_month = None
        self._budget_months = None
        self._transactions = None
        self.stats = None
        self.budgets = None
        self._processed_budgets = [] 

    def add_budgets(self, budgetreader : BudgetReader):
        print(f'adding budgets {budgetreader.budgets_filename}')
        if budgetreader.budgets_filename in self._processed_budgets:
            logging.debug('not allowing reading same file twice')
            return
        if self.budgets is None:
            self.budgets = budgetreader.budgets
        else:
            self.budgets = pandas.concat([self.budgets,budgetreader.budgets]).groupby(['envelope','month']).sum(min_count=1)
            #print(self.budgets)
        self._processed_budgets.append(budgetreader.budgets_filename)

    def add_transactions(self, transactions : TransactionsReader):

        new_statements = transactions.get_statements()

        new_statements.envelope = new_statements.envelope.fillna('NOT SET')
        new_statements = new_statements.drop('need',axis=1).dropna() ## todo: fix it correctly
        new_statements['month'] = new_statements['date'].apply(lambda s: s[0:7])

        if self._transactions is None:
            self._transactions = new_statements
        else:
            self._transactions = pandas.concat([self._transactions, new_statements])

        logging.info(f"added {new_statements.shape[0]} transactions. Now containing a total of {self._transactions.shape[0]}")
    
    def _propagate_budgets(self, gdf):
        gdf.budget = gdf.budget.ffill().bfill()
        return gdf.fillna(0)


    def _calc_monthly_states(self, gdf):
        gdf = self._verify_all_months_in_data(gdf)

        gdf = self._propagate_budgets(gdf)

        gdf = self._apply_adjustments(gdf)

        gdf = gdf.query(f'month >= "{self._first_month}"')
        gdf.loc[:,'difference'] = gdf.budget - gdf.amount
        gdf.loc[:,'cumsum'] = gdf.difference.cumsum()
        gdf.loc[:,'carryover'] = gdf.difference.shift(1).cumsum()
        return gdf

    def _apply_adjustments(self, gdf):
        gdf.budget = gdf.fillna(0).apply(lambda r: r.budget + r.adjustment,axis=1,result_type="expand")
        gdf.rename(columns={'adjustment': 'adjusted'})

        return gdf

    def _verify_all_months_in_data(self, gdf):

        for v in self._budget_months:
            if v not in gdf.month.values:
                r = gdf.iloc[-1]
                r.month = v
                r.amount = pandas.NA
                r.adjustment = pandas.NA
                r.budget = pandas.NA
                gdf = pandas.concat([gdf,r.to_frame().T])
                gdf = gdf.sort_values('month')
        return gdf
    
    def get_envelope_stats(self) -> pandas.DataFrame:

        if self._first_month is None:
            self._first_month = '2022-09' ##TODO: CALCULATE WHICH WOULD BE THE FIRST MONTH
        
        self._update_budget_months() 

        monthly_stats =  self._transactions.query(f'month >= "{self._first_month}"').groupby(['envelope','month']).agg({'amount':'sum'}).sort_index()
        joined = self.budgets.join(monthly_stats,how='outer')

        envelope_development = joined.reset_index().groupby('envelope').apply(self._calc_monthly_states)
        envelope_development['state_month'] = envelope_development['difference'].round()
        envelope_development['state'] = envelope_development['cumsum'].round()

        return envelope_development[['envelope','month','budget','adjustment','state_month','state','carryover']].query('budget>0').set_index(['envelope','month']).sort_index()


    def _update_budget_months(self) -> None:
        self._last_month = self._transactions.month.max()
        self._budget_months = []

        min_year,min_month = [int(x) for x in self._first_month.split('-')]
        all_months = [self._first_month]
        current_month = min_month
        current_year = min_year

        while all_months[-1] != self._last_month:
            current_month += 1
            if current_month > 12:
                current_year += 1
                current_month = 1
            
            current_month_string = f'{current_year}-{str(current_month).zfill(2)}'
            all_months.append(current_month_string)
        self._budget_months = all_months        
        logging.info(f"Months to be considered are {self._budget_months}")
        
        

