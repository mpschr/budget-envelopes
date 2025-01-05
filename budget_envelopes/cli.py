"""Console script for budget_envelopes."""
import sys

print(sys.path)
import random
import string
import click
import json
from .plot import plot_month
from .budget_reader import BudgetReader
from .envelope_stats_calculator import EnvelopeStatsCalculator
from .transactions_reader import TransactionsReader
import logging
import pandas
from datetime import datetime


logging.basicConfig(encoding="utf-8", level=logging.DEBUG)
_current_month = str(datetime.today())[0:7]

@click.command()
@click.option(
    "--budgets",
    "-b",
    default=None,
    help="Path to budgets csv file (fixed format)",
    multiple=True,
)
@click.option(
    "--transactions",
    "-t",
    default=None,
    help="Path to file including transactions in either csv or json format. Json should be an array of objects.",
    multiple=True,
)
@click.option(
    "--amount-field",
    "-$",
    help="The field which supplying the amount of the transactions",
)
@click.option(
    "--date-field",
    "-D",
    multiple=True,
    help="The field supplying the date of the transaction. Can be supplied multiple times in order of priority (e.g. transaction date, booking date)",
)
@click.option(
    "--envelope-field",
    "-E",
    help="Field supplying the envelope (category) from which the money is drawn or put into. Must match categories in budgets-file",
)
@click.option(
    "--debit-flag-field",
    help="Field supplying the debit/credit flag. Also supply --debit-flag",
)
@click.option(
    "--debit-flag",
    help="Content of --debit-flag-field when transaction is a debit transaction. Otherwise credit transaction assumed.",
)
@click.option(
    "--first-month",
    help="Supply from which month the transctions and budgets should be calculated forwards. The format is '2023-05'",
)
@click.option(
    "--last-month",
    help=f"Supply from which month the transctions and budgets should be calculated forwards. The format is '{_current_month}'." +
    f" Default value is current Month ({_current_month})",
    default=_current_month
)
@click.option(
    "--output-file",
    "-o",
    default="data/envelope-stats.json",
    help="Output file name for .json file",
)
@click.option(
    "--extra-files",
    "-x",
    is_flag=True,
    help = 'Stores multiple extra files along the envelope-stats.json:\n' +
    'envelope-stats-history.json: Monthly development history of the envelopes' + 
    'envelope-stats-aggregated.json: Yearly aggregation of the envelopes' +
    'envelope-stats.png: A somewhat weird plot of the current state.' 
)
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
    output_file,
    debit_flag_field=None,
    debit_flag=None,
    session=None,
    first_month=None,
    last_month=None,
    extra_files=False
):
    """Console script for budget_envelopes."""
    click.echo(
        "Replace this message by putting your code into " "budget_envelopes.cli.main"
    )

    if session is None:
        session = "".join(random.choices(string.ascii_uppercase + string.digits, k=15))
        #logging.info(session)

    esc = EnvelopeStatsCalculator(first_month=first_month, last_month=last_month)

    for bfile in budgets:
        budgetreader = BudgetReader(filename=bfile)
        esc.add_budgets(budgetreader)

    for f in transactions:
        reader = TransactionsReader(
            filename=f,
            amount_field=amount_field,
            date_field=date_field,
            envelope_field=envelope_field,
            debit_flag_field=debit_flag_field,
            debit_flag=debit_flag,
            session=session,
        )

        esc.add_transactions(reader)

    ## write output files
    stats = esc.get_envelope_stats()
    stats_json = stats.query(f"month == '{last_month}'").reset_index().to_dict("records")

    if extra_files == True:
        write_json_current_state(output_file, stats_json)
        write_history_and_aggregation_csvs(output_file, stats)    
        make_plot(output_file, last_month)

def write_history_and_aggregation_csvs(output_file, stats):
    
    # aggregation csv
    stats.reset_index().to_csv(output_file.replace(".json", "-history-monthly.csv"))

    stats.reset_index().assign(year=lambda df: df.month.str[:4])\
        .groupby(['envelope','year']).agg({
        'budget': sum,
        'adjustment': sum,
        'state': 'last'
    })\
    .sort_values(['year','envelope']).to_csv(output_file.replace(".json", "-aggregated.csv"))

def write_json_current_state(output_file, stats_json):
    with open(output_file, "w") as o:
        json.dump(stats_json, o, indent=4)
        logging.info(
            f"envelope stats of {len(stats_json)} envelopes written to file {output_file}"
        )


def make_plot(output_file, last_month):
    logging.getLogger("matplotlib").setLevel(logging.ERROR)
    logging.getLogger("PIL").setLevel(logging.ERROR)

    envelopes = pandas.read_json(output_file).sort_values("envelope", ascending=False)
    envelopes_currentmonth = envelopes.loc[envelopes.month == last_month]
    logging.debug("Plotting month " + envelopes_currentmonth.month.unique())
    plot_month(envelopes_currentmonth, output_file.replace(".json", ".png"))

    for month in envelopes.loc[envelopes.month != envelopes.month.max()].month.unique():
        plotfilename = output_file.replace(".json", f"-{month}.png")
        plot_month(envelopes.loc[envelopes.month == month], plotfilename)
        logging.info(
            f"envelope stats for month {month} envelopes written to file {plotfilename}"
        )


if __name__ == "__main__":
    sys.exit(main_cli())  # pragma: no cover
