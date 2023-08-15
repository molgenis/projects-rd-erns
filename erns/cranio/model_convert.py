#///////////////////////////////////////////////////////////////////////////////
# FILE: model_convert.py
# AUTHOR: David Ruvolo
# CREATED: 2023-08-11
# MODIFIED: 2023-08-11
# PURPOSE: convert EMX1 model to EMX2 format
# STATUS: in.progress
# PACKAGES: NA
# COMMENTS: NA
#///////////////////////////////////////////////////////////////////////////////

from datatable import dt, f, as_type
import pandas as pd
import csv
import re
from tqdm import tqdm

# create emx1 to emx2 data type mappings
datatypes = {
  'bool' : 'bool',
  'categorical': 'ontology',
  'categorical_mref': 'ontology_array',
  'categoricalmref': 'ontology_array',
  'compound': 'heading',
  'date' : 'date',
  'datetime' : 'datetime',
  'decimal' : 'decimal',
  'email': 'email',
  'enum': None, # temporary mapping
  'file' : 'file',
  'hyperlink': 'hyperlink', # temporary mapping
  'int': 'int',
  'long': 'bigint',  # use `int` for now
  'mref': 'ref_array',
  'one_to_many': 'refback', # process mappedBy
  'string': 'string',
  'text' : 'text',
  'xref': 'ref'
}

# import data
file = "./erns/cranio/source.xlsx"
# pkgs = dt.Frame(pd.read_excel(file, sheet_name='packages'))
entities = dt.Frame(pd.read_excel(file, sheet_name='entities'))
attribs = dt.Frame(pd.read_excel(file, sheet_name='attributes'))

#///////////////////////////////////////////////////////////////////////////////

# ~ 1 ~
# Transform attributes to molgenis.csv format

# drop center-level schema
entities = entities[f.package == 'cranio', :]
attribs = attribs[dt.re.match(f.entity,'.*_DE1_.*') == False, :]

# drop uncessary columns
for column in attribs.names:
  if re.match(r'^((label|description)-[a-zA-Z]{1,})', column):
    del attribs[column]

  elif dt.unique(attribs[column]).to_list()[0] == [None]:
    del attribs[column]


# convert dataTypes ==> columnTypes
attribs['columnType'] = dt.Frame([
  'auto_id' if row[1] is True else datatypes[row[0]]
  for row in attribs[:, ['dataType','auto']].to_tuples()
])

# set required
attribs['required'] = dt.Frame([
  value is False for value in attribs['nillable'].to_list()[0]
])

# set key
attribs['key'] = dt.Frame([
  1 if value is True else None
  for value in attribs['idAttribute'].to_list()[0]
])

# set table name (i.e., drop `cranio_` prefix )
attribs['tableName'] = dt.Frame([
  re.sub(r'^(cranio_)', '', value)
  for value in attribs['entity'].to_list()[0]
])


# set refTable: drop schema prefix
attribs['refTable'] = dt.Frame([
  None if value is None else (
    re.sub(r'^(cranio_)', '', value)
  )
  for value in attribs['refEntity'].to_list()[0]
])

# capture order of tables and variables for sorting
# start at 1 as the table names will be row zero
tableCounter = 0
rowCounter = 1
for index in range(0,attribs.nrows):
  if index == 0:
    attribs[index, '_tableOrder'] = tableCounter
    attribs[index, '_rowOrder'] = rowCounter
  else:
    if attribs[index, 'tableName'] != attribs[index-1, 'tableName']:
      tableCounter += 1
      rowCounter = 1
      
      attribs[index, '_tableOrder'] = tableCounter
      attribs[index, '_rowOrder'] = rowCounter
    else:
      rowCounter += 1
      
      attribs[index, '_tableOrder'] = tableCounter
      attribs[index, '_rowOrder'] = rowCounter


#///////////////////////////////////////////////////////////////////////////////

# ~ 1 ~
# Prepare entities to be appended to emx2 schema

# drop uncessary columns
for column in entities.names:
  if re.match(r'^((label|description)-[a-zA-Z]{1,})', column):
    del entities[column]

  elif dt.unique(entities[column]).to_list()[0] == [None]:
    del entities[column]


for row in range(0, entities.nrows):
  value = entities[row, 'name']
  
  # bring over table order (position within the schema)
  entities[row, '_tableOrder'] = attribs[
    f.tableName==value,
    '_tableOrder'
  ].to_list()[0][0]
  
  # set row order = always 0
  entities[row, '_rowOrder'] = 0
  

#///////////////////////////////////////////////////////////////////////////////

# ~ 2 ~
# Combine objects

attribs.names = {'name': 'columnName'}
entities.names = {'name': 'tableName'}

emx2 = dt.rbind(attribs, entities, force=True)[:, :, dt.sort(f._tableOrder, f._rowOrder)]

# drop columns
del emx2[:, [
  'nillable',
  'unique',
  'visible',
  'readOnly',
  'aggregateable', # not available ?
  'idAttribute',
  'labelAttribute',
  'lookupAttribute',
  'rangeMax',
  'rangeMin',
  'defaultValue',
  'auto',
  'partOfAttribute',
  'entity',
  'refEntity',
  'package',
  'abstract',
  'backend',
  'dataType',
  '_tableOrder',
  '_rowOrder',
]]


# convert reference tables to ontologies where attributes are: 'id' and 'label'
newOntologies = []
for table in dt.unique(emx2['tableName']).to_list()[0]:
  
  # find pseudo-ontologies based on attribute names
  if emx2[f.tableName==table,'columnName'].to_list()[0] == [None, 'id','label']:
    
    # set flag to remove old ref tables and log
    emx2[(f.tableName==table) & (dt.re.match(f.columnName, 'id|label')), 'remove'] = True
    if table not in newOntologies:
      newOntologies.append(table)
    
    # set first row (i.e., table name) as the ontology entry
    emx2[(f.tableName==table) & (f.columnName==None), 'tableType'] = 'ONTOLOGIES'
    
    # find all references in the model and make sure the columnType is ontology or ontology array
    for column in emx2[f.refTable==table, 'columnName'].to_list()[0]:
      currentType = emx2[(f.refTable==table) & (f.columnName==column), 'columnType'].to_list()[0][0]
      if currentType in ['ref','ref_array']:
        emx2[(f.refTable==table) & (f.columnName==column), 'columnType'] = currentType.replace('ref','ontology')
    

# drop old ontology refs
emx2 = emx2[f.remove!=True, :][:, :, dt.sort(f.tableType)]
del emx2['remove']

# convert bool8 to string
for column in emx2.names:
  if (emx2[column].type == dt.Type.bool8):
    emx2[column] = emx2[:, as_type(f[column], dt.Type.str32)]


emx2.to_csv('./erns/cranio/ern_cranio_molgenis.csv')


#///////////////////////////////////////////////////////////////////////////////

# ~ 3 ~
# Parse other sheets and save to file

wb = pd.ExcelFile(file)
wb.sheet_names

tablesToIgnore = [
  'packages',
  'entities',
  'attributes',
  'cranio_subject',
  'cranio_visits_cleft',
  'cranio_visits_synostosis',
  'cranio_variant',
  'cranio_person',
  'cranio_family',
  'cranio_fammember'
]

for sheet in tqdm(wb.sheet_names):
  if sheet not in tablesToIgnore:
    table = re.sub('cranio_','',sheet)
    data = wb.parse(sheet_name=sheet)
    
    if table in newOntologies:
      data = data.rename(columns={'label': 'name'}) \
        .drop('id', axis=1)
    
    data.to_csv(
      f'erns/cranio/lookups/{table}.csv',
      index=False,
      quoting=csv.QUOTE_NONNUMERIC,
      encoding='utf-8'
    )
    