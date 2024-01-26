# ///////////////////////////////////////////////////////////////////////////////
# FILE: build.py
# AUTHOR: David Ruvolo
# CREATED: 2023-05-19
# MODIFIED: 2023-05-19
# PURPOSE: build example dataset
# STATUS: in.progress
# PACKAGES: **see below**
# COMMENTS: NA
# ///////////////////////////////////////////////////////////////////////////////

from os import path
from random import getrandbits
import csv
from datatable import dt, f, as_type
from tqdm import tqdm
from erns.utils.ror import RorClient


def to_csv(data, file):
    data.to_pandas().to_csv(file, index=False, quoting=csv.QUOTE_ALL)


def calculate_age(recent, earliest):
    """Calculate age between two dates"""
    return round(int((recent - earliest).days) / 364.25, 0)


# ///////////////////////////////////////////////////////////////////////////////


ror = RorClient()

# query for institutions
API_URL = 'https://api.ror.org/organizations'
QUERY_COUNTRY = '+OR+'.join([
    "country.country_code:NL",
    "country.country_code:BE",
])

QUERY_TYPE = '+OR+'.join([
    'types:Education',
    'types:Healthcare',
    'types:Archive',
    'types:Government',
    'types:Nonprofit',
])

url = f"{API_URL}?query.advanced=({QUERY_COUNTRY})+AND+({QUERY_TYPE})"
response = ror.session.get(url)
pages = response.json().get('number_of_results')


# get results for each page
rawdata = []
for page in tqdm(range(0, pages)):
    response = ror.session.get(f"{url}&page={page+1}")
    if response.ok:
        json = response.json()
        if json.get('items'):
            rawdata.extend(json.get('items'))

# extract data of interest
data = []
for row in rawdata:
    data.append({
        'id': row.get('id'),
        'code': path.basename(row.get('id')),
        'name': row.get('name'),
        'types': ','.join([type for type in row.get('types')]) if row.get('types') else None,
        'city': row.get('addresses', {})[0]['city'],
        'country': row.get('country', {}).get('country_name'),
        'country_code': row.get('country', {}).get('country_code'),
    })


# get institution-level information
for row in tqdm(data):
    response = ror.session.get(f"{API_URL}/{row['code']}")
    if response.ok:
        json = response.json()
        if json:
            row['established'] = json['established']
            row['latitude'] = json['addresses'][0].get('lat')
            row['longitude'] = json['addresses'][0].get('lng')


# ///////////////////////////////////////////////////////////////////////////////

# ~ 1 ~
# Prepare Example dataset for the "statistics" table

# convert to datatable
orgs = dt.Frame(data)
orgs = orgs[:, dt.first(f[:]), dt.by(f.name)]


# ~ 1a ~
# calculate the oldest universities
orgs['est'] = dt.Frame([
    f"{value}-07-01" if value else value
    for value in orgs['established'].to_list()[0]
])

orgs['today'] = "2023-06-01"
orgs['est'] = orgs[:, as_type(f.est, dt.Type.date32)]
orgs['today'] = orgs[:, as_type(f.today, dt.Type.date32)]

orgs['age'] = dt.Frame([
    calculate_age(recent=row[1], earliest=row[0]) if all(row) else None
    for row in orgs[:, (f.est, f.today)].to_tuples()
])

# select top 10
oldestOrgs = orgs[f.age != None, :][:, :, dt.sort(
    'age', reverse=True)][0:10, (f.name, f.age)]

# set order (descending)
oldestOrgs['valueOrder'] = dt.Frame([
    row[0] for row in enumerate(oldestOrgs['name'].to_list()[0])
])

# set row ID
oldestOrgs['id'] = dt.Frame([
    f"oldest.orgs.{value}" for value in oldestOrgs['valueOrder'].to_list()[0]
])

# set component
oldestOrgs['component'] = 'oldest.organisations'

# set names
oldestOrgs.names = {
    'name': 'label',
    'age': 'value'
}

# ///////////////////////////////////////

# ~ 1b ~
# summarise institutions by type

# summarise data by f.types
countByType = orgs[
    :, dt.count(), dt.by(f.types)
][:, :, dt.sort(f.count, reverse=True)]

# set order (descending)
countByType['valueOrder'] = dt.Frame([
    row[0]
    for row in enumerate(countByType['types'].to_list()[0])
])

# set row ID
countByType['id'] = dt.Frame([
    f"org.type.{value}"
    for value in countByType['valueOrder'].to_list()[0]
])

# set component
countByType['component'] = 'organisations.by.type'

# set names
countByType.names = {
    'types': 'label',
    'count': 'value'
}

# ///////////////////////////////////////


# ~ 1c ~
# Prepare tables

# create ontology for organistations
orgs['codesystem'] = 'ROR'
orgs.names = {'id': 'ontologyTermURI'}

organisations = orgs[:, (
    f.name,
    f.codesystem,
    f.code,
    f.ontologyTermURI,
    f.city,
    f.country,
    f.latitude,
    f.longitude
)]

# create dataproviders table
dataproviders = orgs[:, (f.code, f.name)]
dataproviders.names = {
    'code': 'providerIdentifier',
    'name': 'organisation'
}
dataproviders['hasSubmittedData'] = dt.Frame([
    getrandbits(1)
    for value in dataproviders['providerIdentifier'].to_list()[0]
])

dataproviders['hasSubmittedData'] = dataproviders[
    :, as_type(f.hasSubmittedData, dt.Type.bool8)]
dataproviders['hasSubmittedData'] = dataproviders[
    :, as_type(f.hasSubmittedData, dt.Type.str32)]

# create stats table
stats = dt.rbind(oldestOrgs, countByType)

# create components
components = dt.unique(stats['component'])
components.names = {'component': 'name'}

components[
    f.name == 'oldest.organisations', 'definition'] = 'top 10 oldest organisations'
components[
    f.name == 'organisations.by.type', 'definition'
] = 'number of organisations by type (e.g., healthcare, education, government, etc.)'


to_csv(components, 'emx2/test/components.csv')
to_csv(organisations, 'emx2/test/organisations.csv')
to_csv(dataproviders, 'emx2/test/dataproviders.csv')
to_csv(stats, 'emx2/test/statistics.csv')
