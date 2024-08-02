"""
FILE: summarise_data.py
AUTHOR: David Ruvolo
CREATED: 2023-06-13
MODIFIED: 2024-08-02
PURPOSE: summarise data in the registry and prep for dashboard
STATUS: stable
PACKAGES: NA
COMMENTS: NA
"""

from os import path
import tempfile
from datetime import datetime
import csv
import re
import pytz
import molgenis.client as molgenis
from datatable import dt, f, as_type
import pandas as pd
import numpy as np


def timestamp(tz='Europe/Amsterdam', fmt='%Y-%m-%d'):
    """Get the time of the user's timezone and desired format

    :param tz: the timezone to format time to
    :param tz: str

    :param fmt: time format pattern

    :returns: current datetime based on timezone
    :rtype: str
    """
    return datetime.now(tz=pytz.timezone(tz)).strftime(fmt)


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


class Molgenis(molgenis.Session):
    """Molgenis EMX1 Python Client"""

    def __init__(self, *args, **kwargs):
        super(Molgenis, self).__init__(*args, **kwargs)
        self.file_api = f"{self._root_url}plugin/importwizard/importFile"

    def _dt_to_csv(self, path, datatable):
        """To CSV
        Write datatable object as CSV file

        @param path location to save the file
        @param data datatable object
        """
        data = datatable.to_pandas().replace({np.nan: None})
        data.to_csv(path, index=False, quoting=csv.QUOTE_ALL)

    def import_dt(self, pkg_entity: str, data):
        """Import Datatable As CSV
        Save a datatable object to as csv file and import into MOLGENIS using the
        importFile api.

        @param pkg_entity table identifier in emx format: package_entity
        @param data a datatable object
        @param label a description to print (e.g., table name)
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = f"{tmpdir}/{pkg_entity}.csv"
            self._dt_to_csv(filepath, data)
            with open(path.abspath(filepath), 'r', encoding='utf-8') as file:
                response = self._session.post(
                    url=self.file_api,
                    headers=self._headers.token_header,
                    files={'file': file},
                    params={'action': 'add_update_existing',
                            'metadataAction': 'ignore'}
                )
                if (response.status_code // 100) != 2:
                    print2('Failed to import data into',
                           pkg_entity, '(', response.status_code, ')')
                else:
                    print2('Imported data into', pkg_entity)
                return response


def flatten_dataset(data, col_patterns=None):
    """Flatten Dataset
    Flatten all nested attributes in a recordset based on a specific column names.

    @param data a recordset
    @param column string containing row headers to detect: "subjectID|id|value"
    @return a new recordset containing flattened data
    """
    new_data = list(data)
    for row in new_data:
        if '_href' in row:
            del row['_href']
        for column in row.keys():
            if isinstance(row[column], dict):
                if bool(row[column]):
                    col_match = re.search(
                        col_patterns, ','.join(row[column].keys()))
                    if bool(col_match):
                        row[column] = row[column][col_match.group()]
                    else:
                        print(
                            f'Variable {column} is type "dict", but no target column found')
                else:
                    row[column] = None
            if isinstance(row[column], list):
                if bool(row[column]):
                    values = []
                    for nestedrow in row[column]:
                        col_match = re.search(
                            col_patterns, ','.join(nestedrow.keys()))
                        if bool(col_match):
                            values.append(nestedrow[col_match.group()])
                        else:
                            print(
                                f'Variable {column} is type "list", but no target column found')
                    if bool(values):
                        row[column] = ','.join(values)
                else:
                    row[column] = None
    return new_data

# ///////////////////////////////////////////////////////////////////////////////

# ~ 0 ~
# Connect to database and retrieve data


print2('Connecting to database....')

# for local dev
# from dotenv import load_dotenv
# from os import environ
# load_dotenv()
# ernskin = Molgenis(environ['ERRAS_PROD_HOST'])
# ernskin.login(environ['ERRAS_PROD_USR'], environ['ERRAS_PROD_PWD'])

# for deployment
ernskin = Molgenis('http://localhost/api/', token='${molgenisToken}')

# ///////////////////////////////////////

print2('Pulling subject metadata....')

# get metadata
subjects_raw = ernskin.get(
    'skin_allSubject',
    attributes='ID_EUPID,dateBirth,biologicalSex,diseaseGroup,centre',
    batch_size=10000
)

subject_dt = flatten_dataset(subjects_raw, 'value_en|value|id')
subject_dt = dt.Frame(subject_dt)

# get stats
stats = ernskin.get('stats_stats')
stats_dt = dt.Frame(flatten_dataset(stats, col_patterns='name'))

# get healthcare providers
providers_dt = dt.Frame(ernskin.get('stats_dataproviders'))
del providers_dt['_href']

# ///////////////////////////////////////////////////////////////////////////////

# ~ 1 ~
# Summarise data by age

print2('Summarising data by age....')

# For now, use today's date as the default. This should be updated later
print2('Isolating date of birth and initialising recent date....')
age_dt = subject_dt[:, {
    'dateBirth': as_type(f.dateBirth, dt.Type.date32),
    'dateToday': as_type(timestamp(), dt.Type.date32)
}]

# calculate age: use .25 and round to 4 digits for specificity
print2('Calculating age....')
age_dt['age'] = dt.Frame([
    round(int((row[1] - row[0]).days) / 364.25, 4) if all(row) else None
    for row in age_dt[:, (f.dateBirth, f.dateToday)].to_tuples()
])

# bin data by age category and summarise data
print2('Binning age by age categories....')
age_df = age_dt.to_pandas()
age_bins = [0, 0.25, 1, 5, 13, 18, 40, 60, np.inf]
age_labels = [
    'Newborn',
    'Infant',
    'Todler',
    'Kids',
    'Teenagers',
    'Adults < 40',
    'Adults < 60',
    'Elderly persons',
]

age_df['bin'] = pd.cut(
    age_df['age'],
    bins=age_bins,
    labels=age_labels,
    right=False
)

# summarise by bin and update main dataset
print2('Summarising data by age category and updating stats dataset....')
age_dt = dt.Frame(age_df)
age_by_group = age_dt[:, dt.count(), dt.by(f.bin)]

for age_bin in age_by_group['bin'].to_list()[0]:
    stats_dt[
        f.label == age_bin, 'value'
    ] = age_by_group[f.bin == age_bin, 'count']

# ///////////////////////////////////////////////////////////////////////////////

# ~ 2 ~
# Summarise data sex at birth
print2('Summarising data by biological sex....')

# number of patients by `sex_at_birth_dt`
print2('Counting data by category....')
sex_at_birth_dt = subject_dt[:, dt.count(), dt.by(f.biologicalSex)]

# calculate percent for each record
print2('Calculating percentages....')
sex_at_birth_dt['total'] = sum(sex_at_birth_dt['count'].to_list()[0])

sex_at_birth_dt['rate'] = dt.Frame([
    round(row[0]/row[1], 2) if all(row) else 0
    for row in sex_at_birth_dt[:, (f.count, f.total)].to_tuples()
])

sex_at_birth_dt['id'] = dt.Frame([
    f"sex-{value.lower()}"
    for value in sex_at_birth_dt['biologicalSex'].to_list()[0]
])

print2('Updating stats dataset....')
for _id in sex_at_birth_dt['id'].to_list()[0]:
    stats_dt[f.id == _id, 'value'] = sex_at_birth_dt[f.id == _id, 'rate']

# ///////////////////////////////////////////////////////////////////////////////

# ~ 2 ~
# Summarise enrollment by disease group
print2('Summarising data by disease group....')

# get lookup table for disease group
print2('Pulling reference dataset for disease groups....')
diseases_dt = dt.Frame(ernskin.get('erras_diseasegroup'))[
    :, {'id': f.id, 'label': f.value}]
diseases_dt.key = 'id'


# summarise groups and merge labels
print2('Summarising by disease groups and merging labels....')
disease_groups_dt = subject_dt[:, dt.count(), dt.by(f.diseaseGroup)][
    :, {'id': f.diseaseGroup, 'value': f.count}
][:, :, dt.join(diseases_dt)]

disease_groups_dt['id'] = disease_groups_dt[:, 'enrollment-' + f.id]

print2('Updating stats datasets....')
for _id in disease_groups_dt['id'].to_list()[0]:
    stats_dt[f.id == _id, 'value'] = disease_groups_dt[f.id == _id, 'value']

# ///////////////////////////////////////////////////////////////////////////////

# ~ 3 ~
# Summarise submitted patients by centers
print2('Updating centers that have submitted data....')

centers_dt = subject_dt[:, dt.count(), dt.by(f.centre)]

for _id in centers_dt['centre'].to_list()[0]:
    providers_dt[f.alternativeIdentifier == _id, 'hasSubmittedData'] = True

# ///////////////////////////////////////////////////////////////////////////////

# ~ 4 ~
# Prepare summaries for data-highlights component
print2('Updating data highlights.....')

stats_dt[f.label == 'Patients', 'value'] = subject_dt.nrows

stats_dt[f.label == 'Member countries', 'value'] = dt.unique(
    providers_dt[f.hasSubmittedData, 'country']
).nrows

stats_dt[f.label == 'Healthcare providers', 'value'] = dt.unique(
    providers_dt[f.hasSubmittedData, 'code']
).nrows

# ///////////////////////////////////////////////////////////////////////////////

# ~ 2 ~
# import data into stats_stats
print2('Importing summarised datasets....')

ernskin.import_dt('stats_dataproviders', providers_dt)
ernskin.import_dt('stats_stats', stats_dt)

ernskin.logout()
