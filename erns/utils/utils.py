# ///////////////////////////////////////////////////////////////////////////////
# FILE: utils.py
# AUTHOR: David Ruvolo
# CREATED: 2023-06-13
# MODIFIED: 2023-06-13
# PURPOSE: misc utils
# STATUS: stable / ongoing
# PACKAGES: **see below**
# COMMENTS: NA
# ///////////////////////////////////////////////////////////////////////////////

import re
import copy
from datetime import datetime
import pytz


def flatten_data(data: list = None, col_patterns: str = None):
    """Flatten dataset by column

    :param data: recordset containing nested data (objects and arrays)
    :type data: recordset (i.e.,list of dictionaries)

    :param col_patterns: names of the nested keys that contain the data to extract
      that are formatted as a re search pattern (key1|key2|keyN)

    :returns: recordset without nested data
    :rtype: recordset
    """
    new_data = copy.deepcopy(data)
    for row in new_data:
        if '_href' in row:
            del row['_href']
        for column in row.keys():
            if isinstance(row[column], dict):
                if bool(row[column]):
                    col_match_dict = re.search(
                        col_patterns, ','.join(row[column].keys()))
                    if bool(col_match_dict):
                        row[column] = row[column][col_match_dict.group()]
                    else:
                        print(
                            f'Variable {column} is type "dict", but no target column found')
                else:
                    row[column] = None
            if isinstance(row[column], list):
                if bool(row[column]):
                    values = []
                    for nestedrow in row[column]:
                        col_match_list = re.search(
                            col_patterns, ','.join(nestedrow.keys()))
                        if bool(col_match_list):
                            values.append(nestedrow[col_match_list.group()])
                        else:
                            print(
                                f'Variable {column} is type "list", but no target column found')
                    if bool(values):
                        row[column] = ','.join(values)
                else:
                    row[column] = None
    return new_data


def print2(*args):
    """Print message with timestamp
    :param *args: one or more strings containing a message to print
    :type *args: str

    :returns: a message with a timestamp
    :rtype: str
    """
    msg = ' '.join(map(str, args))
    time = timestamp(fmt='%H:%M:%S.%f')[:-2]
    print(f"[{time}] {msg}")


def timestamp(tz='Europe/Amsterdam', fmt='%Y-%m-%d'):
    """Get the time of the user's timezone and desired format

    :param tz: the timezone to format time to
    :param tz: str

    :param fmt: time format pattern

    :returns: current datetime based on timezone
    :rtype: str
    """
    return datetime.now(tz=pytz.timezone(tz)).strftime(fmt)
