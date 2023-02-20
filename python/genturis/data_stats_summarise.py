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
from datetime import datetime
from os import environ
from tqdm import tqdm
import pandas as pd
import numpy as np
import functools
import operator
import pytz
import re
load_dotenv()

genturis=Molgenis(environ['GENTURIS_PROD_HOST'])
genturis.login(environ['GENTURIS_PROD_USR'], environ['GENTURIS_PROD_PWD'])

# genturis=Molgenis(environ['GENTURIS_ACC_HOST'])
# genturis.login(environ['GENTURIS_ACC_USR'], environ['GENTURIS_ACC_PWD'])

def print2(*args):
  message = ' '.join(map(str, args))
  time = datetime.now(tz=pytz.timezone('Europe/Amsterdam')).strftime('%H:%M:%S.%f')[:-3]
  print(f'[{time}] {message}')


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
  
def findDateLastContact(data):
  """Find data of last contact
  @return date string or None
  """
  if bool(data.get('YearDeath')):
    return data['YearDeath']
  else:
    if bool(data.get('DateLastInfo')):
      return data['DateLastInfo']
    elif bool(data.get('YearFollowup')):
      return data['YearFollowup']
    else:
      return None
      
def yearToDate(value, format="-07-01"):
  """Year to date
  If a value is only a year, reformat it as a yyyy-mm-dd.
  
  @param value a string containing a year
  @param format date format to append to the year (default `-07-01`)
  
  @return a date string in yyyy-mm-dd format
  """
  return f"{value}{format}"
  
#///////////////////////////////////////////////////////////////////////////////

# ~ 1 ~
# Retrieve data
# In order to summarise the data for the dashboard, Collate all available EMX Packages

print2('Create a list of available EMX packages....')

# retrieve system meta
packages = dt.Frame(genturis.get(
  entity = 'sys_md_Package',
  attributes = 'id,label',
  q = "entityTypes=like=subject"
))
del packages['_href']

# retrieve data from stats table
print2('Retrieving reference datasets....')
inclusionCriteria = dt.Frame(genturis.get('genturis_InclCriteria'))
inclusionCriteriaUnexplained = dt.Frame(genturis.get('genturis_InclCriteriaUnexplain'))
variantClassification = dt.Frame(genturis.get('genturis_variantClass'))
sexCodes = dt.Frame(genturis.get('genturis_sex'))

del inclusionCriteria['_href']
del inclusionCriteriaUnexplained['_href']
del variantClassification['_href']
del sexCodes['_href']

# retrieve inclusion criteria
print2('Retrieving current stats data...')
ernstats = dt.Frame(genturis.get(entity = 'ernstats_stats'))
del ernstats['_href']

print2('Retrieving inclusion criteria....')
diseaseGroupCriteria = dt.Frame(genturis.get('ernstats_inclusionCriteria'))
del diseaseGroupCriteria['_href']

diseaseGroups = diseaseGroupCriteria[
  :, dt.first(f[:]), dt.by(f.groupID,f.groupName)
][:, (f.groupID, f.groupName)]

# print2('Reshaping inclusion criteria dataset....')
# diseaseGroupGenes = {}
# diseaseGroupOrdo = {}
# for group in dt.unique(diseaseGroupCriteria[f.type=='GENE','groupID']).to_list()[0]:
#   # isolate group *n* genes
#   diseaseGroupGenes[group] = diseaseGroupCriteria[
#     (f.type=='GENE') & (f.groupID==group),
#     'value'
#   ].to_list()[0]
  
#   # isolate group *n* ORDO codes
#   diseaseGroupOrdo[group] = diseaseGroupCriteria[
#     (f.type=='ORDO') & (f.groupID==group),
#     'value'
#   ].to_list()[0]

#///////////////////////////////////////

# ~ 1a ~
# Refresh Database IDs
# It is recommended to refresh the values in the databaseIDs. This allows us to
# link the EMX packages with the providers dataset, and update submission status
print2('Updating EMX IDs in ERN Data Providers....')

providers = dt.Frame(genturis.get('ernstats_dataproviders'))
del providers['_href']

providers['databaseID'] = dt.Frame([
  packages[f.label==value, 'id'].to_list()[0][0]
  if value in packages['label'].to_list()[0] else None
  for value in providers['projectName'].to_list()[0]
])

genturis.importDatatableAsCsv('ernstats_dataproviders',providers)

#///////////////////////////////////////

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
print2('Retrieving subject metadata.....')

subjects = []
packageIDs = packages['id'].to_list()[0]

columns=','.join([
  'ID_Patient',
  'Sex',
  # columns for calculating age
  'YearBirth',
  'YearDeath',
  'DateLastInfo',
  'YearFollowup',
  # columns for calcuating disease group assignment
  'InclCriteria',
  'VariantClass_1',
  'VariantClass_2',
  'VariantClass_3',
  'VariantClass_4',
  'VariantGene_1',
  'VariantGene_2',
  'VariantGene_3',
  'VariantGene_4',
  'ORDO',
  'InclCriteriaUnexplained',
])

for pkg in tqdm(packageIDs):
  print2('\tQuerying',f"{pkg}_subject")
  pkgData = genturis.get(f"{pkg}_subject", attributes=columns,batch_size=1000)
  if bool(pkgData):
    for row in pkgData:
      row['databaseID'] = pkg
    providers[f.databaseID==pkg, 'hasSubmittedData'] = True
    subjects += pkgData
  else:
    providers[f.databaseID==pkg, 'hasSubmittedData'] = False

print2(f"Retrieved {len(subjects)} subjects....")

#///////////////////////////////////////

# ~ 1c ~
# Reshape subjects dataset
print2('Transforming subjects dataset....')

subjectsDT = flattenDataset(subjects, columnPatterns='id|code')
subjectsDT = dt.Frame(subjectsDT)

# fix extra white space in subjectID
subjectsDT['ID_Patient'] = dt.Frame([
  value.strip()
  for value in subjectsDT['ID_Patient'].to_list()[0]
])


# format YearBirth
print2('Applying default date format...')

subjectsDT['YearBirth'] = dt.Frame([
  yearToDate(value) if value else value
  for value in subjectsDT['YearBirth'].to_list()[0]
])

# Format YearFollowup if available
if 'YearFollowup' in subjectsDT.names:
  subjectsDT['YearFollowup'] = dt.Frame([
    yearToDate(value) if value else value
    for value in subjectsDT['YearFollowup'].to_list()[0]
  ])
else:
  subjectsDT['YearFollowup'] = None


# Format YearDeath if available
if 'YearDeath' in subjectsDT.names:
  subjectsDT['YearDeath'] = dt.Frame([
    yearToDate(value) if value else value
    for value in subjectsDT['YearDeath'].to_list()[0]
  ])
else:
  subjectsDT['YearDeath'] = None


# find most recent date
recentDates = subjectsDT[:, (f.DateLastInfo,f.YearFollowup, f.YearDeath)] \
  .to_pandas() \
  .replace({np.nan: None}) \
  .to_dict('records')

subjectsDT['recentDate'] = dt.Frame([
  findDateLastContact(row)
  for row in recentDates
])


# change class to date32
subjectsDT[
  :, dt.update(
    YearBirth = as_type(f.YearBirth, dt.Type.date32),
    recentDate = as_type(f.recentDate, dt.Type.date32)
  )
]

# format ORDO string
subjectsDT['ORDO'] = dt.Frame([
  value.strip() if value else value
  for value in subjectsDT['ORDO'].to_list()[0]
])

# check IDs
if dt.unique(subjectsDT['ID_Patient']).nrows != subjectsDT.nrows:
  raise SystemError('Warning: There are duplicate IDs in column ID_Patient. Review and filter data accordingly.')

#///////////////////////////////////////////////////////////////////////////////

# ~ 2 ~
# Summarise data

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
  round(int((row[1] - row[0]).days) / 364.25, 4)
  if row[0] and row[1] else None
  for row in subjectsDT[:, (f.YearBirth, f.recentDate)].to_tuples()
])

# apply maximum age to missing values
if subjectsDT[f.age==None,'age'].nrows > 0:
  print2('Applying max age to missing values...')
  maxAge = subjectsDT[:, dt.max(f.age)].to_list()[0][0]
  subjectsDT['age'] = dt.Frame([
    maxAge if not bool(value) else value
    for value in subjectsDT['age'].to_list()[0]
  ])

# bin age
subjectsPD = subjectsDT.to_pandas()
bins = [0] + [num for num in range(20,80,10)] + [np.inf]
labels=['<20','20-29','30-39','40-49','50-59','60-69','70+']

subjectsPD['bin']=pd.cut(subjectsPD['age'],bins=bins,labels=labels,right=False)
subjectsDT = dt.Frame(subjectsPD)

# Summarise data and update stats dataset
ageByGroup = subjectsDT[:, dt.count(), dt.by(f.bin)]

for value in ageByGroup['bin'].to_list()[0]:
  if value in ernstats[f.component=='barchart-age', 'label'].to_list()[0]:
    ernstats[f.label==value,'value'] = ageByGroup[
      f.bin==value, 'count'
    ].to_list()[0][0]
  else:
    raise SystemError(f'Error: age group {value} not found in stats table!')

#///////////////////////////////////////

# ~ 2c ~
# Summarise sexAtBirth

sexAtBirth = subjectsDT[:, dt.count(), dt.by(f.Sex)]
sexAtBirth.names = { 'Sex': 'id' }

# merge reference list
sexCodes.key = 'id'
sexAtBirth = sexAtBirth[:, :, dt.join(sexCodes)]

for value in sexAtBirth['label'].to_list()[0]:
  if value in ernstats[f.component=='pie-sex-at-birth','label'].to_list()[0]:
    ernstats[f.label==value,'value'] = sexAtBirth[
      f.label==value,'count'
    ].to_list()[0][0]
  else:
    raise SystemError(f"Error: value {value} uknown. Please check sex code mappings....")

#///////////////////////////////////////

# ~ 2d ~
# Apply thematic disease groups (TDG) and summarise
# 1 = nf
# 2 = lynch
# 3 = hboc
# 4 = other

subjectsDT['diseaseGroup'] = None

# ~ 2d.i ~
# Assign TDG based on one inclusion criteria
print2('Setting diseaseGroup based on `InclCriteria`....')

subjectsDT['diseaseGroup'] = dt.Frame([
  # TDG #3
  # If there isn't a value and the value equals the 1st inclusion criteria value
  diseaseGroups[f.id=='3','groupName'].to_list()[0][0]
  if not bool(value) & (value == inclusionCriteria[f.id==1,'label'].to_list()[0][0])
  else (
    # FOR TDG #2
    # If there isn't a value and the value equals the 2nd inclusion criteria value
    diseaseGroups[f.id=='2','groupName'].to_list()[0][0]
    if not bool(value) & (value == inclusionCriteria[f.id==2,'label'].to_list()[0][0])
    else value
  )
  for value in subjectsDT['InclCriteria'].to_list()[0]
])

# ~ 2d.ii ~
# Assign TDG based on one inclusion criteria + gen
# Does the case meet the following conditions?
#
#  [] The value "Other..." for inclusion criteria
#  [] Has a classification of "Likely Pathogenic" or "Pathogenic"
#  [] The gene appears in the disease group gene list
#  [] A TDG was assigned not in an earlier step
#
print2('Setting diseaseGroup based on `InclCriteria`, classification, and gene...')
genesByGroup=diseaseGroupCriteria[f.type=='GENE',(f.groupName,f.value)]
geneList = genesByGroup['value'].to_list()[0]

subjectsDT['diseaseGroup'] = dt.Frame([
  row[3] if not all(row) else (
    genesByGroup[f.value==row[2], 'groupName'].to_list()[0][0]
    if (
      row[0] == inclusionCriteria[f.id==3,'label'].to_list()[0][0] &
      row[1] in ['Likely pathogenic', 'Pathogenic'] &
      row[2] in geneList
    )
    else row[3]
  ) 
  
  for row in subjectsDT[:, (
    f.InclCriteria,
    f.VariantClass_1,
    f.VariantGene_1,
    f.diseaseGroup
  )].to_tuples()
])

# ~ 2d.iii ~
# Assign TDG based on ORDO codes
# Does the case meet the following conditions?
#
#  [] The ORDO code appears in the code list
#  [] A TDG was assigned not in an earlier step
#
print2('Setting disease group based on ORDO codes....')

ordoByGroup = diseaseGroupCriteria[f.type=='ORDO', (f.groupName,f.value)]
ordoList = ordoByGroup['value'].to_list()[0]

subjectsDT['diseaseGroup'] = dt.Frame([
  row[1] if bool(row[1]) else (
    ordoByGroup[f.value==row[0], 'groupName'].to_list()[0][0]
    if row[0] in ordoList
    else row[1]
  )
  for row in subjectsDT[:, (f.ORDO, f.diseaseGroup)].to_tuples()
])

# ~ 2d.iv ~
# Manually set TDG based on unexplained exclusion criteria
print2('Setting disease groups based on `InclCriteriaUnexplained`...')

# set TDG #2 for unexplained criteria ID==2|3
subjectsDT['diseaseGroup'] = dt.Frame(
  row[1] if bool(row[1]) else (
    row[1] if not bool(row[0]) else (
      diseaseGroups[f.id=='2','groupName'].to_list()[0][0]
      if row[0] in inclusionCriteriaUnexplained[
        (f.id==2) | (f.id==3),
        f.label
      ].to_list()[0]
      else row[1]
    )
  )
  for row in subjectsDT[:, (f.InclCriteriaUnexplained, f.diseaseGroup)].to_tuples()
)

# set TDG #3 for unexplained criteria ID==4|5
subjectsDT['diseaseGroup'] = dt.Frame(
  row[1] if bool(row[1]) else (
    row[1] if not bool(row[0]) else (
      diseaseGroups[f.id=='2','groupName'].to_list()[0][0]
      if row[0] in inclusionCriteriaUnexplained[
        (f.id==4) | (f.id==5),
        f.label
      ].to_list()[0]
      else row[1]
    )
  )
  for row in subjectsDT[:, (f.InclCriteriaUnexplained, f.diseaseGroup)].to_tuples()
)

# ~ 2d.v ~
# Override TDG for special cases
print2('Overriding diseaseGroup based on group 2 assignment and ORDO code...')

subjectsDT['diseaseGroup'] = dt.Frame([
  diseaseGroups[f.id=='4','groupName'].to_list()[0][0]
  if row[1] == '2' & row[0] == 'ORPHA:252202'
  else row[1]
  for row in subjectsDT[:, (f.ORDO, f.diseaseGroup)].to_tuple()
])

# TODO
# ~ 2d.vi ~
# Override TDG based on ....
subjectsDT['diseaseGroup'] = dt.Frame([
  
])

# ~ 2d.vii ~
# Override TDG 3 based on ORDO code
# Change to Group 4 if the following conditions are met
#
#   [ ] Current TDG is 3
#   [ ] ORDO term is: Ataxia-telangiectasia
#
subjectsDT['diseaseGroup'] = dt.Frame([
  row[1] if not bool(row[1]) else (
    diseaseGroups[f.id=='4', 'groupName'].to_list()[0][0]
    if (
      row[0] == 'ORPHA:100' &
      row[1] == diseaseGroups[f.id=='3', 'groupName'].to_list()[0][0]
    )
    else row[1]
  )
  for row in subjectsDT[:, (f.ORDO, f.diseaseGroup)].to_tuple()
])

# ~ 2d.ix ~
# Override TDG if ORDO is "Birt-Hogg-Dubé syndrome" (ORPHA:122)
subjectsDT['diseaseGroup'] = dt.Frame([
  diseaseGroups[f.id=='4', 'groupName'].to_list()[0][0]
  if row[0] == 'ORPHA:122'
  else row[1]
  for row in subjectsDT[:, (f.ORDO, f.diseaseGroup)].to_tuple()
])


#///////////////////////////////////////////////////////////////////////////////

# ~ 3 ~
# Import data

genturis.importDatatableAsCsv(pkg_entity='ernstats_dataproviders', data=providers)
genturis.importDatatableAsCsv(pkg_entity='ernstats_stats', data=ernstats)

genturis.logout()