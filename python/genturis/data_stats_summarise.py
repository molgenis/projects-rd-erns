#///////////////////////////////////////////////////////////////////////////////
# FILE: data_stats_summarise.py
# AUTHOR: David Ruvolo
# CREATED: 2023-02-16
# MODIFIED: 2023-02-16
# PURPOSE: summarise data for dashboard
# STATUS: in.progress
# PACKAGES: NA
# COMMENTS: NA
#///////////////////////////////////////////////////////////////////////////////

from python.utils.molgenis2 import Molgenis
from datatable import dt, f, as_type
from dotenv import load_dotenv
from os import environ
from tqdm import tqdm
import pandas as pd
import numpy as np
import functools
import operator
import re
load_dotenv()

genturis=Molgenis(environ['GENTURIS_PROD_HOST'])
genturis.login(environ['GENTURIS_PROD_USR'], environ['GENTURIS_PROD_PWD'])

def flattenDataset(data, columnPatterns=None):
  """Flatten Dataset
  Flatten all nested attributes in a recordset based on a specific column names.
  
  @param data a recordset
  @param column string containing row headers to detect: "subjectID|id|value"
  @return a new recordset containing flattened data
  """
  newData = data
  for row in tqdm(newData):
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

# ~ 1 ~
# Retrieve data
# In order to summarise the data for the dashboard, Collate all available EMX Packages

# retrieve system meta
packages = dt.Frame(genturis.get(
  entity = 'sys_md_Package',
  attributes = 'id,label',
  q = "entityTypes=like=subject"
))
del packages['_href']

# retrieve data from stats table
ernstats = dt.Frame(genturis.get(entity = 'ernstats_stats'))
del ernstats['_href']

# ~ 1a ~
# Refresh Database IDs
# It is recommended to refresh the values in the databaseIDs. This allows us to
# link the EMX packages with the providers dataset, and update submission status
providers = dt.Frame(genturis.get('ernstats_dataproviders'))
del providers['_href']

providers['databaseID'] = dt.Frame([
  packages[f.label==value, 'id'].to_list()[0][0]
  if value in packages['label'].to_list()[0] else None
  for value in providers['projectName'].to_list()[0]
])

genturis.importDatatableAsCsv('ernstats_dataproviders',providers)

# ~ 1b ~
# Retrieve metadata
# Using the list of emx package IDs, loop through each table and retrieve the
# following information.
#
#   1. Sex
#   2. Year of Birth if known
#   3. Date at time of inclusion
#   4. Thematic disease grouping
#

subjects = []
packageIDs = packages['id'].to_list()[0]

for pkg in tqdm(packageIDs):
  pkgData = genturis.get(
    entity=f"{pkg}_subject",
    attributes='ID_Patient,Sex,YearBirth,DateLastInfo,YearFollowup,ORDO',
    batch_size=1000
  )
  if bool(pkgData):
    for row in pkgData:
      row['databaseID'] = pkg
    providers[f.databaseID==pkg, 'hasSubmittedData'] = True
    subjects += pkgData
  else:
    providers[f.databaseID==pkg, 'hasSubmittedData'] = False

print(f"Retrieved {len(subjects)} subjects")

# ~ 1c ~
# Reshape subjects dataset

subjectsDT = flattenDataset(subjects, columnPatterns='label|code')
subjectsDT = dt.Frame(subjectsDT)

# fix extra white space in subjectID
subjectsDT['ID_Patient'] = dt.Frame([
  value.strip()
  for value in subjectsDT['ID_Patient'].to_list()[0]
])

# format YearBirth
subjectsDT['YearBirth'] = dt.Frame([
  f"{value}-01-01" if value else value
  for value in subjectsDT['YearBirth'].to_list()[0]
])

# Format YearFollowup if available
if 'YearFollowup' in subjectsDT.names:
  subjectsDT['YearFollowup'] = dt.Frame([
    f"{value}-01-01" if value else value
    for value in subjectsDT['YearFollowup'].to_list()[0]
  ])
else:
  subjectsDT['YearFollowup'] = None

# find most recent date -- YearFollowup takes priority over DateLastInfo
subjectsDT['recentDate'] = dt.Frame([
  row[1] if bool(row[1]) else row[0]
  for row in subjectsDT[:, (f.DateLastInfo, f.YearFollowup)].to_tuples()
])

# as.date
subjectsDT[
  :, dt.update(
    YearBirth = as_type(f.YearBirth, dt.Type.date32),
    recentDate = as_type(f.recentDate, dt.Type.date32)
  )
]

# format ORDO string
subjectsDT['ORDO'] = dt.Frame([
  value.replace(':','_').strip() if value else value
  for value in subjectsDT['ORDO'].to_list()[0]
])


# check IDs
if dt.unique(subjectsDT['ID_Patient']).nrows != subjectsDT.nrows:
  raise SystemError('Warning: There are duplicate IDs in column ID_Patient. Review and filter data accordingly.')

#///////////////////////////////////////////////////////////////////////////////

# ~ 2 ~
# Calculate descriptives

# ~ 2a ~
# Calcuate data-highlights

# get total submitted patients
totalPatients = dt.unique(subjectsDT['ID_Patient']).nrows

# find active centers to get countries
activeCenterIDs = dt.unique(subjectsDT['databaseID']).to_list()[0]
activeCenters = providers[
  functools.reduce(operator.or_, (f.databaseID == id for id in activeCenterIDs)), :
]

totalCenters = dt.unique(activeCenters['projectName']).nrows
totalCountries = dt.unique(activeCenters['country']).nrows

# update data-highlights using ID (patients, countries, centres)
ernstats[f.id=='data-highlight-0','value'] = totalPatients
ernstats[f.id=='data-highlight-1','value'] = totalCountries
ernstats[f.id=='data-highlight-2','value'] = totalCenters

#///////////////////////////////////////

# ~ 2b ~
# Calculate age by age range
# Here we would like to summarise age by age group (<20, 20-29, etc.). Using
# all row-level data, calculate the age using the most recent date, and then
# apply bins (as defined in the dashboard). From there, summarise the data
# by age group

# Calcuate age at the row-level
subjectsDT['age'] = dt.Frame([
  round(int((row[1] - row[0]).days) / 365.25, 4)
  if row[0] and row[1] else None
  for row in subjectsDT[:, (f.YearBirth, f.recentDate)].to_tuples()
])

# Create bins for age ranges
subjectsPD = subjectsDT.to_pandas()
bins = pd.IntervalIndex.from_tuples([
  (0, 19.9999),
  (20,29.9999),
  (30,39.9999),
  (40,49.9999),
  (50,59.9999),
  (60,69.9999),
  (70,np.inf)
])

labels=['<20','20-29','30-39','40-49','50-59','60-69','70+']

subjectsPD['bin'] = pd.cut(subjectsPD['age'], bins=bins).map(dict(zip(bins,labels)))
subjectsDT = dt.Frame(subjectsPD)

# Summarise data and update stats dataset
ageByGroup = subjectsDT[:, dt.count(), dt.by(f.bin)]

for value in ageByGroup['bin'].to_list()[0]:
  if value in ernstats[f.component=='barchart-age', 'label'].to_list()[0]:
    ernstats[f.label==value,'value'] = ageByGroup[f.bin==value,'count'].to_list()[0][0]
  else:
    raise SystemError(f'Error: age group {value} not found in stats table!')

#///////////////////////////////////////

# ~ 2c ~
# Summarise sexAtBirth
sexAtBirth = subjectsDT[:, dt.count(), dt.by(f.Sex)]
for value in sexAtBirth['Sex'].to_list()[0]:
  if value in ernstats[f.component=='pie-sex-at-birth','label'].to_list()[0]:
    ernstats[f.label==value,'value'] = sexAtBirth[f.Sex==value,'count'].to_list()[0][0]
  else:
    raise SystemError(f"ERror: value {value} not a known sex code")

#///////////////////////////////////////

# ~ 2d ~
# Summarise data by thematic disease group
# TBD


#///////////////////////////////////////////////////////////////////////////////

# ~ 3 ~
# Import data

genturis.importDatatableAsCsv(pkg_entity='ernstats_dataproviders', data=providers)
genturis.importDatatableAsCsv(pkg_entity='ernstats_stats', data=ernstats)

genturis.logout()