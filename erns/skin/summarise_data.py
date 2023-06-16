#///////////////////////////////////////////////////////////////////////////////
# FILE: summarise_data.py
# AUTHOR: David Ruvolo
# CREATED: 2023-06-13
# MODIFIED: 2023-06-16
# PURPOSE: summarise data in the registry and prep for dashboard
# STATUS: stable
# PACKAGES: NA
# COMMENTS: NA
#///////////////////////////////////////////////////////////////////////////////

from erns.utils.molgenis2 import Molgenis
from erns.utils.utils import flattenDataset
from datatable import dt, f, as_type
from dotenv import load_dotenv
from datetime import datetime
from os import environ
import pandas as pd
import numpy as np
import pytz
load_dotenv()

def today(tz='Europe/Amsterdam'):
  return datetime.now(tz=pytz.timezone(tz)).strftime('%Y-%m-%d')

ernskin = Molgenis(environ['ERRAS_PROD_HOST'])
ernskin.login(environ['ERRAS_PROD_USR'], environ['ERRAS_PROD_PWD'])


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
  'Adults group 1',
  'Adults group 2',
  'Elderly persons',
]

agePD['bin'] = pd.cut(agePD['age'],bins=bins,labels=labels,right=False)
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

diseaseGroupDT = subjectsDT[
  :, dt.count(), dt.by(f.diseaseGroup)
][
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
