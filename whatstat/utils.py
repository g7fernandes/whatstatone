from typing import List, Dict, Any, Iterable, Union
from datetime import datetime, timedelta
import unicodedata
import re
import sys


def get_dates(start: datetime, final: datetime) -> List[datetime]:
    start = datetime(start.year, start.month, start.day)
    final = datetime(final.year, final.month, final.day)
    return [start + timedelta(days=d)
            for d in range((final - start + timedelta(days=1)).days)]


def require_input(question: str,
                  options: Dict[str, Any],
                  case_sensitive: bool = True) -> Any:
    '''require_input
    Requests input from the user from a set of options. If an nonexistent
    option is chosen, then it will ask again. The option will map to a return
    according to the dict. Case insensitive.

    Inputs:
    ------
    question : str
        String with the request to be displayed.
    options : dict[str, Any]
        If the input maches the key, the value is returned.

    Returns:
    --------
    valid_answer : Any
        Value of the dict of the maching key
    '''

    valid_answer = ''
    while not valid_answer:
        answer = input(question)
        if case_sensitive:
            valid_answer = options.get(answer, '')
        else:
            for k, v in options.items():
                if k == answer:
                    valid_answer = v
                    break
    return valid_answer

# remove control chars


all_chars = (chr(i) for i in range(sys.maxunicode))
categories = {'Cc', 'Cf'}
control_chars = ''.join(
    c for c in all_chars if unicodedata.category(c) in categories)
control_char_re = re.compile('[%s]' % re.escape(control_chars))


def remove_control_chars(s: str) -> str:
    return control_char_re.sub('', s)


def log2console(s: str):
    sys.stdout.write(f'{s}')


def iso8601_to_datetime(date: str):
    date_list = [int(d) for d in date.split('-')]
    return datetime(year=date_list[0],
                    month=date_list[1],
                    day=date_list[2])


def date2int(date: datetime) -> int:
    return (date.year * 10**6
            + date.month * 10**4
            + date.day * 10**2
            + date.hour)


def get_different_key(keys: List[Any],
                      structure: Iterable) -> Union[Any, List[Any]]:

    different = []
    if isinstance(structure, dict):
        structure = structure.keys()
    for item in structure:
        if item not in keys:
            different.append(item)
    return different
