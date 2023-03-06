#///////////////////////////////////////////////////////////////////////////////
# FILE: data_stats_summarise.py
# AUTHOR: David Ruvolo
# CREATED: 2023-02-16
# MODIFIED: 2023-03-06
# PURPOSE: summarise data for dashboard
# STATUS: stable
# PACKAGES: **see below**
# COMMENTS: NA
#///////////////////////////////////////////////////////////////////////////////

from erns.utils.molgenis2 import Molgenis
from datatable import dt, f, as_type
from dotenv import load_dotenv
from datetime import datetime
from os import environ
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

def extractColumnNames(data, pattern):
  cols = data[:, [name for name in data.names if re.search(pattern, name)]].names
  return list(cols)
  
def calcRowSums(data, colname, genes, geneColumns, classColumns, zygosityColumns=None):
  """Calculate Row Sums
  Calculate row sums based on the count of each gene in genes multiplied by
  classification of pathogenic or likely pathogenic.

  @param data datatable object
  @param colname name of the column to create
  @param genes a list of genes to check
  @param geneColumns a list of one or more gene columns to check
  @param classColumns a list of one or more classification columns to check
  @param zygosityColumns a list of one or more zygosity columns to check
  
  @return integer
  """
  subjectIDs = data['ID_Patient'].to_list()[0]
  for id in subjectIDs:
    row = data[f.ID_Patient == id, :]
    rowSum = 0
    for gene in genes:
      geneCount = 0
      likelyPathogenicCount = 0
      pathogenicCount = 0
      zygosityCount = 0

      for geneColumn in geneColumns:
        if row[geneColumn].to_list()[0][0] == gene:
          geneCount += 1 # how many cases of gene X are there?

      for classColumn in classColumns:
        if row[classColumn].to_list()[0][0] == '2': # likely pathogenic (2)
          likelyPathogenicCount += 1
        if row[classColumn].to_list()[0][0] == '3': # pathogenic (3)
          pathogenicCount += 1

      genePathogenic = geneCount * pathogenicCount
      geneLikelyPathogenic = geneCount * likelyPathogenicCount

      if zygosityColumns:
        for zygosityColumn in zygosityColumns:
          if row[zygosityColumn].to_list()[0][0] == '1': # homozygous germline variant (1)
            zygosityCount += 1

        genePathZyg = genePathogenic * zygosityCount
        geneLikelyPathZyg = geneLikelyPathogenic * zygosityCount        
        rowSum += (genePathZyg + geneLikelyPathZyg)
      else:
        rowSum += (genePathogenic + geneLikelyPathogenic)
    data[f.ID_Patient==id, colname] = rowSum

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
  'VariantZygosity_1',
  'VariantZygosity_2',
  'VariantZygosity_3',
  'VariantZygosity_4',
  'ORDO',
  'InclCriteriaUnexplained',
])

for pkg in packageIDs:
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

subjectsDT = flattenDataset(subjects, columnPatterns='id|code|value')
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
print2('Determining the most recent date....')
recentDates = subjectsDT[:, (f.DateLastInfo,f.YearFollowup, f.YearDeath)] \
  .to_pandas() \
  .replace({np.nan: None}) \
  .to_dict('records')

subjectsDT['recentDate'] = dt.Frame([
  findDateLastContact(row)
  for row in recentDates
])

# change class to date32
subjectsDT[:, dt.update(
  YearBirth = as_type(f.YearBirth, dt.Type.date32),
  recentDate = as_type(f.recentDate, dt.Type.date32)
)]

# format ORDO string
subjectsDT['ORDO'] = dt.Frame([
  value.strip() if value else value for value in subjectsDT['ORDO'].to_list()[0]
])

# check IDs
if dt.unique(subjectsDT['ID_Patient']).nrows != subjectsDT.nrows:
  raise SystemError('Warning: There are duplicate IDs in column ID_Patient. Review and filter data accordingly.')

#///////////////////////////////////////////////////////////////////////////////

# ~ 2 ~
# Summarise data
print2('Creating summary stats for data-highlights.....')

# ~ 2a ~
# Calcuate data-highlights

# get total submitted patients
totalPatients = dt.unique(subjectsDT['ID_Patient']).nrows

# find active centers to get countries
activeCenterIDs = dt.unique(subjectsDT['databaseID']).to_list()[0]
activeCenters = providers[
  functools.reduce(
    operator.or_, (f.databaseID == id for id in activeCenterIDs)
  ), :
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
print2('Calculating age....')

# Calcuate age at the row-level
subjectsDT['age'] = dt.Frame([
  round(int((row[1] - row[0]).days) / 364.25, 4)
  if row[0] and row[1] else None
  for row in subjectsDT[:, (f.YearBirth, f.recentDate)].to_tuples()
])

# apply maximum age to missing values
print2('Applying max.age where age cannot be calculated....')
if subjectsDT[f.age==None,'age'].nrows > 0:
  print2('Applying max age to missing values...')
  maxAge = subjectsDT[:, dt.max(f.age)].to_list()[0][0]
  subjectsDT['age'] = dt.Frame([
    maxAge if not bool(value) else value
    for value in subjectsDT['age'].to_list()[0]
  ])

# bin age
print2('Creating bins for age....')
subjectsPD = subjectsDT.to_pandas()
bins = [0] + [num for num in range(20,80,10)] + [np.inf]
labels=['<20','20-29','30-39','40-49','50-59','60-69','70+']

subjectsPD['bin']=pd.cut(subjectsPD['age'],bins=bins,labels=labels,right=False)
subjectsDT = dt.Frame(subjectsPD)

# Summarise data and update stats dataset
print2('Summarising by age range and updating dataset....')
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
print2('Summarising sexAtBirth....')
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
# Apply thematic disease groups (TDG) and summarise. Each check will return the
# TDG identifier which will be recoded into group names before merging with the
# main summary stats dataset. For reference, the group IDs are listed below.
#
#  1 = nf
#  2 = lynch
#  3 = hboc
#  4 = other
#
print2('Determining thematic disease group assignment....')
subjectsDT['diseaseGroup'] = None

# ~ 2d.i ~
# Assign TDG 2 or 3 based on one inclusion criteria. The following conditions
# must be met.
#   3: If there isn't a value and the value equals the 1st inclusion criteria value
#   2: If there isn't a value and the value equals the 2nd inclusion criteria value
#
print2('Setting diseaseGroup based on `InclCriteria`....')

subjectsDT['diseaseGroup'] = dt.Frame([
  '3' if not bool(value) & (value == 1) else (
    '2' if not bool(value) & (value == 2) else value
  )
  for value in subjectsDT['InclCriteria'].to_list()[0]
])

# subjectsDT[:, dt.count(), dt.by(f.diseaseGroup)]

# ~ 2d.ii ~
# Assign TDG based on one inclusion criteria + gen
# Does the case meet the following conditions?
#
#  [] The value "Other..." for inclusion criteria
#  [] Has a classification of "Likely Pathogenic" (2) or "Pathogenic" (3)
#  [] The gene appears in the disease group gene list
#  [] A TDG was assigned not in an earlier step
#
print2('Setting diseaseGroup based on `InclCriteria`, classification, and gene...')
genesByGroup=diseaseGroupCriteria[f.type=='GENE',(f.groupID,f.value)]
geneList = genesByGroup['value'].to_list()[0]

subjectsDT['diseaseGroup'] = dt.Frame([
  row[3] if not all(row) else (
    genesByGroup[f.value==row[2], 'groupID'].to_list()[0][0]
    if (
      # inclusion criteria == "Other proven pathogenic..."
      (str(row[0]) == '3') &
      (str(row[1]) == '2' or str(row[1]) == '3') &
      (str(row[2]) in geneList)
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
ordoByGroup = diseaseGroupCriteria[f.type=='ORDO', (f.groupID,f.value)]
ordoList = ordoByGroup['value'].to_list()[0]

subjectsDT['diseaseGroup'] = dt.Frame([
  row[1] if bool(row[1]) else (
    ordoByGroup[f.value==row[0], 'groupID'].to_list()[0][0]
    if row[0] in ordoList
    else row[1]
  )
  for row in subjectsDT[:, (f.ORDO, f.diseaseGroup)].to_tuples()
])

# ~ 2d.iv ~
# Manually set TDG based on unexplained exclusion criteria
print2('Setting disease groups based on `InclCriteriaUnexplained`...')

# set TDG #2 for unexplained criteria ID==2|3
subjectsDT['diseaseGroup'] = dt.Frame([
  row[1] if bool(row[1]) else (
    '2'
    if (str(row[0]) == '2') or (str(row[0] == '3'))
    else row[1]
  )
  for row in subjectsDT[:, (f.InclCriteriaUnexplained, f.diseaseGroup)].to_tuples()
])

# set TDG #3 for unexplained criteria ID==4|5
subjectsDT['diseaseGroup'] = dt.Frame([
  row[1] if bool(row[1]) else (
    '2' if ((str(row[0]) == '4') or (str(row[0]) == '5'))
    else row[1]
  )
  for row in subjectsDT[:, (f.InclCriteriaUnexplained, f.diseaseGroup)].to_tuples()
])

# ~ 2d.v ~
# Override TDG for special cases
# If the group assignment is 2 and the ORDO code is 252202, then assign to group 4
# ORDO Term: "Constitutional mismatch repair deficiency syndrome"
print2('Overriding diseaseGroup based on group 2 assignment and ORDO code...')
subjectsDT['diseaseGroup'] = dt.Frame([
  '4' if (row[1] == '2') & (str(row[0]) == 'ORPHA:252202') else row[1]
  for row in subjectsDT[:, (f.ORDO, f.diseaseGroup)].to_tuples()
])


# ~ 2d.vi-vii ~
# Calculate rowsums and override
# Find out which columns are present in the datasets
geneCols = extractColumnNames(subjectsDT, re.compile(r'^(VariantGene_)'))
classCols = extractColumnNames(subjectsDT, re.compile(r'^(VariantClass_)'))
zygosityCols = extractColumnNames(subjectsDT, re.compile(r'^(VariantZygosity_)'))

# ~ 2d.vi ~
# Override TDG based on gene and classification status
calcRowSums(
  data = subjectsDT,
  colname='sumGeneClass',
  genes = ['MLH1','MSH2', 'MSH6', 'PMS2'],
  geneColumns = geneCols,
  classColumns = classCols
)

# Change the group to 4 if the sum >= 2 and the current group is 2
subjectsDT['diseaseGroup'] = dt.Frame([
  '4' if (row[0] == '2') & (row[1] >= 2) else row[0]
  for row in subjectsDT[:, ['diseaseGroup', 'sumGeneClass']].to_tuples()
])

# ~ 2d.vii ~
# Override TDG based on gene, classification, and zygosity
calcRowSums(
  data = subjectsDT,
  colname='sumGeneClassZygosity',
  genes = ['MLH1','MSH2', 'MSH6', 'PMS2'],
  geneColumns = geneCols,
  classColumns = classCols,
  zygosityColumns=zygosityCols
)

# change the group to 4 if the sum >= 1 and the current group is 2
subjectsDT['diseaseGroup'] = dt.Frame([
  '4' if (row[0] == '2') & (row[1] >= 1) else row[0]
  for row in subjectsDT[:, ['diseaseGroup', 'sumGeneClassZygosity']].to_tuples()
])

# ~ 2d.vii ~
# Override TDG 3 based on ORDO code
calcRowSums(
  data = subjectsDT,
  colname = 'rowSumGroup3',
  genes = ['ATM'],
  geneColumns = geneCols,
  classColumns = classCols
)

# if rowsum > 1 and group is 3, change to group 4
subjectsDT['diseaseGroup'] = dt.Frame([
  '4' if (row[0] == '3') & (row[1] >= 1) else row[0]
  for row in subjectsDT[:, ['diseaseGroup', 'rowSumGroup3']].to_tuples()
])

# ~ 2d.ix ~
# Override TDG if ORDO is "Birt-Hogg-Dubé syndrome" (ORPHA:122)
subjectsDT['diseaseGroup'] = dt.Frame([
  '4' if row[0] == 'ORPHA:122' else row[1]
  for row in subjectsDT[:, (f.ORDO, f.diseaseGroup)].to_tuples()
])

# ~ 2d.x ~
# Summarise by group
print2('Summarizing by groups....')
countByGroup = subjectsDT[:, dt.count(), dt.by(f.diseaseGroup)]
countByGroup['groupName'] = dt.Frame([
  diseaseGroups[f.groupID == value, 'groupName'].to_list()[0][0]
  for value in countByGroup['diseaseGroup'].to_list()[0]
])

# set undetermined group
if countByGroup[f.diseaseGroup==None,:].nrows > 0:
  countByGroup[f.diseaseGroup==None, 'groupName'] = 'Undetermined'

# update ernstats datasets
for value in countByGroup['groupName'].to_list()[0]:
  if 'Other rare' in value:
    group2 = ernstats[f.component=='table-enrollment-disease-group','label'].to_list()[0][2]
    ernstats[f.label==group2,'value'] = countByGroup[f.groupName==value, 'count'].to_list()[0][0]
  elif value in ernstats[f.component=='table-enrollment-disease-group','label'].to_list()[0]:
    ernstats[f.label==value,'value'] = countByGroup[
      f.groupName==value,'count'
    ].to_list()[0][0]
  else:
    raise SystemError(f"Error: value '{value}' uknown. Please check disease group mappings....")

#///////////////////////////////////////////////////////////////////////////////

# ~ 3 ~
# Import data

genturis.importDatatableAsCsv(pkg_entity='ernstats_dataproviders', data=providers)
genturis.importDatatableAsCsv(pkg_entity='ernstats_stats', data=ernstats)

genturis.logout()
