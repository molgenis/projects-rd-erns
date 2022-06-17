#'////////////////////////////////////////////////////////////////////////////
#' FILE: dataproviders_cleaner.py
#' AUTHOR: David Ruvolo
#' CREATED: 2022-06-17
#' MODIFIED: 2022-06-17
#' PURPOSE: cleaning script for dataproviders
#' STATUS: experimental
#' PACKAGES: pandas
#' COMMENTS: NA
#'////////////////////////////////////////////////////////////////////////////

import pandas as pd
from python.api.ror import RorClient
import csv

ror = RorClient()

data = pd.read_csv('data/dataproviders.csv').to_dict('records')
dataproviders = []

for row in data:
  q=row['projectName']
  print('Querying', q)
  response = ror.searchOrganizations(query=q)
  result=response[0]
  newProvider = {
    'name': result.get('name'),
    'displayName': result.get('name'),
    'city': result.get('addresses')[0]['city'],
    'country': result.get('country').get('country_name'),
    'longitude': result.get('addresses')[0].get('lng'),
    'latitude': result.get('addresses')[0].get('lat'),
    'codesystem': 'ROR',
    'code': result.get('id'),
    'iri': result.get('id'),
    'projectName': q,
    'verifiedResult': ''
  }
  dataproviders.append(newProvider)

pd.DataFrame(dataproviders).to_csv(
  path_or_buf='data/dataproviders_clean.csv',
  index=False,
  encoding="utf-8",
  quoting=csv.QUOTE_NONNUMERIC
)


response = ror.searchOrganizations(query="")
result=response[0]
{
    'name': result.get('name'),
    'displayName': result.get('name'),
    'city': result.get('addresses')[0]['city'],
    'country': result.get('country').get('country_name'),
    'longitude': result.get('addresses')[0].get('lng'),
    'latitude': result.get('addresses')[0].get('lat'),
    'codesystem': 'ROR',
    'code': result.get('id'),
    'iri': result.get('id')
}

#//////////////////////////////////////////////////////////////////////////////

# ~ 0 ~
# Prepare Dataset
# import raw provider dataset and clean column names and init columns to
# match the shape of the entity

# data = pd.read_excel('data/GENTURIS registry-Prefix.xlsx')[[
#   'Name of Healthcare Provider - instituut (bron: genturis website)',
#   'city',
#   'country'
# ]]

# data=data.rename(columns={
#   'Name of Healthcare Provider - instituut (bron: genturis website)': 'projectName'
# })

# data[[
#   'name',
#   'displayName',
#   'hasSubmittedData',
#   'longitude',
#   'latitude',
#   'codesystem',
#   'code',
#   'iri'
# ]] = ''

# data=data[[
#   'name',
#   'displayName',
#   'hasSubmittedData',
#   'city',
#   'country',
#   'longitude',
#   'latitude',
#   'codesystem',
#   'code',
#   'iri',
#   'projectName'
# ]]
# data.to_csv('data/dataproviders.csv',index=False)