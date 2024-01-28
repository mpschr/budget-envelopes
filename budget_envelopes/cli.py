"""Console script for budget_envelopes."""
import sys
import random
import string
import click
import json
from budget_envelopes.plot import plot_month
from budget_envelopes.budget_reader import BudgetReader
from budget_envelopes.envelope_stats_calculator import EnvelopeStatsCalculator
from budget_envelopes.transactions_reader import TransactionsReader
import logging
import pandas
from datetime import datetime


logging.basicConfig(encoding="utf-8", level=logging.DEBUG)


@click.command()
@click.option("--budgets","-b", default=None, help="Path to budgets csv file (fixed format)", multiple=True)
@click.option("--transactions", "-t", default=None, help="Path to file including transactions", multiple=True)
@click.option("--amount-field", "-$")
@click.option("--date-field", "-D", multiple=True)
@click.option("--envelope-field", "-E")
@click.option("--need-field", "-N")
@click.option("--debit-flag-field")
@click.option("--debit-flag")
@click.option("--first-month")
@click.option("--output-file",  "-o", default="data/envelope-stats.json", help="Output file name for .json file")
@click.option(
    "--session",
    "-S",
    help="When adding multiple files per CLI, use a session string that ties the calls together",
)
def main_cli(
    transactions,
    budgets,
    amount_field,
    envelope_field,
    date_field,
    need_field,
    output_file,
    debit_flag_field=None,
    debit_flag=None,
    session=None,
    first_month=None):
    """Console script for budget_envelopes."""
    click.echo(
        "Replace this message by putting your code into " "budget_envelopes.cli.main"
    )

    if session is None:
        session = "".join(random.choices(string.ascii_uppercase + string.digits, k=15))
        logging.info(session)

    esc = EnvelopeStatsCalculator(first_month=first_month)

    for bfile in budgets:
        budgetreader = BudgetReader(filename=bfile);
        esc.add_budgets(budgetreader)

    for f in transactions:
        reader = TransactionsReader(
            filename=f,
            amount_field=amount_field,
            date_field=date_field,
            envelope_field=envelope_field,
            need_field=need_field,
            debit_flag_field=debit_flag_field,
            debit_flag=debit_flag,
            session=session,
        )

        esc.add_transactions(reader)

    stats = esc.get_envelope_stats()#.drop_duplicates() ## todo: bug?
    month_now = f'{datetime.now().year}-{datetime.now().month:02d}'
    stats_json = stats.query(f"month == '{month_now}'").reset_index().to_dict('records')
    stats.reset_index().to_csv(output_file.replace('.json','.csv'))
    with open(output_file, "w") as o:
        json.dump(stats_json, o, indent=4)
        logging.info(f"envelope stats of {len(stats_json)} envelopes written to file {output_file}")

    make_plot(output_file)

def make_plot(output_file):

    logging.getLogger('matplotlib').setLevel(logging.ERROR)
    logging.getLogger('PIL').setLevel(logging.ERROR)


    envelopes = pandas.read_json(output_file).sort_values('envelope',ascending=False)
    envelopes_currentmonth = envelopes.loc[envelopes.month == envelopes.month.max()]
    plot_month(envelopes_currentmonth, output_file.replace('.json','.png'))

    for month in envelopes.loc[envelopes.month != envelopes.month.max()].month.unique():
        plotfilename = output_file.replace('.json', f'-{month}.png')
        plot_month(envelopes.loc[envelopes.month == month], plotfilename )
        logging.info(f"envelope stats for month {month} envelopes written to file {plotfilename}")



if __name__ == "__main__":
    sys.exit(main_cli())  # pragma: no cover
