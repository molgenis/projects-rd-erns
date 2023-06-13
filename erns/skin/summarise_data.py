#///////////////////////////////////////////////////////////////////////////////
# FILE: summarise_data.py
# AUTHOR: David Ruvolo
# CREATED: 2023-06-13
# MODIFIED: 2023-06-13
# PURPOSE: summarise data in the registry and prep for dashboard
# STATUS: in.progress
# PACKAGES: NA
# COMMENTS: NA
#///////////////////////////////////////////////////////////////////////////////

from erns.utils.molgenis2 import Molgenis
from erns.utils.utils import flattenDataset
from datatable import dt, f, as_type
from dotenv import load_dotenv
from os import environ
import pandas as pd
import numpy as np
load_dotenv()

ernskin = Molgenis(environ['ERRAS_PROD_HOST'])
ernskin.login(environ['ERRAS_PROD_USR'], environ['ERRAS_PROD_PWD'])


# get metadata
subjects = ernskin.get('skin_allSubject', batch_size=10000)
subjectsDT = flattenDataset(data=subjects, columnPatterns='value_en|value|id')
subjectsDT = dt.Frame(subjectsDT)

# get stats
statsDT = dt.Frame(ernskin.get('ernstats_stats'))
del statsDT['_href']

#///////////////////////////////////////////////////////////////////////////////

# ~ 1 ~
# Summarise data

# ~ 1a ~
# Summarise data by age

ageDT = subjectsDT[:, {
  'dateBirth': f.dateBirth,
  'dateToday': '2023-06-01'
}]

ageDT[:, dt.update(
  dateBirth=as_type(f.dateBirth,dt.Type.date32),
  dateToday=as_type(f.dateToday,dt.Type.date32),
)]


ageDT['age'] = dt.Frame([
  round(int((row[1] - row[0]).days) / 364.25, 4)
  if all(row) else None
  for row in ageDT[:, (f.dateBirth, f.dateToday)].to_tuples()  
])

agePD = ageDT.to_pandas()
bins = [0] + [num for num in range(20,80,10)] + [np.inf]
labels=['<20','20-29','30-39','40-49','50-59','60-69','70+']

agePD['bin']=pd.cut(agePD['age'],bins=bins,labels=labels,right=False)
ageDT = dt.Frame(agePD)

ageByGroup = ageDT[:, dt.count(), dt.by(f.bin)]

for bin in ageByGroup['bin'].to_list()[0]:
  statsDT[f.label==bin, 'value'] = ageByGroup[f.bin==bin,'count']

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
  f"sex-at-birth-{value.lower()}"
  for value in sexAtBirth['biologicalSex'].to_list()[0]
])


for id in sexAtBirth['id'].to_list()[0]:
  statsDT[f.id==id, 'value'] = sexAtBirth[f.id==id,'rate']

ernskin.importDatatableAsCsv('ernstats_stats', statsDT)


#///////////////////////////////////////////////////////////////////////////////

# ~ 999 ~
# Create Initial data structures

# # create disease groups
# groupsDT = dt.Frame(
#   flattenDataset(
#     data = ernskin.get('erras_diseasegroup'), 
#     columnPatterns='id|value'
#   )
# )[:, {'id':f.id, 'label':f.value}]

# groupsDT['value'] = 0
# groupsDT[:, dt.update(id=as_type(f.id, dt.Type.int32))]
# groupsDT['valueOrder'] = groupsDT[:, f.id-1]

# groupsDT['id'] = groupsDT[:, 'enrollment-' + f.id]

# ernskin.importDatatableAsCsv('ernstats_stats', groupsDT)

# # define age groups
# ageDT = dt.Frame(label=['<20','20-29','30-39','40-49','50-59','60-69','70+'])
# ageDT[['id','valueOrder']] = range(0,ageDT.nrows)
# ageDT['value'] = 0
# ageDT['id'] = ageDT[:, 'age-group-' + f.id]

# ernskin.importDatatableAsCsv('ernstats_stats',ageDT)