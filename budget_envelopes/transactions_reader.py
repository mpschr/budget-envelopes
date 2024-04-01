"""Main module."""
import json
import pandas
import logging
import dateutil.parser as dateparser
import datetime 

logging.basicConfig(encoding="utf-8", level=logging.DEBUG)


AMT = "amount_field"
ENVELOPE = "envelope_field"
DATE = "date_field"
DEBIT_FLAG_FIELD = "debit_flag_field"
DEBIT_FLAG = "debit_flag"
FILENAME = "filename"
SESSION = "session"


class TransactionsReader(object):
    def __new__(cls, *args, **kwargs):
        if cls == TransactionsReader:
            # Factory class has been instantiated: enter if in base class factory mode
            if kwargs["filename"].endswith(".json"):
                return super().__new__(JSONTransactionsReader)            
            elif kwargs["filename"].endswith(".csv"):
                return super().__new__(CSVTransactionsReader)
            else:
                raise Exception("Transactions-input: Either .json or .csv-file needed.")            
        else:
            # one of the factory products has been instantiated directly
            return super().__new__(cls)

    def __init__(self, 
                 filename: str,
                 amount_field: str,
                 date_field: list,
                 envelope_field: str,
                 debit_flag_field : str = False,
                 debit_flag : str = None,
                 session : str = None,
                   *args, **kwargs):
        
        allowed_keys = set(
            [AMT, DATE, ENVELOPE, DEBIT_FLAG_FIELD, DEBIT_FLAG, FILENAME, SESSION]
        )
        self.__dict__.update((k, False) for k in allowed_keys)
        self.__dict__.update({
            FILENAME: filename,
            AMT: amount_field,
            DATE: date_field,
            ENVELOPE: envelope_field,
            DEBIT_FLAG_FIELD: debit_flag_field,
            DEBIT_FLAG: debit_flag,
            SESSION: session    
        })
        self.__dict__.update((k, v) for k, v in kwargs if k in allowed_keys)

        self._extracted_contents = None

        self._read_transactions()

    def get_statements(self) -> pandas.DataFrame:
        return self._extracted_contents

    def _read_transactions(self):
        raise NotImplementedError

    def extract_contents(self, jsoncontents: list[dict]):
        extracted_contents = []
        ignored_due_tue_date_count = 0

        for x in jsoncontents:
            # x is a transaction in json format
            x = pandas.Series(x).dropna().to_dict()

            # d is a dictionary where extracted infrmation is stored into
            d = {}
            
            self._extract_amount(x, d)
            self._extract_date(x, d)
            self._extract_envelope(x, d)

            # ignore bookings set for the future
            if d["date"] > datetime.date.today():
                ignored_due_tue_date_count += 1
                continue   
            if "date" not in d:
                logging.error(f"No Date found for {x}")
                continue

            extracted_contents.append(d)
            self.add_parent_envelopes(extracted_contents, d)

        logging.info(f"ignored {ignored_due_tue_date_count} transactions, set for future date")
        return extracted_contents

    def _extract_amount(self, source: dict, target: dict) -> None:
        # extract amount using the supplied AMT key
        target["amount"] = float(source[self.__dict__[AMT]])

        # adjust Credit/Debit with flag, if needed, using DEBIT_FLAG_FIELD & DEBIT_FLAG
        # e.g. Flag Field: BOOKINGTYPE , Debit Flag [String]: "DBT"
        if self.__dict__[DEBIT_FLAG_FIELD] != False:
            if source[self.__dict__[DEBIT_FLAG_FIELD]] != self.__dict__[DEBIT_FLAG]:
                target["amount"] = -target["amount"]

    def _extract_envelope(self, source: dict, target: dict) -> None: 
        # Extracts the envelope (category) of the source dict using the supplied ENVELOPE key
        try:
            target["envelope"] = source[self.__dict__[ENVELOPE]]
        except KeyError:
            target["envelope"] = ""

    def _extract_date(self, source: dict, target: dict) -> None:
        # Extracts the date of the source dict using the supplied DATE key
        for date in self.__dict__[DATE]:
            if date in source:
                target["date"] =  dateparser.parse(source[date]).date()
                ## valid date found no need to look at lower prio fields
                break

    def add_parent_envelopes(self, extracted_contents, d):
        try:
            hierarchy = d["envelope"].split(":")
        except AttributeError:
            print(d)
        while len(hierarchy) > 0:
            hierarchy.pop()
            parent_envelope = ":".join(hierarchy)
            dcopy = d.copy()
            dcopy["envelope"] = parent_envelope
            extracted_contents.append(dcopy)


class CSVTransactionsReader(TransactionsReader):

    """
    CSV Reader class.
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

        filepath = self.__dict__[FILENAME]
        with open(filepath, "r") as f:
            filecontents = pandas.read_csv(filepath)
            jsoncontents = filecontents.to_dict("records")

            extracted_contents = self.extract_contents(jsoncontents)
            self._extracted_contents = pandas.DataFrame(extracted_contents)
            del jsoncontents
            del filecontents


class JSONTransactionsReader(TransactionsReader):
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

        filepath = self.__dict__[FILENAME]
        with open(filepath, "r") as f:
            filecontents = f.readlines()
            jsoncontents = json.loads("".join(filecontents))

            extracted_contents = self.extract_contents(jsoncontents)
            self._extracted_contents = pandas.DataFrame(extracted_contents)
            del jsoncontents
            del filecontents
