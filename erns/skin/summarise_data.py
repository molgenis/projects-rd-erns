#///////////////////////////////////////////////////////////////////////////////
# FILE: summarise_data.py
# AUTHOR: David Ruvolo
# CREATED: 2023-06-13
# MODIFIED: 2023-06-20
# PURPOSE: summarise data in the registry and prep for dashboard
# STATUS: stable
# PACKAGES: NA
# COMMENTS: NA
#///////////////////////////////////////////////////////////////////////////////

import molgenis.client as molgenis
from datatable import dt, f, as_type
from datetime import datetime
from os import path
import pandas as pd
import numpy as np
import tempfile
import pytz
import csv
import re

def today(tz='Europe/Amsterdam'):
  return datetime.now(tz=pytz.timezone(tz)).strftime('%Y-%m-%d')

class Molgenis(molgenis.Session):
  def __init__(self, *args, **kwargs):
    super(Molgenis, self).__init__(*args, **kwargs)
    self.fileImportEndpoint = f"{self._root_url}plugin/importwizard/importFile"
  
  def _print(self, *args):
    """Print
    Print a message with a timestamp, e.g., "[16:50:12.245] Hello world!".

    @param *args one or more strings containing a message to print
    @return string
    """
    message = ' '.join(map(str, args))
    time = datetime.now(tz=pytz.timezone('Europe/Amsterdam')).strftime('%H:%M:%S.%f')[:-3]
    print(f'[{time}] {message}')
  
  def _datatableToCsv(self, path, datatable):
    """To CSV
    Write datatable object as CSV file

    @param path location to save the file
    @param data datatable object
    """
    data = datatable.to_pandas().replace({np.nan: None})
    data.to_csv(path, index=False, quoting=csv.QUOTE_ALL)
  
  def importDatatableAsCsv(self, pkg_entity: str, data):
    """Import Datatable As CSV
    Save a datatable object to as csv file and import into MOLGENIS using the
    importFile api.
    
    @param pkg_entity table identifier in emx format: package_entity
    @param data a datatable object
    @param label a description to print (e.g., table name)
    """
    with tempfile.TemporaryDirectory() as tmpdir:
      filepath=f"{tmpdir}/{pkg_entity}.csv"
      self._datatableToCsv(filepath, data)
      with open(path.abspath(filepath),'r') as file:
        response = self._session.post(
          url = self.fileImportEndpoint,
          headers = self._headers.token_header,
          files = {'file': file},
          params = {'action': 'add_update_existing', 'metadataAction': 'ignore'}
        )
        if (response.status_code // 100 ) != 2:
          self._print('Failed to import data into', pkg_entity, '(', response.status_code, ')')
        else:
          self._print('Imported data into', pkg_entity)
        return response
      
def flattenDataset(data, columnPatterns=None):
  """Flatten Dataset
  Flatten all nested attributes in a recordset based on a specific column names.
  
  @param data a recordset
  @param column string containing row headers to detect: "subjectID|id|value"
  @return a new recordset containing flattened data
  """
  newData = list(data)
  for row in newData:
    if '_href' in row:
      del row['_href']
    for column in row.keys():
      if isinstance(row[column], dict):
        if bool(row[column]):
          columnMatch = re.search(columnPatterns, ','.join(row[column].keys()))
          if bool(columnMatch):
            row[column] = row[column][columnMatch.group()]
          else:
            print(f'Variable {column} is type "dict", but no target column found')
        else:
          row[column] = None
      if isinstance(row[column], list):
        if bool(row[column]):
          values = []
          for nestedrow in row[column]:
            columnMatch = re.search(columnPatterns, ','.join(nestedrow.keys()))
            if bool(columnMatch):
              values.append(nestedrow[columnMatch.group()])
            else:
              print(f'Variable {column} is type "list", but no target column found')
          if bool(values):
            row[column] = ','.join(values)
        else:
          row[column] = None
  return newData

#///////////////////////////////////////////////////////////////////////////////

# ~ 0 ~
# Connect to database and retrieve data

# for local dev
# from dotenv import load_dotenv
# from os import environ
# load_dotenv()
# ernskin = Molgenis(environ['ERRAS_PROD_HOST'])
# ernskin.login(environ['ERRAS_PROD_USR'], environ['ERRAS_PROD_PWD'])

# for deployment
ernskin = Molgenis('http://localhost/api/', token='${molgenisToken}')

#///////////////////////////////////////

# get metadata
subjects = ernskin.get('skin_allSubject', batch_size=10000)
subjectsDT = flattenDataset(data=subjects, columnPatterns='value_en|value|id')
subjectsDT = dt.Frame(subjectsDT)

# get stats
stats = ernskin.get('stats_stats')
statsDT = dt.Frame(flattenDataset(stats, columnPatterns='name'))

# get healthcare providers
providersDT = dt.Frame(ernskin.get('stats_dataproviders'))
del providersDT['_href']

#///////////////////////////////////////////////////////////////////////////////

# ~ 1 ~
# Summarise data

# ~ 1a ~
# Summarise data by age
# For now, use today's date as the default. This should be updated later
ageDT = subjectsDT[:, {
  'dateBirth': f.dateBirth,
  'dateToday': today()
}]


ageDT[:, dt.update(
  dateBirth=as_type(f.dateBirth,dt.Type.date32),
  dateToday=as_type(f.dateToday,dt.Type.date32),
)]


# calculate age
ageDT['age'] = dt.Frame([
  round(int((row[1] - row[0]).days) / 364.25, 4) if all(row) else None
  for row in ageDT[:, (f.dateBirth, f.dateToday)].to_tuples()  
])

# create bins and summarise data
agePD = ageDT.to_pandas()
bins = [0, 0.25, 1, 5,13,18,40, 60,np.inf]
labels = [
  'Newborn',
  'Infant',
  'Todler',
  'Kids',
  'Teenagers',
  'Adults < 40',
  'Adults < 60',
  'Elderly persons',
]

agePD['bin'] = pd.cut(agePD['age'],bins=bins,labels=labels,right=False)

# summarise by bin and update main dataset
ageDT = dt.Frame(agePD)
ageByGroup = ageDT[:, dt.count(), dt.by(f.bin)]

for bin in ageByGroup['bin'].to_list()[0]:
  statsDT[f.label==bin, 'value'] = ageByGroup[f.bin==bin,'count']
  
#///////////////////////////////////////

# ~ 1b ~
# Summarise data by `sexAtBirth`
# number of patients by `sexAtBirth`
sexAtBirth = subjectsDT[:, dt.count(), dt.by(f.biologicalSex)]

# calculate percent for each record
sexAtBirth['total'] = sum(sexAtBirth['count'].to_list()[0])

sexAtBirth['rate'] = dt.Frame([
  round(row[0]/row[1], 2) if all(row) else 0
  for row in sexAtBirth[:, (f.count,f.total)].to_tuples()
])

sexAtBirth['id'] = dt.Frame([
  f"sex-{value.lower()}"
  for value in sexAtBirth['biologicalSex'].to_list()[0]
])

for id in sexAtBirth['id'].to_list()[0]:
  statsDT[f.id==id, 'value'] = sexAtBirth[f.id==id,'rate']

#///////////////////////////////////////

# ~ 1c ~
# Summarise enrollment by disease group

# get lookup table for disease group
groups = dt.Frame(ernskin.get('erras_diseasegroup'))[:, {'id': f.id, 'label': f.value}]
groups.key = 'id'

diseaseGroupDT = subjectsDT[:, dt.count(), dt.by(f.diseaseGroup)][
  :, {'id': f.diseaseGroup, 'value': f.count}
][:, :, dt.join(groups)]

diseaseGroupDT['id'] = diseaseGroupDT[:, 'enrollment-' + f.id]

for id in diseaseGroupDT['id'].to_list()[0]:
  statsDT[f.id==id, 'value'] = diseaseGroupDT[f.id==id,'value']

#///////////////////////////////////////

# ~ 1d ~
# Summarise submitted patients by centers
centersDT = subjectsDT[:, dt.count(), dt.by(f.centre)]

for id in centersDT['centre'].to_list():
  providersDT[f.alternativeIdentifier==id, 'hasSubmittedData'] = True

ernskin.importDatatableAsCsv('stats_dataproviders', providersDT)

# ~ 1e ~
# Prepare summaries for data-highlights component

statsDT[f.label=='Patients', 'value'] = subjectsDT.nrows

statsDT[f.label=='Member countries', 'value'] = dt.unique(
  providersDT[f.hasSubmittedData,'country']
).nrows

statsDT[f.label=='Healthcare providers', 'value'] = dt.unique(
  providersDT[f.hasSubmittedData, 'code']
).nrows

#///////////////////////////////////////////////////////////////////////////////

# ~ 2 ~
# import data into stats_stats
ernskin.importDatatableAsCsv('stats_stats', statsDT)
