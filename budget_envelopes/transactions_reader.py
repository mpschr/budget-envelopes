"""Main module."""
import json
import sys; print(sys.version)
import pandas
import logging
logging.basicConfig(encoding='utf-8', level=logging.DEBUG)



AMT = 'amount_field'
ENVELOPE = 'envelope_field'
NEED = 'need_field'
DATE = 'date_field'
DEBIT_FLAG_FIELD = 'debit_flag_field'
DEBIT_FLAG = 'debit_flag'
FILENAME = 'filename'
SESSION = 'session'


class TransactionsReader(object):

    def __new__(cls, *args, **kwargs):

        if cls == TransactionsReader:
            #enter if in base class factory mode
            if kwargs['filename'].endswith('.json'):
                return JSONTransactionsReader(*args, **kwargs)
            if kwargs['filename'].endswith('.csv'):
                return CSVTransactionsReader(*args, **kwargs)
        else:
            #cls.__init__(cls)
            # return self (cls)
            instance = super().__new__(cls)
            return instance


    def __init__(self, *args, **kwargs):
        allowed_keys = set([AMT, DATE, ENVELOPE, NEED, DEBIT_FLAG_FIELD, DEBIT_FLAG, FILENAME, SESSION])
        self.__dict__.update((k, False) for k in allowed_keys)
        self.__dict__.update((k, v) for k, v in kwargs.items() if k in allowed_keys)

        self._extracted_contents = None

        self._read_transactions()


    def get_statements(self) -> pandas.DataFrame:
        return self._extracted_contents

    def _read_transactions(self):
        raise NotImplementedError

    def extract_contents(self, jsoncontents: list[dict]):
        extracted_contents = []

        for x in jsoncontents:

            x = pandas.Series(x).dropna().to_dict()

            d={}
            d['amount'] = float(x[self.__dict__[AMT]])

            for date in self.__dict__[DATE]:
                if date in x:
                    d['date'] = x[date]
                    break
            if 'date' not in d:
                logging.error(f'No Date found for {x}')
                continue

            try:
                d['envelope'] = x[self.__dict__[ENVELOPE]]
            except KeyError:
                d['envelope'] = ''

            if self.__dict__[DEBIT_FLAG_FIELD] != False:
                if x[self.__dict__[DEBIT_FLAG_FIELD]] != self.__dict__[DEBIT_FLAG]:
                    d['amount'] = -d['amount']

            try:
                d['need'] = x[self.__dict__[NEED]]
            except KeyError:
                pass

            extracted_contents.append(d)
            self.add_parent_envelopes(extracted_contents, d)
        return extracted_contents


    def add_parent_envelopes(self, extracted_contents, d):

        try:
          hierarchy = d['envelope'].split(':')
        except AttributeError:
            print(d)
        while len(hierarchy) > 0:       
            hierarchy.pop()
            parent_envelope = ':'.join(hierarchy)
            dcopy = d.copy()
            dcopy['envelope'] = parent_envelope
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
        with open(filepath, 'r') as f:
            filecontents = pandas.read_csv(filepath)
            jsoncontents = filecontents.to_dict('records')

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
        with open(filepath, 'r') as f:
            filecontents = f.readlines()
            jsoncontents = json.loads(''.join(filecontents))

            extracted_contents = self.extract_contents(jsoncontents)
            self._extracted_contents = pandas.DataFrame(extracted_contents)
            del jsoncontents
            del filecontents

